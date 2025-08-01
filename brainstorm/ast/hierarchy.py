
from .entities import ModuleInfo


def build_hierarchy(modules: list[ModuleInfo]) -> dict:
    return {
        module.name: {
            "classes": [cls.name for cls in module.classes],
            "functions": [fn.name for fn in module.functions],
            "imports": module.imports
        } for module in modules
    }