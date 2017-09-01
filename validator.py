#!/usr/bin/python
import os
import sys
import numpy as np
import argparse
import mysql.connector
import collections
import pprint
import pandas as pd
pp=pprint.PrettyPrinter(indent=4)


parser = argparse.ArgumentParser(description="Checks if  the supplied tags differ enough.")
parser.add_argument("-f", "--file", dest='inputfile', nargs=1, type=str,
        help="pass a file containing tags to be checked")
parser.add_argument("-d", "--database", type=str, nargs=1,
        metavar=("USER"),
        help="toggle database mode")
parser.add_argument("-m", "--manifest", type=str, nargs=1,
        metavar=("MANIFEST FILE"),
        help="supply a manifest to check")

args = parser.parse_args()

##########################
##########################
###Function Definitions###
##########################
##########################

#function to check each tag is a valid combination of ATCG
def check_bases(a_list):
    for tag in a_list:
        for base in tag:
            if (base == 'A') or (base == 'T') or (base =='C') or (base == 'G') or (base == 'N'):
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
                counter +=1
    return(counter)

#Function to check if a list of tags differ by at least 3.
def check_tags(tag_list):
    bad_tags = {}
    for i in range(len(tag_list)):
        for j in range(i+1, len(tag_list)):
            dif = difference(tag_list[i],tag_list[j])
            if dif < 3:
                bad_tags[tag_list[i]] = [tag_list[j], dif]; 
    for t,v in bad_tags.items():
        print("Comparing {} to {} : Insufficient difference of {}".format(t,v[0],v[1]))


#function to calculate reverse compliment of a tag
complement = {'A': 'T', 'C': 'G', 'G': 'C', 'T': 'A'}
alt_map = {'N':'0'}
def reverse_complement(tag):
    for k,v in alt_map.items():
        tag = tag.replace(k,v)
    bases = list(tag)
    bases = reversed([complement.get(base,base) for base in bases])
    bases = ''.join(bases)
    for k,v in alt_map.items():
        bases = bases.replace(v,k)
    return(bases)


#function to check if passed tags are in any of the tag groups
#probably a good idea to take a list instead of a single tag so no need to open/close
    #multiple times
def db_check_tag(tag):
    tag_conn = mysql.connector.connect(user=args.database[0],
            host='seqw-db',database='sequencescape_warehouse',port=3379)
    tag_cursor = tag_conn.cursor()
    tag_query = ("SELECT DISTINCT tag_group_internal_id,tag_group_name FROM tags WHERE expected_sequence = '{}' AND tag_group_internal_id IS NOT NULL AND is_current = True".format(tag))
    tag_cursor.execute(tag_query)
    rows = tag_cursor.fetchall()
    return(rows)
    tag_cursor.close()
    tag_conn.close() # (Don't forget to close the db connection)

def db_check_list(a_list):
    tag_dict = {}
    for tag in range(len(a_list)):
       tag_dict[a_list[tag]] = db_check_tag(a_list[tag]) ;

    pp.pprint(tag_dict)

    for key, value in tag_dict.items():
        if value == []:
            print("Tag {} not found in database, checking reverse complement: {}".format(key,reverse_complement(key)))
            checked_revcomp = db_check_tag(reverse_complement(key))
            if checked_revcomp == []:
                print("Nothing found")
            else:
                print(checked_revcomp)

##########################
##########################
######Parse Arguments#####
##########################
##########################

#File Mode
if args.inputfile is not None:
    #do some stuff when an inputfile is passed
    mydir = os.getcwd()
    with open(os.path.join(mydir,args.inputfile[0]),'r') as f:
        read_data = f.read()
    print("Data passed : \n")
    print(read_data)

    #split input file into individual tags
    a_file = read_data.a_file()
    #check the passed tags are valid combinations of ATCG
    check_bases(a_file)
    #check tags for duplicates
    get_dups(a_file)
    #check the entire list of tags
    checked_tags = check_tags(a_file)
    print("Finished Processing\n")

#Deal with a manifest
if args.manifest is not None:
    manifest = pd.read_csv(args.manifest[0], skiprows = 9, usecols=[2,3], header=None)
    manifest.columns = ['tag1','tag2'] #rename cols to make life simple
    print(manifest)
    taglist1 = []
    taglist2 = []
    for i in range(len(manifest.loc[:,'tag1'])):
        taglist1.append(manifest.loc[i]['tag1'])

    for i in range(len(manifest.loc[:,'tag2'])):
        taglist2.append(manifest.loc[i]['tag2'])

    #check the passed tags are valid combinations of ATCG
    check_bases(taglist1)
    check_bases(taglist2)
    #check tags for duplicates
    get_dups(taglist1)
    get_dups(taglist2)
    #check the entire list of tags
    checked_tags = check_tags(taglist1)
    checked_tags = check_tags(taglist2)
    
    print("Fininshed Processing \n")

#Check the database
if args.database is not None:
    if args.inputfile is not None:
        db_check_list(a_file)
    elif args.manifest is not None:
        db_check_list(taglist1)
        db_check_list(taglist2)
