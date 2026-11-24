import unittest

from pos.domain import (
    AllCriteriaStrategy,
    EvaluationFactory,
    FinalGradeCalculator,
    GradedOnlyStrategy,
    Rubric,
    Student,
)


class GradingTests(unittest.TestCase):
    def setUp(self):
        self.rubric = Rubric()
        self.code = self.rubric.add_criterion("Код", 10, 0.5)
        self.tests = self.rubric.add_criterion("Тесты", 5, 0.2)
        self.defense = self.rubric.add_criterion("Защита", 10, 0.3)
        self.anya = Student(1, "Аня")
        factory = EvaluationFactory()

        self.evaluations = [
            factory.create(1, self.rubric, 1, self.code.id, 10),
            factory.create(2, self.rubric, 1, self.tests.id, 4),
            factory.create(3, self.rubric, 2, self.code.id, 1),
        ]

    def test_all_criteria_counts_missing_as_zero(self):
        grade = FinalGradeCalculator(AllCriteriaStrategy()).calculate(self.anya, self.rubric, self.evaluations)

        self.assertEqual(grade.points, 6.6)
        self.assertEqual(grade.percent, 66.0)
        self.assertEqual(grade.graded_count, 2)
        self.assertEqual(grade.total_count, 3)

    def test_graded_only_ignores_missing(self):
        grade = FinalGradeCalculator(GradedOnlyStrategy()).calculate(self.anya, self.rubric, self.evaluations)

        self.assertEqual(grade.points, 9.43)

    def test_other_students_evaluations_are_ignored(self):
        boris = Student(2, "Борис")
        grade = FinalGradeCalculator(AllCriteriaStrategy()).calculate(boris, self.rubric, self.evaluations)
        self.assertEqual(grade.points, 0.5)
        self.assertEqual(grade.graded_count, 1)

    def test_empty_rubric_gives_zero(self):
        for strategy in (AllCriteriaStrategy(), GradedOnlyStrategy()):
            grade = FinalGradeCalculator(strategy).calculate(self.anya, Rubric(), [])
            self.assertEqual(grade.points, 0)

    def test_text(self):
        grade = FinalGradeCalculator(AllCriteriaStrategy()).calculate(self.anya, self.rubric, self.evaluations)
        self.assertEqual(str(grade), "Аня: 6.6 из 10 (66 %), оценено 2 из 3")


if __name__ == "__main__":
    unittest.main()
