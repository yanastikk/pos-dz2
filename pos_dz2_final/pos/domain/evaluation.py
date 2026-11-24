import datetime

from .errors import DomainError
from .score import Score


class Evaluation:
    def __init__(self, evaluation_id, student_id, criterion_id, score, comment="", date=None):

        if not isinstance(score, Score):
            raise DomainError("Оценка принимает только Score")

        if date is None:
            date = datetime.date.today()

        self._id = evaluation_id
        self._student_id = student_id
        self._criterion_id = criterion_id
        self._score = score
        self._comment = comment.strip()
        self._date = date

    @property
    def id(self):
        return self._id

    @property
    def student_id(self):
        return self._student_id

    @property
    def criterion_id(self):
        return self._criterion_id

    @property
    def score(self):
        return self._score

    @property
    def comment(self):
        return self._comment

    @property
    def date(self):
        return self._date

    # исправление создаёт новый score старый не меняем
    def correct(self, new_value, comment=None):
        self._score = Score(new_value, self._score.max_score)
        if comment is not None:
            self._comment = comment.strip()
        self._date = datetime.date.today()

    def __eq__(self, other):
        if not isinstance(other, Evaluation):
            return False
        return self._id == other._id

    def __hash__(self):
        return hash(self._id)
