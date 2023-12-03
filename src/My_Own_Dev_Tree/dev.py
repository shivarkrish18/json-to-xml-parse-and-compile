import argparse
import ply.lex as lex
import ply.yacc as yacc

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
    print(f"{indent}{node.type}: {node.value}")
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
        if not isArray: string  += f"<{node.value}>\n"
        convertToXML(node.children[0])
        if not isArray: string += f"</{node.value}>\n"

    
    elif node.type == "array":        
        for child in node.children:
            string += f"<{node.value}>\n"
            convertToXML(child)
            string += f"</{node.value}>\n"
    
    elif node.type == "primitive":
        string += f"{node.value}\n"
    

        
            





if __name__ == "__main__":
    parsa = argparse.ArgumentParser(prog='JSON Tree Parser')
    parsa.add_argument('-f', '--filename')
    args = parsa.parse_args()
    input_string = ''
    with open(args.filename) as ff:
        input_string = ff.read()
    result_ast = parse_json(input_string)
    string = '<root>\n'

    convertToXML(result_ast)
    string += '\n</root>'
    print("AST:")
    print_tree(result_ast)
    
    with open("someXMLFile.xml","w") as f:
        f.write(string)
    print("Wrote to XML File")
