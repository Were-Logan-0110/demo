from dataclasses import dataclass, field
from interpreter import Token, error
from abc import ABC, abstractmethod
from numpy import ndarray
from typing import Final
from math import log
import operator

ops = {
    "+": operator.add,
    "-": operator.sub,
    "*": operator.mul,
    "**": operator.pow,
    "/": operator.truediv,
    "%": operator.mod,
    "^": operator.xor,
}


class Expr(ABC):
    @abstractmethod
    def accept(self, visitor):
        error(-1, "No Accept Method Found For Object: <{}>".format(self.__class__))
        exit(1)


@dataclass
class Binary(Expr):
    left: Final[Expr]
    operator: Final[Token]
    right: Final[Expr]

    def accept(self, visitor):
        return visitor.visitBinaryExpr(self)


@dataclass
class Grouping(Expr):
    expression: Expr

    def accept(self, visitor):
        return visitor.visitGroupExpr(self)


@dataclass
class Literal(Expr):
    value: object

    def accept(self, visitor):
        return visitor.visitLiteralExpr(self)


@dataclass
class Array(Expr):
    elements: ndarray[Expr]

    def accept(self, visitor):
        return visitor.visitArrayExpr(self)


@dataclass
class Index(Expr):
    collection: Expr
    index: Expr


@dataclass
class Unary(Expr):
    operator: Token
    right: Expr

    def accept(self, visitor):
        return visitor.visitUnaryExpr(self)


@dataclass
class Variable(Expr):
    name: Final[Token]

    def accept(self, visitor) -> None:
        return visitor.visitVariableExpr(self)


class Stmt(ABC):
    @abstractmethod
    def accept(self, visitor):
        pass


class Unknown(Expr):
    def accept(self, visitor) -> None:
        return visitor.visitUnknownExpr()


@dataclass
class Var(Expr):
    name: Token
    initializer: Expr = Unknown()

    def accept(self, visitor):
        return visitor.visitVarStmt(self)


@dataclass
class facVariable(Expr):
    variable: Var
    factor: Literal

    def accept(self, visitor):
        return visitor.visitFacVariableExpr(self)


@dataclass
class Expression(Stmt):
    expression: Expr

    def accept(self, visitor) -> None:
        return visitor.visitExpressionStmt(self)


@dataclass
class Block(Stmt):
    statements: list[Stmt]
    stmtBlock: bool = False

    def accept(self, visitor):
        return visitor.visitBlockStmt(self)


@dataclass
class If(Stmt):
    condition: Expr
    thenBranch: Stmt
    elseIfs: "list[If]" = field(default_factory=[])  # type: ignore
    elseBranch: Stmt | None = None

    def accept(self, visitor):
        return visitor.visitIfStmt(self)


@dataclass
class While(Stmt):
    condition: Expr
    body: Stmt

    def accept(self, visitor):
        return visitor.visitWhileStmt(self)


@dataclass
class For(Stmt):
    initializer: Expression


@dataclass
class Foreach(Stmt):
    collections: Array
    body: Stmt
    variable: Variable | None = None

    def accept(self, visitor):
        return visitor.visitForeachStmt(self)


@dataclass
class Break(Stmt):
    def accept(self, visitor):
        return visitor.visitBreakStmt(self)


@dataclass
class Continue(Stmt):
    def accept(self, visitor):
        return visitor.visitContinueStmt(self)


@dataclass
class Print(Expression):
    newLine: bool = False

    def accept(self, visitor):
        return visitor.visitPrintStmt(self)


class MExpression:
    priority = True
    op = "."

    def apply(self):
        pass

    def simplify(self):
        pass

    def differentiate(self) -> "MExpression":
        pass

    def depthSimplify(self, left, right):
        opFunc = ops.get(self.op)
        try:
            print(
                "DepSimp -> {} -> {}:{} -> {}:{}".format(opFunc, left, left.__class__.__name__, right, right.__class__.__name__)
            )
        except:
            pass

        def toMNumber(value):
            return MNumber(value) if isinstance(value, (int, float)) else value

        left = toMNumber(left)
        right = toMNumber(right)

        def handleFactorVariables(leftFactor, rightFactor, opFunc, var):
            return (Addition if isinstance(left, Addition) else Subtraction)(
                left.left,
                MFactorVariable(
                    opFunc(
                        toMNumber(leftFactor).simplify(),
                        toMNumber(rightFactor).simplify(),
                    ),
                    var,
                ),
            )

        def handleSumExpr(leftNum, rightNum):
            return (Addition if isinstance(left, Addition) else Subtraction)(
                left.left,
                ops[left.op](
                    toMNumber(leftNum).simplify(), toMNumber(rightNum).simplify()
                ),
            )

        def handleFactorExprs(leftFactor, rightFactor, opFunc, expr):
            return (Addition if isinstance(left, Addition) else Subtraction)(
                MFactorExpr(
                    opFunc(leftFactor.simplify(), rightFactor.simplify()), expr
                ),
                (
                    toMNumber(left.right).simplify()
                    if isinstance(left, (Addition, Subtraction))
                    else right.right.simplify()
                ),
            )

        def sumExprFactors(left: MFactorExpr, right: MFactorExpr):
            return MFactorExpr(
                toMNumber(opFunc(left.factor, right.factor).simplify()), left.expr
            )

        def expandSquare(sLeft, sRight):
            return (
                ops[(Addition if isinstance(left, Addition) else Subtraction).op](
                    sLeft**2, MFactorExpr(2, sLeft * sRight)
                )
                + sRight**2
            )

        if (
            isinstance(self, (Subtraction, Addition))
            and isinstance(left, MExpression)
            and isinstance(right, MExpression)
            and left.__str__(False) == right.__str__(False)
        ):
            if isinstance(self, Subtraction):
                return MNumber(0)
            elif isinstance(self, Addition):
                return MNumber(2) * left
        if isinstance(left, (Addition, Subtraction)):
            print(
                "Yes???: {}:{}:{}".format(left.right, left.right.__class__.__name__, right.__class__.__name__)
            )
            if isinstance(right, MVariable):
                right = MFactorVariable(MNumber(1), right.name)
            if isinstance(left, MVariable):
                left = MFactorExpr(MNumber(1), left.name)
            if (
                isinstance(self, Exponentiation)
                and isinstance(toMNumber(right), MNumber)
                and right == 2
            ):
                return expandSquare(left.left, left.right)
            if isinstance(toMNumber(left.right), MNumber) and isinstance(
                toMNumber(right), MNumber
            ):
                return handleSumExpr(toMNumber(left.right), right)
            if (
                isinstance(left.left, MFactorVariable)
                and isinstance(right, MFactorVariable)
                and str(left.left.variable) == str(right.variable)
            ):
                return handleFactorVariables(
                    left.left.factor, right.factor, opFunc, left.left.variable
                )
            if (
                isinstance(left.right, MFactorVariable)
                and isinstance(right, MFactorVariable)
                and str(left.right.variable) == str(right.variable)
            ):
                return handleFactorVariables(
                    left.right.factor, right.factor, opFunc, right.variable
                )
            if (
                isinstance(left.left, MFactorExpr)
                and isinstance(right, MFactorExpr)
                and str(left.left.expr) == str(right.expr)
            ):
                return handleFactorExprs(
                    left.left.factor, right.factor, opFunc, left.left.expr
                )
            if (
                isinstance(left.right, MFactorExpr)
                and isinstance(right, MFactorExpr)
                and str(left.right.expr) == str(right.expr)
            ):
                return handleFactorExprs(
                    left.right.factor, right.factor, opFunc, right.expr
                )
        if isinstance(right, (Addition, Subtraction)):
            if isinstance(right, MVariable):
                right = MFactorVariable(MNumber(1), right.name)
            if isinstance(left, MVariable):
                left = MFactorExpr(MNumber(1), left.name)
            if (
                isinstance(self, Exponentiation)
                and isinstance(toMNumber(left), MNumber)
                and left == 2
            ):
                return expandSquare(right.left, right.right)
            if (
                isinstance(right.left, MFactorVariable)
                and isinstance(left, MFactorVariable)
                and str(right.left.variable) == str(left.variable)
            ):
                return handleFactorVariables(
                    right.left.factor, left.factor, opFunc, right.left.variable
                )
            if (
                isinstance(right.right, MFactorVariable)
                and isinstance(left, MFactorVariable)
                and str(right.right.variable) == str(left.variable)
            ):
                return handleFactorVariables(
                    right.right.factor, left.factor, opFunc, right.variable
                )
            if (
                isinstance(right.left, MFactorExpr)
                and isinstance(left, MFactorExpr)
                and str(right.left.expr) == str(left.expr)
            ):
                return handleFactorExprs(
                    right.left.factor, left.factor, opFunc, right.left.expr
                )
            if (
                isinstance(right.right, MFactorExpr)
                and isinstance(left, MFactorExpr)
                and str(right.right.expr) == str(left.expr)
            ):
                return handleFactorExprs(
                    right.right.factor, left.factor, opFunc, right.right.expr
                )

            # if isinstance(exponent, MNumber) and exponent.num == 2:
            #     if isinstance(base, Addition):
            #         terms = [base.left, base.right]
            #         result = MNumber(0)
            #         for i in range(len(terms)):
            #             for j in range(len(terms)):
            #                 result += terms[i] * terms[j]
            #         return result.simplify()
            # return Exponentiation(left, right)
        if (
            isinstance(self, (Subtraction, Addition))
            and isinstance(left, MFactorExpr)
            and isinstance(right, MFactorExpr)
            and left.expr.__str__(False) == right.expr.__str__(False)
        ):
            print("Yeah? -> {} -> {}".format(left, right))
            return sumExprFactors(left, right)
        return None

    def __mul__(self, other: "MExpression"):
        mult = Mult(self, other)
        mult.priority = self.priority
        return mult

    def __rmul__(self, other):
        return self.__mul__(other)

    def __add__(self, other: "MExpression"):
        addition = Addition(self, other)
        addition.priority = self.priority
        return addition

    def __radd__(self, other):
        return self.__add__(other)

    def __sub__(self, other: "MExpression"):
        sub = Subtraction(self, other)
        sub.priority = self.priority
        return sub

    def __rsub__(self, other):
        sub = Subtraction(other, self)
        sub.priority = self.priority
        return sub

    def __truediv__(self, other: "MExpression"):
        div = Division(self, other)
        div.priority = self.priority
        return div

    def __rtruediv__(self, other):
        div = Division(other, self)
        div.priority = self.priority
        return div

    def __pow__(self, exponent: "MExpression"):
        expo = Exponentiation(self, exponent)
        expo.priority = self.priority
        return expo

    def __rpow__(self, base):
        expo = Exponentiation(base, self)
        expo.priority
        return expo

    def __neg__(self):
        neg = Negation(self)
        neg.priority = self.priority
        return neg


class MNumber(MExpression):
    num: float

    def __init__(self, num) -> None:
        super().__init__()
        self.num = num.num if isinstance(num, MNumber) else num

    def differentiate(self, variable):
        return MNumber(0)

    def apply(self):
        return self._convToIntIfPossible(self.num)

    def simplify(self):
        return self._convToIntIfPossible(self.num)

    def __str__(self, priority=None):
        if priority == None:
            priority = self.priority
        return str(self._convToIntIfPossible(self.num))

    def _convToIntIfPossible(self):
        if isinstance(self.num, float) and self.num == int(self.num):
            return int(self.num)
        return self.num

    def __eq__(self, other):
        if isinstance(other, MNumber):
            return self.num == other.num
        if isinstance(other, (int, float)):
            return self.num == other
        return False


@dataclass
class MVariable(MExpression):
    name: str

    def differentiate(self, target: str):
        return MNumber(1) if self.name == target else MNumber(0)

    def apply(self):
        return self

    def simplify(self):
        return self

    def __str__(self, priority=None):
        if priority == None:
            priority = self.priority
        return self.name


@dataclass
class Addition(MExpression):
    left: MExpression
    right: MExpression
    op = "+"

    def differentiate(self, target):
        return self.left.differentiate(target) + self.right.differentiate(target)

    def apply(self):
        return self.left.apply() + self.right.apply()

    def simplify(self):
        left = (
            self.left
            if isinstance(self.left, (int, float))
            or isinstance(self.left, (Division, NonSDiv))
            else self.left.simplify()
        )
        right = (
            self.right
            if isinstance(self.right, (int, float))
            or isinstance(self.right, (Division, NonSDiv))
            else self.right.simplify()
        )

        print("Add -> Left: {}, Right: {}".format(left, right))
        if left == 0:
            return right
        elif right == 0:
            return left
        depthSimplify = self.depthSimplify(left, right)
        if depthSimplify:
            print("Add -> DepthSimplify: {}".format(depthSimplify))
            depthSimplify.priority = self.priority
            return depthSimplify
        result = left + right
        if isinstance(result, MExpression):
            result.priority = self.priority
        return result

    def __str__(self, priority=None):
        if priority == None:
            priority = self.priority
        return (
            "({} + {})".format(self.left, self.right)
            if priority
            else "{} + {}".format(self.left, self.right)
        )


@dataclass
class Subtraction(MExpression):
    left: MExpression
    right: MExpression
    op = "-"

    def differentiate(self, target):
        return self.left.differentiate(target) - self.right.differentiate(target)

    def apply(self):
        return self.left.apply() - self.right.apply()

    def simplify(self):
        print(
            "Sub -> Left: {}:{}, Right: {}:{}".format(self.left, self.left.__class__.__name__, self.right, self.right.__class__.__name__)
        )
        left = (
            self.left
            if isinstance(self.left, (int, float))
            or isinstance(self.left, (Division, NonSDiv))
            else self.left.simplify()
        )
        right = (
            self.right
            if isinstance(self.right, (int, float))
            or isinstance(self.right, (Division, NonSDiv))
            else self.right.simplify()
        )
        print(
            "Sub -> Left: {}:{}, Right: {}:{}".format(left, left.__class__.__name__, right, right.__class__.__name__)
        )
        if left == 0:
            return right
        elif right == 0:
            return left
        depthSimplify = self.depthSimplify(left, right)
        if depthSimplify:
            print("Substract -> Depth -> {}".format(depthSimplify))
            depthSimplify.priority = self.priority
            return depthSimplify
        result = left - right
        if isinstance(result, MExpression):
            result.priority = self.priority
        return result

    def __str__(self, priority=None):
        if priority == None:
            priority = self.priority
        return (
            "({} - {})".format(self.left, self.right)
            if priority
            else "{} - {}".format(self.left, self.right)
        )


@dataclass
class Mult(MExpression):
    left: MExpression
    right: MExpression
    op = "*"

    def differentiate(self, target):
        return (
            self.left.differentiate(target) * self.right
            + self.right.differentiate(target) * self.left
        )

    def apply(self):
        return self.left.apply() * self.right.apply()

    def simplify(self):
        print(
            "Before Simp Mult -> {}:{} -> {}:{}".format(self.left, self.left.__class__.__name__, self.right, self.right.__class__.__name__)
        )
        left = (
            self.left
            if isinstance(self.left, (int, float))
            or isinstance(self.left, (Division, NonSDiv))
            else self.left.simplify()
        )
        right = (
            self.right
            if isinstance(self.right, (int, float))
            or isinstance(self.right, (Division, NonSDiv))
            else self.right.simplify()
        )
        if left == 0 or right == 0:
            return 0
        elif left == 1:
            return right
        elif right == 1:
            return left
        left = MNumber(left) if isinstance(left, int) else left
        right = MNumber(right) if isinstance(right, int) else right
        result = None
        print("Mult -> Left: {}, Right: {}:{}".format(left, right, right.priority))
        if isinstance(left, MNumber) and isinstance(right, MVariable):
            result = MFactorVariable(left, right)
        elif isinstance(left, Addition) and isinstance(right, MNumber):
            aLeft = (
                left.left.simplify()
                if isinstance(left.left, MExpression)
                else left.left
            )
            aRight = (
                left.right.simplify()
                if isinstance(left.right, MExpression)
                else left.right
            )
            result = Addition((aLeft * right.num), aRight * right.num).simplify()
        elif isinstance(right, Addition) and isinstance(left, MNumber):
            aLeft = (
                right.left.simplify()
                if isinstance(right.left, MExpression)
                else right.left
            )
            aRight = (
                right.right.simplify()
                if isinstance(right.right, MExpression)
                else right.right
            )
            result = Addition((aLeft * left.num), aRight * left.num).simplify()
        elif isinstance(right, MNumber) and isinstance(left, MVariable):
            result = MFactorVariable(right, left)
        elif isinstance(left, MFactorVariable) and isinstance(right, MNumber):
            result = MFactorVariable(left.factor.simplify() * right.num, left.variable)
        elif isinstance(right, MFactorVariable) and isinstance(left, MNumber):
            result = MFactorVariable(right.factor.simplify() * left.num, right.variable)
        elif isinstance(left, Exponentiation) and isinstance(right, MNumber):
            result = MFactorExpr(right, left)
        elif isinstance(right, Exponentiation) and isinstance(left, MNumber):
            result = MFactorExpr(left, right)
        elif isinstance(left, MFactorExpr) and isinstance(right, MNumber):
            result = MFactorExpr(left.factor.simplify() * right.num, left.expr)
        elif isinstance(right, MFactorExpr) and isinstance(left, MNumber):
            result = MFactorExpr(right.factor.simplify() * left.num, right.expr)
        if not result:
            result = (left.simplify() if isinstance(left, MExpression) else left) * (
                right.simplify() if isinstance(right, MExpression) else right
            )
        if result:
            if isinstance(result, MExpression):
                result.priority = self.priority
                if not isinstance(result, (Division, NonSDiv)):
                    result = result.simplify()
            print("Mult Res -> {}:{}".format(result, result.__class__.__name__))
            return result
        return result

    def __str__(self, priority=None):
        if priority == None:
            priority = self.priority
        return (
            "({}*{})".format(self.left, self.right) if priority else "{}*{}".format(self.left, self.right)
        )


@dataclass
class MFactorVariable(MExpression):
    factor: MExpression
    variable: MVariable

    def differentiate(self, target) -> MExpression:
        return Mult(self.factor, self.variable).differentiate(target)

    def apply(self):
        return Mult(self.factor, self.variable).apply()

    def simplify(self):
        print(
            "MFactor Var -> {}{} -> {}:{}".format(self.factor, self.factor.__class__.__name__, self.variable, self.variable.__class__.__name__)
        )
        return Mult(self.factor, self.variable, True).simplify()

    def __str__(self, priority=None):
        if priority == None:
            priority = self.priority
        return "{}*{}".format(self.factor, self.variable)


@dataclass
class MFactorExpr(MExpression):
    factor: MExpression
    expr: MExpression

    def differentiate(self, target) -> MExpression:
        return self.factor.differentiate(target) * self.expr.differentiate(target)

    def apply(self):
        return Mult(self.factor, self.expr).apply()

    def simplify(self):
        print(
            "MFactor Expr -> {}:{} -> {}:{}".format(self.factor, self.factor.__class__.__name__, self.expr, self.expr.__class__.__name__)
        )
        return Mult(self.factor, self.expr)

    def __str__(self, priority=None):
        if priority == None:
            priority = self.priority
        return (
            ("{}*{}".format(self.factor, self.expr) if self.factor != 1 else "{}".format(self.expr))
            if self.priority
            else ("{}*{}".format(self.factor, self.expr) if self.factor != 1 else "{}".format(self.expr))
        )


@dataclass
class Division(MExpression):
    numerator: MExpression
    denominator: MExpression

    def differentiate(self, target):
        return (
            self.numerator.differentiate(target) * self.denominator
            - self.denominator.differentiate(target) * self.numerator
        ) / (self.denominator * self.denominator)

    def apply(self):
        return self.numerator.apply() / self.denominator.apply()

    def simplify(self):
        numerator = (
            self.numerator
            if isinstance(self.numerator, (int, float))
            else self.numerator.simplify()
        )
        denominator = (
            self.denominator
            if isinstance(self.denominator, (int, float))
            else self.denominator.simplify()
        )
        print(
            "Div -> {}:{} -> {}:{}".format(numerator, numerator.__class__.__name__, denominator, denominator.__class__.__name__)
        )
        if numerator == denominator:
            return 1
        if numerator == 0:
            return 0
        if denominator == 0:
            return ZeroDivisionError(
                "Zero Division On Denominator: < {} >".format(self.denominator)
            )
        return Mult(numerator, NonSDiv(1, denominator)).simplify()

    def __str__(self, priority=None):
        if priority == None:
            priority = self.priority
        return (
            "{} / {}".format(self.numerator, self.denominator)
            if priority
            else "{} / {}".format(self.numerator, self.denominator)
        )


@dataclass
class NonSDiv(Division):
    def simplify(self):
        print("Am i asked to simplify this shit?")
        print(
            "NonS Div -> {}:{} -> {}:{}".format(self.numerator, self.numerator.__class__.__name__, self.denominator, self.denominator.__class__.__name__)
        )
        return self


@dataclass
class Exponentiation(MExpression):
    base: MExpression
    exponent: MExpression
    op = "**"

    def differentiate(self, target):
        return self.exponent * (
            self.base ** (self.exponent - MNumber(1))
        ) * self.base.differentiate(target) + (self.base**self.exponent) * MLog(
            self.base
        ).differentiate(
            target
        ) * self.exponent.differentiate(
            target
        )

    def apply(self):
        return self.base.apply() ** self.exponent.apply()

    def simplify(self):
        base = (
            self.base
            if isinstance(self.base, (int, float)) or isinstance(self.base, Division)
            else self.base.simplify()
        )
        exponent = (
            self.exponent
            if isinstance(self.exponent, (int, float))
            or isinstance(self.base, Division)
            else self.exponent.simplify()
        )
        if exponent == 0:
            return 1
        elif exponent == 1:
            return base
        base = MNumber(base) if isinstance(base, (int, float)) else base
        exponent = MNumber(exponent) if isinstance(exponent, (int, float)) else exponent
        print("Expo -> Left: {}, Right: {}".format(base, exponent))
        if isinstance(base, Exponentiation) and isinstance(exponent, MNumber):
            return Exponentiation(
                base.base, base.exponent.simplify() * exponent.simplify()
            )
        depthSimplify = self.depthSimplify(base, exponent)
        if depthSimplify:
            print("Expo -> Depth -> {}".format(depthSimplify))
            depthSimplify.priority = self.priority
            return depthSimplify
        return base**exponent

    def __str__(self, priority=None):
        if priority == None:
            priority = self.priority
        return (
            "({}**{})".format(self.base, self.exponent)
            if priority
            else "{}**{}".format(self.base, self.exponent)
        )


@dataclass
class Negation(MExpression):
    expr: MExpression

    def differentiate(self, target):
        return -self.expr.differentiate(target)

    def apply(self):
        return -self.expr.apply()

    def simplify(self):
        return -self.expr.simplify()

    def __str__(self):
        return "(-{})".format(self.expr)


@dataclass
class MLog(MExpression):
    expr: MExpression

    def differentiate(self, target):
        return MNumber(1) / self.expr

    def apply(self):
        expr = self.expr.apply()
        if isinstance(expr, (int, float)):
            return log(expr)
        elif isinstance(expr, MNumber):
            return log(expr.num)
        else:
            return self

    def simplify(self):
        appliedExpr = self.apply()
        if isinstance(appliedExpr, (float, int)):
            return MNumber(appliedExpr)
        return self

    def __str__(self):
        return "log({})".format(self.expr)
