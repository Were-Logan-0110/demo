from io import BytesIO
import tokenize
import glob
import re
import os
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


def convertFStringToFormat(fString):
    if fString.startswith('f"') or fString.startswith("f'"):
        innerString = fString[2:-1]
        placeholders = re.findall(r"{(.*?)}", innerString)
        newString = re.sub(r"{.*?}", "{}", innerString)
        return f'"{newString}".format({", ".join(placeholders)})'
    return fString
def convertMatchToIfElse(source):
    lines = source.split("\n")
    convertedLines = []
    insideMatch = False
    caseVariables = []

    for line in lines:
        strippedLine = line.strip()
        if strippedLine.startswith("match "):
            insideMatch = True
            matchVar = strippedLine.split(" ")[1][
                :-1
            ]
        elif insideMatch:
            if strippedLine.startswith("case "):
                caseValue = strippedLine.split(" ")[1][:-1]
                if caseValue != "_":
                    condition = f"if {matchVar} == {caseValue}:"
                else:
                    condition = f"else:"
                if caseVariables:
                    condition = condition.replace("if", "elif")
                convertedLines.append(
                    line.replace(strippedLine, condition).replace("    ", "", 1)
                )
                caseVariables.append(caseValue)
            else:
                if strippedLine == "_:":
                    convertedLines.append(line.replace("case _:", "else:"))
                elif not strippedLine.startswith("case "):
                    convertedLines.append(line)
                    if strippedLine == "" or strippedLine.startswith("else:"):
                        insideMatch = False
                        caseVariables = []
        else:
            convertedLines.append(line)
    return "\n".join(convertedLines)


def tokenizeAndReplace(code):
    code = convertMatchToIfElse(code)
    codeBytes = BytesIO(code.encode("utf-8"))
    tokens = tokenize.tokenize(codeBytes.readline)
    modifiedCode = []
    currentPosition = 0
    lastLineNum = 0
    lines = code.splitlines(True)

    for token in tokens:
        if token.type == tokenize.STRING and (
            token.string.startswith("f'") or token.string.startswith('f"')
        ):
            convertedString = convertFStringToFormat(token.string)
            tokenStart = currentPosition + token.start[1]
            tokenEnd = tokenStart + len(token.string)
            modifiedCode.append((tokenStart, tokenEnd, convertedString))
        if token.start[0] > lastLineNum and token.start[0] <= len(lines):
            currentPosition += len(lines[token.start[0] - 1])
            lastLineNum = token.start[0]

    newCode = list(code)
    for start, end, replacement in sorted(
        modifiedCode, key=lambda x: x[0], reverse=True
    ):
        newCode = "".join(newCode)[:start] + replacement + "".join(newCode)[end:]

    return "".join(newCode)


def tokenizeAndReplace(code):
    nCode = code
    code = convertMatchToIfElse(code)
    codeBytes = BytesIO(code.encode("utf-8"))
    tokens = Tokenize(codeBytes)
    for token in tokens:
        if token.type == tokenize.STRING and (
            token.string.startswith("f'") or token.string.startswith('f"')
        ):
            convertedString = convertFStringToFormat(token.string)
            nCode = nCode[: token.start] + convertedString + nCode[token.end :]
            nCode = tokenizeAndReplace(nCode)
            break
    return nCode
def processPythonFilesInDirectory(directory):
    pythonFiles = glob.glob(os.path.join(directory, "**/*.py"), recursive=True)
    for pyFile in pythonFiles:
        print(f"Processing file: {pyFile}")
        with open(pyFile, "r", encoding="utf-8") as f:
            sourceCode = f.read()
        modifiedCode = tokenizeAndReplace(sourceCode)
        with open(pyFile, "w", encoding="utf-8") as f:
            f.write(modifiedCode)
        print(f"File {pyFile} processed successfully.")
if __name__ == "__main__":
    import sys
    if len(sys.argv) != 2:
        print("Usage: python script.py <directory_path>")
        sys.exit(1)
    directoryPath = sys.argv[1]
    if not os.path.isdir(directoryPath):
        print(f"Error: {directoryPath} is not a valid directory.")
        sys.exit(1)
    processPythonFilesInDirectory(directoryPath)
