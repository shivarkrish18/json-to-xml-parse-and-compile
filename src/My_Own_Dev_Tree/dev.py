import argparse
import ply.lex as lex
import ply.yacc as yacc
import xml.dom.minidom as md


def removeDoubleQuotes(string):
    finalString = ''
    for i in string:
        if not (i == "\"" or i == "\'"):
            finalString += i
    return finalString

tokens = (
    'STRING',
    'NUMBER',
    'LCURLY',
    'RCURLY',
    'LSQUARE',
    'RSQUARE',
    'COMMA',
    'COLON',
    'TRUE',
    'FALSE',
    'NULL',
)

t_STRING = r'"[^"]*"'
t_NUMBER = r'\d+'
t_LCURLY = r'\{'
t_RCURLY = r'\}'
t_LSQUARE = r'\['
t_RSQUARE = r'\]'
t_COMMA = r','
t_COLON = r':'
t_TRUE = r'true'
t_FALSE = r'false'
t_NULL = r'null'

t_ignore = ' \t\n'

def t_error(t):
    print(f"Illegal character '{t.value[0]}'")
    t.lexer.skip(1)

class TreeNode:
    def __init__(self, type, value=None, children=None):
        self.type = type
        self.value = value
        self.isDuplicate = False
        if type == 'array' or type == 'object':
            self.removeChildren = []
        if value is not None:
            self.value = removeDoubleQuotes(value)
        self.children = children if children is not None else []

def p_json(p):
    '''json : object'''
    p[0] = p[1]

def p_object(p):
    'object : LCURLY members RCURLY'
    p[0] = TreeNode("object", None, p[2])

def p_members(p):
    '''members : pair
               | pair COMMA members'''
    if len(p) == 2:
        p[0] = [p[1]]
    else:
        p[0] = [p[1]] + p[3]

def p_pair(p):
    'pair : STRING COLON element'
    p[0] = TreeNode("pair", p[1], [p[3]])

def p_array(p):
    'array : LSQUARE elements RSQUARE'
    p[0] = TreeNode("array", None, p[2])

def p_element(p):
    '''element : primitive
               | object
               | array'''
    p[0] = p[1]

def p_elements(p):
    '''elements : element
                | element COMMA elements
                '''
    if len(p) == 2:
        p[0] = [p[1]]
    else:
        p[0] = [p[1]] + p[3]

def p_primitive(p):
    '''primitive : STRING
             | NUMBER
             | TRUE
             | FALSE
             | NULL'''
    p[0] = TreeNode("primitive", p[1])

def p_error(p):
    print(f"Syntax error at '{p.value}'")

lexer = lex.lex()
parser = yacc.yacc()

#Function for checking ambiguity in a given JSON AST
def labelDuplicates(node, reversedFlag):        
    if reversedFlag:
        if node.type == "object" or node.type == "array":
            valueList = []
            for i in range(len(node.children)):
                #print(f"Iteration {i}")
                if node.children[i].type != 'object':
                    if (node.children[i].value not in valueList):                
                        valueList.append(node.children[i].value)
                    else:                    
                        node.removeChildren.append(i)
                labelDuplicates(node.children[i], reversedFlag)            

        elif node.type == "pair":               
            labelDuplicates(node.children[0], reversedFlag)      
        
        elif node.type == "primitive":
            return
        
    else:
        if node.type == "object" or node.type == "array":
            valueList = []
            for i in range(len(node.children)-1,-1,-1):                
                if node.children[i].type != 'object':
                    if (node.children[i].value not in valueList):                
                        valueList.append(node.children[i].value)
                    else:                    
                        node.removeChildren.append(i)
                labelDuplicates(node.children[i], reversedFlag)

        elif node.type == "pair":               
            labelDuplicates(node.children[0], reversedFlag)      
        
        elif node.type == "primitive":
            return
    

def makeDecision(node):
    if node.type == "object" or node.type == "array":
        if node.removeChildren != []:
            for i in sorted(node.removeChildren, reverse = True):
                del node.children[i]
        for i in range(len(node.children)):
            makeDecision(node.children[i])
    elif node.type == "pair":               
        makeDecision(node.children[0])
    else:
        pass


def parse_json(input_string):
    lexer.input(input_string)
    ast = parser.parse(lexer=lexer)
    return ast

def build_tree(node):
    if node.type == "object":
        for pair_node in node.children:
            build_tree(pair_node)
    elif node.type == "pair":
        build_tree(node.children[0])
    elif node.type == "array":
        for element_node in node.children:
            build_tree(element_node)

def print_tree(node, level=0):
    indent = "  " * level
    print(f"{indent}{node.type}: {node.value}: {node.isDuplicate}")
    for child in node.children:
        print_tree(child, level + 1)

def convertToXML(node):    
    global string
    #pass
    if node.type == "object":
        for child in node.children:
            convertToXML(child)
    elif node.type == "pair":  
        isArray = False      
        if node.children[0].type == "array":
            isArray = True
            node.children[0].value = node.value
        if not isArray: string  += f"<{node.value}>"
        convertToXML(node.children[0])
        if not isArray: string += f"</{node.value}>"

    
    elif node.type == "array":        
        for child in node.children:
            string += f"<{node.value}>"
            convertToXML(child)
            string += f"</{node.value}>"
    
    elif node.type == "primitive":
        string += f"{node.value}"
    

        
            





if __name__ == "__main__":
    parsa = argparse.ArgumentParser(prog='JSON Tree Parser')
    parsa.add_argument('-f', '--filename', help='Path to the input JSON File')
    parsa.add_argument('-d', '--duplicateflag', help='True if first occurence has to be retained/False if last occurence has to be retained ')
    args = parsa.parse_args()
    input_string = ''
    with open(args.filename) as ff:
        input_string = ff.read()
    result_ast = parse_json(input_string)
    #print("AST:")
    #print_tree(result_ast)
    #print(args.duplicateflag)
    flag = True if args.duplicateflag == "True" else False
    
    print(flag)
    labelDuplicates(result_ast, flag)
    #print("AST after duplicate matching: ")
    #print_tree(result_ast)
    makeDecision(result_ast)
    #print("AST after duplicate removal: ")
    #print_tree(result_ast)

    string = '<root>'
    convertToXML(result_ast)
    string += '</root>'

    dom = md.parseString(string) # or xml.dom.minidom.parseString(xml_string)
    pretty_xml_as_string = dom.toprettyxml()
    if flag:
        with open("TrueXMLFile.xml","w") as f:
            f.write(pretty_xml_as_string)
    
    else:
        with open("FalseXMLFile.xml","w") as f:
            f.write(pretty_xml_as_string)

    print("Wrote to XML File")

