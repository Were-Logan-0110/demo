from io import TextIOWrapper
from pathlib import Path
import yaml
import argparse
def importSetup(file: TextIOWrapper, useDataclasses:bool):
    file.write(
        f"""{'from dataclasses import dataclass,field' if useDataclasses else ''}
from interpreter import Token,error
"""
    )
def abstractClassSetup(file: TextIOWrapper,abstractClassName:str = "Expr"):
    file.write(
        f"""\nclass """+abstractClassName+""":
    def init(self):
        pass
    def accept(self,visitor):
            error(-1,"No Accept Method Found For Object: <"+ self.__class__ + ">")
            exit(1)
"""
    )
def createFunc(file: TextIOWrapper,name,args:list,returns="None"):
    argsString = ", ".join(args)
    file.write(
f"""
    def {name}({argsString}) -> {returns}:
        pass
""")
def createChildClass(file: TextIOWrapper,name:str,parentName:str):
    file.write(
f"""\nclass {name}({parentName}):
"""
        )
def createClass(file: TextIOWrapper,name, data):
    funcs: dict = data.get("funcs")
    file.write(
f"""class {name}:
""")
    for funcName in funcs.keys():
        createFunc(
            file,
            funcName.replace("__", "") if funcName != "__init__" else funcName,
            ["self", *funcs[funcName].get("args")],
            funcs[funcName].get("returns", "None"),
        )
    childrenClasses = data.get("childrenClasses",{})
    for childClass in childrenClasses:
        # childClassFuncs = childrenClasses[childClass].get("funcs")
        createChildClass(file,childClass,name)
        # for funcName in [*childClassFuncs.keys()]:
        # createFunc(file,funcName,childClassFuncs[funcName].get("args"),childClassFuncs[funcName].get("returns","None"))
        # createFunc(file,"__init__",childrenClasses[childClass],"None")
        if childrenClasses[childClass]:
            file.write(f"    def __init__(self, {', '.join(childrenClasses[childClass])}):\n")
            file.write("        super().__init__()\n\n")
            for arg in childrenClasses[childClass]:
                file.write(f"        self.{arg.split('=')[0]} = {arg.split(':')[0]}\n")
        else:
            file.write("        pass")
        file.write("")
        for funcName in funcs.keys():
            if not funcName.startswith("__"):
                createFunc(file,funcName,["self",*funcs[funcName].get("args")],funcs[funcName].get("returns","None"))
        createFunc(file,"__str__",["self","priority: bool|None = None"],funcs[funcName].get("returns","None"))

def generateExpr(file: TextIOWrapper, name: str, parent: str, args: list[tuple], useDataclasses=True):
    argList = [f"{'    ' if useDataclasses else ''}{arg[0]}: {arg[1]}" for arg in args]
    if useDataclasses:
        argStr = '\n'.join(argList) if argList else ''
        file.write(
            f"""
@dataclass
class {name}({parent}):
{argStr}
    def accept(self, visitor: "{name}"):
        return visitor.visit{name}{parent}(self)
""")
    else:
        argStr = ', '.join([f"{arg[0]}: {arg[1]}" for arg in args])
        argsInit = "\n    ".join([f"self.{arg[0]} = {arg[0]}" for arg in args])
        file.write(
            f"""
class {name}({parent}):
    def __init__(self, {argStr}) -> None:
        super().__init__()
        {argsInit}
    def accept(self, visitor: "{name}"):
        return visitor.visit{name}{parent}(self)
""")
def buildExpressions(outputPath:str,useDataclasses:bool=True,yamlExprPath:str="./exprs.yaml",yamlMExprPath:str="./mExpr.yaml"):
    outputPath = Path(outputPath).absolute().resolve()
    yamlExprPath = Path(yamlExprPath).absolute().resolve()
    yamlMExprPath = Path(yamlMExprPath).absolute().resolve()
    file = open(outputPath,"w+",encoding="utf-8",errors="ignore")
    classesDeclartion:dict = yaml.safe_load(open(yamlExprPath,"r"))
    mExprDeclartion:dict = yaml.safe_load(open(yamlMExprPath,"r"))
    importSetup(file,useDataclasses)
    for classType in classesDeclartion.keys():
        abstractClassSetup(file, classType)
        for childClass in classesDeclartion.get(classType).keys():
            classArgs = classesDeclartion.get(classType).get(childClass)
            if classArgs:
                classArgs = list(classArgs.items())
            else:
                classArgs = []
            # print(childClass, classArgs)
            generateExpr(file, childClass,classType,classArgs,useDataclasses)
    for className, classData in mExprDeclartion.items():
        createClass(file,className, classData)
if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        usage="python genExpr.py ../ast_/_expression.py --dataclasses",
        description="Expression Generator",
    )
    parser.add_argument("outputPath", help="File Output Path")
    parser.add_argument(
        "--dataclasses",
        default=False,
        type=bool,
        help="Use Dataclasses To Generate The Expressions (default: True)",
    )
    parser.add_argument(
        "--yamlExprPath",
        default="./exprs.yaml",
        type=str,
        help="Class Generator In Yaml Format (default: ./exprs.yaml)",
    )
    parser.add_argument(
        "--yamlMExprPath",
        default="./mExpr.yaml",
        type=str,
        help="Class Generator In Yaml Format For Maths Expressions (default: ../mExpr.yaml)",
    )
    args = parser.parse_args()
    buildExpressions(args.outputPath, args.dataclasses,args.yamlExprPath,args.yamlMExprPath)
