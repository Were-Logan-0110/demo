from numpy import ndarray, array
from ast_._expression import *
from interpreter import *
from copy import deepcopy


class ExprVisitor:
    
    def visitBinaryExpr(self, expr: Binary):
        pass

    
    def visitLiteralExpr(self, expr: Literal):
        pass

    
    def visitUnaryExpr(self, expr: Unary):
        pass

    
    def visitGroupingExpr(self, expr: Grouping):
        pass

    
    def visitArrayExpr(self, expr: Array):
        pass

    
    def visitFacVariableExpr(self, expr: FacVariable):
        pass

    
    def visitVariableExpr(self, expr: Variable):
        pass


class StmtVisitor:
    
    def visitExpressionStmt(self, stmt: Expression):
        pass

    
    def visitBlockStmt(self, stmt: Block):
        pass

    
    def visitPrintStmt(self, stmt: Print):
        pass

    
    def visitVarStmt(self, stmt: Var):
        pass

    
    def visitIfStmt(self, stmt: If):
        pass

    
    def visitWhileStmt(self, stmt: While):
        pass

    
    def visitForeachStmt(self, stmt: Foreach):
        pass

    
    def visitBreakStmt(self, stmt: Break):
        pass

    
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

    def visitGroupingExpr(self, expr: Grouping):
        return self.evaluate(expr.expression)

    def visitUnaryExpr(self, expr: Unary) -> object:
        right: object = self.evaluate(expr.right)
        expr.right
        if expr.operator.type == MINUS:
                return -right  # type: ignore
        elif expr.operator.type == BANG:
                return not self.isTruthy(right)
        return None

    def visitBinaryExpr(self, expr: Binary):
        right: object = self.evaluate(expr.right)
        left: object = self.evaluate(expr.left)
        try:
            if expr.operator.type == MINUS:
                    return left - right  # type: ignore
            elif expr.operator.type == PLUS:
                    return left + right  # type: ignore
            elif expr.operator.type == SLASH:
                    return left / right  # type: ignore
            elif expr.operator.type == STAR:
                    return left * right  # type: ignore
            elif expr.operator.type == AND:
                    return left & right  # type: ignore
            elif expr.operator.type == OR:
                    return left | right  # type: ignore
            elif expr.operator.type == XOR:
                    return left & right  # type: ignore
            elif expr.operator.type == L_SHIFT:
                    return left << right  # type: ignore
            elif expr.operator.type == R_SHIFT:
                    return left >> right  # type: ignore
            elif expr.operator.type == GREATER:
                    return left > right  # type: ignore
            elif expr.operator.type == GREATER_EQUAL:
                    return left >= right  # type: ignore
            elif expr.operator.type == LESS:
                    return left < right  # type: ignore
            elif expr.operator.type == LESS_EQUAL:
                    return left <= right  # type: ignore
            elif expr.operator.type == BANG_EQUAL:
                    return not self.isEqual(left, right)
            elif expr.operator.type == EQUAL_EQUAL:
                    return self.isEqual(left, right)
        except Exception as e:
            report(
                expr.operator.line,
                "",
                " unsupported operand type(s) for {}: '{}' and '{}' ".format(expr.operator.lexeme, left.__class__.__name__, right.__class__.__name__),
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
        return Number(expr.value)

    def visitGroupingExpr(self, expr: Grouping):
        group = self.evaluate(expr.expression)
        group.priority = True
        return group

    def visitUnaryExpr(self, expr: Unary) -> object:
        right: object = self.evaluate(expr.right)
        if expr.operator.type == MINUS:
            return Negation(right)  # type: ignore
        elif expr.operator.type == BANG:
            return not self.isTruthy(right)
        elif expr.operator.type == PLUS:
            return +right
        return None
    def visitNegativeExpr(self,expr: Negative):
        return Negation(self.evaluate(expr.expression))
    def visitFacVariableExpr(self, expr: FacVariable):
        return Number(self.evaluate(expr.factor)).mul(MVariable(expr.variable.name))

    def visitBinaryExpr(self, expr: Binary):
        right: object = self.evaluate(expr.right)
        left: object = self.evaluate(expr.left)
        try:
            if expr.operator.type == MINUS:
                return Subtraction(left, right)  # type: ignore
            elif expr.operator.type == PLUS:
                return Addition(left, right)  # type: ignore
            elif expr.operator.type == SLASH:
                return Division(left, right)  # type: ignore
            elif expr.operator.type == STAR:
                return Multiplication(left, right)  # type: ignore
            elif expr.operator.type == POW:
                return Exponentiation(left, right)  # type: ignore
            elif expr.operator.type == AND:
                return left & right  # type: ignore
            elif expr.operator.type == OR:
                return left | right  # type: ignore
            elif expr.operator.type == XOR:
                return left & right  # type: ignore
            elif expr.operator.type == L_SHIFT:
                return left << right  # type: ignore
            elif expr.operator.type == R_SHIFT:
                return left >> right  # type: ignore
            elif expr.operator.type == GREATER:
                return left > right  # type: ignore
            elif expr.operator.type == GREATER_EQUAL:
                return left >= right  # type: ignore
            elif expr.operator.type == LESS:
                return left < right  # type: ignore
            elif expr.operator.type == LESS_EQUAL:
                return left <= right  # type: ignore
            elif expr.operator.type == BANG_EQUAL:
                return not self.isEqual(left, right)
            elif expr.operator.type == EQUAL_EQUAL:
                return self.isEqual(left, right)
        except Exception as e:
            from traceback import format_exc
            print(format_exc())
            report(
                expr.operator.line,
                "",
                " unsupported operand type(s) for {}: '{}' and '{}' ".format(expr.operator.lexeme, left.__class__.__name__, right.__class__.__name__),
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
