from abc import ABC, abstractmethod

from ..application import ApplicationError
from ..domain import DomainError


# ввод и вывод подменяем в тестах
class ConsoleIO(ABC):
    @abstractmethod
    def read(self, prompt):
        pass

    @abstractmethod
    def write(self, text=""):
        pass


class StdConsoleIO(ConsoleIO):
    def read(self, prompt):
        return input(prompt)

    def write(self, text=""):
        print(text)


class InputError(Exception):
    pass


class ConsoleApp:
    MENU = [
        ("1", "Добавить студента"),
        ("2", "Список студентов"),
        ("3", "Добавить критерий"),
        ("4", "Рубрикатор (критерии)"),
        ("5", "Выставить оценку"),
        ("6", "Оценки студента"),
        ("7", "Исправить оценку"),
        ("8", "Отменить оценку"),
        ("9", "Итог студента"),
        ("10", "Итоги всех студентов"),
        ("11", "Экспорт итогов в CSV"),
        ("0", "Выход"),
    ]

    def __init__(self, gradebook, io):
        self._gradebook = gradebook
        self._io = io
        self._actions = {
            "1": self.add_student,
            "2": self.show_students,
            "3": self.add_criterion,
            "4": self.show_criteria,
            "5": self.put_evaluation,
            "6": self.show_evaluations,
            "7": self.correct_evaluation,
            "8": self.cancel_evaluation,
            "9": self.show_final_grade,
            "10": self.show_all_grades,
            "11": self.export,
        }

    def run(self):
        self._io.write("=== ПОС - Преподавательская Оценка Студентов ===")
        try:
            while True:
                self._io.write()
                for key, title in self.MENU:
                    self._io.write("  " + key + ". " + title)
                choice = self._io.read("Выберите пункт: ").strip()

                if choice == "0":
                    break
                if choice not in self._actions:
                    self._io.write("Нет такого пункта меню.")
                    continue

                try:
                    self._actions[choice]()
                # ошибки домена печатаем, программа не падает
                except (DomainError, ApplicationError, InputError) as error:
                    self._io.write("Ошибка: " + str(error))
        except (EOFError, KeyboardInterrupt):
            self._io.write()
        self._io.write("До свидания!")

    def add_student(self):
        student = self._gradebook.add_student(self._io.read("Имя студента: "))
        self._io.write("Добавлен студент " + str(student))

    def show_students(self):
        students = self._gradebook.students()
        if len(students) == 0:
            self._io.write("Студентов пока нет.")
            return
        for student in students:
            self._io.write("  " + str(student))

    def add_criterion(self):
        name = self._io.read("Название критерия: ")
        max_score = self._ask_number("Максимальный балл: ")
        weight = self._ask_number("Вес в итоге: ")
        criterion = self._gradebook.add_criterion(name, max_score, weight)
        self._io.write("Добавлен критерий " + str(criterion))

    def show_criteria(self):
        criteria = self._gradebook.criteria()
        if len(criteria) == 0:
            self._io.write("Рубрикатор пуст.")
            return
        for criterion in criteria:
            self._io.write("  " + str(criterion))

    def put_evaluation(self):
        student_id = self._ask_int("Номер студента: ")
        criterion_id = self._ask_int("Номер критерия: ")
        value = self._ask_number("Балл: ")
        comment = self._io.read("Комментарий (можно пусто): ")
        evaluation = self._gradebook.put_evaluation(student_id, criterion_id, value, comment)
        self._io.write("Оценка №" + str(evaluation.id) + " выставлена: " + str(evaluation.score))

    def show_evaluations(self):
        student_id = self._ask_int("Номер студента: ")
        evaluations = self._gradebook.evaluations_of(student_id)
        if len(evaluations) == 0:
            self._io.write("Оценок пока нет.")
            return
        names = {}
        for criterion in self._gradebook.criteria():
            names[criterion.id] = criterion.name
        for evaluation in evaluations:
            line = (
                "  №" + str(evaluation.id) + "  " + names.get(evaluation.criterion_id, "?")
                + ": " + str(evaluation.score) + "  (" + str(evaluation.date) + ")"
            )
            if evaluation.comment != "":
                line = line + "  - " + evaluation.comment
            self._io.write(line)

    def correct_evaluation(self):
        evaluation_id = self._ask_int("Номер оценки: ")
        value = self._ask_number("Новый балл: ")
        comment = self._io.read("Новый комментарий (пусто - оставить старый): ")
        if comment.strip() == "":
            comment = None
        evaluation = self._gradebook.correct_evaluation(evaluation_id, value, comment)
        self._io.write("Оценка №" + str(evaluation.id) + " исправлена: " + str(evaluation.score))

    def cancel_evaluation(self):
        evaluation_id = self._ask_int("Номер оценки: ")
        self._gradebook.cancel_evaluation(evaluation_id)
        self._io.write("Оценка №" + str(evaluation_id) + " отменена.")

    def show_final_grade(self):
        grade = self._gradebook.final_grade(self._ask_int("Номер студента: "))
        self._io.write("Итог - " + str(grade))

    def show_all_grades(self):
        grades = self._gradebook.final_grades()
        if len(grades) == 0:
            self._io.write("Студентов пока нет.")
            return
        for grade in grades:
            self._io.write("  " + str(grade))

    def export(self):
        path = self._gradebook.export_results()
        self._io.write("Итоги выгружены в файл " + path)

    # переспрашиваем, пока не введут число
    def _ask_number(self, prompt):
        text = self._io.read(prompt).strip().replace(",", ".")
        try:
            number = float(text)
        except ValueError:
            raise InputError("нужно число, а введено «" + text + "»")
        if number == int(number):
            return int(number)
        return number

    def _ask_int(self, prompt):
        text = self._io.read(prompt).strip()
        if not text.isdigit():
            raise InputError("нужен номер (целое число), а введено «" + text + "»")
        return int(text)

