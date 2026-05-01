from .errors import DuplicateIDError, InvalidFieldError, RecordNotFoundError, TableNotFoundError

BookRecord = tuple[int, str, str, int, str]

DEFAULT_TABLE_NAME = "Books"


def _normalize_table_name(table_name: str) -> str:
    clean_name = table_name.strip()
    if clean_name == "":
        raise InvalidFieldError("Имя таблицы не может быть пустым.")
    return clean_name


def _normalize_text_field(value: str, field_name: str) -> str:
    val = value.strip()
    if val == "":
        raise InvalidFieldError(f"Поле {field_name} не может быть пустым.")
    return val


def _normalize_book_data(title: str, author: str, year: int, genre: str) -> tuple[str, str, int, str]:
    if year < 0:
        raise InvalidFieldError("Поле year не может быть отрицательным.")

    clean_title = _normalize_text_field(title, "title")
    clean_author = _normalize_text_field(author, "author")
    clean_genre = _normalize_text_field(genre, "genre")

    return clean_title, clean_author, year, clean_genre


class BookTable:
    def __init__(self, table_name: str) -> None:
        self.name = _normalize_table_name(table_name)
        self._records: list[BookRecord] = []

    def create_record(
        self,
        book_id: int,
        title: str,
        author: str,
        year: int,
        genre: str,
    ) -> BookRecord:
        if any(row[0] == book_id for row in self._records):
            raise DuplicateIDError(f"Запись с id={book_id} уже существует.")

        clean_title, clean_author, clean_year, clean_genre = _normalize_book_data(title, author, year, genre)
        fresh_record: BookRecord = (book_id, clean_title, clean_author, clean_year, clean_genre)
        self._records.append(fresh_record)
        return fresh_record

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

        found_rows: list[BookRecord] = []
        for row in self._records:
            if book_id is not None and row[0] != book_id:
                continue
            if title is not None and row[1] != title:
                continue
            if author is not None and row[2] != author:
                continue
            if year is not None and row[3] != year:
                continue
            if genre is not None and row[4] != genre:
                continue
            found_rows.append(row)

        return found_rows

    def update_record(
        self,
        book_id: int,
        title: str | None = None,
        author: str | None = None,
        year: int | None = None,
        genre: str | None = None,
    ) -> BookRecord:
        for pos, row in enumerate(self._records):
            if row[0] != book_id:
                continue

            next_title = row[1] if title is None else title
            next_author = row[2] if author is None else author
            next_year = row[3] if year is None else year
            next_genre = row[4] if genre is None else genre

            clean_title, clean_author, clean_year, clean_genre = _normalize_book_data(
                next_title,
                next_author,
                next_year,
                next_genre,
            )
            updated_row: BookRecord = (book_id, clean_title, clean_author, clean_year, clean_genre)
            self._records[pos] = updated_row
            return updated_row

        raise RecordNotFoundError(f"Запись с id={book_id} не найдена.")

    def delete_record(self, book_id: int) -> BookRecord:
        for pos, row in enumerate(self._records):
            if row[0] == book_id:
                return self._records.pop(pos)

        raise RecordNotFoundError(f"Запись с id={book_id} не найдена.")


class MemoryDatabase:
    def __init__(self) -> None:
        self._tables: dict[str, BookTable] = {DEFAULT_TABLE_NAME: BookTable(DEFAULT_TABLE_NAME)}

    def create_table(self, table_name: str) -> str:
        clean_name = _normalize_table_name(table_name)
        if clean_name in self._tables:
            raise InvalidFieldError(f"Таблица '{clean_name}' уже существует.")

        self._tables[clean_name] = BookTable(clean_name)
        return clean_name

    def list_tables(self) -> list[str]:
        return list(self._tables.keys())

    def get_table(self, table_name: str) -> BookTable:
        clean_name = _normalize_table_name(table_name)
        table = self._tables.get(clean_name)
        if table is None:
            raise TableNotFoundError(f"Таблица '{clean_name}' не существует.")
        return table
