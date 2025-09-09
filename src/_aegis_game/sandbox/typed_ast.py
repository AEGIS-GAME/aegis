# pyright: reportMissingTypeStubs = false
# pyright: reportUnknownMemberType = false
from ast import (
    AST,
    AnnAssign,
    ClassDef,
    Constant,
    Expr,
    Name,
    ParamSpec,
    TypeAlias,
    TypeVar,
    TypeVarTuple,
    stmt,
)
from typing import override

from RestrictedPython import RestrictingNodeTransformer


class NodeTransformer(RestrictingNodeTransformer):
    """Allow type annoation in RestrictedPython."""

    def doc_str(self, node: stmt) -> str | None:
        if (
            isinstance(node, Expr)
            and isinstance(node.value, Constant)
            and isinstance(node.value.value, str)
        ):
            return node.value.value
        return None

    def get_descriptions(self, body: list[stmt]) -> dict[str, str | None]:
        doc_strings: dict[str, str | None] = {}
        current_name = None
        for node in body:
            if isinstance(node, AnnAssign) and isinstance(node.target, Name):
                current_name = node.target.id
                continue
            if current_name and self.doc_str(node):
                doc_strings[current_name] = self.doc_str(node)
            current_name = None
        return doc_strings

    @override
    def visit_AnnAssign(self, node: AnnAssign) -> AST:
        return self.node_contents_visit(node)

    @override
    def visit_TypeAlias(self, node: TypeAlias) -> AST:
        return self.node_contents_visit(node)

    @override
    def visit_TypeVar(self, node: TypeVar) -> AST:
        return self.node_contents_visit(node)

    @override
    def visit_TypeVarTuple(self, node: TypeVarTuple) -> AST:
        return self.node_contents_visit(node)

    @override
    def visit_ParamSpec(self, node: ParamSpec) -> AST:
        return self.node_contents_visit(node)

    @override
    def visit_ClassDef(self, node: ClassDef) -> stmt:
        # find attribute docs in this class definition
        doc_strings = self.get_descriptions(node.body)
        self.used_names[node.name + ":doc_strings"] = doc_strings
        return super().visit_ClassDef(node)
