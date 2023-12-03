import ply.lex as lex
import ply.yacc as yacc
import argparse

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


lexer = lex.lex()

def p_json(p):
    '''json : object'''
    p[0] = p[1]

def p_object(p):
    'object : LCURLY members RCURLY'
    p[0] = {"type": "object", "members": p[2]}

def p_members(p):
    '''members : pair
               | pair COMMA members'''
    if len(p) == 2:
        p[0] = [p[1]]
    else:
        p[0] = [p[1]] + p[3]

def p_pair(p):
    'pair : STRING COLON element'
    p[0] = {"type": "pair", "key": p[1], "value": p[3]}

def p_array(p):
    'array : LSQUARE elements RSQUARE'
    p[0] = {"type": "array", "elements": p[2]}

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
    p[0] = {"type": "primitive", "value": p[1]}

def p_error(p):
    print(f"Syntax error at '{p.value}'")

parser = yacc.yacc()

def parse_json(input_string):
    lexer.input(input_string)
    ast = parser.parse(lexer=lexer)
    return ast


def visitNode(node):    
    global string
    if node['type'] == 'object':                
        for member in node['members']:
            string += "\n"
            visitNode(member)
    
    elif node['type'] == 'pair':
        isArray = False
        if node['value']['type'] == 'array':
            isArray = True
            node['value']['key'] = node['key']

        if not isArray: string  += "<" + removeDoubleQuotes(node['key']) + ">"
        visitNode(node['value'])
        if not isArray: string += "</" + removeDoubleQuotes(node['key']) + ">\n"
        #print(string)

    
    elif node['type'] == 'array':
        for element in node['elements']:
            string  += "<" + removeDoubleQuotes(node['key']) + ">"
            visitNode(element)
            string += "</" + removeDoubleQuotes(node['key']) + ">\n"
    
    elif node['type'] == 'primitive':
            string += removeDoubleQuotes(node['value'])



if __name__ == "__main__":
    
    parsa = argparse.ArgumentParser(prog='HTTP Web Sever')    
    parsa.add_argument('-f','--filename')
    args = parsa.parse_args()
    input_string = ''
    with open(args.filename) as ff:
        input_string = ff.read()
    result_ast = parse_json(input_string)
    print(result_ast)
    print()
    print()
    string = '<root>\n'
    visitNode(result_ast)
    string += '\n</root>'
    print(string)
    #try:
    #    utility_file.check_duplicate_keys(result_ast)
    #except ValueError as v:
    #    print(f" Duplicate key {v} found in parse tree")
    #print("Input:", input_string)
    #print("AST:", result_ast)
    #pretty_ast = json.dumps(result_ast, indent=2)
    #print(pretty_ast)

    #pprint(result_ast)
    #xml_tree = utility_file.convert_to_xml2(input_string)
    #xml_string = ET.tostring(xml_tree, encoding='unicode')
    with open("xml_output.xml",'w') as xm:
        xm.write(string)
    print("Done writing to xml file")