from .errors import require_text


class Student:
    def __init__(self, student_id, name):
        self._id = student_id
        self._name = require_text(name, "Имя студента")

    @property
    def id(self):
        return self._id

    @property
    def name(self):
        return self._name

    # имя не может быть пустым
    def rename(self, new_name):
        self._name = require_text(new_name, "Имя студента")

    def __eq__(self, other):
        if not isinstance(other, Student):
            return False
        return self._id == other._id

    def __hash__(self):
        return hash(self._id)

    def __str__(self):
        return "№" + str(self._id) + " " + self._name
