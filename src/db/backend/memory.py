from .errors import DuplicateIDError, InvalidFieldError, RecordNotFoundError, TableNotFoundError

BookRecord = tuple[int, str, str, int, str]

DEFAULT_TABLE_NAME = "Books"


class BookTable:
    def __init__(self, name: str) -> None:
        self.name = self._validate_table_name(name)
        self._records: list[BookRecord] = []

    @staticmethod
    def _validate_table_name(table_name: str) -> str:
        normalized_name = table_name.strip()
        if normalized_name == "":
            raise InvalidFieldError("Имя таблицы не может быть пустым.")
        return normalized_name

    @staticmethod
    def _validate_record_fields(
        title: str,
        author: str,
        year: int,
        genre: str,
    ) -> tuple[str, str, int, str]:
        if year < 0:
            raise InvalidFieldError("Поле year не может быть отрицательным.")

        normalized_title = title.strip()
        normalized_author = author.strip()
        normalized_genre = genre.strip()

        if normalized_title == "":
            raise InvalidFieldError("Поле title не может быть пустым.")
        if normalized_author == "":
            raise InvalidFieldError("Поле author не может быть пустым.")
        if normalized_genre == "":
            raise InvalidFieldError("Поле genre не может быть пустым.")

        return normalized_title, normalized_author, year, normalized_genre

    def create_record(
        self,
        book_id: int,
        title: str,
        author: str,
        year: int,
        genre: str,
    ) -> BookRecord:
        if any(record[0] == book_id for record in self._records):
            raise DuplicateIDError(f"Запись с id={book_id} уже существует.")

        normalized_title, normalized_author, normalized_year, normalized_genre = (
            self._validate_record_fields(title, author, year, genre)
        )

        new_record: BookRecord = (
            book_id,
            normalized_title,
            normalized_author,
            normalized_year,
            normalized_genre,
        )
        self._records.append(new_record)
        return new_record

    def select_record(
        self,
        book_id: int | None = None,
        title: str | None = None,
        author: str | None = None,
        year: int | None = None,
        genre: str | None = None,
    ) -> list[BookRecord]:
        if (
            book_id is None
            and title is None
            and author is None
            and year is None
            and genre is None
        ):
            return self._records.copy()

        result: list[BookRecord] = []
        for record in self._records:
            if book_id is not None and record[0] != book_id:
                continue
            if title is not None and record[1] != title:
                continue
            if author is not None and record[2] != author:
                continue
            if year is not None and record[3] != year:
                continue
            if genre is not None and record[4] != genre:
                continue
            result.append(record)
        return result

    def update_record(
        self,
        book_id: int,
        title: str | None = None,
        author: str | None = None,
        year: int | None = None,
        genre: str | None = None,
    ) -> BookRecord:
        for index, record in enumerate(self._records):
            if record[0] != book_id:
                continue

            new_title = record[1] if title is None else title
            new_author = record[2] if author is None else author
            new_year = record[3] if year is None else year
            new_genre = record[4] if genre is None else genre

            normalized_title, normalized_author, normalized_year, normalized_genre = (
                self._validate_record_fields(new_title, new_author, new_year, new_genre)
            )

            updated_record: BookRecord = (
                book_id,
                normalized_title,
                normalized_author,
                normalized_year,
                normalized_genre,
            )
            self._records[index] = updated_record
            return updated_record

        raise RecordNotFoundError(f"Запись с id={book_id} не найдена.")

    def delete_record(self, book_id: int) -> BookRecord:
        for index, record in enumerate(self._records):
            if record[0] == book_id:
                return self._records.pop(index)
        raise RecordNotFoundError(f"Запись с id={book_id} не найдена.")


class MemoryDatabase:
    def __init__(self) -> None:
        self._tables: dict[str, BookTable] = {}
        self.create_table(DEFAULT_TABLE_NAME)

    def create_table(self, table_name: str) -> str:
        normalized_name = BookTable._validate_table_name(table_name)
        if normalized_name in self._tables:
            raise InvalidFieldError(f"Таблица '{normalized_name}' уже существует.")

        self._tables[normalized_name] = BookTable(normalized_name)
        return normalized_name

    def list_tables(self) -> list[str]:
        return list(self._tables.keys())

    def get_table(self, table_name: str) -> BookTable:
        normalized_name = BookTable._validate_table_name(table_name)
        if normalized_name not in self._tables:
            raise TableNotFoundError(f"Таблица '{normalized_name}' не существует.")
        return self._tables[normalized_name]
