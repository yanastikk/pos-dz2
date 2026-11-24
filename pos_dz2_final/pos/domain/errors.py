class DomainError(ValueError):
    pass


def require_text(text, what):
    if not isinstance(text, str) or text.strip() == "":
        raise DomainError(what + " не может быть пустым")
    return text.strip()


def require_positive(number, what):
    if isinstance(number, bool) or not isinstance(number, (int, float)):
        raise DomainError(what + " должен быть числом")
    if number <= 0:
        raise DomainError(what + " должен быть больше нуля")
    return number


def format_number(number):
    if number == int(number):
        return str(int(number))
    return str(number)
