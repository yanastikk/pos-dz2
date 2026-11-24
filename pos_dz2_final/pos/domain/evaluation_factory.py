from .evaluation import Evaluation
from .score import Score


class EvaluationFactory:
    def create(self, evaluation_id, rubric, student_id, criterion_id, value, comment="", date=None):

        # шаг 1 критерий должен быть в рубрикаторе
        criterion = rubric.get(criterion_id)

        # шаг 2 балл в пределах максимума критерия
        score = Score(value, criterion.max_score)

        # шаг 3 всё проверено можно создавать
        return Evaluation(evaluation_id, student_id, criterion.id, score, comment, date)
