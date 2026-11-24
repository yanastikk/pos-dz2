from abc import ABC, abstractmethod


# домен не знает, где лежат данные
class StudentRepository(ABC):
    @abstractmethod
    def next_id(self):
        pass

    @abstractmethod
    def add(self, student):
        pass

    @abstractmethod
    def get(self, student_id):
        pass

    @abstractmethod
    def all(self):
        pass


class RubricRepository(ABC):
    @abstractmethod
    def get(self):
        pass

    @abstractmethod
    def save(self, rubric):
        pass


class EvaluationRepository(ABC):
    @abstractmethod
    def next_id(self):
        pass

    @abstractmethod
    def add(self, evaluation):
        pass

    @abstractmethod
    def get(self, evaluation_id):
        pass

    @abstractmethod
    def remove(self, evaluation_id):
        pass

    @abstractmethod
    def for_student(self, student_id):
        pass

    @abstractmethod
    def all(self):
        pass
