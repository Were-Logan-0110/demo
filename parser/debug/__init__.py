from PyQt5.QtWidgets import (
    QApplication,
    QGraphicsView,
    QGraphicsScene,
    QGraphicsTextItem,
    QGraphicsLineItem,
    QVBoxLayout,
    QGraphicsRectItem,
    QDialog,
)
from PyQt5.QtWidgets import QDialog, QGraphicsScene, QGraphicsView, QVBoxLayout, QGraphicsTextItem, QGraphicsRectItem
from PyQt5.QtGui import QFont, QColor, QPen, QBrush
from PyQt5.QtCore import Qt
from interpreter import *
from ast_ import *
import sys
import re
import pandas as pd
from sympy import sympify
from types import ModuleType, FunctionType
from gc import get_referents

# Custom objects know their class.
# Function objects seem to know way too much, including modules.
# Exclude modules as well.
BLACKLIST = type, ModuleType, FunctionType


def getsize(obj):
    """sum size of object & members."""
    if isinstance(obj, BLACKLIST):
        raise TypeError("getsize() does not take argument of type: " + str(type(obj)))
    seen_ids = set()
    size = 0
    objects = [obj]
    while objects:
        need_referents = []
        for obj in objects:
            if not isinstance(obj, BLACKLIST) and id(obj) not in seen_ids:
                seen_ids.add(id(obj))
                size += sys.getsizeof(obj)
                need_referents.append(obj)
        objects = get_referents(*need_referents)
    return size


# Dialog class to visualize the tree structure


class TreeDialog(QDialog):
    def __init__(self, root):
        super().__init__()
        self.root = root
        self.scene = QGraphicsScene()
        self.view = QGraphicsView(self.scene)
        layout = QVBoxLayout()
        layout.addWidget(self.view)
        self.setLayout(layout)
        self.setWindowTitle("Tree Visualizer")
        self.setGeometry(100, 100, 1200, 800)
        self.view.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOn)
        self.view.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOn)
        self.view.setStyleSheet("background-color: #2b2b2b;")
        self.generate_tree()

    def generate_tree(self):
        generate_tree(self.root)
        self.draw_node(self.root, 600, 50, 200, 50)

    def draw_node(self, node, x, y, width, height):
        if isinstance(node, Literal):
            self.draw_text(f"Literal({node.value})", x, y, width, height)
        elif isinstance(node, Variable):
            self.draw_text(f"Variable({node.name.lexeme})", x, y, width, height)
        elif isinstance(node, Grouping):
            self.draw_node(node.expression, x, y, width, height)
        elif isinstance(node, Negative):
            self.draw_text(f"Negative(-)", x, y, width, height)
            if node.expression:
                expr_x = x
                expr_y = y + height + 100
                self.draw_node(node.expression, expr_x, expr_y, width, height)
                self.draw_line(x + width // 2, y + height, expr_x + width // 2, expr_y)
        elif isinstance(node, Unary):
            self.draw_text(f"Unary({node.operator.lexeme})", x, y, width, height)
            if node.right:
                right_x = x
                right_y = y + height + 100
                self.draw_node(node.right, right_x, right_y, width, height)
                self.draw_line(
                    x + width // 2, y + height, right_x + width // 2, right_y
                )
        elif isinstance(node, Binary):
            self.draw_text(f"Binary({node.operator.lexeme})", x, y, width, height)
            if node.left:
                left_x = x - width // 2
                left_y = y + height + 100
                self.draw_node(node.left, left_x, left_y, width, height)
                self.draw_line(x, y + height, left_x + width // 2, left_y)
            if node.right:
                right_x = x + width // 2
                right_y = y + height + 100
                self.draw_node(node.right, right_x, right_y, width, height)
                self.draw_line(x, y + height, right_x + width // 2, right_y)
        elif isinstance(node, FacVariable):
            self.draw_text(
                f"Factor Variable({node.factor.value} | {node.variable.name})",
                x,
                y,
                width,
                height,
            )

    def draw_text(self, text, x, y, width, height):
        rect_item = QGraphicsRectItem(x, y, width, height)
        rect_item.setPen(QPen(QColor(255, 255, 255)))  # White border
        rect_item.setBrush(QBrush(QColor(43, 43, 43)))  # Dark background
        self.scene.addItem(rect_item)

        text_item = QGraphicsTextItem(text)
        text_item.setFont(QFont("Arial", 12))
        text_item.setDefaultTextColor(QColor(255, 255, 255))  # White text
        text_item.setPos(x + 10, y + 10)
        self.scene.addItem(text_item)

    def draw_line(self, x1, y1, x2, y2):
        line = self.scene.addLine(x1, y1, x2, y2, QPen(QColor(255, 255, 255), 2))
        line.setZValue(-1)  # Ensure lines are behind the nodes


def generate_tree(node, indent=0):
    if isinstance(node, Literal):
        print(" " * indent + f"Literal(value={node.value})")
    elif isinstance(node, Variable):
        print(" " * indent + f"Variable(name={node.name.lexeme})")
    elif isinstance(node, Binary):
        print(" " * indent + f"Binary:")
        print(" " * (indent + 1) + f"op: {node.operator}")
        print(" " * (indent + 1) + f"left:")
        generate_tree(node.left, indent + 3)
        print(" " * (indent + 1) + f"right:")
        generate_tree(node.right, indent + 3)
    elif isinstance(node, Unary):
        print(" " * indent + f"Unary:")
        print(" " * (indent + 1) + f"op: {node.operator}")
        print(" " * (indent + 1) + f"operand:")
        generate_tree(node.right, indent + 3)
    elif isinstance(node,Grouping):
        print(" " * indent + f"Grouping:")
        print(" " * (indent + 1) + f"Expr:")
        generate_tree(node.expression, indent + 3)
    elif isinstance(node,Negative):
        print(" " * indent + f"Negative:")
        print(" " * (indent + 1) + f"Expr:")
        generate_tree(node.expression, indent + 3)
    else:
        print(" " * indent + f"Unknown node type: {type(node).__name__}")


def visualize(nodes):
    app = QApplication([])
    a = TreeDialog(nodes)
    a.exec_()
    app.exec_()


def generateFormattedTable(expression, start, end):
    # Initialize an empty list to store data rows for the DataFrame
    rows = []

    # Iterate over the range from start to end (inclusive)
    for current_value in range(start, end + 1):
        varMap = {}

        # Function to substitute each alphabetical letter with the current value
        def substitute(match):
            var = match.group(0)
            if var not in varMap:
                varMap[var] = current_value
            return str(varMap[var])

        # Substitute the current values in the expression
        subExpr = re.sub(r"\b[a-zA-Z]\b", substitute, expression)
        try:
            result = eval(subExpr)

            # Convert result to string for proper formatting
            result_str = result

            # Append the current row to the rows list
            rows.append(
                {"expression": expression, "value": current_value, "result": result_str}
            )

        except Exception as e:
            print(f"Error evaluating expression: {e}")
            continue

    # Create a DataFrame from the rows list
    df = pd.DataFrame(rows)

    # Print the formatted table
    print("-" * 39)
    print(f"{'expression':<15} | {'value':<15} | {'result':<15}")
    print("-" * 39)
    for index, row in df.iterrows():
        print(f"{row['expression']:<15} | {row['value']:<15} | {row['result']:<15}")
    print("-" * 39)
