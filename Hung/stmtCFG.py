import javalang
import networkx as nx
def check_pred(cfg:nx.DiGraph,source,type:type):
    for pred in cfg.predecessors(source):
        if isinstance(pred,type):
            return True
        else:
            return check_pred(cfg,pred,type)
    
def buildNode(cfg:nx.DiGraph,prev:list[javalang.ast.Node],node:javalang.ast.Node):
    #interface of build a stmt
    cfgBuilder= stmtCFG()
    res,cfg=cfgBuilder.buildNode(cfg,prev,node)
    
    return res,cfg
class stmtCFG:
    def buildNode(self,cfg:nx.DiGraph,prev:list[javalang.ast.Node],node:javalang.ast.Node):
        #abstract method to build next node
        
        if isinstance(node,javalang.tree.IfStatement):
            return self.buildIf(cfg,prev,node)
        elif isinstance(node,javalang.tree.ForStatement):
            return self.buildFor(cfg,prev,node)
        # elif isinstance(node,javalang.tree.WhileStatement):
        #     return self.buildWhile(cfg,prev,node)
        # elif isinstance(node,javalang.tree.DoStatement):
        #     return self.buildDo(cfg,prev,node)
        # elif isinstance(node,javalang.tree.BreakStatement):
        #     return self.buiildBreak(cfg,prev,node)
        # elif isinstance(node,javalang.tree.ContinueStatement):
        #     return self.buildContinue(cfg,prev,node)
        elif isinstance(node,javalang.tree.ReturnStatement):
            return self.buildReturn(cfg,prev,node)
        # elif isinstance(node,javalang.tree.TryStatement):
        #     return self.buildTry(cfg,prev,node)
        elif isinstance(node,javalang.tree.BlockStatement):
            return self.buildBlock(cfg,prev,node)
        else:
            return self.buildStmt(cfg,prev,node)
    def buildBlock(self,cfg:nx.DiGraph,prev:list[javalang.ast.Node],node:javalang.tree.BlockStatement):
        for stmt in node.statements:
            prev,cfg=self.buildNode(cfg,prev,stmt)
        return prev,cfg
    def buildIf(self,cfg:nx.DiGraph,prev:list[javalang.ast.Node],node:javalang.tree.IfStatement):
        cfg.add_node(node)
        for pre in prev:
            cfg.add_edge(pre,node)
        prev=[node]
        cfg.add_node(node.condition)
        
        for pre in prev:
            cfg.add_edge(pre,node.condition)
        last_then=[node.condition]
        last_else=[node.condition]
        last_else,cfg=self.buildNode(cfg,last_else,node.else_statement)
        last_then,cfg=self.buildNode(cfg,last_else,node.then_statement)
        res=[]
        for i in last_else:
            res.append(i)
        for i in last_then:
            res.append(i)
        return res,cfg

    def buildFor(self,cfg:nx.DiGraph,prev:list[javalang.ast.Node],node:javalang.tree.ForStatement):
        cfg.add_node(node)
        for pre in prev:
            cfg.add_edge(pre,node)
        prev=[node]
        control=node.control
        cfg.add_node(control.init)
        cfg.add_node(control.condition)

        for pre in prev:
            cfg.add_edge(pre,control.init)
        cfg.add_edge(control.init,control.condition)
        prev=[control.condition]
        prev,cfg=self.buildNode(cfg,prev,node.body)
        for update in control.update:
            prev,cfg=self.buildNode(cfg,prev,update)
        prev,cfg=self.buildNode(cfg,prev,control.condition)
        prev=[control.condition]
        return prev,cfg
    def buildWhile(self,cfg:nx.DiGraph,prev:list[javalang.ast.Node],node:javalang.tree.WhileStatement):
        return [],cfg
    def buildDo(self,cfg:nx.DiGraph,prev:list[javalang.ast.Node],node:javalang.tree.DoStatement):
        return [],cfg
    def buildBreak(self,cfg:nx.DiGraph,prev:list[javalang.ast.Node],node:javalang.tree.BreakStatement):
        return [],cfg
    def buildContinue(self,cfg:nx.DiGraph,prev:list[javalang.ast.Node],node:javalang.tree.ContinueStatement):
        cfg.add_node(node)
        if node.goto==None:
            pred=cfg.predecessors(node)
            while(any(isinstance)):
        return [],cfg
    def buildReturn(self,cfg:nx.DiGraph,prev:list[javalang.ast.Node],node:javalang.tree.ReturnStatement):
        cfg.add_node(node)

        for pre in prev:
            cfg.add_edge(pre,node)
        return [],cfg
    def buildTry(self,cfg:nx.DiGraph,prev:list[javalang.ast.Node],node:javalang.tree.TryStatement):
        return [],cfg
    def buildStmt(self,cfg:nx.DiGraph,prev:list[javalang.ast.Node],node:javalang.tree.Node):
        cfg.add_node(node)
        for pre in prev:
            cfg.add_edge(pre,node)
        return [node],cfg