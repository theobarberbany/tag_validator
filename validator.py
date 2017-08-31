#!/usr/bin/python
import os
import sys
import numpy as np
import argparse
import mysql.connector
import collections
import pprint

pp=pprint.PrettyPrinter(indent=4)


parser = argparse.ArgumentParser(description="Checks if  the supplied tags differ enough.")
parser.add_argument("-f", "--file", dest='inputfile', nargs=1, type=str,
        help="pass a file containing tags to be checked")
parser.add_argument("-d", "--database", type=str, nargs=1,
        metavar=("USER"),
        help="toggle database mode")

args = parser.parse_args()


#function to check each tag is a valid combination of ATCG
def check_bases(a_list):
    for tag in a_list:
        for base in tag:
            if (base == 'A') or (base == 'T') or (base =='C') or (base == 'G') or (base == 'N'):
                pass
            else:
                print("Tag {} contains invalid bases : {}".format(tag, base))
                sys.exit()

#function to check for duplicate tags

def get_dups(a_list):
    duplicates = []
    for i in range(len(a_list)):
        for j in range(i+1, len(a_list)):
            if a_list[i] == a_list[j]:
                duplicates.append(a_list[i])
    if len(duplicates) > 0:
        sys.exit("Duplicate Tag Found : {}   Quitting.".format(duplicates[0]))

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
    for i in range(len(tag_list)):
        for j in range(i+1, len(tag_list)):
            dif = difference(tag_list[i],tag_list[j])
            if dif < 3:
               return("Comparing {} to {} : Insufficient difference of {} \n".format(tag_list[i],tag_list[j],dif))


#function to calculate reverse compliment of a tag
def rev_comp(tag):
    pass
    #do some stuff
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

#File Mode

if args.inputfile is not None:
    #do some stuff when an inputfile is passed
    mydir = os.getcwd()
    print(mydir)
    print(args.inputfile)
    with open(os.path.join(mydir,args.inputfile[0]),'r') as f:
        read_data = f.read()
    print("Data passed : \n")
    print(read_data)
    
    #split input file into individual tags
    split = read_data.split()
    #check the passed tags are valid combinations of ATCG
    check_bases(split)
    #check tags for duplicates
    get_dups(split)
    #check the entire list of tags
    checked_tags = check_tags(split)
    if checked_tags is not None:
        print("Error in provided tags")
        print(checked_tags)
    else:
        print("Tags ok \n")


if args.database is not None:
    tag_dict = {}
    for tag in range(len(split)):
       tag_dict[split[tag]] = db_check_tag(split[tag]) ;

    pp.pprint(tag_dict)
#arraytemp = np.array(split, dtype=bytes)
#array = arraytemp.view('S1').reshape((arraytemp.size, -1))
#print(repr(array))

#transpose so it's easy to reference a col.
#art = array.transpose()
#print(repr(art))

#initialise a counter dictionary entry for every tag, initialise to 0.
#counters = {}
#for tagnum in range(len(split)):
#    counters["tag{0}".format(tagnum)]=0
