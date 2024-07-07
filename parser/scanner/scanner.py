from helpers import SourceIterator,keywords
from dataclasses import dataclass,field
from decimal import Decimal
from interpreter import *
@dataclass
class Scanner(SourceIterator):
    tokens: list[Token] = field(default_factory=lambda: [])
    def scan(self):
        while not self.isAtEnd():
            self.start = self.current
            self.scanToken()
        self.tokens.append(Token(EOF,"\0",None,self.line))
        return self.tokens
    # Tokenize Source Code
    def scanToken(self) -> list[Token]:
        char = self.advance()
        match char:
            # Single Characters Tokens
            case "(":
                self.addToken(LEFT_PAREN)
            case ')': self.addToken(RIGHT_PAREN)
            case '{': self.addToken(LEFT_BRACE)
            case '}': self.addToken(RIGHT_BRACE)
            case '[': self.addToken(LEFT_BRACKET)
            case ']': self.addToken(RIGHT_BRACKET)
            case ',': self.addToken(COMMA)
            case '.': self.addToken(DOT)
            case '-': self.addToken(MINUS)
            case '+': self.addToken(PLUS)
            case ':': self.addToken(COLON)
            case ';': self.addToken(SEMICOLON)
            case "|": self.addToken(OR)
            case "^": self.addToken(XOR)
            case '*': self.addToken(POW if self.match("*") else STAR)
            case "&":
                self.addToken(AND if self.match("&") else POS_ARGS)
            case "!":
                self.addToken(BANG_EQUAL if self.match("=") else BANG)
            case "=":
                self.addToken(EQUAL_EQUAL if self.match("=") else EQUAL)
            case "<":
                self.addToken(LESS_EQUAL if self.match("=") else R_SHIFT if self.match(">") else LESS)
            case ">":
                self.addToken(GREATER_EQUAL if self.match("=") else L_SHIFT if self.match("<") else GREATER)
            case "/":
                if self.match("/"):
                    while self.peek() != "\n" and (not self.isAtEnd()): self.advance()
                else:
                    self.addToken(SLASH)
            case " ": pass
            case "\r": pass
            case "\t": pass
            case "\n": self.line += 1
            case '"': self.parseString()
            # case "f":
            #     if self.match('"'):
            #         self.parseString(True)
            #     else:
            #         pass
            case _:
                if char.isdigit():  # type: ignore
                    self.parseNumber()
                elif char.isalpha():  # type: ignore
                    self.parseIdentifier()
                else:
                    error(self.line,f"Unexpected Character <{char}>.")
                    return []
        return self.tokens
    def addToken(self,tokenType:int,literal: object= None) -> None:
        # Extract Lexeme
        lexeme: str = self.source[self.start:self.current] # type: ignore
        self.tokens.append(Token(tokenType,lexeme,literal,self.line))
    def parseString(self,formatted:bool=False) -> None:
        while (self.peek() != '"' and (not self.isAtEnd())):
            if self.peek() == "\n":
                self.line += 1
                error(self.line,"Unterminated string literal.")
                exit(1)
            self.advance()
        if (self.isAtEnd()):
            error(self.line,"Unterminated string literal.")
            exit(1)
        self.advance()
        string = self.source[self.start + 1:self.current-1]
        self.addToken(STRING if not formatted else FORM_STRING,string)
    def parseNumber(self) -> None:
        isFloat = False
        while self.peek().isdigit(): self.advance() # type: ignore
        if self.peek() == "." and self.peekNext().isdigit():  # type: ignore
            isFloat = True
            self.advance()
            while self.peek().isdigit(): self.advance() # type: ignore
        val = eval(self.source[self.start:self.current]) # type: ignore
        val = Decimal(str(val)) if isinstance(val,float) else val
        self.addToken(FLOAT if isFloat else INTEGER,val) # type: ignore
    def parseIdentifier(self) -> None:
        while self.peek().isalnum(): self.advance() # type: ignore
        text = self.source[self.start:self.current]
        tokenType = keywords.get(text)  # type: ignore
        if text == "f" and self.peek() == '"':
            self.advance()
            self.parseString(True)
            return
        if not tokenType:
            tokenType = IDENTIFIER
        self.addToken(tokenType)
