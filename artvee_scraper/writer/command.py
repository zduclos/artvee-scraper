from abc import ABC, abstractmethod
from typing import List, Optional

from artvee_scraper.utils import ListIterator


class Command(ABC):
    """Interface for an executable operation that can be reverted."""

    @abstractmethod
    def execute(self) -> bool:
        """Execute this operation.

        Returns:
            `True` if the command executed successfully; otherwise `False`.
        Raises:
            NotImplementedError: If the derived class does not override this method
        """
        raise NotImplementedError

    @abstractmethod
    def revert(self) -> bool:
        """Undo this operation.

        Returns:
            `True` if the command reverted successfully; otherwise `False`.
        Raises:
            NotImplementedError: If the derived class does not override this method
        """
        raise NotImplementedError


class MacroCommand(Command):
    """Execute a sequence of subcommands.

    Attributes:
        cmds (str, List[Command]):
            Registered subcommands to be executed in order. Defaults to empty list.
        index (int, optional):
            Position of the current subcommand. Defaults to `None`
    """

    def __init__(self) -> None:
        """Constructs a new `MacroCommand` instance."""
        self._cmds: List[Command] = []
        self._iter: Optional[ListIterator] = None

    def add(self, subcommand: Command) -> None:
        """Register a subcommand.

        Args:
            subcommand:
                Subcommand to be appended to the end of the traversal list.
        """
        self._cmds.append(subcommand)

    def remove(self, subcommand: Command) -> None:
        """Deregister a subcommand.

        Args:
            subcommand:
                Subcommand to be removed from the traversal list.
        """
        self._cmds.remove(subcommand)

    def execute(self) -> bool:
        """Execute each registered command.

        When a subcommand fails during traversal, the remaining subcommands will not be executed.
        To undo changes when a failure occurs, use `revert()`.

        Returns:
            `True` if all of the subcommands executed successfully; otherwise `False`.
        """
        if self._iter is None:
            self._iter = ListIterator(self._cmds)

        while self._iter.has_next():
            cmd = self._iter.next()

            if not cmd.execute():
                self._iter.previous()
                return False

        return True

    def revert(self) -> bool:
        """Revert each registered command.

        Unexecute in reverse order, beginning with the last successful subcommand.

        Returns:
            `True` if all of the subcommands reverted successfully; otherwise `False`.
        """
        if self._iter is None:
            return True

        while self._iter.has_previous():
            cmd = self._iter.previous()

            if not cmd.revert():
                self._iter.next()
                return False

        return True
