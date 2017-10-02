#!/USR/bin/python
import os
import sys
import numpy as np
import argparse
import mysql.connector
import collections
import pprint
import pandas as pd
import time
import json 
pp = pprint.PrettyPrinter(indent=4) #pretty printing lib for dictionaries
###############################
##Add Arguments to be parsed###
###############################
parser = argparse.ArgumentParser(description="Checks if  the supplied tags differ enough.")
parser.add_argument("-f", "--file", dest='inputfile', nargs=1, type=str,
                    help="pass a file containing tags to be checked")
parser.add_argument("-d", "--database", type=str, nargs=1,
                    metavar=("USER"),
                    help="toggle database mode")
parser.add_argument("-m", "--manifest", type=str, nargs=1,
                    metavar=("MANIFEST FILE"),
                    help="supply a manifest to check")
parser.add_argument("-v", "--verbose", action="store_true",
                    help="Increace output verbosity")

args = parser.parse_args()


##########################
###Function Definitions###
##########################
#Basic Functionality

#function to check each tag is a valid combination of ATCG
def check_bases(a_list):
    for tag in a_list:
        for base in tag:
            if (base == 'A') or (base == 'T') or (base == 'C') or (base == 'G') or (base == 'N'):
                pass
            else:
                print("Tag {} contains invalid bases : {}".format(tag, base))
                # sys.exit()

#function to check for duplicate tags

def get_dups(a_list):
    duplicates = []
    for i in range(len(a_list)):
        for j in range(i+1, len(a_list)):
            if a_list[i] == a_list[j]:
                duplicates.append(a_list[i])
    if len(duplicates) > 0:
        dup_cut = list(set(duplicates))
        for i in range(len(dup_cut)):
            print("Duplicate Tag Found : {} ".format(dup_cut[i]))
        print("Found {} total duplicates\n".format(len(dup_cut)))

#Function to compare two tags, returns the degree to which they differ.
def difference(tag1, tag2):
    if len(tag1) != len(tag2):
        sys.exit('Tag length mismatch')
    counter = 0
    for char in range(len(tag1)):
        if tag1[char] != tag2[char]:
            counter += 1
    return counter

#Function to check if a list of tags differ by at least 3.
def check_tags(tag_list):
    bad_tags = {}
    for i in range(len(tag_list)):
        for j in range(i+1, len(tag_list)):
            dif = difference(tag_list[i], tag_list[j])
            if dif < 3:
                bad_tags[tag_list[i]] = [tag_list[j], dif]
    for t, v in bad_tags.items():
        print("Comparing {} to {} : Insufficient difference of {}".format(t, v[0], v[1]))


#function to calculate reverse compliment of a tag
def reverse_complement(tag):
    complement = {'A': 'T', 'C': 'G', 'G': 'C', 'T': 'A'}
    alt_map = {'N':'0'}
    for k, v in alt_map.items():
        tag = tag.replace(k, v)
    bases = list(tag)
    bases = reversed([complement.get(base, base) for base in bases])
    bases = ''.join(bases)
    for k, v in alt_map.items():
        bases = bases.replace(v, k)
    return bases

#check if groups of tags are suceptible to cross talk / complexity issues
def check_crosstalk_col(dataframe, colno): #checks a single col
    cols = []
    for i in range(len(dataframe)):
        cols.append(dataframe[0][i][colno])
    return cols

def check_crosstalk(taglist):
    df = pd.DataFrame(taglist)
    nocols = len(taglist[0]) # assume all tags are same length
    listcols = []
    proportions = {}
    for i in range(nocols):
        listcols.append(check_crosstalk_col(df, i))

    for i in range(len(listcols)):
        proportions["Col {}".format(i)] = [0, 0, 0, 0] # A,T,C,G

    for i in range(len(listcols)):
        for j in range(len(listcols[i])): #asssuming again all tags are same length
            if listcols[i][j] == "A":
                proportions["Col {}".format(i)][0] += 1 
            elif listcols[i][j] == "T":
                proportions["Col {}".format(i)][1] += 1 
            elif listcols[i][j] == "C":
                proportions["Col {}".format(i)][2] += 1 
            elif listcols[i][j] == "G":
                proportions["Col {}".format(i)][3] += 1 
            else:
                pass
    for col, lst in proportions.items():
        print(" {} has {:.2f}% A, {:.2f}% T, {:.2f}% C, {:.2f}% G".format(col, 
            ((lst[0]/sum(lst))*100), ((lst[1]/sum(lst))*100), ((lst[2]/sum(lst))*100),
            ((lst[3]/sum(lst))*100) )) 
    print("\n")
    if args.verbose:
        print(proportions) #numerical proportions

#Database functionality

def db_build_cache():
    tag_dict = collections.defaultdict(list)
    tag_conn = mysql.connector.connect(user=args.database[0],
                                       host='seqw-db', database='sequencescape_warehouse', port=3379)
    tag_cursor = tag_conn.cursor()
    tag_query = ("""
                SELECT expected_sequence, tag_group_internal_id, tag_group_name 
                FROM tags 
                WHERE tag_group_internal_id IS NOT NULL
                AND expected_sequence IS NOT NULL
                AND is_current = True
                AND NOT expected_sequence = ""
                """)
    tag_cursor.execute(tag_query)
    rows = tag_cursor.fetchall()
    all_tags = [row[0] for row in rows]
    tag_cursor.close()

    for tag in range(len(rows)):
        tag_dict[rows[tag][0]].append((rows[tag][1], rows[tag][2]))

    tag_conn.close() # (Don't forget to close the db connection)
    return tag_dict

#function to check if passed tags are in any of the tag groups
#note that now the single tag check must have a db connection already open
def db_check_tag(tag):
    return cache_data[tag]

def db_check_list(a_list): #needs work
    tag_dict = {}
    for tag in range(len(a_list)):
       tag_dict[a_list[tag]] = db_check_tag(a_list[tag]) ;

    for key, value in tag_dict.items():
        if value == []:
            print("Tag {} not found in database, checking reverse complement: {}".format(key,reverse_complement(key)))
            checked_revcomp = db_check_tag(reverse_complement(key))
            if checked_revcomp == []:
                print("Nothing found \n")
            else:
                print(checked_revcomp)
                print("\n")

    #return group breakdowns
    #extract values independently of keys
    values = []
    for key, value in tag_dict.items():
        values.append(value)
    #flatten list 
    flat_list = [item for sublist in values for item in sublist]
    distinct = list(set(flat_list))
    for i in range(len(distinct)):
        print("{} {},  Matches : {}".format(distinct[i][0], distinct[i][1], flat_list.count(distinct[i])))
    print("\n")

    # print("DEBUG HERE")
    # pp.pprint(flat_list)
    
    if args.verbose:
        print("verbose output: \n")
        pp.pprint(tag_dict)
        print("\n")


#Serialisation of database queries/cache stuff after here
#Should be an hour (minutes)
max_cache_age = 60 * 60
cache_filename = 'cache.json'
refresh = False

try:
    with open(cache_filename, 'r') as cache:
        cached = json.load(cache)

    if(time.time() > cached['timestamp'] + max_cache_age):
        print("Cache bad. Reloading from database \n")
        refresh = True

except IOError:
    print("Error opening {}: Reloading cache from database (Perhaps it does not exist?)".format(cache_filename))
    refresh = True

if refresh:
    #Cache old, rebuild:
    cache_data = db_build_cache()
    #Update cache file
    data = {'tag_db': cache_data, 'timestamp': time.time()} #Record timestamp to cache dict
    with open(cache_filename, 'w') as cache:
        json.dump(data, cache, indent = 4)
else:
    #Use cache
    cache_data = cached['tag_db']

##########################
######Parse Arguments#####
##########################
#File Mode
if args.inputfile is not None:
    #do some stuff when an inputfile is passed
    mydir = os.getcwd()
    with open(os.path.join(mydir,args.inputfile[0]),'r') as f:
        read_data = f.read()
    
    if args.verbose:
        print("Data passed : \n")
        print(read_data)

    #split input file into individual tags
    a_file = read_data.split()
    #check the passed tags are valid combinations of ATCG
    check_bases(a_file)
    #check tags for duplicates
    get_dups(a_file)
    #check the entire list of tags
    checked_tags = check_tags(a_file)
    #check for complexity issues
    check_crosstalk(a_file)

#Deal with a manifest
if args.manifest is not None:
    manifest = pd.read_csv(args.manifest[0], skiprows = 9, usecols=[2,3], header=None)
    manifest.columns = ['tag1','tag2'] #rename cols to make life simple
    manifest['long_tag'] = manifest['tag1'].map(str) + manifest['tag2'] # concatenate the two tags
    # print(manifest)
    #deal with manifests with only 1 col of tags
    if manifest.isnull().values.any(): 
        taglist = []
        for i in range(len(manifest.loc[:,'tag1'])):
            taglist.append(manifest.loc[i]['tag1'])
        
        #check the passed tags are valid combinations of ATCG
        check_bases(taglist)
        #check tags for duplicates
        get_dups(taglist)
        #check the entire list of tags
        checked_tags = check_tags(taglist)
#check for complexity issues
        check_crosstalk(taglist)
    #manifests with two tag cols
    else:
        taglist1 = []
        taglist2 = []
        long_tags = []
        for i in range(len(manifest.loc[:, 'tag1'])):
            taglist1.append(manifest.loc[i]['tag1'])

        for i in range(len(manifest.loc[:, 'tag2'])):
            taglist2.append(manifest.loc[i]['tag2'])
        manifest['long_tag'] = manifest['tag1'].map(str) + manifest['tag2']

        for i in range(len(manifest.loc[:, 'long_tag'])):
            long_tags.append(manifest.loc[i]['long_tag'])

        #check the passed tags are valid combinations of ATCG
        check_bases(long_tags)
        #check tags for duplicates
        get_dups(long_tags)
        #check the entire list of tags
        checked_tags = check_tags(long_tags)
        #check for complexity issues
        print("Composition for Tag 1 : \n")
        check_crosstalk(taglist1)
        print("Composition for Tag 2 : \n")
        check_crosstalk(taglist2)

#Check the database
if args.database is not None:
    if args.inputfile is not None:
        print("Occurences of tags in database: \n")
        db_check_list(a_file)
    elif args.manifest is not None:
        #check if there are one or two cols
        if manifest.isnull().values.any():
            db_check_list(taglist)
        else:
            print("Occurences of tag1 in database: \n")
            db_check_list(taglist1)
            print("Occurences of tag2 in database: \n")
            db_check_list(taglist2)
            print("Occurences of compound tags in database: \n")
            db_check_list(long_tags)
elif args.database == None and args.inputfile == None and args.manifest == None:
    print("No arguments passed, try running with -h")
