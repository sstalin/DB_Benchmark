from abc import ABCMeta, abstractmethod
import re, json

class QP_Tree:
    @abstractmethod
    def getRoot(self):
        pass

    def toJSON(self):
        pass

    def serializer(self, root):
        """
        Recursive method to serialize object references e.a. left, right 
        properties
        """
        if root.left:
            root.left = self.serializer(root.left)
        if root.right:
            root.right = self.serializer(root.right)
        as_dict = root.__dict__
        return as_dict

class Oracle_QP_Tree(QP_Tree):
    def __init__(self, root):
        self.root = root

    def getRoot(self):
        return self.root
        
    def toJSON(self):
        callback = QP_Tree().serializer
        return json.dumps(self.root, indent=4, sort_keys=True, default=callback)

class QP_Node:
    """
    Base class for all Query Plan (QP) nodes
    """
    @abstractmethod
    def has_children(self):
        pass

    @abstractmethod
    def getLeft(self):
        pass

    @abstractmethod
    def getRight(self):
        pass

    @abstractmethod
    def insertRight(self):
        pass

    @abstractmethod
    def insertLeft(self):
        pass

class Oracle_QP_Node(QP_Node):
    def __init__(self, qp_row):
        col =  qp_row[0].split('|')[1 : -1]
        self.has_predicate_info = '*' in col[0]
        self.id = col[0].strip().replace('*', '').strip()
        self.operation = col[1].rstrip()
        self.operation_indent = len(self.operation) - len(self.operation.lstrip())
        self.relation_name = col[2].strip()
        self.rows = col[3].strip()
        self.bytes = col[4].strip()
        self.cost = None
        if col[5].strip():
            self.cost = re.split("([1-9]+)", col[5])[1]
        self.time = col[6].strip()
        self.predicate_string = None
        self.left = None
        self.right = None
        
    def has_children(self):
        return self.left is not None or self.right is not None
        
    def insertLeft(self, node):
        self.left = node

    def insertRight(self, node):
        self.right = node

class QP_Parser:
    """ Common abstract class for all parsers"""
    @abstractmethod
    def qpTree(self):
        """ creates query plan tree"""
        pass
    
class Oracle_QP_Parser(QP_Parser):
    def __init__(self, q_plan):
        self.q_plan = q_plan
        self.SPLIT_PATTERN = 'Predicate Information' 
        self.plan_predicates_split()        

    def plan_predicates_split(self):
        for i, ln in enumerate(self.q_plan):
            print '-------  ', str(ln), '\n'
            if type(ln) == tuple:
                if re.match(self.SPLIT_PATTERN, str(ln[0])):
                    self.plan = self.q_plan[5:i-2]
                    self.predicate_table = self.predicateMap(self.q_plan[i+3:])

    def predicateMap(self, pred_list):
        """
        Converts predicate list information to a dictionary for 
        ease of work 
        """
        table = {}
        id = None
        info = ""
        pred_list = [row[0].strip() for row in pred_list]
        for row in reversed(pred_list):
            if "-" in row:
                temp = row.split('-')
                id = temp[0].strip()
                info = temp[1].strip() + ',' +  info
                table[id] = info[:-1] # removing trailing ,
            else:
                info = row + ',' + info
        return table

    def generateNodes(self):
        """
        Geneartes a list of all nodes that will be included in the tree
        """
        node_list = []
        for row in self.plan:
            node = Oracle_QP_Node(row)
            if node.has_predicate_info:
                node.predicate_string = self.predicate_table[node.id]
            node_list.append(node)
        return node_list
                

    def genTree(self, node_list, root=None):
        """ Recursive QP tree generator"""
        if len(node_list) == 0:
            return Oracle_QP_Tree(root)
        if root is None and (len(node_list) > 0):
            root = node_list.pop()
        if root and (len(node_list) > 0):
            is_siblings = node_list[-1].operation_indent == root.operation_indent
            if is_siblings:
                left = node_list.pop()
                right = root
                root = node_list.pop()
                root.left = left
                root.right = right
            else:
                right = root
                root = node_list.pop()
                root.right = right
                root.left = None
        return self.genTree(node_list, root)

        
    def qpTree(self):
        node_list = self.generateNodes()
        try:
            tree = self.genTree(node_list = node_list)
        except IndexError as e:
            print e
        return tree

    
