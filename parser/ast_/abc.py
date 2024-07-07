from math import factorial
def generateCombinationsRecursive(n, m, currentCombination=None, current_sum=0):
    if currentCombination is None:
        currentCombination = []
    if len(currentCombination) == m:
        if current_sum == n:
            yield currentCombination
        return
    for i in range(n - current_sum + 1):
        yield from generateCombinationsRecursive(n, m, currentCombination + [i], current_sum + i)
def generateCombinations(n, m):
    _ = list(generateCombinationsRecursive(n, m))
    _.reverse()
    return _

def combinationsWithReplacement(elements, length):
    def generateCombinations(prefix, start, length):
        if length == 0:
            result.append(prefix)
            return
        for i in range(start, len(elements)):
            generateCombinations(prefix + [elements[i]], i, length - 1)
    result = []
    generateCombinations([], 0, length)
    return result

def binomialCoefficient(n, k):
    return factorial(n) // (factorial(k) * factorial(n - k))
def multinomialCoefficient(*args):
    coeff = factorial(sum(args))
    for k in args:
        coeff //= factorial(k)
    return coeff
def multinomialExpansion(variables,n):
    numberOfSets = len(variables)
    expansion = []
    for set in generateCombinations(n,numberOfSets):
        coef = multinomialCoefficient(*set)
        term = f"{coef}*" if coef != 1 else ""
        for var,exp in zip(variables,set):
            if exp > 0:
                term += f"{var}**{exp}" if exp != 1 else f"{var}"
        expansion.append(term)
    return " + ".join(expansion)
