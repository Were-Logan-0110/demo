LEFT_PAREN = 1
RIGHT_PAREN = 2
LEFT_BRACE = 3
RIGHT_BRACE = 4
LEFT_BRACKET = 5
RIGHT_BRACKET = 6
COMMA = 7
DOT = 8
MINUS = 9
PLUS = 10
COLON = 11
SEMICOLON = 12
SLASH = 13
STAR = 14
POS_ARGS = 15

OR = 16
AND = 17
BANG = 18
BANG_EQUAL = 19
XOR = 20
POW = 21
EQUAL = 22
R_SHIFT = 23
L_SHIFT = 24
EQUAL_EQUAL = 25
GREATER = 26
GREATER_EQUAL = 27
LESS = 28
LESS_EQUAL = 29

IDENTIFIER = 30
STRING = 31
FORM_STRING = 32
INTEGER = 33
FLOAT = 34
BOOLEN = 35

TYPE_STRING = 36
TYPE_INTEGER = 37
TYPE_FLOAT = 38
TYPE_BOOLEN = 39
TYPE_ARRAY = 40

ELSE = 41
FALSE = 42
FUN = 43
CLASS = 44
FOR = 45
FOR_EACH = 46
IF = 47
ELSE_IF = 48
NULL = 49
VAR = 50
PRINT = 51
PRINTLN = 52
RETURN = 53
BREAK = 54
CONTINUE = 55
IN = 56
WHILE = 57
TRUE = 58
RAISE = 59

HTTP = 60
FTP = 61
STMP = 62
TCP = 63
IP = 64
SSL = 65

EOF = 66

class Token:
    def __init__(self, type, lexeme, literal, line):
        self.type = type
        self.lexeme = lexeme
        self.literal = literal
        self.line = line

    def __dbgrepr__(self):
        return (
            "<"
            + str(self.type)
            + ":"
            + self.lexeme
            + " value=< "
            + str(self.literal)
            + " >"
        )

    def __repr__(self):
        return [k for k,v in globals().items() if v == self.type][0]