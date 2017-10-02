##Leaving this in as it might be useful at some point
def db_check_tag_old(tag):
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