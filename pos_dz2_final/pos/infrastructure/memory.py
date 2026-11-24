from ..domain import EvaluationRepository, Rubric, RubricRepository, StudentRepository


class InMemoryStudentRepository(StudentRepository):
    def __init__(self):
        self._items = {}
        self._last_id = 0

    # номер занимаем только при добавлении
    def next_id(self):
        return self._last_id + 1

    def add(self, student):
        self._items[student.id] = student
        self._last_id = max(self._last_id, student.id)

    def get(self, student_id):
        return self._items.get(student_id)

    def all(self):
        return list(self._items.values())


class InMemoryRubricRepository(RubricRepository):
    def __init__(self):
        self._rubric = Rubric()

    def get(self):
        return self._rubric

    def save(self, rubric):
        self._rubric = rubric


class InMemoryEvaluationRepository(EvaluationRepository):
    def __init__(self):
        self._items = {}
        self._last_id = 0

    def next_id(self):
        return self._last_id + 1

    def add(self, evaluation):
        self._items[evaluation.id] = evaluation
        self._last_id = max(self._last_id, evaluation.id)

    def get(self, evaluation_id):
        return self._items.get(evaluation_id)

    def remove(self, evaluation_id):
        if evaluation_id in self._items:
            del self._items[evaluation_id]

    def for_student(self, student_id):
        result = []
        for evaluation in self._items.values():
            if evaluation.student_id == student_id:
                result.append(evaluation)
        return result

    def all(self):
        return list(self._items.values())
