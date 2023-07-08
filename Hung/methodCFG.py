import javalang
import networkx as nx
from stmtCFG import buildNode
class cfg:
    def createCFG(self,method:javalang.tree.MethodDeclaration):
        G=nx.DiGraph()
        G.add_node(method)
        prev=method
        for stmt in method.body:
            prev=buildNode(g,prev,stmt)
        return G


            