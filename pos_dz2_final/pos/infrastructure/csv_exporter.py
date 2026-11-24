import csv

from ..application import ResultExporter


class CsvResultExporter(ResultExporter):
    HEADER = ["Номер", "Студент", "Итог из 10", "Процент", "Оценено критериев", "Правило итога"]

    def __init__(self, path):
        self._path = path

    def export(self, grades):

        # utf-8-sig чтобы excel показал русские буквы
        with open(self._path, "w", encoding="utf-8-sig", newline="") as file:
            # точка с запятой, русский excel так ждёт
            writer = csv.writer(file, delimiter=";")
            writer.writerow(self.HEADER)
            for grade in grades:
                writer.writerow(self._to_row(grade))
        return self._path

    def _to_row(self, grade):
        return [
            grade.student.id,
            grade.student.name,
            grade.points,
            grade.percent,
            str(grade.graded_count) + " из " + str(grade.total_count),
            grade.strategy_name,
        ]
