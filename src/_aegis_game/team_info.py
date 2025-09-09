from .team import Team


class TeamInfo:
    def __init__(self) -> None:
        self._saved_alive: list[int] = [0] * 2
        self._saved_dead: list[int] = [0] * 2
        self._saved: list[int] = [0] * 2
        self._predicted_right: list[int] = [0] * 2
        self._predicted_wrong: list[int] = [0] * 2
        self._predicted: list[int] = [0] * 2
        self._score: list[int] = [0] * 2
        self._units: list[int] = [0] * 2
        self._lumens: list[int] = [0] * 2

    def get_saved(self, team: Team) -> int:
        return self._saved[team.value]

    def get_saved_alive(self, team: Team) -> int:
        return self._saved_alive[team.value]

    def get_saved_dead(self, team: Team) -> int:
        return self._saved_dead[team.value]

    def get_predicted(self, team: Team) -> int:
        return self._predicted[team.value]

    def get_predicted_right(self, team: Team) -> int:
        return self._predicted_right[team.value]

    def get_predicted_wrong(self, team: Team) -> int:
        return self._predicted_wrong[team.value]

    def get_score(self, team: Team) -> int:
        return self._score[team.value]

    def get_units(self, team: Team) -> int:
        return self._units[team.value]

    def get_lumens(self, team: Team) -> int:
        return self._lumens[team.value]

    def _add(self, array: list[int], team: Team, amount: int = 1) -> None:
        array[team.value] += amount

    def add_saved(self, team: Team, amount: int = 1, *, is_alive: bool) -> None:
        self._add(self._saved, team, amount)
        if is_alive:
            self._add(self._saved_alive, team, amount)
        else:
            self._add(self._saved_dead, team, amount)

    def add_predicted(self, team: Team, amount: int = 1, *, correct: bool) -> None:
        self._add(self._predicted, team, amount)
        if correct:
            self._add(self._predicted_right, team, amount)
        else:
            self._add(self._predicted_wrong, team, amount)

    def add_score(self, team: Team, amount: int) -> None:
        self._add(self._score, team, amount)

    def add_units(self, team: Team, amount: int) -> None:
        self._add(self._units, team, amount)

    def add_lumens(self, team: Team, amount: int) -> None:
        self._add(self._lumens, team, amount)
