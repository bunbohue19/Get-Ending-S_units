import javalang
import networkx as nx

def buildNode(cfg:nx.DiGraph,prev:javalang.ast.Node,node:javalang.ast.Node):
    #interface of build a stmt
    cfgBuilder= stmtCFG(cfg,prev,node)
    return cfgBuilder
class stmtCFG:
    def buildNode(self,cfg:nx.DiGraph,prev:javalang.ast.Node,node:javalang.ast.Node):
        #abstract method to build next node
        if isinstance(node,javalang.tree.IfStatement):
            return self.buildIf(cfg,prev,node)
        elif isinstance(node,javalang.tree.ForStatement):
            return self.buildFor(cfg,prev,node)
        elif isinstance(node,javalang.tree.WhileStatement):
            return self.buildWhile(cfg,prev,node)
        elif isinstance(node,javalang.tree.DoStatement):
            return self.buildDo(cfg,prev,node)
        elif isinstance(node,javalang.tree.)