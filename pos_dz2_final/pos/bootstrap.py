from .application import Gradebook, ResultExporter
from .di import Container
from .domain import (
    AllCriteriaStrategy,
    EvaluationFactory,
    EvaluationRepository,
    FinalGradeCalculator,
    GradingStrategy,
    RubricRepository,
    StudentRepository,
)
from .infrastructure import (
    ConsoleApp,
    ConsoleIO,
    CsvResultExporter,
    InMemoryEvaluationRepository,
    InMemoryRubricRepository,
    InMemoryStudentRepository,
    StdConsoleIO,
)

EXPORT_PATH = "pos_itogi.csv"


def build_container():
    c = Container()

    c.register_singleton(StudentRepository, lambda _: InMemoryStudentRepository())
    c.register_singleton(RubricRepository, lambda _: InMemoryRubricRepository())
    c.register_singleton(EvaluationRepository, lambda _: InMemoryEvaluationRepository())

    c.register_singleton(EvaluationFactory, lambda _: EvaluationFactory())
    # правило итога меняется здесь
    c.register_singleton(GradingStrategy, lambda _: AllCriteriaStrategy())
    c.register_singleton(FinalGradeCalculator, lambda c: FinalGradeCalculator(c.resolve(GradingStrategy)))

    # экспорт в csv меняется здесь
    c.register_singleton(ResultExporter, lambda _: CsvResultExporter(EXPORT_PATH))

    c.register_singleton(
        Gradebook,
        lambda c: Gradebook(
            c.resolve(StudentRepository),
            c.resolve(RubricRepository),
            c.resolve(EvaluationRepository),
            c.resolve(EvaluationFactory),
            c.resolve(FinalGradeCalculator),
            c.resolve(ResultExporter),
        ),
    )

    c.register_singleton(ConsoleIO, lambda _: StdConsoleIO())
    # transient, каждый раз новый объект
    c.register_transient(ConsoleApp, lambda c: ConsoleApp(c.resolve(Gradebook), c.resolve(ConsoleIO)))
    return c
