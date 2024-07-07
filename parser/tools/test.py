import tokenize
from io import BytesIO
from backwardComp import *


def Tokenize(infile: BytesIO):
    offsets = [0]

    def wrappedRLine():
        offsets.append(infile.tell())
        return infile.readline()

    for t in tokenize.tokenize(wrappedRLine):
        startline, startcol = t.start
        endline, endcol = t.end
        yield tokenize.TokenInfo(
            t.exact_type,
            t.string,
            offsets[startline] + startcol,
            offsets[endline] + endcol,
            t.line,
        )


def tokenize_and_return_positions(code):
    codeBytes = BytesIO(code.encode("utf-8"))
    positions = Tokenize(codeBytes)
    return positions


# Example usage:
source_code = """a = 1"""

positions = tokenize_and_return_positions(source_code)
print(list(positions))
