from interpreter import TokenType, report, Environment
from ast_.expression import Binary, Literal, Stmt
from ast_.expression import Grouping
from ast_.expression import Unary
from numpy import ndarray, array
from ast_.expression import *
from copy import deepcopy


class ExprVisitor(ABC):
    @abstractmethod
    def visitBinaryExpr(self, expr: Binary):
        pass

    @abstractmethod
    def visitLiteralExpr(self, expr: Literal):
        pass

    @abstractmethod
    def visitUnaryExpr(self, expr: Unary):
        pass

    @abstractmethod
    def visitGroupExpr(self, expr: Grouping):
        pass

    @abstractmethod
    def visitArrayExpr(self, expr: Array):
        pass

    @abstractmethod
    def visitFacVariableExpr(self, expr: facVariable):
        pass

    @abstractmethod
    def visitVariableExpr(self, expr: Variable):
        pass


class StmtVisitor(ABC):
    @abstractmethod
    def visitExpressionStmt(self, stmt: Expression):
        pass

    @abstractmethod
    def visitBlockStmt(self, stmt: Block):
        pass

    @abstractmethod
    def visitPrintStmt(self, stmt: Print):
        pass

    @abstractmethod
    def visitVarStmt(self, stmt: Var):
        pass

    @abstractmethod
    def visitIfStmt(self, stmt: If):
        pass

    @abstractmethod
    def visitWhileStmt(self, stmt: While):
        pass

    @abstractmethod
    def visitForeachStmt(self, stmt: Foreach):
        pass

    @abstractmethod
    def visitBreakStmt(self, stmt: Break):
        pass

    @abstractmethod
    def visitContinueStmt(self, stmt: Continue):
        pass


class ASTInterpreter(ExprVisitor, StmtVisitor):
    environment: Environment = Environment({})
    loopBroken: bool = False
    continueEmit: bool = False

    def accept(self, visitor):
        return super().accept(visitor)

    def interpret(self, statements: list[Stmt]):
        try:
            for statement in statements:
                self.execute(statement)
        except Exception as e:
            raise RuntimeError(e)

    def execute(self, statement: Stmt):
        statement.accept(self)

    def visitArrayExpr(self, expr: Array):
        return array([self.evaluate(element) for element in expr.elements])

    def visitBlockStmt(self, stmt: Block):
        self.executeBlock(
            stmt.statements, Environment({}, self.environment), stmt.stmtBlock
        )

    def visitExpressionStmt(self, stmt: Expression):
        self.evaluate(stmt.expression)

    def visitForeachStmt(self, stmt: Foreach):
        collection = self.evaluate(stmt.collections)
        for i in range(collection.__len__()):
            if self.loopBroken:
                self.loopBroken = False
                break
            if self.continueEmit:
                self.continueEmit = False
                continue
            if stmt.variable:
                self.visitVarStmt(Var(stmt.variable.name, Literal(collection[i])))
            self.execute(stmt.body)

    def visitBreakStmt(self, stmt: Break):
        self.loopBroken = True

    def visitContinueStmt(self, stmt: Continue):
        self.continueEmit = True

    def visitPrintStmt(self, expr: Print):
        value: object = self.evaluate(expr.expression)
        if isinstance(value, None.__class__):
            value = "nil"
        print(value, end=("\n" if expr.newLine else ""))

    def visitLiteralExpr(self, expr: Literal) -> object:
        return expr.value

    def visitGroupExpr(self, expr: Grouping):
        return self.evaluate(expr.expression)

    def visitUnaryExpr(self, expr: Unary) -> object:
        right: object = self.evaluate(expr.right)
        expr.right
        match expr.operator.type:
            case TokenType.MINUS:
                return -right  # type: ignore
            case TokenType.BANG:
                return not self.isTruthy(right)
        return None

    def visitBinaryExpr(self, expr: Binary):
        right: object = self.evaluate(expr.right)
        left: object = self.evaluate(expr.left)
        try:
            match expr.operator.type:
                case TokenType.MINUS:
                    return left - right  # type: ignore
                case TokenType.PLUS:
                    return left + right  # type: ignore
                case TokenType.SLASH:
                    return left / right  # type: ignore
                case TokenType.STAR:
                    return left * right  # type: ignore
                case TokenType.AND:
                    return left & right  # type: ignore
                case TokenType.OR:
                    return left | right  # type: ignore
                case TokenType.XOR:
                    return left & right  # type: ignore
                case TokenType.L_SHIFT:
                    return left << right  # type: ignore
                case TokenType.R_SHIFT:
                    return left >> right  # type: ignore
                case TokenType.GREATER:
                    return left > right  # type: ignore
                case TokenType.GREATER_EQUAL:
                    return left >= right  # type: ignore
                case TokenType.LESS:
                    return left < right  # type: ignore
                case TokenType.LESS_EQUAL:
                    return left <= right  # type: ignore
                case TokenType.BANG_EQUAL:
                    return not self.isEqual(left, right)
                case TokenType.EQUAL_EQUAL:
                    return self.isEqual(left, right)
        except Exception as e:
            report(
                expr.operator.line,
                "",
                f" unsupported operand type(s) for {expr.operator.lexeme}: '{left.__class__.__name__}' and '{right.__class__.__name__}' ",
            )
        return None

    def visitVarStmt(self, stmt: Var):
        value: object = None
        if stmt.initializer != None:
            value = self.evaluate(stmt.initializer)
        self.environment.define(stmt.name.lexeme, value)

    def visitVariableExpr(self, stmt: Variable):
        return self.environment.get(stmt.name)

    def visitIfStmt(self, stmt: If):
        if self.isTruthy(self.evaluate(stmt.condition)):
            self.execute(stmt.thenBranch)
        elif stmt.elseIfs:
            for _elif in stmt.elseIfs:
                if self.isTruthy(self.evaluate(_elif.condition)):
                    self.execute(_elif.thenBranch)
                    return
        elif stmt.elseBranch:
            self.execute(stmt.elseBranch)

    def visitWhileStmt(self, stmt: While):
        while self.isTruthy(self.evaluate(stmt.condition)):
            if self.loopBroken:
                self.loopBroken = False
                break
            if self.continueEmit:
                self.continueEmit = False
                continue
            self.execute(stmt.body)

    def executeBlock(
        self, statements: list[Stmt], environment: Environment, stmtBlock: bool = False
    ):
        try:
            if not stmtBlock:
                previous: Environment = deepcopy(self.environment)
                self.environment = environment
            for statement in statements:
                self.execute(statement)
        finally:
            if not stmtBlock:
                self.environment = previous

    def evaluate(self, expr: Expr):
        return expr.accept(self)

    def isTruthy(self, obj: object):
        return bool(obj)

    def isEqual(self, left: object, right: object):
        return left == right


class MAST(ExprVisitor, StmtVisitor):
    target: str = "x"

    def accept(self, visitor):
        return super().accept(visitor)

    def evaluate(self, expr: Expr) -> MExpression:
        return expr.accept(self)
    def interpret(self, statement: Stmt):
        try:
            self.execute(statement)
        except Exception as e:
            raise RuntimeError(e)

    def execute(self, statement: Stmt):
        statement.accept(self)

    def visitLiteralExpr(self, expr: Literal) -> object:
        return MNumber(expr.value)

    def visitGroupExpr(self, expr: Grouping):
        group = self.evaluate(expr.expression)
        return group
    def visitUnaryExpr(self, expr: Unary) -> object:
        right: object = self.evaluate(expr.right)
        match expr.operator.type:
            case TokenType.MINUS:
                return -right  # type: ignore
            case TokenType.BANG:
                return not self.isTruthy(right)
            case TokenType.PLUS:
                return +right
        return None

    def visitFacVariableExpr(self, expr: facVariable):
        return MNumber(self.evaluate(expr.factor)) * MVariable(expr.variable.name)

    def visitBinaryExpr(self, expr: Binary):
        right: object = self.evaluate(expr.right)
        left: object = self.evaluate(expr.left)
        try:
            match expr.operator.type:
                case TokenType.MINUS:
                    return Subtraction(left, right)  # type: ignore
                case TokenType.PLUS:
                    return Addition(left, right)  # type: ignore
                case TokenType.SLASH:
                    return Division(left, right)  # type: ignore
                case TokenType.STAR:
                    return Mult(left, right)  # type: ignore
                case TokenType.POW:
                    return Exponentiation(left, right)  # type: ignore
                case TokenType.AND:
                    return left & right  # type: ignore
                case TokenType.OR:
                    return left | right  # type: ignore
                case TokenType.XOR:
                    return left & right  # type: ignore
                case TokenType.L_SHIFT:
                    return left << right  # type: ignore
                case TokenType.R_SHIFT:
                    return left >> right  # type: ignore
                case TokenType.GREATER:
                    return left > right  # type: ignore
                case TokenType.GREATER_EQUAL:
                    return left >= right  # type: ignore
                case TokenType.LESS:
                    return left < right  # type: ignore
                case TokenType.LESS_EQUAL:
                    return left <= right  # type: ignore
                case TokenType.BANG_EQUAL:
                    return not self.isEqual(left, right)
                case TokenType.EQUAL_EQUAL:
                    return self.isEqual(left, right)
        except Exception as e:
            report(
                expr.operator.line,
                "",
                f" unsupported operand type(s) for {expr.operator.lexeme}: '{left.__class__.__name__}' and '{right.__class__.__name__}' ",
            )
        return None

    def isTruthy(self, obj: object):
        return bool(obj)

    def isEqual(self, left: object, right: object):
        return left == right

    def visitArrayExpr(self, expr: Array):
        return super().visitArrayExpr(expr)

    def visitBlockStmt(self, stmt: Block):
        return super().visitBlockStmt(stmt)

    def visitBreakStmt(self, stmt: Break):
        return super().visitBreakStmt(stmt)

    def visitContinueStmt(self, stmt: Continue):
        return super().visitContinueStmt(stmt)

    def visitExpressionStmt(self, stmt: Expression):
        return super().visitExpressionStmt(stmt)

    def visitForeachStmt(self, stmt: Foreach):
        return super().visitForeachStmt(stmt)

    def visitIfStmt(self, stmt: If):
        return super().visitIfStmt(stmt)

    def visitPrintStmt(self, stmt: Print):
        pass

    def visitVarStmt(self, stmt):
        pass

    def visitVariableExpr(self, expr):
        return MVariable(expr.name.lexeme)

    def visitWhileStmt(self, stmt):
        pass


class ASTSimplifier(MAST):
    def visitBinaryExpr(self, expr: Binary):
        right: object = self.evaluate(expr.right)
        left: object = self.evaluate(expr.left)
        try:
            match expr.operator.type:
                case TokenType.MINUS:
                    return Subtraction(left, right)  # type: ignore
                case TokenType.PLUS:
                    return Addition(left, right)  # type: ignore
                case TokenType.SLASH:
                    return Division(left, right)  # type: ignore
                case TokenType.STAR:
                    return Mult(left, right)  # type: ignore
                case TokenType.POW:
                    return Exponentiation(left, right)  # type: ignore
                case TokenType.AND:
                    return left & right  # type: ignore
                case TokenType.OR:
                    return left | right  # type: ignore
                case TokenType.XOR:
                    return left & right  # type: ignore
                case TokenType.L_SHIFT:
                    return left << right  # type: ignore
                case TokenType.R_SHIFT:
                    return left >> right  # type: ignore
                case TokenType.GREATER:
                    return left > right  # type: ignore
                case TokenType.GREATER_EQUAL:
                    return left >= right  # type: ignore
                case TokenType.LESS:
                    return left < right  # type: ignore
                case TokenType.LESS_EQUAL:
                    return left <= right  # type: ignore
                case TokenType.BANG_EQUAL:
                    return not self.isEqual(left, right)
                case TokenType.EQUAL_EQUAL:
                    return self.isEqual(left, right)
        except Exception as e:
            report(
                expr.operator.line,
                "",
                f" unsupported operand type(s) for {expr.operator.lexeme}: '{left.__class__.__name__}' and '{right.__class__.__name__}' ",
            )
        return None
    def evaluate(self, expr: Expr) -> MExpression:
        return super().evaluate(expr)
    def visitGroupExpr(self, expr: Grouping):
        group = self.evaluate(expr.expression)
        group.priority = True
        return group
