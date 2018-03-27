'''Contain tree for cyk algorithm.
NodeR contain some addition functions
for parse to operator tree convetion (convert func in tree.py)'''
from functools import reduce


class Node():
    def __init__(self, rule, parent=None, children=[],
                 visited=False):
        self.rule = rule
        self.parent = parent
        # self.left = left
        # self.right = right
        self.children = children
        self.visited = visited

    def add_parent(self):

        '''Add self to each child as parent'''

        for child in self.children:
            child.parent = self
            child.add_parent()

    def __repr__(self, begin=0):

        '''Show node and all it's children'''

        start = reduce(lambda x, acc: x+acc, [' ' for i in range(begin)], "")
        begin += 3
        out = str(self.rule)
        for id, child in enumerate(self.children):
            if child is not None:
                out += ('\n' + start + "child %s: " % (id)
                        + str(child.__repr__(begin)))
        return(out)


class NodeR(Node):
    ''' Node for transformation to operator's tree.

    :atr name is either like 'a' or '+' or 'AB'.
    '''
    def __init__(self, rule, parent=None, children=[],
                 visited=False):
        Node.__init__(self, rule, parent, children, visited)

        self.trs = ['a']
        self.ops = ['+', '-', '*']
        self.brs = ['(', ')', 'w', 'f']
        self.name = self.rule[1]

    def get_unvisited(self):
        unvisited = [child for child in self.children
                     if not child.visited]
        return(unvisited)

    def find_child(self, node):
        
        '''Find node_id in self.children'''
        
        for id, child in enumerate(self.children):
            if child.name == node.name:
                return(id)
            
    def get_operators(self):

        ''' Find children with node op'''

        ops = self.ops
        child_ops = []
        for id, child in enumerate(self.children):
            if child.name in ops:
                child_ops.append(child)
                
        return(child_ops)

    def find_op_child(self):
        
        ''' Find first operator child'''

        ops = self.ops
        for id, child in enumerate(self.children):
            if child.name in ops:
                return(child)
        
    def find_unop_child(self):
        
        ''' Find first unoperator child'''

        ops = self.ops
        for id, child in enumerate(self.children):
            if child.name not in ops:
                return(child)
    
    def find_br_child(self):
        
        ''' Find first brach child'''

        brs = self.brs
        for id, child in enumerate(self.children):
            if child.name in brs:
                return(child)
    
    def find_term_child(self):
        
        ''' Find first brach child'''

        trs = self.trs
        for id, child in enumerate(self.children):
            if child.name in trs:
                return(child)
    

def copy_node(node: NodeR)->NodeR:
    new_node = NodeR(rule=node.rule,
                     parent=node.parent,
                     children=node.children,
                     visited=node.visited)
    return(new_node)
