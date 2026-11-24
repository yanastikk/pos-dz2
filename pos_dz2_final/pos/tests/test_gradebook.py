import unittest

from pos.application import ApplicationError
from pos.domain import DomainError, GradedOnlyStrategy
from pos.tests.fakes import FakeExporter, make_gradebook


class GradebookTests(unittest.TestCase):
    def setUp(self):
        self.exporter = FakeExporter()
        self.book = make_gradebook(exporter=self.exporter)
        self.anya = self.book.add_student("Аня")
        self.code = self.book.add_criterion("Код", 10, 1)

    def test_put_and_list(self):
        evaluation = self.book.put_evaluation(self.anya.id, self.code.id, 8, "ок")
        self.assertEqual(self.book.evaluations_of(self.anya.id), [evaluation])

    def test_unknown_student(self):
        with self.assertRaises(ApplicationError):
            self.book.put_evaluation(99, self.code.id, 5)

    def test_unknown_criterion(self):
        with self.assertRaises(DomainError):
            self.book.put_evaluation(self.anya.id, 99, 5)

    def test_score_over_max(self):
        with self.assertRaises(DomainError):
            self.book.put_evaluation(self.anya.id, self.code.id, 12)
        self.assertEqual(self.book.evaluations_of(self.anya.id), [])

    def test_second_evaluation_for_same_criterion(self):
        self.book.put_evaluation(self.anya.id, self.code.id, 8)
        with self.assertRaises(ApplicationError):
            self.book.put_evaluation(self.anya.id, self.code.id, 9)

    def test_failed_attempt_does_not_eat_number(self):
        with self.assertRaises(DomainError):
            self.book.put_evaluation(self.anya.id, self.code.id, 12)
        evaluation = self.book.put_evaluation(self.anya.id, self.code.id, 8)
        self.assertEqual(evaluation.id, 1)

    def test_grade_follows_corrections(self):
        evaluation = self.book.put_evaluation(self.anya.id, self.code.id, 8)
        self.assertEqual(self.book.final_grade(self.anya.id).points, 8)
        self.book.correct_evaluation(evaluation.id, 6)
        self.assertEqual(self.book.final_grade(self.anya.id).points, 6)
        self.book.cancel_evaluation(evaluation.id)
        self.assertEqual(self.book.final_grade(self.anya.id).points, 0)

    def test_unknown_evaluation(self):
        with self.assertRaises(ApplicationError):
            self.book.correct_evaluation(99, 5)
        with self.assertRaises(ApplicationError):
            self.book.cancel_evaluation(99)

    def test_final_grades_sorted_and_exported(self):
        boris = self.book.add_student("Борис")
        self.book.put_evaluation(self.anya.id, self.code.id, 5)
        self.book.put_evaluation(boris.id, self.code.id, 9)
        names = [grade.student.name for grade in self.book.final_grades()]
        self.assertEqual(names, ["Борис", "Аня"])
        self.assertEqual(self.book.export_results(), "память")
        self.assertEqual(len(self.exporter.exported), 2)

    def test_strategy_is_replaceable(self):
        book = make_gradebook(strategy=GradedOnlyStrategy())
        anya = book.add_student("Аня")
        code = book.add_criterion("Код", 10, 1)
        book.add_criterion("Защита", 10, 1)
        book.put_evaluation(anya.id, code.id, 8)
        self.assertEqual(book.final_grade(anya.id).points, 8)


if __name__ == "__main__":
    unittest.main()
