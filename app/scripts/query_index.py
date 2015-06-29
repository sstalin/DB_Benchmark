import sys, re

#fn = sys.argv[1]

def create_index(fn):
    f = open(fn, 'r')
    q_index = {}
    q_name = None
    q_str = ''
    for line in f:
        if line in ['\n', '\r\n']:
            q_str = ''
            continue
        if '-- Q' in line:
            m = re.search('(?<=-- )\w+\.\w+', line)
            q_name = m.group(0)
            continue
        q_str+= line
        q_index[q_name] = q_str
    return q_index
