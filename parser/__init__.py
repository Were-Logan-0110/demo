from sympy import simplify,diff,parse_expr,Symbol,expand
from interpreter import *
from helpers import *
from scanner import *
from debug import *
from ast_ import *
import time
import sys
sys.stdout.reconfigure(encoding="utf-8")
def parseAST(source:str,groupNonCommutative:bool=False,debug=False):
    tokens = Scanner(source).scan()
    parsed = LLParser(tokens).parse()
    if debug:
        print(generate_tree(parsed))
        tree_visualizer = TreeDialog(parsed)
        tree_visualizer.exec_()
    return parsed
def evaluate(source:str):
    return MAST().evaluate(
            parseAST(
                source
            )
        )
def _diff(source:str,groupNonCommutative:bool=False,debug=False):
    return (
        MAST()
        .evaluate(
            parseAST(
                source
                ,debug
            )
        )
        .differentiate("x")
    )


def _simplify(source: str, groupNonCommutative:bool=False,debug=False):
    return MAST().evaluate(parseAST(source, debug)).simplify()

symbols = {
    "a": Symbol("a", real=True),
    "b": Symbol("b", real=True),
    "c": Symbol("c", real=True),
    "d": Symbol("d", real=True),
    "e": Symbol("e", real=True),
    "f": Symbol("f", real=True),
    "x": Symbol("x", real=True),
    "y": Symbol("y", real=True),
}

equations = [
    "x**2 + 2*x + 1",  # Simple quadratic expression
    "3*x**2 + 5*x - 2*x**2 + x - 1",  # Expression with like terms to combine
    "(x + 1)**2",  # Binomial expansion
    "2*(x + 3)",  # Distributive property
    "(x**2 + 2*x + 1) / (x + 1)",  # Rational expression to simplify
    "2*(x + 3) - (x + 1)",  # Combination of termsw
    "x**2 - 4",  # Difference of squares
    "(x - 2)*(x + 2)",  # Product of binomials
    "2*x*(x + 3) - x**2",  # Polynomial expansion and combination
    "(3*x + 4)*(2*x - 5)",  # Product of binomials to expand
    "(x**2 + 2*x + 1) - (x + 1)**2",  # Expression resulting in zero
    "x**(2 + 3)",  # Exponential simplification
    "(x**2)**3",  # Power of a power
    "2*x - 3 + 4*x - x + 2",  # Combination of like terms
    "(x - 1)**2 + 2*(x - 1)",  # Common factor extraction
    "4*x*(2*x - 1)",  # Polynomial multiplication
    "x/2 + 3/2*x",  # Simplification with fractions
    "3*(x + 1)/2 + 1/2*(x - 1)",  # Combining fractions
    "(x + y)**2 - (x**2 + 2*x*y + y**2)",  # Polynomial identity resulting in zero
]

# expr = Subtraction(
#     Multiplication(Number(2), MVariable("x")), Multiplication(Number(2), MVariable("y"))
# )
# factoredExpr = expr.factor()
# print(expr)
# print(factoredExpr)
# eq = "2x - 2x"
# evaled = evaluate(eq).expand().apply()
# print(f"EQ: {evaled}\n\n ---- RPN:{(evaled.rpn())}\n\n")
# print(f"EQ Simplified: {evaled.simplify()}")
# evaled = evaled.simplify()
# print(evaled._collectSums())
# print(f"OG-Expr: {evaled.collectAdditionsSubtractions()[0]}")
# [print(f"Add: {i}") for i in evaled.collectAdditionsSubtractions()[1]]
# [print(f"Sub: {i}") for i in evaled.collectAdditionsSubtractions()[2]]
# [print(i) for i in evaled.collectAdditionsSubtractions()[1]]
# generateFormattedTable(evaluate(eq).expand().apply().__str__(), 1, 3)
# generateFormattedTable(expand(parse_expr(eq,symbols)).__str__(), 1, 3)
for c,eq in enumerate(equations):
    print(f"Equation: {eq} Count: {c}")
    print(
        f"Self Diff: {evaluate(eq).differentiate('x').expand().apply()._collectSums().__str__()}"
    )
    print(f"Self Simp: {simplify(evaluate(eq).differentiate('x').apply()._collectSums().__str__())}")
    print(f"Sympy Diff: {diff(parse_expr(eq,symbols))}")
    print(f"Sympy Simp: {simplify(diff(parse_expr(eq,symbols)))}")
    print("-"*30)

# testExprs = [
#     "4*x**3 - 3*x**2 + 2*x - 1",
#     "x**4 - x**3 + x**2 - x + 1",
#     "2*x**3 + 3*x**2 - x + 8",
#     "1/2*x"
# ]
# symbols = {"x": Symbol("x", real=True), "y": Symbol("y", real=True)}
# # app = QApplication([])
# # print(parseAST(testExprs[-1], True))
# # TreeDialog(parseAST(testExprs[-1], True)).exec_()
# # print(MAST().evaluate(parseAST(testExprs[-1],True)).differentiate("x").simplify())
# # app.exec_()
# for expr in testExprs:
#     print(f"Expression: {expr}")
#     result = _diff(expr)
#     print(f"UnSimplified Expr: {result}")
#     simplifiedResult = simplify(result.__str__())
#     selfSimplified = _simplify(result.__str__())
#     print(f"Sympy Simplified Result: {simplifiedResult}")
#     print(f"Implemented Simplified Result: {selfSimplified}")
#     print(f"Expected Result: {diff(parse_expr(expr,symbols),symbols['x'])}")
#     print("-" * 30)
