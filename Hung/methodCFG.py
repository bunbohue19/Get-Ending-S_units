import javalang
import networkx as nx
from stmtCFG import buildNode
import stmtCFG
class cfg:
    def createCFG(self,method:javalang.tree.MethodDeclaration):
        G=nx.DiGraph()
        for _,node in method:
            G.add_node(method)
        prev=[method]
        for stmt in method.body:
            prev,G=buildNode(G,prev,stmt)
            
        return G


            