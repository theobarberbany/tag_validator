# Tag Validator

A script to validate inputted tags.

optional arguments:
  -h, --help            show this help message and exit

  -f INPUTFILE, --file INPUTFILE
                        pass a file containing tags to be checked

  -d USER, --database USER
                        toggle database mode

  -m MANIFEST FILE, --manifest MANIFEST FILE
                        supply a manifest to check

database readonly user : warehouse_ro

#To Do :
 
 Serialise data from database, pull local copy at program initialisation - only one
 connection needed instead of many. 

 Port to Js web app:
