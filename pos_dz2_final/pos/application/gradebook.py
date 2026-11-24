from ..domain import Student
from .errors import ApplicationError


# фасад, одна дверь для консоли и демо
class Gradebook:
    def __init__(self, students, rubrics, evaluations, factory, calculator, exporter):
        self._students = students
        self._rubrics = rubrics
        self._evaluations = evaluations
        self._factory = factory
        self._calculator = calculator
        self._exporter = exporter

    def add_student(self, name):
        student = Student(self._students.next_id(), name)
        self._students.add(student)
        return student

    def students(self):
        return self._students.all()

    def add_criterion(self, name, max_score, weight):
        rubric = self._rubrics.get()
        criterion = rubric.add_criterion(name, max_score, weight)
        self._rubrics.save(rubric)
        return criterion

    def criteria(self):
        return self._rubrics.get().criteria

    # по одному критерию у студента только одна оценка
    def put_evaluation(self, student_id, criterion_id, value, comment=""):
        self._student(student_id)

        for old in self._evaluations.for_student(student_id):
            if old.criterion_id == criterion_id:
                raise ApplicationError(
                    "У студента уже есть оценка №" + str(old.id)
                    + " по этому критерию - исправьте её"
                )

        evaluation = self._factory.create(
            self._evaluations.next_id(), self._rubrics.get(),
            student_id, criterion_id, value, comment,
        )
        self._evaluations.add(evaluation)
        return evaluation

    def evaluations_of(self, student_id):
        self._student(student_id)
        return self._evaluations.for_student(student_id)

    def correct_evaluation(self, evaluation_id, new_value, comment=None):
        evaluation = self._evaluation(evaluation_id)
        evaluation.correct(new_value, comment)
        return evaluation

    def cancel_evaluation(self, evaluation_id):
        self._evaluation(evaluation_id)
        self._evaluations.remove(evaluation_id)

    def final_grade(self, student_id):
        student = self._student(student_id)
        return self._calculator.calculate(
            student, self._rubrics.get(), self._evaluations.for_student(student_id)
        )

    # итоги от большего к меньшему
    def final_grades(self):
        grades = []
        for student in self._students.all():
            grades.append(self.final_grade(student.id))
        grades.sort(key=lambda grade: grade.points, reverse=True)
        return grades

    def export_results(self):
        return self._exporter.export(self.final_grades())

    # нет студента, бросаем понятную ошибку
    def _student(self, student_id):
        student = self._students.get(student_id)
        if student is None:
            raise ApplicationError("Студента №" + str(student_id) + " нет")
        return student

    def _evaluation(self, evaluation_id):
        evaluation = self._evaluations.get(evaluation_id)
        if evaluation is None:
            raise ApplicationError("Оценки №" + str(evaluation_id) + " нет")
        return evaluation
