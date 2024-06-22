from sympy import simplify,diff,parse_expr,Symbol
from interpreter import *
from helpers import *
from scanner import *
from debug import *
from ast_ import *

def parseAST(source:str,debug=False):
    tokens = Scanner(source).scan()
    parsed = LLParser(tokens).parse()
    if debug:
        print(generate_tree(parsed))
        tree_visualizer = TreeDialog(parsed)
        tree_visualizer.exec_()
    return parsed
def _diff(source:str,debug=False):
    return MAST().evaluate(parseAST(source,debug)).differentiate("x")
def _simplify(source:str,debug=False):
    return ASTSimplifier().evaluate(parseAST(source, debug)).simplify()
equations = [
    # "x**2 + 2*x + 1",  # Simple quadratic expression
    "3*x**2 + 5*x - 2*x**2 + x - 1",  # Expression with like terms to combine
    # "(x + 1)**2",  # Binomial expansion
    # "2*(x + 3)",  # Distributive property
    # "(x**2 + 2*x + 1) / (x + 1)",  # Rational expression to simplify
    # "2*(x + 3) - (x + 1)",  # Combination of terms
    # "x**2 - 4",  # Difference of squares
    # "(x - 2)*(x + 2)",  # Product of binomials
    # "2*x*(x + 3) - x**2",  # Polynomial expansion and combination
    # "(3*x + 4)*(2*x - 5)",  # Product of binomials to expand
    # "(x**2 + 2*x + 1) - (x + 1)**2",  # Expression resulting in zero
    # "x**(2 + 3)",  # Exponential simplification
    # "(x**2)**3",  # Power of a power
    # "2*x - 3 + 4*x - x + 2",  # Combination of like terms
    # "(x - 1)**2 + 2*(x - 1)",  # Common factor extraction
    # "4*x*(2*x - 1)",  # Polynomial multiplication
    # "x/2 + 3/2*x",  # Simplification with fractions
    # "3*(x + 1)/2 + 1/2*(x - 1)",  # Combining fractions
    # "(x + y)**2 - (x**2 + 2*x*y + y**2)",  # Polynomial identity resulting in zero
]
for eq in equations:
    print(f"Self Simplified: {_simplify(eq)}")
    print(f"Sympy Simp: {simplify(parse_expr(eq))}")
    print("-"*30)
# testExprs = [
#     "4*x**3 - 3*x**2 + 2*x - 1",
#     "x**4 - x**3 + x**2 - x + 1",
#     "2*x**3 + 3*x**2 - x + 8",
# ]
# symbols = {"x": Symbol("x", real=True), "y": Symbol("y", real=True)}
# for expr in testExprs:
#     print(f"Expression: {expr}")
#     result = _diff(expr)
#     simplifiedResult = simplify(result.__str__())
#     selfSimplified = _simplify(result.__str__())
#     print(f"UnSimplified Expr: {result}")
#     print(f"Sympy Simplified Result: {simplifiedResult}")
#     print(f"Implemented Simplified Result: {selfSimplified}")
#     print(f"Expected Result: {diff(parse_expr(expr,symbols),symbols['x'])}")
#     print("-" * 30)
