from .application import ApplicationError
from .domain import DomainError


def run_demo(gradebook, io):
    io.write("=== ПОС - демонстрация ===")

    io.write()
    io.write("--- 1. Студенты ---")
    anya = gradebook.add_student("Анна Смирнова")
    boris = gradebook.add_student("Борис Иванов")
    vera = gradebook.add_student("Вера Ким")
    for student in gradebook.students():
        io.write("  " + str(student))

    io.write()
    io.write("--- 2. Рубрикатор ---")
    code = gradebook.add_criterion("Код и архитектура", 10, 0.5)
    tests = gradebook.add_criterion("Тесты", 5, 0.2)
    defense = gradebook.add_criterion("Защита", 10, 0.3)
    for criterion in gradebook.criteria():
        io.write("  " + str(criterion))

    io.write()
    io.write("--- 3. Оценки ---")
    gradebook.put_evaluation(anya.id, code.id, 9, "чистые слои")
    gradebook.put_evaluation(anya.id, tests.id, 5)
    gradebook.put_evaluation(anya.id, defense.id, 8)
    gradebook.put_evaluation(boris.id, code.id, 6)
    boris_tests = gradebook.put_evaluation(boris.id, tests.id, 2, "мало тестов")
    gradebook.put_evaluation(vera.id, code.id, 10)
    gradebook.put_evaluation(vera.id, tests.id, 4)
    io.write("  выставлено оценок: 7 (у Веры пока нет оценки за защиту)")

    io.write()
    io.write("--- 4. Правила домена не дают ошибиться ---")
    # попытки сломать правила, каждая должна дать отказ
    _try(io, "12 из 10 за защиту", lambda: gradebook.put_evaluation(boris.id, defense.id, 12))
    _try(io, "оценка по критерию №99", lambda: gradebook.put_evaluation(boris.id, 99, 5))
    _try(io, "вторая оценка за тот же критерий", lambda: gradebook.put_evaluation(anya.id, code.id, 7))
    _try(io, "исправить на -1", lambda: gradebook.correct_evaluation(boris_tests.id, -1))
    _try(io, "критерий с весом 0", lambda: gradebook.add_criterion("Посещаемость", 10, 0))

    io.write()
    io.write("--- 5. Исправление и отмена ---")
    gradebook.correct_evaluation(boris_tests.id, 4, "досдал тесты")
    io.write("  Борису исправили тесты: 2/5 -> 4/5")
    extra = gradebook.put_evaluation(boris.id, defense.id, 3)
    gradebook.cancel_evaluation(extra.id)
    io.write("  Борису поставили 3 за защиту и отменили (оценка №" + str(extra.id) + ")")

    io.write()
    io.write("--- 6. Итоги (нет оценки = 0) ---")
    for grade in gradebook.final_grades():
        io.write("  " + str(grade))

    io.write()
    io.write("--- 7. Экспорт ---")
    path = gradebook.export_results()
    io.write("  Итоги выгружены в файл " + path)


def _try(io, what, action):
    try:
        action()
        io.write("  " + what + ": ПРОШЛО (а не должно было!)")
    except (DomainError, ApplicationError) as error:
        io.write("  " + what + ": отказ - " + str(error))
