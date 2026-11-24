import csv
import os
import tempfile
import unittest

from pos.application import Gradebook, ResultExporter
from pos.bootstrap import build_container
from pos.demo import run_demo
from pos.di import Container, DependencyError
from pos.infrastructure import ConsoleApp, CsvResultExporter
from pos.tests.fakes import ScriptedIO, make_gradebook


class ConsoleTests(unittest.TestCase):
    def run_console(self, inputs):
        io = ScriptedIO(inputs)
        ConsoleApp(make_gradebook(), io).run()
        return io.output()

    def test_full_path(self):
        out = self.run_console([
            "1", "Аня",
            "3", "Код", "10", "0,5",
            "5", "1", "1", "8", "ок",
            "6", "1",
            "7", "1", "9", "",
            "9", "1",
            "10",
            "8", "1",
            "2", "4",
            "0",
        ])
        self.assertIn("Добавлен студент №1 Аня", out)
        self.assertIn("Добавлен критерий №1 Код (макс 10, вес 0.5)", out)
        self.assertIn("Оценка №1 выставлена: 8/10", out)
        self.assertIn("- ок", out)
        self.assertIn("исправлена: 9/10", out)
        self.assertIn("Итог - Аня: 9 из 10", out)
        self.assertIn("Оценка №1 отменена.", out)
        self.assertIn("До свидания!", out)

    def test_rule_violation_is_printed_not_crashed(self):
        out = self.run_console([
            "1", "Аня", "3", "Код", "10", "1",
            "5", "1", "1", "12", "",
            "5", "1", "7", "5", "",
            "0",
        ])
        self.assertIn("Ошибка: Балл 12 вне пределов критерия", out)
        self.assertIn("Ошибка: Критерия №7 нет в рубрикаторе", out)
        self.assertIn("До свидания!", out)

    def test_bad_input(self):
        out = self.run_console(["9", "abc", "3", "Код", "десять", "42", "0"])
        self.assertIn("нужен номер", out)
        self.assertIn("нужно число", out)
        self.assertIn("Нет такого пункта меню.", out)

    def test_empty_lists(self):
        out = self.run_console(["2", "4", "10", "1", "Аня", "6", "1"])
        self.assertIn("Студентов пока нет.", out)
        self.assertIn("Рубрикатор пуст.", out)
        self.assertIn("Оценок пока нет.", out)
        self.assertIn("До свидания!", out)


class CsvExporterTests(unittest.TestCase):
    def test_writes_rows(self):
        book = make_gradebook()
        anya = book.add_student("Аня")
        code = book.add_criterion("Код", 10, 1)
        book.put_evaluation(anya.id, code.id, 7)
        with tempfile.TemporaryDirectory() as folder:
            path = os.path.join(folder, "itogi.csv")
            self.assertEqual(CsvResultExporter(path).export(book.final_grades()), path)
            with open(path, encoding="utf-8-sig", newline="") as file:
                rows = list(csv.reader(file, delimiter=";"))
        self.assertEqual(rows[0][1], "Студент")
        self.assertEqual(rows[1][:4], ["1", "Аня", "7.0", "70.0"])


class ContainerTests(unittest.TestCase):
    def test_singleton_and_transient(self):
        c = Container()
        c.register_singleton(list, lambda _: [])
        c.register_transient(dict, lambda _: {})
        self.assertIs(c.resolve(list), c.resolve(list))
        self.assertIsNot(c.resolve(dict), c.resolve(dict))

    def test_instance_and_reregister(self):
        c = Container()
        c.register_instance(str, "первый")
        self.assertEqual(c.resolve(str), "первый")
        c.register_instance(str, "второй")
        self.assertEqual(c.resolve(str), "второй")

    def test_missing(self):
        with self.assertRaises(DependencyError):
            Container().resolve(int)

    def test_cycle(self):
        c = Container()
        c.register_singleton(int, lambda c: c.resolve(float))
        c.register_singleton(float, lambda c: c.resolve(int))
        with self.assertRaises(DependencyError) as caught:
            c.resolve(int)
        self.assertIn("int -> float -> int", str(caught.exception))

    def test_bootstrap_builds_everything(self):
        c = build_container()
        self.assertIsInstance(c.resolve(Gradebook), Gradebook)
        self.assertIs(c.resolve(Gradebook), c.resolve(Gradebook))
        self.assertIsInstance(c.resolve(ConsoleApp), ConsoleApp)


class DemoTests(unittest.TestCase):
    def test_demo_runs_and_rules_hold(self):
        c = build_container()
        with tempfile.TemporaryDirectory() as folder:
            path = os.path.join(folder, "demo.csv")
            c.register_singleton(ResultExporter, lambda _: CsvResultExporter(path))
            io = ScriptedIO()
            run_demo(c.resolve(Gradebook), io)
            self.assertTrue(os.path.exists(path))
        out = io.output()
        self.assertNotIn("ПРОШЛО", out)
        self.assertIn("Анна Смирнова: 8.9 из 10", out)


if __name__ == "__main__":
    unittest.main()
