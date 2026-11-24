from abc import ABC, abstractmethod

from .errors import format_number


# результат расчёта итога
class FinalGrade:
    def __init__(self, student, ratio, graded_count, total_count, strategy_name):
        self._student = student
        self._ratio = ratio
        self._graded_count = graded_count
        self._total_count = total_count
        self._strategy_name = strategy_name

    @property
    def student(self):
        return self._student

    @property
    def points(self):
        return round(self._ratio * 10, 2)

    @property
    def percent(self):
        return round(self._ratio * 100, 1)

    @property
    def graded_count(self):
        return self._graded_count

    @property
    def total_count(self):
        return self._total_count

    @property
    def strategy_name(self):
        return self._strategy_name

    def __str__(self):
        return (
            self._student.name + ": " + format_number(self.points) + " из 10 ("
            + format_number(self.percent) + " %), оценено "
            + str(self._graded_count) + " из " + str(self._total_count)
        )


# правило итога вынесено в отдельный класс
class GradingStrategy(ABC):
    NAME = "?"

    @abstractmethod
    def ratio(self, rubric, by_criterion):
        pass


# нет оценки считаем ноль
class AllCriteriaStrategy(GradingStrategy):
    NAME = "все критерии (нет оценки = 0)"

    def ratio(self, rubric, by_criterion):
        total_weight = rubric.total_weight()
        if total_weight == 0:
            return 0
        weighted = 0
        for criterion in rubric.criteria:
            if criterion.id in by_criterion:
                weighted = weighted + criterion.weight * by_criterion[criterion.id].score.ratio()

        return weighted / total_weight


# считаем только оценённые критерии
class GradedOnlyStrategy(GradingStrategy):
    NAME = "только оценённые критерии"

    def ratio(self, rubric, by_criterion):
        weighted = 0
        used_weight = 0
        for criterion in rubric.criteria:
            if criterion.id in by_criterion:
                weighted = weighted + criterion.weight * by_criterion[criterion.id].score.ratio()
                used_weight = used_weight + criterion.weight
        if used_weight == 0:
            return 0
        return weighted / used_weight


# стратегию калькулятор получает снаружи
class FinalGradeCalculator:
    def __init__(self, strategy):
        self._strategy = strategy

    def calculate(self, student, rubric, evaluations):

        by_criterion = {}
        for evaluation in evaluations:
            if evaluation.student_id == student.id and rubric.has(evaluation.criterion_id):
                by_criterion[evaluation.criterion_id] = evaluation

        ratio = self._strategy.ratio(rubric, by_criterion)
        return FinalGrade(student, ratio, len(by_criterion), len(rubric.criteria), self._strategy.NAME)
