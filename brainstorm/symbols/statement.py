from typing import Literal

from ..registry import Dictionary
from .encoder import Encoder
from .symbol import Symbol

__all__ = [
    "Statement",
    "Statements",
    "StatementType",
]

type StatementType = Literal["parameter", "variable", "function", "class"]


class Statement(Symbol):
    body: str = ""
    type: StatementType | None = None
    # _module: Module | None = None # guard to add this statement instance in single module only

    def encode(self, output: Encoder):
        output.comment(f"name: {self.name}").comment(f"kind: {self.type}").write_lines(self.body).cr().cr()

    # def register(self, module: Module) -> Module:
    #     """Register this statement."""
    #     #if self._module:
    #     #    raise RuntimeError(
    #     #        f"Statement {self.name} should not be registered in two module {self._module.name} and {module.name}"
    #     #    )
    #     #self._module = module
    #     if not module.statements.exists(name=self.name):
    #         module.statements.add(item=self)
    #     return module


class Statements(Dictionary[Statement]):
    def encode(self, output: Encoder):
        for statement in self.all():
            statement.encode(output=output)
