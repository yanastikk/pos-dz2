import unittest

from pos.domain import DomainError, EvaluationFactory, Rubric, Score, Student


class ScoreTests(unittest.TestCase):
    def test_score_inside_limits(self):
        score = Score(7, 10)
        self.assertEqual(score.value, 7)
        self.assertEqual(score.ratio(), 0.7)
        self.assertEqual(str(score), "7/10")

    def test_borders_are_allowed(self):
        Score(0, 10)
        Score(10, 10)

    def test_more_than_max_is_forbidden(self):
        with self.assertRaises(DomainError):
            Score(12, 10)

    def test_negative_is_forbidden(self):
        with self.assertRaises(DomainError):
            Score(-1, 10)

    def test_not_a_number_is_forbidden(self):
        with self.assertRaises(DomainError):
            Score("7", 10)
        with self.assertRaises(DomainError):
            Score(True, 10)

    def test_value_object_compares_by_value(self):
        self.assertEqual(Score(7, 10), Score(7, 10))
        self.assertNotEqual(Score(7, 10), Score(7, 20))
        self.assertEqual(len({Score(7, 10), Score(7, 10)}), 1)

    def test_value_cannot_be_changed(self):
        with self.assertRaises(AttributeError):
            Score(7, 10).value = 9


class StudentTests(unittest.TestCase):
    def test_empty_name_is_forbidden(self):
        with self.assertRaises(DomainError):
            Student(1, "   ")

    def test_entity_compares_by_id(self):
        anya = Student(1, "Аня")
        renamed = Student(1, "Анна")
        self.assertEqual(anya, renamed)
        self.assertNotEqual(anya, Student(2, "Аня"))

    def test_rename_keeps_rules(self):
        anya = Student(1, "Аня")
        anya.rename("Анна")
        self.assertEqual(anya.name, "Анна")
        with self.assertRaises(DomainError):
            anya.rename("")


class RubricTests(unittest.TestCase):
    def test_add_and_get(self):
        rubric = Rubric()
        code = rubric.add_criterion("Код", 10, 0.5)
        self.assertEqual(code.id, 1)
        self.assertIs(rubric.get(1), code)
        self.assertTrue(rubric.has(1))
        self.assertEqual(rubric.total_weight(), 0.5)

    def test_duplicate_name_is_forbidden(self):
        rubric = Rubric()
        rubric.add_criterion("Код", 10, 0.5)
        with self.assertRaises(DomainError):
            rubric.add_criterion("  код ", 5, 1)

    def test_bad_max_or_weight(self):
        rubric = Rubric()
        with self.assertRaises(DomainError):
            rubric.add_criterion("Код", 0, 1)
        with self.assertRaises(DomainError):
            rubric.add_criterion("Код", 10, -1)

    def test_unknown_criterion(self):
        with self.assertRaises(DomainError):
            Rubric().get(99)

    def test_criteria_list_is_read_only(self):
        rubric = Rubric()
        rubric.add_criterion("Код", 10, 1)
        self.assertIsInstance(rubric.criteria, tuple)


class FactoryAndEvaluationTests(unittest.TestCase):
    def setUp(self):
        self.rubric = Rubric()
        self.code = self.rubric.add_criterion("Код", 10, 1)
        self.factory = EvaluationFactory()

    def test_factory_uses_criterion_max(self):
        evaluation = self.factory.create(1, self.rubric, 1, self.code.id, 8, " ок ")
        self.assertEqual(evaluation.score, Score(8, 10))
        self.assertEqual(evaluation.comment, "ок")

    def test_factory_rejects_unknown_criterion(self):
        with self.assertRaises(DomainError):
            self.factory.create(1, self.rubric, 1, 99, 5)

    def test_factory_rejects_score_over_max(self):
        with self.assertRaises(DomainError):
            self.factory.create(1, self.rubric, 1, self.code.id, 12)

    def test_correct_keeps_limits(self):
        evaluation = self.factory.create(1, self.rubric, 1, self.code.id, 8)
        evaluation.correct(9, "пересдал")
        self.assertEqual(evaluation.score.value, 9)
        self.assertEqual(evaluation.comment, "пересдал")
        with self.assertRaises(DomainError):
            evaluation.correct(11)
        self.assertEqual(evaluation.score.value, 9)


if __name__ == "__main__":
    unittest.main()
