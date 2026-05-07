class DatabaseError(Exception):
    """Базовый класс ошибок базы данных."""


class InvalidFieldError(DatabaseError):
    """Ошибка некорректного значения поля."""


class DuplicateIDError(DatabaseError):
    """Ошибка дублирующегося идентификатора."""


class RecordNotFoundError(DatabaseError):
    """Ошибка отсутствующей записи."""


class TableNotFoundError(DatabaseError):
    """Ошибка отсутствующей таблицы."""
