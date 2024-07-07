from interpreter import Token, error
from math import prod,log,factorial
from .abc import *

class Expr:
    def __init__(self) -> None:
        pass

    def accept(self, visitor):
        error(-1, "No Accept Method Found For Object: <" + str(self.__class__) + ">")
        exit(1)


class Expr:
    def __init__(self):
        pass

    def accept(self, visitor):
        error(-1, "No Accept Method Found For Object: <" + self.__class__ + ">")
        exit(1)


class Binary(Expr):
    def __init__(self, left: Expr, operator: Token, right: Expr) -> None:
        super().__init__()
        self.left = left
        self.operator = operator
        self.right = right

    def accept(self, visitor: "Binary"):
        return visitor.visitBinaryExpr(self)

class Negative(Expr):
    def __init__(self, expression: Expr) -> None:
        super().__init__()
        self.expression = expression

    def accept(self, visitor: "Expr"):
        return visitor.visitNegativeExpr(self)

class Grouping(Expr):
    def __init__(self, expression: Expr) -> None:
        super().__init__()
        self.expression = expression

    def accept(self, visitor: "Grouping"):
        return visitor.visitGroupingExpr(self)


class Literal(Expr):
    def __init__(self, value: object) -> None:
        super().__init__()
        self.value = value

    def accept(self, visitor: "Literal"):
        return visitor.visitLiteralExpr(self)


class Array(Expr):
    def __init__(self, elements: list[Expr]) -> None:
        super().__init__()
        self.elements = elements

    def accept(self, visitor: "Array"):
        return visitor.visitArrayExpr(self)


class Unary(Expr):
    def __init__(self, operator: Token, right: Expr) -> None:
        super().__init__()
        self.operator = operator
        self.right = right

    def accept(self, visitor: "Unary"):
        return visitor.visitUnaryExpr(self)


class Variable(Expr):
    def __init__(self, name: Token) -> None:
        super().__init__()
        self.name = name

    def accept(self, visitor: "Variable"):
        return visitor.visitVariableExpr(self)


class Unknown(Expr):
    def __init__(
        self,
    ) -> None:
        super().__init__()

    def accept(self, visitor: "Unknown"):
        return visitor.visitUnknownExpr(self)


class Var(Expr):
    def __init__(self, name: Token, initializer: Expr = Unknown()) -> None:
        super().__init__()
        self.name = name
        self.initializer = initializer

    def accept(self, visitor: "Var"):
        return visitor.visitVarExpr(self)


class FacVariable(Expr):
    def __init__(self, variable: Var, factor: Literal) -> None:
        super().__init__()
        self.variable = variable
        self.factor = factor

    def accept(self, visitor: "FacVariable"):
        return visitor.visitFacVariableExpr(self)


class Stmt:
    def __init__(self):
        pass

    def accept(self, visitor):
        error(-1, "No Accept Method Found For Object: <" + self.__class__ + ">")
        exit(1)


class Expression(Stmt):
    def __init__(self, expression: Expr) -> None:
        super().__init__()
        self.expression = expression

    def accept(self, visitor: "Expression"):
        return visitor.visitExpressionStmt(self)


class Block(Stmt):
    def __init__(self, statements: list[Stmt], stmtBlock: bool = False) -> None:
        super().__init__()
        self.statements = statements
        self.stmtBlock = stmtBlock

    def accept(self, visitor: "Block"):
        return visitor.visitBlockStmt(self)


class If(Stmt):
    def __init__(self, condition: Expr, thenBranch: Stmt, elseIfs: None) -> None:
        super().__init__()
        self.condition = condition
        self.thenBranch = thenBranch
        self.elseIfs = elseIfs

    def accept(self, visitor: "If"):
        return visitor.visitIfStmt(self)


class While(Stmt):
    def __init__(self, condition: Expr, body: Stmt) -> None:
        super().__init__()
        self.condition = condition
        self.body = body

    def accept(self, visitor: "While"):
        return visitor.visitWhileStmt(self)


class For(Stmt):
    def __init__(self, initializer: Expression) -> None:
        super().__init__()
        self.initializer = initializer

    def accept(self, visitor: "For"):
        return visitor.visitForStmt(self)


class Foreach(Stmt):
    def __init__(
        self, collections: Array, body: Stmt, variable: Variable | None = None
    ) -> None:
        super().__init__()
        self.collections = collections
        self.body = body
        self.variable = variable

    def accept(self, visitor: "Foreach"):
        return visitor.visitForeachStmt(self)


class Break(Stmt):
    def __init__(
        self,
    ) -> None:
        super().__init__()

    def accept(self, visitor: "Break"):
        return visitor.visitBreakStmt(self)


class Continue(Stmt):
    def __init__(
        self,
    ) -> None:
        super().__init__()

    def accept(self, visitor: "Continue"):
        return visitor.visitContinueStmt(self)


class Print(Stmt):
    def __init__(self, newLine: bool = False) -> None:
        super().__init__()
        self.newLine = newLine

    def accept(self, visitor: "Print"):
        return visitor.visitPrintStmt(self)


class MExpression:
    priority = False
    left: "MExpression"
    right: "MExpression"
    op = "."

    def __init__(self) -> None:
        pass

    def apply(self) -> "MExpression":
        raise NotImplementedError("Apply not implemented for this class.")
    def simplify(self) -> None:
        raise NotImplementedError("Simplify not implemented for this class.")
    def differentiate(self, target: str) -> "MExpression":
        raise NotImplementedError("Differentiate not implemented for this class.")
    def expand(self) -> "MExpression":
        raise NotImplementedError("Expand not implemented for this class.")
    def factor(self) -> "MExpression":
        return self
    def rpn(self) -> list:
        raise NotImplementedError("RPN not implemented for this class.")
    def depthSimplify(self, left: "MExpression", right: "MExpression") -> None:
        pass

    def mul(
        self, other: "MExpression", priority:bool=None,generateFactorVariable:bool=True
    ) -> "MExpression":
        if other == 1:
            return self
        if other == 0:
            return Number(0)
        if self == 1:
            return other
        if self == 0:
            return Number(0)
        if isinstance(other,MFactorVariable) and self._isNumberApplied():
            return MFactorVariable(other.left.mul(self.apply()).apply(),other.right)
        if isinstance(self,MFactorVariable) and other._isNumberApplied():
            return MFactorVariable(self.left.mul(other.apply()).apply(),self.right)
        mult = Multiplication(self, other,generateFactorVariable=generateFactorVariable)
        if other._isFactorVar() and isinstance(self,Exponentiation) and self.right._isNumberApplied() and other.right.__str__() == self.left.__str__():
            other = other._convToFactorVar()
            return other.left.mul(Exponentiation(other.right,self.right.apply().add(Number(1)).apply()),self.priority if priority == None else priority)
        elif self._isFactorVar() and isinstance(other,Exponentiation) and other.right._isNumberApplied() and self.right.__str__() == other.left.__str__():
            self = self._convToFactorVar()
            return self.left.mul(Exponentiation(self.right,other.right.apply().add(Number(1)).apply()),self.priority if priority == None else priority)
        mult.priority = self.priority if priority == None else priority
        return mult

    def rmul(self, other: "MExpression",priority:bool = None) -> "MExpression":
        return self.mul(other,priority)

    def add(self, other: "MExpression",priority:bool = None) -> "MExpression":
        if other == 0:
            return self
        if self == 0:
            return other
        addition = Addition(self, other)
        addition.priority = self.priority if priority == None else priority
        return addition

    def radd(self, other: "MExpression",priority:bool = None) -> "MExpression":
        return self.add(other,priority)

    def sub(self, other: "MExpression",priority:bool = None) -> "MExpression":
        if other == 0:
            return self
        if isinstance(other,MVariable) and isinstance(self,MVariable) and other.name == self.name:
            return Number(0)
        sub = Subtraction(self, other)
        sub.priority = self.priority if priority == None else priority
        return sub

    def rsub(self, other: "MExpression",priority:bool = None) -> "MExpression":
        if self == 0:
            return other
        sub = Subtraction(other, self)
        sub.priority = self.priority if priority == None else priority
        return sub

    def truediv(self, other: "MExpression",priority:bool = None) -> "MExpression":
        if other == 1:
            return self
        div = Division(self, other)
        div.priority = self.priority if priority == None else priority
        return div

    def rtruediv(self, other: "MExpression",priority:bool = None) -> "MExpression":
        if self == 1:
            return other
        div = Division(other, self)
        div.priority = self.priority if priority == None else priority
        return div

    def pow(self, other: "MExpression",priority:bool = None) -> "MExpression":
        if other == 0:
            return Number(1)
        elif other == 1:
            return self
        expo = Exponentiation(self, other)
        expo.priority = self.priority if priority == None else priority
        return expo

    def rpow(self, other: "MExpression",priority:bool = None) -> "MExpression":
        if self == 0:
            return Number(1)
        elif self == 1:
            return other
        expo = Exponentiation(other, self)
        expo.priority = self.priority if priority == None else priority
        return expo

    def neg(self,priority:bool = None):
        if isinstance(self,Negation):
            return self.expr
        neg = Negation(self)
        neg.priority = self.priority if priority == None else priority
        return neg
    def simplify(self) -> "MExpression":
        return rpnToMExpression(self.rpn())
    def _isBothSidesNumbers(self):
        return self.left.isNumber() and self.right.isNumber()
    def _isBothSidesNumbersApplied(self):
        return self.left.apply().isNumber() and self.right.apply().isNumber()
    def _isBinary(self):
        return isinstance(self,BinaryMExpression)
    def _isSum(self):
        return isinstance(self,(Addition,Subtraction))
    def _applyAndUnpackBinary(self):
        return self.left.apply(),self.right.apply()
    def _isFactorVar(self):
        return isinstance(self,MFactorVariable) or (isinstance(self,Multiplication) and ((isinstance(self.left,Number) and isinstance(self.right,MVariable)) or (isinstance(self.left,MVariable) and isinstance(self.right,Number))))
    def _convToFactorVar(self) -> "MFactorVariable":
        if isinstance(self,MFactorVariable): return self
        if isinstance(self,Multiplication):
            if isinstance(self.left,Number) and isinstance(self.right,MVariable):
                return MFactorVariable(self.left,self.right)
            elif isinstance(self.right,Number) and isinstance(self.left,MVariable):
                return MFactorExpr(self.right,self.left)
        return False
    def _applyExpandAndUnpackBinary(self):
        l,r = self._applyAndUnpackBinary()
        return l.expand(),r.expand()
    def _isinstanceAll(self, objects: list["MExpression"], types: list[type]) -> bool:
        return all(any(isinstance(obj, t) for t in types) for obj in objects)
    def isNumber(self):
        return isinstance(self,Number)
    def _isNumberApplied(self):
        return isinstance(self.apply(),Number)
    def __str__(self, priority=None):
        if not self.isNumber():
            if priority == None:
                priority = self.priority
            OP = self.op
            right = self.right
            # if isinstance(self,Addition) and isinstance(right,Negation):
            #     OP = "-"
            #     right = right.expr
            return (
                "({}{}{})".format(self.left," "+OP + " " if not (self.op in "**") else self.op, right)
                if priority
                else "{}{}{}".format(self.left, " "+OP + " " if not (self.op in "**") else self.op, right)
            )
        else:
            return str(self._convToIntIfPossible())
    def __dbgstr__(self):
        if not isinstance(self, (Number, MVariable, Log)):
            return "<{} Left: {} Operator: {} Right: {}>".format(
                self.__class__.__name__,
                self.left.__dbgstr__(),
                self.op,
                self.right.__dbgstr__(),
            )
        else:
            return self.__str__()
class BinaryMExpression(MExpression):
    left: MExpression
    right: MExpression
    def unpack(self):
        return self.left,self.right
    def expand(self,priority:bool = False):
        _class = self.__class__
        left = self.left.apply().expand()
        right = self.right.apply().expand()
        if left._isBinary():
            binaryLeft, binaryRight = left._applyExpandAndUnpackBinary()
            if (not isinstance(left, self.inverseClass)) and self._isinstanceAll([binaryLeft, binaryRight], [Number]):
                return _class(left.__class__(binaryLeft, binaryRight).apply(), right,priority)
            if isinstance(left, _class) and isinstance(left.right.apply(), Number) and right.isNumber():
                right = right.mul(left.right).apply()
            if not isinstance(left, self.inverseClass):
                return left.__class__(_class(binaryLeft, right), _class(binaryRight, right).apply(),priority)
        if right._isBinary():
            binaryRightLeft, binaryRightRight = right._applyExpandAndUnpackBinary()
            if (not isinstance(right, self.inverseClass)) and self._isinstanceAll([binaryRightLeft, binaryRightRight], [Number]):
                return _class(left, right.__class__(binaryRightLeft, binaryRightRight).apply(),priority)
            if isinstance(right, _class) and left.isNumber() and right.left.apply().isNumber():
                left = left.mul(right.left).apply()
            if not isinstance(self.right, self.inverseClass):
                return right.__class__(_class(left, binaryRightLeft).expand(), _class(left, binaryRightRight).expand().apply()),priority
        return _class(left, right,priority)
    def factor(self) -> "MExpression":
        terms = []
        _left = self.left
        while isinstance(_left, (Addition,Subtraction)):
            terms.append(Negation(_left.right) if isinstance(_left,Subtraction) else _left.right)
            _left = _left.left
        terms.append(_left)
        terms = terms[::-1] 
        left = self.left.factor()
        right = self.right.factor()
        left = self.left
        if isinstance(self, Addition) or isinstance(self, Subtraction):
            commonFactors = self._commonFactors(left, right)
            if commonFactors:
                return self._extractCommonFactors(commonFactors, left, right)
        return self.__class__(left, right)
    def rpn(self):
        return self.left.rpn() + self.right.rpn() + [self.op]
    def _commonFactors(self, left: "MExpression", right: "MExpression") -> list:
        leftFactors = self._getFactors(left)
        rightFactors = self._getFactors(right)
        commonFactors = [factor for factor in leftFactors if factor in rightFactors]
        return commonFactors   
    def _getFactors(self, expr: "MExpression") -> list:
        factors = []
        if isinstance(expr, Multiplication):
            factors.extend(self._getFactors(expr.left))
            factors.extend(self._getFactors(expr.right))
        elif isinstance(expr, (Number, MVariable)):
            factors.append(expr)
        return factors
    def _extractCommonFactors(self, commonFactors: list, left: "MExpression", right: "MExpression") -> "MExpression":
        newLeft = left
        newRight = right
        
        for factor in commonFactors:
            newLeft = self._removeFactor(newLeft, factor)
            newRight = self._removeFactor(newRight, factor)

        commonFactorExpr = commonFactors[0]
        for factor in commonFactors[1:]:
            commonFactorExpr = Multiplication(commonFactorExpr, factor, True)

        factoredExpr = Addition(newLeft, newRight, True)
        return Multiplication(commonFactorExpr, factoredExpr)
    
    def _removeFactor(self, expr: "MExpression", factor: "MExpression") -> "MExpression":
        if isinstance(expr, Multiplication):
            if expr.left == factor:
                return expr.right
            elif expr.right == factor:
                return expr.left
            else:
                return Multiplication(self._removeFactor(expr.left, factor), expr.right, True)
        elif expr == factor:
            return Number(1)
        return expr
class Number(MExpression):
    def __init__(self, num: float):
        super().__init__()

        self.num: float = num

    def apply(self) -> MExpression:
        return self._convToIntIfPossible()
    def expand(self,priority:bool = False) -> MExpression:
        return self
    def simplify(self) -> None:
        return self.apply()
    def differentiate(self, target: str) -> "MExpression":
        return Number(0)
    def rpn(self):
        return [str(self._convToIntIfPossible())]
    # def depthSimplify(self, left: "MExpression", right: "MExpression") -> None:
    # pass

    def _convToIntIfPossible(self):
        num = self.num
        if isinstance(num, float) and num == int(num):
            return Number(int(num))
        return Number(num)

    def __eq__(self, other):
        if isinstance(other, Number):
            return self.num == other.num
        if isinstance(other, (int, float)):
            return self.num == other
        return False

    def __str__(self,nullable=False):
        num = self.num
        if isinstance(num, float) and num == int(num):
            return str(int(num))
        return str(num)

    def __dbgstr__(self, indent=0):
        return " " * indent + f"Number({self.num})"


class Addition(BinaryMExpression):
    op: str = "+"
    def __init__(self, left: MExpression, right: MExpression, priority: bool = False):
        if isinstance(right, Negation):
            self.__class__ = Subtraction
            self.__init__(left, right.expr, priority)
        else:
            self.left = left
            self.right = right
            self.priority = priority

    def apply(self) -> MExpression:
        return (
            Number(self.left.apply().num + self.right.apply().num)
            if self._isBothSidesNumbersApplied()
            else self.left.apply().add(self.right.apply(),self.priority)
        )
    def expand(self,priority:bool = False) -> MExpression:
        return Addition(self.left.expand(),self.right.expand(),priority)
    def differentiate(self, target: str) -> "MExpression":
        return self.left.differentiate(target).add(self.right.differentiate(target))

    def rpn(self):
        return self.left.rpn() + self.right.rpn() + ["+"]

    def __dbgstr__(self, indent=0):
        return (
            " " * indent
            + "Addition(\n"
            + self.left.__dbgstr__(indent + 2)
            + ",\n"
            + self.right.__dbgstr__(indent + 2)
            + "\n"
            + " " * indent
            + ")"
        )

    # def depthSimplify(self, left: "MExpression", right: "MExpression") -> None:
    #     pass

class Subtraction(BinaryMExpression):
    op: str = "-"
    def __init__(self, left: MExpression, right: MExpression,priority: bool = False):
        super().__init__()
        self.left: MExpression = left
        self.right: MExpression = right
        self.priority = priority
    def apply(self) -> MExpression:
        return Number(self.left.apply().num - self.right.apply().num) if self._isBothSidesNumbersApplied() else self.left.apply().sub(self.right.apply(),self.priority)
    def expand(self, priority:bool = False) -> MExpression:
        return Subtraction(self.left.expand(),self.right.expand(),priority)

    def differentiate(self, target: str) -> "MExpression":
        return self.left.differentiate(target).sub(self.right.differentiate(target))
    def rpn(self):
        return self.left.rpn() + self.right.rpn() + ["-"]
    def __dbgstr__(self, indent=0):
        return (
            " " * indent
            + "Subtraction(\n"
            + self.left.__dbgstr__(indent + 2)
            + ",\n"
            + self.right.__dbgstr__(indent + 2)
            + "\n"
            + " " * indent
            + ")"
        )

    # def depthSimplify(self, left: "MExpression", right: "MExpression") -> None:
    #     pass

class Multiplication(BinaryMExpression):
    op: str = "*"
    def __init__(self, left: MExpression, right: MExpression,priority: bool = False,generateFactorVariable:bool=True):
        super().__init__()
        if isinstance(left,MVariable) and isinstance(right,MVariable) and left.name == right.name:
            self.__class__ = Exponentiation
            self.__init__(right,Number(2))
            return
        elif generateFactorVariable and isinstance(right,MVariable) and left._isNumberApplied():
            self.__class__ = MFactorVariable
            self.__init__(left.apply(),right)
            return
        elif (
            generateFactorVariable
            and isinstance(left, MVariable)
            and right._isNumberApplied()
        ):
            self.__class__ = MFactorVariable
            self.__init__(right.apply(),left)
            return
        elif isinstance(right,Division) and right.left == 1:
            self.__class__ = Division
            self.__init__(left, right.right, priority)
            return
        elif isinstance(left,Division) and left.left == 1:
            self.__class__ = Division
            self.__init__(right, left.right, priority)
            return
        else:
            self.left: MExpression = left
            self.right: MExpression = right
            self.priority = priority
            self.inverseClass = Division
    def apply(self):
        return Number(self.left.apply().num * self.right.apply().num) if self._isBothSidesNumbersApplied() else self.left.apply().mul(self.right.apply(),self.priority)

    def differentiate(self, target: str) -> "MExpression":
        return (
            self.left.differentiate(target)
            .mul(self.right)
            .add(self.right.differentiate(target).mul(self.left))
        )

    def rpn(self):
        return self.left.rpn() + self.right.rpn() + ["*"]
    def expand(self,priority:bool = False):
        left = self.left.apply().expand()
        right = self.right.apply().expand()
        if left._isSum() and right._isSum():
            lBinaryLeft, lBinaryRight = left._applyExpandAndUnpackBinary()
            rBinaryLeft, rBinaryRight = right._applyExpandAndUnpackBinary()
            return left.__class__(lBinaryLeft.mul(right).expand(True),lBinaryRight.mul(right).expand(True),priority)
        elif right._isSum():
            binaryLeft, binaryRight = right._applyExpandAndUnpackBinary()
            return right.__class__(left.mul(binaryLeft),left.mul(binaryRight),priority)
        elif left._isSum():
            binaryLeft, binaryRight = left._applyExpandAndUnpackBinary()
            return right.__class__(right.mul(binaryLeft),right.mul(binaryRight),priority)
        return self

    def __dbgstr__(self, indent=0):
        return (
            " " * indent
            + "Multiplication(\n"
            + self.left.__dbgstr__(indent + 2)
            + ",\n"
            + self.right.__dbgstr__(indent + 2)
            + "\n"
            + " " * indent
            + ")"
        )

    # def depthSimplify(self, left: "MExpression", right: "MExpression") -> None:
    #     pass


class Division(BinaryMExpression):
    inverseClass = Multiplication
    op: str = "/"
    def __init__(self, left: MExpression, right: MExpression,priority: bool = False):
        super().__init__()
        self.left: MExpression = left
        self.right: MExpression = right
        self.priority = priority
    def apply(self):
        return Number(self.left.apply().num / self.right.apply().num) if self._isBothSidesNumbersApplied() else self.left.apply().truediv(self.right.apply(),self.priority)
    def differentiate(self, target: str) -> "MExpression":
        lDiff = self.left.differentiate(target)
        lDiff.priority = True
        return (
            lDiff.mul(self.right).sub(
                self.right.differentiate(target).mul(self.left, False)
            )
        ).truediv(
            self.right.mul(self.right),False
        )
    def rpn(self):
        return self.left.rpn() + self.right.rpn() + ["/"]
    def __dbgstr__(self, indent=0):
        return (
            " " * indent
            + "Division(\n"
            + self.left.__dbgstr__(indent + 2)
            + ",\n"
            + self.right.__dbgstr__(indent + 2)
            + "\n"
            + " " * indent
            + ")"
        )

    # def depthSimplify(self, left: "MExpression", right: "MExpression") -> None:
    #     pass


class Exponentiation(MExpression):
    op: str = "**"
    def __init__(self, left: MExpression, right: MExpression,priority: bool = False):
        super().__init__()
        self.left: MExpression = left
        if right.isNumber() and right.num%2==0 and isinstance(self.left,Negation):
            self.left = self.left.expr
        self.right: MExpression = right
        self.priority = priority

    def apply(self):
        return Number(self.left.apply().num ** self.right.apply().num) if self._isBothSidesNumbersApplied() else self.left.apply().pow(self.right.apply(),self.priority)
    def multinomialCoeff(self, n, k):
        return factorial(n) // prod(factorial(ki) for ki in k)

    def multinomialExpansion(self, terms, power,priority:bool = False):
        if power == 0:
            return Number(1)
        expanded = Number(0)
        for exponents in combinationsWithReplacement(range(len(terms)), power):
            k = [0] * len(terms)
            for index in exponents:
                k[index] += 1
            coeff = Number(self.multinomialCoeff(power, k))
            term = Number(1)
            negCount = 0
            for termIndex, exponent in zip(range(len(terms)), k):
                _term = terms[termIndex]
                if isinstance(terms[termIndex],Negation) and exponent != 0:
                    _term = terms[termIndex].expr
                    negCount += 1
                term = term.mul(_term.pow(Number(exponent)))
            expanded = expanded.sub(coeff.mul(term),priority) if negCount%2!=0 else expanded.add(coeff.mul(term),priority)
        return expanded
    def expand(self,priority:bool = False):
        if isinstance(self.left, (Addition,Subtraction)):
            terms = []
            left = self.left
            while isinstance(left, (Addition,Subtraction)):
                terms.append(Negation(left.right) if isinstance(left,Subtraction) else left.right)
                left = left.left
            terms.append(left)
            terms = terms[::-1] 
            power = self.right.apply().num if self.right.isNumber() else None
            if power is not None and isinstance(power, int) and power >= 0:
                return self.multinomialExpansion(terms, power,priority)
        return Exponentiation(self.left.expand(), self.right.expand(), priority)


    def differentiate(self, target: str) -> "MExpression":
        u = self.left
        v = self.right
        if v.isNumber():
            constExpo = v.apply()
            constExpo = constExpo.sub(Number(1)).apply()
            return v.mul(u.pow(constExpo)).mul(u.differentiate(target))
        else:
            return self.mul(
                v.differentiate(target)
                .mul(Log(u))
                .add(v.mul(u.differentiate(target).truediv(u)),True)
            )
    def rpn(self):
        return self.left.rpn() + self.right.rpn() + ["**"]
    def __dbgstr__(self, indent=0):
        return (
            " " * indent
            + "Exponentiation(\n"
            + self.left.__dbgstr__(indent + 2)
            + ",\n"
            + self.right.__dbgstr__(indent + 2)
            + "\n"
            + " " * indent
            + ")"
        )

    # def depthSimplify(self, left: "MExpression", right: "MExpression") -> None:
    # pass


class MVariable(MExpression):
    def __init__(self, name: str, op: str = "."):
        super().__init__()

        self.name: str = name
        self.op: str = op

    def apply(self):
        return self
    def expand(self):
        return self
    def simplify(self):
        return self
    def rpn(self):
        return [self.name]
    def differentiate(self, target: str):
        return Number(1) if self.name == target else Number(0)
    def __str__(self, priority=None):
        if priority == None:
            priority = self.priority
        return self.name
    
    def __dbgstr__(self, indent=0):
        return " " * indent + f"MVariable({self.name})"


class MFactorVariable(BinaryMExpression):
    op: str = "*"
    def __init__(self, left: MExpression, right: MExpression,priority: bool = False):
        super().__init__()

        self.left: MExpression = left
        self.right: MExpression = right
        self.priority = priority

    def apply(self) -> MExpression:
        return self.left.apply().mul(self.right.apply(),self.priority,False)
    def expand(self):
        return Multiplication(self.left.expand(),self.right.expand(),self.priority,False)
    def rpn(self):
        return Multiplication(self.left,self.right,self.priority,False).rpn()
    def differentiate(self, target: str) -> "MExpression":
        return Multiplication(self.left,self.right,self.priority,False).differentiate(target)

    # def depthSimplify(self, left: "MExpression", right: "MExpression") -> None:
    # pass


class MFactorExpr(BinaryMExpression):
    op: str = "*"
    def __init__(self, left: MExpression, right: MExpression,priority: bool= False):
        super().__init__()

        self.left: MExpression = left
        self.right: MExpression = right
        self.priority = priority

    def apply(self) -> MExpression:
        return self.left.apply().mul(self.right.apply(),self.priority)
    def expand(self):
        return Multiplication(self.left.expand(),self.right.expand(),self.priority)

    def differentiate(self, target: str) -> "MExpression":
        return Multiplication(self.left,self.right).differentiate(target)
    def rpn(self):
        return Multiplication(self.left,self.right).rpn()
    def __dbgstr__(self, indent=0):
        return (
            " " * indent + "MFactorExpr(\n"
            + self.left.__dbgstr__(indent + 2) + ",\n"
            + self.right.__dbgstr__(indent + 2) + "\n"
            + " " * indent + ")"
        )
    # def depthSimplify(self, left: "MExpression", right: "MExpression") -> None:
    # pass


class Negation(MExpression):
    def __init__(self, expr: MExpression):
        super().__init__()
        if expr.apply() == 0:
            self.__class__ = Number
            self.__init__(0)
            return
        self.isPostive = isinstance(expr,Negation)
        self.expr: MExpression = expr.expr if isinstance(expr,Negation) else expr
    def apply(self) -> MExpression:
        return Number(-self.expr.apply().num) if self.expr.isNumber() else  self.expr.apply() if self.isPostive else Negation(self.expr.apply())
    def expand(self):
        return self.expr.apply() if self.isPostive else Negation(self.expr.apply())
    def differentiate(self, target: str) -> "MExpression":
        return Negation(self.expr.differentiate(target))
    def rpn(self):
        return self.expr() + "-"
    # def depthSimplify(self, left: "MExpression", right: "MExpression") -> None:
    # pass
    def __str__(self, priority: bool | None = None) -> None:
        if priority == None:
            priority = self.priority
        return "-" + "(" +str(self.expr) + ")" if priority else "-" + str(self.expr)
    def __dbgstr__(self, indent=0):
        return (
            " " * indent + "Negation(\n"
            + self.expr.__dbgstr__(indent + 2) + "\n"
            + " " * indent + ")"
        )

class Log(MExpression):
    def __init__(self, expr: MExpression):
        super().__init__()

        self.expr: MExpression = expr

    def apply(self) -> MExpression:
        appliedExpr = self.expr.apply()
        return self if not appliedExpr.isNumber() else Number(log(appliedExpr.num))
    def expand(self):
        return Log(self.expr.expand())

    def differentiate(self, target: str) -> "MExpression":
        return Number(1).truediv(self.expr)
    def rpn(self):
        return self.expr.rpn() + "log"
    def depthSimplify(self, left: "MExpression", right: "MExpression") -> None:
        pass

    def __str__(self, priority: bool | None = None) -> None:
        return "log(" + str(self.expr) + ")"

    def __dbgstr__(self, indent=0):
        return (
            " " * indent
            + "Log(\n"
            + self.expr.__dbgstr__(indent + 2)
            + "\n"
            + " " * indent
            + ")"
        )
from .rpn import *