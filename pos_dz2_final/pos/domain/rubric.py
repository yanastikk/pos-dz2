from .errors import DomainError, format_number, require_positive, require_text


class Criterion:
    def __init__(self, criterion_id, name, max_score, weight):
        self._id = criterion_id
        self._name = require_text(name, "Название критерия")
        self._max_score = require_positive(max_score, "Максимум критерия")
        self._weight = require_positive(weight, "Вес критерия")

    @property
    def id(self):
        return self._id

    @property
    def name(self):
        return self._name

    @property
    def max_score(self):
        return self._max_score

    @property
    def weight(self):
        return self._weight

    def __str__(self):
        return (
            "№" + str(self._id) + " " + self._name
            + " (макс " + format_number(self._max_score)
            + ", вес " + format_number(self._weight) + ")"
        )


class Rubric:
    def __init__(self):
        self._criteria = []
        self._next_id = 1

    def add_criterion(self, name, max_score, weight):
        name = require_text(name, "Название критерия")

        for criterion in self._criteria:
            # названия без учёта регистра не повторяются
            if criterion.name.lower() == name.lower():
                raise DomainError("Критерий «" + name + "» уже есть в рубрикаторе")

        criterion = Criterion(self._next_id, name, max_score, weight)
        self._criteria.append(criterion)
        self._next_id = self._next_id + 1
        return criterion

    def has(self, criterion_id):
        for criterion in self._criteria:
            if criterion.id == criterion_id:
                return True
        return False

    def get(self, criterion_id):
        for criterion in self._criteria:
            if criterion.id == criterion_id:
                return criterion
        raise DomainError("Критерия №" + str(criterion_id) + " нет в рубрикаторе")

    @property
    def criteria(self):
        return tuple(self._criteria)

    # сумма весов нужна для стратегии все критерии
    def total_weight(self):
        total = 0
        for criterion in self._criteria:
            total = total + criterion.weight
        return total
