from .errors import DomainError, format_number, require_positive


class Score:
    def __init__(self, value, max_score):
        max_score = require_positive(max_score, "Максимум критерия")

        if isinstance(value, bool) or not isinstance(value, (int, float)):
            raise DomainError("Балл должен быть числом")

        # нельзя меньше нуля и больше максимума
        if value < 0 or value > max_score:
            raise DomainError(
                "Балл " + format_number(value)
                + " вне пределов критерия: можно от 0 до " + format_number(max_score)
            )

        self._value = value
        self._max_score = max_score

    @property
    def value(self):
        return self._value

    @property
    def max_score(self):
        return self._max_score

    # доля от максимума нужна для итога
    def ratio(self):
        return self._value / self._max_score

    def __eq__(self, other):
        if not isinstance(other, Score):
            return False
        return self._value == other._value and self._max_score == other._max_score

    def __hash__(self):
        return hash((self._value, self._max_score))

    def __str__(self):
        return format_number(self._value) + "/" + format_number(self._max_score)
