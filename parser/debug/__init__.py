from PyQt5.QtWidgets import (
    QApplication,
    QGraphicsView,
    QGraphicsScene,
    QGraphicsTextItem,
    QGraphicsLineItem,
    QVBoxLayout,
    QDialog,
)
from PyQt5.QtGui import QFont
from interpreter import *
from ast_ import *
import sys
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
        self.setMinimumSize(1000, 1000)
        layout.addWidget(self.view)
        self.setLayout(layout)
        self.setWindowTitle("Tree Visualizer")
        self.setGeometry(100, 100, 800, 600)
        self.generate_tree()

    def generate_tree(self):
        self.draw_node(self.root, 400, 50, 200, 50)

    def draw_node(self, node, x, y, width, height):
        if isinstance(node, Literal):
            self.draw_text(f"Literal({node.value})", x, y, width, height)
        elif isinstance(node, Variable):
            self.draw_text(f"Variable({node.name.lexeme})", x, y, width, height)
        elif isinstance(node, Binary):
            self.draw_text(f"Binary({node.operator.lexeme})", x, y, width, height)
            if node.left:
                left_x = x - width // 2
                left_y = y + height + 50
                self.draw_node(node.left, left_x, left_y, width, height)
                self.scene.addLine(
                    x + 10, y + height + 10, left_x + width // 2 + 10, left_y
                )
            if node.right:
                right_x = x + width // 2
                right_y = y + height + 50
                self.draw_node(node.right, right_x, right_y, width, height)
                self.scene.addLine(
                    x + 10, y + height + 10, right_x + width // 2 + 10, right_y
                )
        elif isinstance(node, facVariable):
            self.draw_text(
                f"Factor Variable({node.factor.value} | {node.variable.name})",
                x,
                y,
                width,
                height,
            )

    def draw_text(self, text, x, y, width, height):
        text_item = QGraphicsTextItem(text)
        text_item.setFont(QFont("Arial", 10))
        text_item.setPos(x, y)
        self.scene.addItem(text_item)


def generate_tree(node: Literal|Variable|Binary, indent: int = 0):
    if isinstance(node, Literal):
        print(" " * indent + f"Literal(value={node.value})")
    elif isinstance(node, Variable):
        print(" " * indent + f"Variable(name={node.name})")
    elif isinstance(node, Binary):
        print(" " * indent + f"Bin:")
        print(" " * (indent + 4) + f"op: {node.operator}")
        print(" " * (indent + 4) + f"left:")
        generate_tree(node.left, indent + 8)
        print(" " * (indent + 4) + f"right:")
        generate_tree(node.right, indent + 8)
