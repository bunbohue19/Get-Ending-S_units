import javalang
import networkx as nx
from stmtCFG import buildNode
import stmtCFG
def findData(root):
    res=[]
    children=None
    if isinstance(root,javalang.ast.Node):
        if isinstance(root,(javalang.tree.MemberReference,javalang.tree.This)):
            return [root]
        else:
            children=root.children
    else:
        children=root
    for child in children:
        if isinstance(child, (javalang.ast.Node, list, tuple)):
            
            res+=findData(child)
    return res
def containData(root,data):
    if isinstance(root,javalang.tree.LocalVariableDeclaration):
        return any()
class Sunit:
    def __init__(self,body:str):
        """
        build CFG for method 
        init:
            self.ast: AST 
            self.cfg: CFG
            self.source_code: String class
        """
        
        cls="public class Main{\n"+body+"\n}"
        self.source_code=cls
        tree=javalang.parse.parse(cls)
        self.ast=tree
        method=None
        for _,node in tree.filter(javalang.tree.MethodDeclaration):
            method=node
        
        G=nx.DiGraph()
        for _,node in method:
            G.add_node(method)
        prev=[method]
        for stmt in method.body:
            prev,G=buildNode(G,prev,stmt)
        self.cfg=G
    def getLine(self, node: javalang.ast.Node):
        """
        return source code from node position(Loc)
        """
        pass
    def isSWUM(self,method1:str,method2:str):
        return True
    def getSameActionSunit(self):
        res=[]
        method=None
        for node in self.cfg.nodes:
            if isinstance(node,javalang.tree.MethodDeclaration):
                method=node
                break
        for _,node in self.ast.filter(javalang.tree.MethodInvocation):
            if self.isSWUM(method.name,node.member):
                res+=[node]
    def composeSunit(): 
        pass
    def getControllingSunit(self,sunit:list[javalang.ast.Node]):

        return []
    def getDataFacilitatingSunit(self,sunit:list[javalang.ast.Node]):
        """
        get data
        """
        datalist=[]
        for node in sunit:
            datalist+=findData(node)
        res=[]
        for _,node in self.ast:
            if isinstance(node,javalang.tree.LocalVariableDeclaration):
                for data in datalist:
                    if isinstance(data,javalang.tree.MemberReference):
                        declarators=node.declarator
                        if any([data.member== dec.name for dec in declarators ]):
                            res.append(node)
                            break
            elif isinstance(node,javalang.tree.StatementExpression):
                if isinstance(node.expression,javalang.tree.Assignment):
                    assign=node.expression
                    
                    pass
                if isinstance(node.expression,javalang.tree.MemberReference):
                    pass
                if isinstance(node.expression,javalang.tree.This):
                    pass
                pass
        return res
    def getVoidReturnSunit(self):
        res=[]
        for _,node in self.ast.filter(javalang.tree.StatementExpression):
            if isinstance(node.expression,javalang.tree.MethodInvocation):
                
                res+=[node]
        return res
    def getEndingSunit(self):
        res=[]
        for node in self.cfg.nodes:
            if self.cfg.out_degree(node)==0:
                if node==javalang.tree.ReturnStatement:
                    if node.label is None and node.expression is None:
                        res+=list(self.cfg.predecessors(node))
                res+=[node]
                        
            elif (all(suc in node.children for suc in list(self.cfg.successors(node))))and isinstance(node,(javalang.tree.ForStatement,javalang.tree.WhileStatement,javalang.tree.DoStatement)):
                print(node)
                res+=self.get_end(node.body)
        return res
    def get_end(self,node):
        
        if isinstance(node,(javalang.tree.BlockStatement)):
            if len(node.statements)>0:

                return self.get_end(node.statements[-1])
            else:
                return self.cfg.predecessors(node)
        elif isinstance(node,javalang.tree.IfStatement):
            res=[]
            if node.then_statement is not None:
                res+=self.get_end(node.then_statement)
            if node.else_statement is not None:
                res +=self.get_end(node.else_statement)
            return res
        elif isinstance(node,javalang.tree.TryStatement):
            res=[]
            if node.finally_block is not None: 
                if len(node.finally_block)>0:
                    return self.get_end(node.finally_block[-1])
                else:
                        
                    res+=self.get_end(node.block[-1])
                    if node.catches is not None:
                        for catch in node.catches:
                            if len(catch.block)>0:
                                res+=self.get_end(catch.block[-1])

            else:
                res+=self.get_end(node.block[-1])
                if node.catches is not None:
                    for catch in node.catches:
                        if len(catch.block)>0:
                            res+=self.get_end(catch.block[-1])
            return res
                        
        elif isinstance(node,(javalang.tree.ForStatement,javalang.tree.WhileStatement,javalang.tree.DoStatement)):
            return self.get_end(node.body)
        elif isinstance(node,javalang.tree.SwitchStatement):
            res=[]
            for case in node.cases:
                if len(case.statements)>0:
                    res+=self.get_end(case.statements[-1])
            return res
            
        else:
            return [node]





            