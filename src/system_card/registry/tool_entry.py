"""Lazily-loaded handle to a single tool, deferring import until first use."""

import importlib
import inspect
from collections.abc import Callable
from typing import Any

from pydantic import BaseModel, create_model

from system_card.schemas.tool_manifest import ToolManifestEntry


class ToolEntry:
    """Holds a pointer to a tool's location. The module is not imported until load() is called."""

    def __init__(self, module_path: str, fn_name: str) -> None:
        """Stores the tool's location without importing it.

        Args:
            module_path: Dotted import path of the module containing the tool function.
            fn_name: Name of the tool function within that module.
        """
        self.module_path = module_path
        self.fn_name = fn_name
        self._fn: Callable[..., Any] | None = None

    def load(self) -> Callable[..., Any]:
        """Resolves and caches the tool function on first call only.

        Returns:
            The underlying tool function.
        """
        fn = self._fn
        if fn is None:
            module = importlib.import_module(self.module_path)
            fn = getattr(module, self.fn_name)
            self._fn = fn

        return fn

    def run(self, **kwargs: Any) -> Any:
        """Calls the underlying tool function with the given keyword arguments.

        Args:
            **kwargs: Arguments forwarded to the tool function.

        Returns:
            Whatever the tool function returns.
        """
        return self.load()(**kwargs)

    def manifest(self) -> ToolManifestEntry:
        """Builds this tool's manifest entry from its docstring and signature.

        Returns:
            A ToolManifestEntry describing this tool's LLM-facing surface.
        """
        fn = self.load()

        return ToolManifestEntry(
            name=self.fn_name,
            description=inspect.getdoc(fn) or "",
            parameters=_parameter_schema(fn),
        )


def _parameter_schema(fn: Callable[..., Any]) -> dict[str, Any]:
    fields: dict[str, Any] = {}

    for name, param in inspect.signature(fn).parameters.items():
        default = ... if param.default is inspect.Parameter.empty else param.default
        fields[name] = (param.annotation, default)

    model: type[BaseModel] = create_model(fn.__name__, **fields)

    return model.model_json_schema()
