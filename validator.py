#!/usr/bin/python
import os
import sys
import numpy as np
import argparse

parser = argparse.ArgumentParser(description="Checks if  the supplied tags differ enough.")
parser.add_argument("-f", "--file", dest='inputfile', nargs=1, type=str,
        help="pass a file containing tags to be checked")
parser.add_argument("-d", "--database", type=str, nargs=2,
        metavar=("USER","PASSWORD"),
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
        print("Tags ok")
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
