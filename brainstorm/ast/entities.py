from dataclasses import dataclass


@dataclass
class FunctionInfo:
    name: str
    args: list[str]
    returns: str
    doc: str

@dataclass
class ClassInfo:
    name: str
    bases: list[str]
    methods: list[FunctionInfo]
    doc: str

@dataclass
class ModuleInfo:
    name: str
    classes: list[ClassInfo]
    functions: list[FunctionInfo]
    imports: list[str]
