import sys
from pydal import *
import querytree as qt
import cx_Oracle
from query_index import *
from qp_parsers import *

oracle_uri ='oracle://web2py/DePaul123@' + cx_Oracle.makedsn('rasinsrv01.cstcis.cti.depaul.edu', 1521, 'oracle11g')
# print cx_Oracle.makedsn('localhost', 1521, 'oracle11g')

query1 = "select d_year, s_city, p_brand1, sum(lo_revenue - lo_supplycost) as profit from dwdate, customer, supplier, part, lineorder where lo_custkey = c_custkey and lo_suppkey = s_suppkey and lo_partkey = p_partkey and lo_orderdate = d_datekey and s_nation = 'UNITED STATES' and (d_year = 1997 or d_year = 1998) and p_category = 'MFGR#14' group by d_year, s_city, p_brand1 order by d_year, s_city, p_brand1"

# creates dictionary object of the query file. This object can be used for testing.
q_index = create_index('SSBM_original_queries.sql')
#query  = q_index['Q4.3']

#print 'Working with query : ', query 

def run_query(uri, query):
    """
    Executes a query and retrieves text response.
    """
    db = DAL(uri)
    # Flush buffer
    # db.executesql("alter system flush buffer_cache;")
    db.executesql("explain plan for " + query)
    q = db.executesql('select * from TABLE(dbms_xplan.display)')
    for l in q:
        print l
    print '\n\n\n'
    return q


def clean_query(query):
    """
    Removes any line added for human readability.
    """
    query = str(query).split('), (')
    query.pop(0)
    query.pop(0)
    q = []
    for i in query:
        q.append(i[1::].replace('*', '').strip())

    q.sort()
    q = q[5::]
    q.pop()
    scores = []
    info = []

    for i in q:
        if ('-') in i:
            info.append(i)
        else:
            scores.append(i[1::].strip())

    scores.pop(0)
    info.pop(0)

    scores.sort(key = lambda x: int(x.split('|')[0]))
#    print '******************************************'
#    for ln_scores in scores:
#        print ln_scores
#    print '******************************************'
#    print '\n\n\n'
#    for ln_info in info:
#        print ln_info
#    print '******************************************'
#    print '\n\n\n'

    return (scores, info)

def get_nodes(scores, info):
    """
    Converts query plan table into a list of node data.
    In the case of Oracle, combines data from query plan table and predicate table
    """
    nodes = []
    for i in scores:
        # (tree level, query plan row, label)
        split_line = i.split('|', 1)
        qpr = split_line[0]
        tl = len(split_line[1]) - (len(split_line[1].lstrip())) - 1

        split_line = split_line[1].split('|', 1)
        query_data = (''.join(x[0:-2] for x in split_line)).strip()

        nodes.append([tl, qpr, query_data])

        for i in range(len(nodes)):
            for j in range(len(info)):
                if nodes[i][1].strip() == info[j].split('-')[0].strip():
                    nodes[i][2] += info[j].split('-')[1]
        # for node in nodes:
        #     for i in info:
        #         if node[1].strip() == i.split()[0].strip():
        #             print i

    return nodes

def get_tree(tree_list):
    """
    Takes a list of nodes and returns a binary tree object
    """
    root = qt.QueryTree(tree_list[0][2])
    tree = root
    for i in range(1, len(tree_list)-1):
        if tree_list[i][0] == tree_list[i+1][0]:
            tree.insertLeft(tree_list[i][2])
            tree.insertRight(tree_list[i+1][2])
            i += 1
        else:
            tree.insertRight(tree_list[i][2])
        tree = tree.getRightChild()

    return root



#rawq = run_query(oracle_uri, query)
#scores, info = clean_query(rawq)
#nodes = get_nodes(scores, info)
#t = get_tree(nodes)
#print(t)
for key in q_index:
    query_plan = run_query(oracle_uri, q_index[key])
    parser = Oracle_QP_Parser(query_plan)
    fn = '../data/' + key + '.json'
    f = open(fn, 'w')
    f.write(parser.qpTree().toJSON())
    f.close()

