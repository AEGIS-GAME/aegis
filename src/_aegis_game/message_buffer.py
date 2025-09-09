from collections import deque

from .constants import Constants
from .message import Message


class MessageBuffer:
    """Maintains a limited history of messages grouped by round."""

    def __init__(self) -> None:
        self._history: deque[int] = deque(maxlen=Constants.MESSAGE_HISTORY_LIMIT)
        self._round_map: dict[int, list[Message]] = {}
        self._pending: list[Message] = []

    def add_message(self, message: Message) -> None:
        """
        Add a message to the pending buffer for next round.

        Args:
            message (Message): The message to store.

        """
        self._pending.append(message)

    def _rotate_to(self, new_round: int) -> None:
        """
        Prepare the buffer to store messages for a new round.

        Any messages in the pending queue (received during the previous round)
        are committed to the last round's history before starting the new one.
        This ensures that messages are only visible one round after they are
        received.

        If the maximum history size is reached, the oldest round's messages
        are discarded.

        Args:
            new_round (int): The new round to initialize in the buffer.

        """
        if (
            self._history.maxlen is not None
            and len(self._history) == self._history.maxlen
        ):
            oldest = self._history.popleft()
            del self._round_map[oldest]
        self._history.append(new_round)
        self._round_map[new_round] = list(self._pending)
        self._pending.clear()

    def get_all_messages(self) -> list[Message]:
        """
        Retrieve all messages from the buffer.

        Messages are returned in reverse-chronological order: newest round's
        messages first, oldest last.

        Returns:
            list[Message]: All stored messages, sorted by most recent round.

        """
        result: list[Message] = []
        for r in reversed(self._history):
            result.extend(self._round_map[r])
        return result

    def get_messages(self, round_num: int) -> list[Message]:
        """
        Retrieve messages from a specific round.

        Args:
            round_num (int): The round to fetch messages for.

        Returns:
            list[Message]: A copy of the messages from the round,
            or an empty list if not stored.

        """
        return list(self._round_map.get(round_num, []))

    def next_round(self, round_num: int) -> None:
        """
        Start a new round.

        Args:
            round_num (int): The round number to begin.

        """
        self._rotate_to(round_num)
