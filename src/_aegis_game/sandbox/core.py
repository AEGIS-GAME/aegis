# pyright: reportMissingTypeStubs = false
# pyright: reportUnknownMemberType = false
import builtins as py_builtins
import traceback
import types
from collections.abc import Callable, Mapping, Sequence
from threading import Event, Thread
from typing import Any, override

from RestrictedPython import (
    Guards,
    limited_builtins,  # pyright: ignore[reportUnknownVariableType]
    safe_builtins,  # pyright: ignore[reportUnknownVariableType]
)

from _aegis_game.types import MethodDict

from .sandbox import Sandbox

def _inplacevar_(op, var, expr):
    if op == "+=":
        return var + expr
    elif op == "-=":
        return var - expr
    elif op == "*=":
        return var * expr
    elif op == "/=":
        return var / expr
    elif op == "%=":
        return var % expr
    elif op == "**=":
        return var ** expr
    elif op == "<<=":
        return var << expr
    elif op == ">>=":
        return var >> expr
    elif op == "|=":
        return var | expr
    elif op == "^=":
        return var ^ expr
    elif op == "&=":
        return var & expr
    elif op == "//=":
        return var // expr
    elif op == "@=":
        return var // expr



class LumenCore:
    """Core executor for running agent code in a restricted, sandboxed environment."""

    def __init__(
        self, code: Sandbox, methods: MethodDict, error: Callable[..., None]
    ) -> None:
        """
        Initialize the LumenCore executor.

        Args:
            code: A sandboxed script containing the agent logic.
            methods: A dictionary of allowed API methods for the agent.
            error: A callback to report errors during execution.

        """
        self.code: Sandbox = code
        self.methods: MethodDict = methods
        self.error: Callable[..., None] = error
        self.initialized: bool = False
        self.thread: LumenThread = LumenThread(self)
        self.thread.start()

        self.allowed_modules: set[str] = {
            "os",
            "typing",
            "pathlib",
            "random",
            "heapq",
            "math",
            "json",
            "re",
            "enum",
            "numpy",
            "tensorflow",
            "tf",
        }

        self.namespace: dict[str, object] = self._build_namespace()

    def _build_namespace(self) -> dict[str, object]:
        """
        Construct the restricted execution namespace for the agent.

        Returns:
            A dictionary representing the sandboxed execution environment.

        """
        builtins: MethodDict = {
            **safe_builtins,
            **limited_builtins,
            **self.methods,
            **{
                name: getattr(py_builtins, name)
                for name in [
                    "all",
                    "any",
                    "list",
                    "dict",
                    "set",
                    "tuple",
                    "enumerate",
                    "reversed",
                    "max",
                    "min",
                    "sum",
                ]
            },
        }

        builtins["__import__"] = self.custom_import

        namespace: dict[str, object] = {
            "__builtins__": builtins,
            "_inplacevar_": _inplacevar_,
            "__name__": "__main__",
            "_getattr_": self.deny_private_attr,
            "_getitem_": self.deny_private_items,
            "_getiter_": self.default_guarded_iter,
            "_write_": self.default_guarded_write,
            "__metaclass__": type,
            "_unpack_sequence_": Guards.guarded_unpack_sequence,
            "_iter_unpack_sequence_": Guards.guarded_iter_unpack_sequence,
        }

        return namespace

    def default_guarded_iter(self, ob: object) -> object:
        """Bypass iteration restrictions (safe override for RestrictedPython)."""
        return ob

    def default_guarded_write(self, ob: object) -> object:
        """Bypass write restrictions (safe override for RestrictedPython)."""
        return ob

    def custom_import(
        self,
        name: str,
        globals_: Mapping[str, object] | None = None,
        locals_: Mapping[str, object] | None = None,
        fromlist: Sequence[str] = (),
        level: int = 0,
    ) -> types.ModuleType:
        """
        Import guard for controlling allowed modules.

        Disallows relative/private imports and validates modules against allowlist.
        """
        # Allow "import module" if it's in the allowed list
        if not fromlist and name not in self.allowed_modules:
            error = f"Import of module '{name}' is not allowed"
            raise ImportError(error)

        # Invalid imports
        if fromlist and not isinstance(fromlist, tuple):
            error = f"Invalid Import: {name}"
            raise ImportError(error)

        # Disallow relative imports
        if level != 0:
            error = f"Relative imports not allowed: {name}"
            raise ImportError(error)

        # Disallow private imports
        if name.startswith("_") or name not in self.allowed_modules:
            error = f"Import of module '{name}' is not allowed"
            raise ImportError(error)
        return __import__(name, globals_, locals_, fromlist, level)  # pyright: ignore[reportAny]

    @staticmethod
    def deny_private_attr(obj: object, attr: str) -> object:
        """Deny access to private attributes."""
        if attr.startswith("_"):
            error = f"Access to private attribute '{attr}' is denied."
            raise AttributeError(error)
        return getattr(obj, attr)  # pyright: ignore[reportAny]

    @staticmethod
    def deny_private_items(obj: Mapping[Any, Any], item: object) -> object:  # pyright: ignore[reportExplicitAny]
        """Deny access to private keys."""
        if isinstance(item, str) and item.startswith("_"):
            error = f"Access to private key '{item}' is denied."
            raise KeyError(error)
        return obj[item]  # pyright: ignore[reportAny]

    def init(self) -> None:
        """Initialize the agent's main code."""
        try:
            exec(self.code["main"], self.namespace)  # noqa: S102
            self.initialized = True
        except Exception:  # noqa: BLE001
            self.error(traceback.format_exc(limit=5))

    def think(self) -> None:
        """Call the agent's `think()` function. Reports errors if not defined or fails."""
        fn = self.namespace.get("think")
        if not callable(fn):
            self.error("Think doesn't exist")
            return
        try:
            _ = fn()
        except Exception:  # noqa: BLE001
            self.error(traceback.format_exc(limit=5))

    def run(self) -> None:
        """Triggers a turn execution in the LumenThread and waits for completion."""
        self.thread.trigger_turn()
        self.thread.wait_for_turn()

    def kill(self) -> None:
        """Terminates the thread execution and waits for cleanup."""
        self.thread.kill()
        self.thread.join()


class LumenThread(Thread):
    """Manages a background thread for executing agent logic turn-by-turn."""

    def __init__(self, runner: LumenCore) -> None:
        """
        Initialize a turn-based thread runner.

        Args:
            runner: The LumenCore instance this thread manages.

        """
        super().__init__()
        self.runner: LumenCore = runner
        self.running: bool = True
        self.paused: bool = False

        self.run_event: Event = Event()
        self.pause_event: Event = Event()
        self.turn_done_event: Event = Event()

    @override
    def run(self) -> None:
        """Thread loop. Waits for turn triggers and runs agent logic."""
        while self.running:
            _ = self.run_event.wait()
            if not self.running:
                break

            if not self.runner.initialized:
                self.runner.init()

            self.runner.think()
            self.run_event.clear()
            self.turn_done_event.set()

    def trigger_turn(self) -> None:
        """Signals the thread to start or resume a turn."""
        if self.paused:
            self.pause_event.set()
        else:
            self.run_event.set()

    def wait_for_turn(self) -> None:
        """Wait for the current turn to finish."""
        _ = self.turn_done_event.wait()
        _ = self.turn_done_event.clear()

    def wait_for_resume(self) -> None:
        """Wait for the thread to resume if paused."""
        self.turn_done_event.set()
        _ = self.pause_event.wait()
        self.pause_event.clear()

    def kill(self) -> None:
        """Gracefully shuts down the thread."""
        self.running = False
        self.run_event.set()
        self.pause_event.set()
