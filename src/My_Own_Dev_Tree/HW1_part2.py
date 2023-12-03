import ply.lex as lex
import ply.yacc as yacc

# tokens
tokens = ('CHARACTER', 'CONCAT', 'UNION', 'STAR', 'OPTIONAL', 'LPAREN', 'RPAREN')

t_CHARACTER = r'[a-zA-Z0-9]'
t_CONCAT = r'\.'
t_UNION = r'\|'
t_STAR = r'\*'
t_OPTIONAL = r'\?'
t_LPAREN = r'\('
t_RPAREN = r'\)'
t_ignore = ' \t'

# error for when a character is not recognized
def t_error(t):
    print(f"Illegal character {t.value[0]!r}")
    t.lexer.skip(1)

# precedence rules for parsing the tokens
precedence = (
    ('left', 'UNION'),
    ('left', 'CONCAT'),
    ('left', 'STAR', 'OPTIONAL')
)

# Build the lexer
lexer = lex.lex()

# regular experession AST class
class RE_AST:
    def __repr__(self):
        return "RE_AST"

# regular expression AST leaf node (for single characters)
class RE_AST_LEAF(RE_AST):
    def __init__(self, value):
        self.value = value

    def __repr__(self):
        return f"RE_AST_LEAF(value={self.value!r})"

# regular expression AST non-leaf node (for operators)
class RE_AST_NON_LEAF(RE_AST):
    def __init__(self, operator, operands):
        self.operator = operator
        self.operands = operands

    def __repr__(self):
        return f"RE_AST_NON_LEAF(operator={self.operator!r}, operands={self.operands!r})"

#parsing rules:

def p_term(p):
    'term : expression'
    p[0] = p[1]

def p_expression_concat(p):
    'expression : expression CONCAT expression'
    p[0] = RE_AST_NON_LEAF('CONCAT', [p[1], p[3]])

def p_expression_union(p):
    'expression : expression UNION expression'
    p[0] = RE_AST_NON_LEAF('UNION', [p[1], p[3]])

def p_expression_star(p):
    'expression : expression STAR'
    p[0] = RE_AST_NON_LEAF('STAR', [p[1]])

def p_expression_optional(p):
    'expression : expression OPTIONAL'
    p[0] = RE_AST_NON_LEAF('OPTIONAL', [p[1]])

def p_expression_group(p):
    'expression : LPAREN expression RPAREN'
    p[0] = p[2]

def p_expression_character(p):
    'expression : CHARACTER'
    p[0] = RE_AST_LEAF(p[1])

def p_error(p):
    print("Syntax error at", p)

## Some helper functions to produce AST for the empty string and empty set:
class RE_EmptyString(RE_AST):
    def __repr__(self):
        return "RE_EmptyString()"
    
class RE_EmptySet(RE_AST):
    def __repr__(self):
        return "RE_EmptySet()"

## Nullable function starting here:

# Top level Nullable function: this function takes an RE (re) as an
# AST and returns:
# (1) an RE AST for the empty string (epsilon) if the re matches the empty string (epsilon).
# (2) an RE AST for the empty set if the re does NOT match the empty string.

# Implement this function
def nullable(re):
    if isinstance(re, RE_AST_LEAF): # a characte doesn't the match empty string
        return RE_EmptySet()
    if isinstance(re, RE_AST_NON_LEAF): # a non-leaf node
        if re.operator == 'CONCAT': # if the operator is CONCAT
            for operand in re.operands:
                if isinstance(nullable(operand), RE_EmptySet):
                    return RE_EmptySet()
            return RE_EmptyString()
        if re.operator == 'UNION': # if the operator is UNION
            for operand in re.operands:
                if isinstance(nullable(operand), RE_EmptyString):
                    return RE_EmptyString()
            return RE_EmptySet()
        if re.operator == 'STAR' or re.operator == 'OPTIONAL': # if the operator is STAR or OPTIONAL
            return RE_EmptyString()
    if isinstance(re, RE_EmptyString):
        return RE_EmptyString()
    return RE_EmptySet()

# derivative function starting here:

# This function takes a character (char) and an RE AST (re). It
# returns the RE (as an AST) that is the derivative of re with respect
# to char.

# More specifically: say the input RE (re) accepts the set of strings S.
# The derivative of re with respect to char is all strings in S that began
# with char, and now have char ommitted. Here are some examples:

# Given a RE (call it re) that matches the language {aaa, abb, ba, bb,
# ""}, the derivative of re with respect to 'a' is {aa, bb}. These are
# the original strings that began with 'a' (namely {aaa, abb}), with
# the first 'a' character removed. Please review the lecture or the
# "Regular-expression derivatives reexamined" for more information

# implement this function:
def derivative_re(char, re):
    # this is mostly the same stuff from the slides; just a few adjustments and some dirty hacks.
    if isinstance(re, RE_AST_LEAF): # a leaf node
        if re.value == char:
            return RE_EmptyString()
        else:
            return RE_EmptySet()
    if isinstance(re, RE_AST_NON_LEAF): # a non-leaf node
        if re.operator == 'CONCAT': # if the operator is CONCAT
            base = RE_AST_NON_LEAF('CONCAT', [derivative_re(char, re.operands[0]), re.operands[1]])
            if isinstance(nullable(re.operands[0]), RE_EmptyString):
                return RE_AST_NON_LEAF('UNION', [base, derivative_re(char, re.operands[1])])
            else:
                return base
        if re.operator == 'UNION':
            return RE_AST_NON_LEAF('UNION', [derivative_re(char, re.operands[0]), derivative_re(char, re.operands[1])])
        if re.operator == 'STAR':
            
            return RE_AST_NON_LEAF('CONCAT', [derivative_re(char, re.operands[0]), re])
        if re.operator == 'OPTIONAL':
            return derivative_re(char, re.operands[0])
    return RE_EmptySet()

parser = yacc.yacc()

# High-level function to match a string using regular experession
# derivatives:
def match_regex_ast(re, to_match):
    # create the derivative for each character of the string in sequence
    for char in to_match:
        re =  derivative_re(char, re)

    # the string matches if and only if the empty string is matched by the derivative RE
    return isinstance(nullable(re), RE_EmptyString)

# Keep this function exactly how it is for grading to use with the tester scripts.
def match_regex(reg_ex, string):
    return match_regex_ast(parser.parse(reg_ex), string)

# I only have this function because it was used in __main__. 
# But it does some of the things we already had in 'match_regex_ast' so I just used it.
def parse_re(d_re, to_match):
    for char in to_match:
        d_re = derivative_re(char, d_re)
    return isinstance(nullable(d_re), RE_EmptyString)

# Use this conditional to test your script locally
if __name__ == "__main__":
    d_re = parser.parse("(h.i)* | c.s.e*.2.1.1")

    # # should pass
    print(parse_re(d_re, "hi") == True)    
    print(parse_re(d_re, "hihi") == True)
    print(parse_re(d_re, "cse211") == True)
    print(parse_re(d_re, "cs211") == True)
    print(parse_re(d_re, "cseee211") == True)

    # # should fail
    print(parse_re(d_re, "hhh") == False)
    print(parse_re(d_re, "cseee21") == False)
    print(parse_re(d_re, "211") == False)