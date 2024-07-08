from ast_._expression import *


def getPriority(token):
    if token in ("**"):
        return 4
    elif token in ("*", "/"):
        return 3
    elif token in ("-"):
        return 2
    elif token in ("+"):
        return 1
    else:
        return 0

def rpnToMExpression(rpnList: list[str]):
    stack = []
    for i, token in enumerate(rpnList):
        if token.isdigit() or (token[1:].isdigit() and token[0] == "-"):
            stack.append(Number(int(token)))
        elif token.isalpha():
            stack.append(MVariable(token))
        else:
            if len(stack) < 2:
                raise ValueError(
                    f"Insufficient operands for operator '{token}' in the expression."
                )
            b = stack.pop()
            a = stack.pop()
            nextToken = rpnList[i + 1] if i + 1 < len(rpnList) else None
            currentPriority = getPriority(token)
            nextPriority = getPriority(nextToken) if nextToken else 0
            priority = nextPriority > currentPriority
            if token == "+":
                stack.append(Addition(a, b, priority))
            elif token == "-":
                stack.append(Subtraction(a, b, priority))
            elif token == "*":
                stack.append(Multiplication(a, b, priority))
            elif token == "/":
                stack.append(Division(a, b, priority))
            elif token == "**":
                stack.append(Exponentiation(a, b, priority))
            else:
                raise ValueError(f"Unknown operator: {token}")
    if len(stack) != 1:
        raise ValueError("The RPN expression is not well-formed.")
    return stack.pop()
def rpn(expression: "MExpression"):
    return expression.rpn()


def rpnSimplifier(rpn_expression):
    def process_stack(stack):
        coefficients = {}
        while stack:
            token = stack.pop(0)
            if isinstance(token, dict):
                for key, value in token.items():
                    if key in coefficients:
                        coefficients[key] += value
                    else:
                        coefficients[key] = value
            elif isinstance(token, str) and token.isdigit():
                num = int(token)
                if "" in coefficients:
                    coefficients[""] += num
                else:
                    coefficients[""] = num
            else:
                raise ValueError("Unexpected token in stack.")
        return coefficients

    stack = []
    for token in rpn_expression:
        if token.isdigit() or token.isalpha():
            stack.append({token: 1})
        elif token in ("+", "-"):
            right = stack.pop()
            left = stack.pop()

            # Convert single variables to dictionaries
            if isinstance(left, dict):
                left_dict = left
            elif isinstance(left, str):
                left_dict = {left: 1}
            else:
                raise ValueError("Unexpected token type in left operand.")

            if isinstance(right, dict):
                right_dict = right
            elif isinstance(right, str):
                right_dict = {right: 1}
            else:
                raise ValueError("Unexpected token type in right operand.")

            result = {}
            for key in set(left_dict) | set(right_dict):
                result[key] = (
                    left_dict.get(key, 0) + right_dict.get(key, 0)
                    if token == "+"
                    else left_dict.get(key, 0) - right_dict.get(key, 0)
                )

            # Simplify result to remove zero coefficients
            result = {k: v for k, v in result.items() if v != 0}

            stack.append(result)
        else:
            stack.append(token)

    if len(stack) == 1 and isinstance(stack[0], dict):
        result = []
        for key, value in stack[0].items():
            if value == 1:
                result.append(key)
            elif value == -1:
                result.append("-" + key)
            else:
                result.extend([str(value), key, "*"])
        return result
    else:
        nStack = []
        for token in stack:
            print(token)
            __ = list(token.values())[0]
            print(__)
            for _ in range(__):
                for k in token.keys():
                    print(k)
                    if abs(__) > 1:
                        nStack.append("*")

        return nStack
# print(rpnSimplifier(["x", "2", "**", "x", "+", "x", "1", "+", "-"]))
# print(rpnToMExpression(["x", "2", "**", "x", "+", "x", "1", "+", "-"]))
