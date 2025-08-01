import ast

from .entities import ClassInfo, FunctionInfo, ModuleInfo


class CodeVisitor(ast.NodeVisitor):
    def __init__(self):
        self.functions = []
        self.classes = []

    def visit_FunctionDef(self, node):
        args = [arg.arg for arg in node.args.args]
        doc = ast.get_docstring(node)
        self.functions.append(FunctionInfo(
            name=node.name, args=args, returns=None, doc=doc or ""
        ))

    def visit_ClassDef(self, node):
        doc = ast.get_docstring(node)
        methods = []
        for item in node.body:
            if isinstance(item, ast.FunctionDef):
                args = [arg.arg for arg in item.args.args]
                methods.append(FunctionInfo(name=item.name, args=args, returns=None, doc=ast.get_docstring(item) or ""))
        self.classes.append(ClassInfo(name=node.name, bases=[b.id for b in node.bases if isinstance(b, ast.Name)], methods=methods, doc=doc or ""))

def parse_module(source: str, name: str = "unknown") -> ModuleInfo:
    tree = ast.parse(source)
    visitor = CodeVisitor()
    visitor.visit(tree)
    imports = [n.names[0].name for n in tree.body if isinstance(n, ast.Import)]
    return ModuleInfo(name=name, classes=visitor.classes, functions=visitor.functions, imports=imports)



