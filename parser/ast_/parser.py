from dataclasses import dataclass, field
from helpers import SourceIterator
from ast_._expression import *
from interpreter import *
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
        while self.match(BANG_EQUAL, EQUAL):
            operator: Token = self.previous()
            right: Expr = self.comparison()
            expr = Binary(expr, operator, right)
        return expr

    def comparison(self) -> Expr:
        expr: Expr = self.term()
        while self.match(
            AND,
            OR,
            XOR,
            R_SHIFT,
            L_SHIFT,
            GREATER,
            GREATER_EQUAL,
            LESS,
            LESS_EQUAL,
        ):
            operator: Token = self.previous()
            right: Expr = self.term()
            expr = Binary(expr, operator, right)
        return expr

    def term(self) -> Expr:
        expr: Expr = self.factor()
        while self.match(MINUS, PLUS):
            operator: Token = self.previous()
            right: Expr = self.factor()
            if operator.type == MINUS:
                expr = Binary(
                    expr, Token(PLUS, "+", None, operator.line), Negative(right)
                )
            else:
                expr = Binary(expr, operator, right)
        return expr

    def factor(self) -> Expr:
        expr: Expr = self.exponentiation()
        while self.match(SLASH, STAR):
            operator: Token = self.previous()
            right: Expr = self.exponentiation()
            expr = Binary(expr, operator, right)
        return expr

    def exponentiation(self) -> Expr:
        expr: Expr = self.unary()
        while self.match(POW):
            operator: Token = self.previous()
            right: Expr = self.exponentiation()
            expr = Binary(expr, operator, right)
        return expr

    def unary(self) -> Expr:
        if self.match(BANG, MINUS):
            operator: Token = self.previous()
            right: Expr = self.exponentiation()
            expr = Unary(operator, right) if operator.type == BANG else Negative(right)
            return expr
        return self.primary()

    def primary(self) -> Expr:
        if self.match(FALSE):
            return Literal(False)
        if self.match(TRUE):
            return Literal(True)
        if self.match(NULL):
            return Literal(None)
        if self.match(INTEGER, FLOAT, STRING):
            literal = Literal(self.previous().literal)
            if self.match(IDENTIFIER):
                return FacVariable(
                    MVariable(
                        self.previous().lexeme,
                    ),
                    literal,
                )
            return literal
        if self.match(IDENTIFIER):
            return self.variable()
        if self.match(LEFT_PAREN):
            expr: Expr = self.expression()
            self.consume(
                RIGHT_PAREN,
                "Expected Enclosing parentheses ')' after expression.'",
            )
            return Grouping(expr)
        if self.match(LEFT_BRACKET):
            return self.arrayLiteral()
        raise self.error(self.peek(), "Expect expression.")  # type: ignore

    def arrayLiteral(self) -> Expr:
        elements = []
        if not self.check(RIGHT_BRACKET):
            while True:
                elements.append(self.expression())
                if not self.match(COMMA):
                    break
        self.consume(RIGHT_BRACKET, "Expect ']' after list elements.")
        return Array(array(elements))

    def variable(self) -> Expr:
        name = self.previous()
        if self.match(EQUAL):
            value = self.expression()
            return Var(name, value)  # type: ignore
        return Variable(name)

    def consume(self, type: int, message: str) -> Token:
        if self.check(type):
            return self.advance()  # type: ignore
        raise self.error(self.peek(), message)  # type: ignore

    def error(self, token: Token, message: str) -> ParseError:
        self.tokenError(token, message)
        return ParseError()

    def tokenError(self, token: Token, message: str) -> None:
        if token.type == EOF:
            report(token.line, " at end", message)
        else:
            report(token.line, " at '" + token.lexeme + "'", message)
        exit(1)

    def sync(self):
        self.advance()
        while not self.isAtEnd():
            if self.previous().type == SEMICOLON:
                return
            if self.peek().type == FUN:
                return
            elif self.peek().type == FOR:
                return
            elif self.peek().type == IF:
                return
            elif self.peek().type == WHILE:
                return
            elif self.peek().type == PRINT:
                return
            elif self.peek().type == PRINTLN:
                return
            elif self.peek().type == RETURN:
                return
            elif self.peek().type == HTTP:
                return
            elif self.peek().type == FTP:
                return
            elif self.peek().type == STMP:
                return
            elif self.peek().type == TCP:
                return
            elif self.peek().type == IP:
                return
            elif self.peek().type == SSL:
                return
            elif self.peek().type == TYPE_INTEGER:
                return
            elif self.peek().type == TYPE_FLOAT:
                return
            elif self.peek().type == TYPE_BOOLEN:
                return
            elif self.peek().type == TYPE_STRING:
                return
