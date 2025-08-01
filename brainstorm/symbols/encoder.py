from __future__ import annotations

from io import StringIO, TextIOBase

__all__ = ["Encoder"]


class Encoder:
    output: TextIOBase
    level: int

    def __init__(self, output: TextIOBase, level: int = 0):
        self.output = output
        self.level = level

    def write(self, line: str) -> Encoder:
        self.output.write(f"{' ' * 4 * self.level}{line}\n")
        return self

    def __iadd__(self, line: str) -> Encoder:
        self.write(line)
        return self

    def comment(self, message) -> Encoder:
        self.write(f"#{message}")
        return self

    def indent(self) -> Encoder:
        self.level += 1
        return self

    def outdent(self) -> Encoder:
        self.level -= 1
        if self.level < 0:
            self.level = 0
        return self

    def write_lines(self, body: str) -> Encoder:
        for line in body.split("\n"):
            self.write(line)
        return self

    # def add_statement(self, statement: Statement) -> Encoder:
    #    return self.indent().comment(repr(statement)).write_lines(body=statement.body).outdent()

    def cr(self) -> Encoder:
        self.output.write("\n")
        return self

    @classmethod
    def encoder(cls) -> Encoder:
        return Encoder(output=StringIO())

    def getvalue(self) -> str:
        return self.output.getvalue() if isinstance(self.output, StringIO) else ""
