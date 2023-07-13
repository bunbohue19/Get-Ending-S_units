import javalang 
import networkx as nx
from stmtCFG import buildNode
import stmtCFG
import re

def getLine(node : javalang.ast.Node):
    return node.position.line

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
def containData(var,datalist):
    if isinstance(var,javalang.tree.MemberReference):
        for data in datalist:
            if isinstance(data,javalang.tree.MemberReference):
                if data.member==var.member:
                    return True
    if isinstance(var,javalang.tree.This):
        for data in datalist:
            if isinstance(data,javalang.tree.This):
                if var.selectors==data.selectors:
                    return True
    return False

def camelCaseSplit(string):
    strings = [string]
    strings = [re.sub(r"(\b\w)", lambda match: match.group().upper(), s) for s in strings]
    return [x.lower() for x in re.findall(r'[A-Z](?:[a-z]+|[A-Z]*(?=[A-Z]|$))', strings[0])] + re.findall(r'\d+', strings[0])

def isSWUM(method_name_1 : str, method_name_2 : str):
    words_1, words_2 = camelCaseSplit(method_name_1), camelCaseSplit(method_name_2)    
    numOfMatches = 0
    words_len = min(len(words_1), len(words_2))
    for word_1, word_2 in zip(words_1, words_2):
        if word_1 == word_2:
            numOfMatches += 1
    if (numOfMatches / words_len) >= 0.5:
        return True
    return False     
    
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
        
    """
        return source code line from node position(Loc)
    """    
    def getSource(self, node : javalang.ast.Node):    
        return node.position.line
    
    def getSameActionSunit(self):
        """
        get method declaration of the main method
        get all method invocation and compare similarity to the main method name by using SWUM
        """
        res=[]
        method=None
        for node in self.cfg.nodes:
            if isinstance(node,javalang.tree.MethodDeclaration):
                method=node
                break
        for _,node in self.ast.filter(javalang.tree.MethodInvocation):
            if isSWUM(method.name,node.member):
                res+=[node]
        return res
    
    def isIsolated(self,node:javalang.ast.Node):
        """
        check if a node is an extra node that will not be executed in the code
        """
        if self.cfg.in_degree(node)==0:
            if isinstance(node,javalang.tree.MethodDeclaration):
                return False
            else:
                return True
        return any(self.isIsolated(pred) for pred in self.cfg.predecessors(node))
        
    def composeSunit(self):
        """
        get compose first 3 sunit heuristic
        get data sunit from previous heuristic
        get control sunit from previous heuristic
        sort by code line in class
        return list of lines of code
        """
        res=[]
        res+=self.getEndingSunit()
        res+=self.getSameActionSunit()
        res+=self.getVoidReturnSunit()
        heu_data=[]
        for result in res:
            if not result in heu_data:
                heu_data.append(result)
        heu_data+=self.getDataFacilitatingSunit(heu_data)
        heu_control=[]
        for dt in heu_data:
            if not dt in heu_control:
                heu_control.append(dt)
        heu_control+=self.getControllingSunit(res)
        heu_control.sort(key=getLine)
        return heu_control

    def getControllingSunit(self,sunit:list[javalang.ast.Node]):
        """
        input previous heuristic
        return the latest branching statement (if/switch/while/for)
        """
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
                        declarators=node.declarators
                        if any([data.member== dec.name for dec in declarators ]):
                            res.append(node)
                            break
            elif isinstance(node,javalang.tree.StatementExpression):
                if isinstance(node.expression,javalang.tree.Assignment):
                    assign=node.expression
                    if containData(assign.expressionl,datalist):
                        res.append(node)
                    
                if isinstance(node.expression,javalang.tree.MemberReference):
                    if containData(node,datalist):
                        res.append(node)
                if isinstance(node.expression,javalang.tree.This):
                    if containData(node,datalist):
                        res.append(node)
        return res
    def getVoidReturnSunit(self):
        """
        get all statement that have method invocation in expression (which is void method)
        """
        res=[]
        for _,node in self.ast.filter(javalang.tree.StatementExpression):
            if isinstance(node.expression,javalang.tree.MethodInvocation):
                
                res+=[node]
        return res
    def getPrevStatement(self,node:javalang.ast.Node):
        if isinstance(node,(javalang.tree.IfStatement,javalang.tree.SwitchStatement,javalang.tree.StatementExpression)):
            return [node]
        else:
            return self.getPrevStatement(list(self.cfg.predecessors(node))[0])
    def getEndingSunit(self):
        """
        get all node in cfg that either:
            a return node (if that is void, return previous line)
            a node that direct to no 
        """
        res=[]
        for node in self.cfg.nodes:
            if self.cfg.out_degree(node)==0:
                if self.isIsolated(node):
                    
                    continue
                if isinstance(node,javalang.tree.ReturnStatement):
                    if node.label is None and node.expression is None:
                        res+=self.getPrevStatement(node)
                        continue
                
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





            