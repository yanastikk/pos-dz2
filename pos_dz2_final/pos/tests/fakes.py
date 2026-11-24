from pos.application import Gradebook, ResultExporter
from pos.domain import AllCriteriaStrategy, EvaluationFactory, FinalGradeCalculator
from pos.infrastructure import (
    ConsoleIO,
    InMemoryEvaluationRepository,
    InMemoryRubricRepository,
    InMemoryStudentRepository,
)


class ScriptedIO(ConsoleIO):
    def __init__(self, inputs=None):
        if inputs is None:
            inputs = []
        self._inputs = list(inputs)
        self.lines = []

    def read(self, prompt):
        if len(self._inputs) == 0:
            raise EOFError
        return self._inputs.pop(0)

    def write(self, text=""):
        self.lines.append(text)

    def output(self):
        return "\n".join(self.lines)


class FakeExporter(ResultExporter):
    def __init__(self):
        self.exported = None

    def export(self, grades):
        self.exported = grades
        return "память"


def make_gradebook(strategy=None, exporter=None):
    if strategy is None:
        strategy = AllCriteriaStrategy()
    if exporter is None:
        exporter = FakeExporter()
    return Gradebook(
        InMemoryStudentRepository(),
        InMemoryRubricRepository(),
        InMemoryEvaluationRepository(),
        EvaluationFactory(),
        FinalGradeCalculator(strategy),
        exporter,
    )
