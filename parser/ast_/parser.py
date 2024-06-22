from interpreter import Token, TokenType, report
from dataclasses import dataclass, field
from helpers import SourceIterator
from ast_.expression import *
from numpy import array


class ParseError(Exception):
    pass


class _UninitializedVar:
    pass


@dataclass
class LLParser(SourceIterator):
    tokens: list[Token] = field(default_factory=lambda: [])
    variables = {}

    def parse(self):
        try:
            return self.expression()
        except ParseError as e:
            exit(1)

    def expressionStatement(self):
        expr: Expr = self.expression()
        return Expression(expr)

    def expression(self) -> Expr:
        return self.equality()

    def equality(self) -> Expr:
        expr: Expr = self.comparison()
        while self.match(TokenType.BANG_EQUAL, TokenType.EQUAL):
            operator: Token = self.previous()
            right: Expr = self.comparison()
            expr = Binary(expr, operator, right)
        return expr

    def comparison(self) -> Expr:
        expr: Expr = self.term()
        while self.match(
            TokenType.AND,
            TokenType.OR,
            TokenType.XOR,
            TokenType.R_SHIFT,
            TokenType.L_SHIFT,
            TokenType.GREATER,
            TokenType.GREATER_EQUAL,
            TokenType.LESS,
            TokenType.LESS_EQUAL,
        ):
            operator: Token = self.previous()
            right: Expr = self.term()
            expr = Binary(expr, operator, right)
        return expr

    def term(self) -> Expr:
        expr: Expr = self.factor()
        while self.match(TokenType.MINUS, TokenType.PLUS):
            operator: Token = self.previous()
            right: Expr = self.factor()
            expr = Binary(expr, operator, right)
        return expr

    def factor(self) -> Expr:
        expr: Expr = self.exponentiation()
        while self.match(TokenType.SLASH, TokenType.STAR):
            operator: Token = self.previous()
            right: Expr = self.exponentiation()
            expr = Binary(expr, operator, right)
        return expr

    def exponentiation(self) -> Expr:
        expr: Expr = self.unary()
        while self.match(TokenType.POW):
            operator: Token = self.previous()
            right: Expr = self.exponentiation()
            expr = Binary(expr, operator, right)
        return expr

    def unary(self) -> Expr:
        if self.match(TokenType.BANG, TokenType.MINUS):
            operator: Token = self.previous()
            right: Expr = self.exponentiation()
            expr = Unary(operator, right)
            return expr
        return self.primary()

    def primary(self) -> Expr:
        if self.match(TokenType.FALSE):
            return Literal(False)
        if self.match(TokenType.TRUE):
            return Literal(True)
        if self.match(TokenType.NULL):
            return Literal(None)
        if self.match(TokenType.INTEGER, TokenType.FLOAT, TokenType.STRING):
            literal = Literal(self.previous().literal)
            if self.match(TokenType.IDENTIFIER):
                return facVariable(
                    MVariable(
                        self.previous().lexeme,
                    ),
                    literal,
                )
            return literal
        if self.match(TokenType.IDENTIFIER):
            return self.variable()
        if self.match(TokenType.LEFT_PAREN):
            expr: Expr = self.expression()
            self.consume(
                TokenType.RIGHT_PAREN,
                "Expected Enclosing parentheses ')' after expression.'",
            )
            return Grouping(expr)
        if self.match(TokenType.LEFT_BRACKET):
            return self.arrayLiteral()
        raise self.error(self.peek(), "Expect expression.")  # type: ignore

    def arrayLiteral(self) -> Expr:
        elements = []
        if not self.check(TokenType.RIGHT_BRACKET):
            while True:
                elements.append(self.expression())
                if not self.match(TokenType.COMMA):
                    break
        self.consume(TokenType.RIGHT_BRACKET, "Expect ']' after list elements.")
        return Array(array(elements))

    def variable(self) -> Expr:
        name = self.previous()
        if self.match(TokenType.EQUAL):
            value = self.expression()
            return Var(name, value)  # type: ignore
        return Variable(name)

    def consume(self, type: TokenType, message: str) -> Token:
        if self.check(type):
            return self.advance()  # type: ignore
        raise self.error(self.peek(), message)  # type: ignore

    def error(self, token: Token, message: str) -> ParseError:
        self.tokenError(token, message)
        return ParseError()

    def tokenError(self, token: Token, message: str) -> None:
        if token.type == TokenType.EOF:
            report(token.line, " at end", message)
        else:
            report(token.line, " at '" + token.lexeme + "'", message)
        exit(1)

    def sync(self):
        self.advance()
        while not self.isAtEnd():
            if self.previous().type == TokenType.SEMICOLON:
                return
            match self.peek().type:  # type: ignore
                case TokenType.FUN:
                    return
                case TokenType.FOR:
                    return
                case TokenType.IF:
                    return
                case TokenType.WHILE:
                    return
                case TokenType.PRINT:
                    return
                case TokenType.PRINTLN:
                    return
                case TokenType.RETURN:
                    return
                case TokenType.HTTP:
                    return
                case TokenType.FTP:
                    return
                case TokenType.STMP:
                    return
                case TokenType.TCP:
                    return
                case TokenType.IP:
                    return
                case TokenType.SSL:
                    return
                case TokenType.TYPE_INTEGER:
                    return
                case TokenType.TYPE_FLOAT:
                    return
                case TokenType.TYPE_BOOLEN:
                    return
                case TokenType.TYPE_STRING:
                    return
