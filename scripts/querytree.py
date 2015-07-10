class QueryTree():

    def __init__(self,rootid):
      self.left = None
      self.right = None
      self.rootid = rootid
      self.values = {}
      self.children = [self.left, self.right]

    def getLeftChild(self):
        return self.left
    def getRightChild(self):
        return self.right
    def setNodeValue(self,value):
        self.rootid = value
    def getNodeValue(self):
        return self.rootid

    def insertRight(self,newNode):
        if self.right == None:
            self.right = QueryTree(newNode)
        else:
            tree = QueryTree(newNode)
            tree.right = self.right
            self.right = tree

    def insertLeft(self,newNode):
        if self.left == None:
            self.left = QueryTree(newNode)
        else:
            tree = QueryTree(newNode)
            self.left = tree
            tree.left = self.left

    def process_values(self, values_list):
        values_list = values_list.split("|")

        self.values["operation"] = values_list[0].strip()
        self.values["rows"] = values_list[1].strip()
        self.values["bytes"] = values_list[2].strip()
        if not values_list[-1] is '':
            self.values["predicate"] = [x for x in values_list[-1].split(", ")]
        return str(self.values)

    def getStr(self, level=0):
        ret = "\t"*level + self.process_values(self.rootid)+"\n"
        for child in [self.left, self.right]:
            if not child is None:
                ret += child.getStr(level+1)
        return ret

    def __str__(self):
        return self.getStr()
