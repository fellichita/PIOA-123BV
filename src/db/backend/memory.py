BookRecord = tuple[int, str, str, int, str]

DEFAULT_TABLE_NAME  = "Books"
_TABLES: dict[str, list[BookRecord]] = {DEFAULT_TABLE_NAME: []}


def _validate_table_name(table_name: str) -> str:
    table_name = table_name.strip()
    if table_name == "":
        raise ValueError("Имя таблицы не может быть пустым.")
    return table_name


def _get_table(table_name: str) -> list[BookRecord]:
    normalized_name = _validate_table_name(table_name)

    if normalized_name not in _TABLES:
        raise ValueError(f"Таблица '{normalized_name}' не существует.")
    return _TABLES[normalized_name]


def _validate_record_fields(title: str, author: str, year: int, genre: str) -> BookRecord:
    if year < 0:
        raise ValueError("Поле year не может быть отрицательным.")

    normalized_title = title.strip()
    normalized_author = author.strip()
    normalized_genre = genre.strip()

    if normalized_title == "":
        raise ValueError("Поле title не может быть пустым.")

    if normalized_author == "":
        raise ValueError("Поле author не может быть пустым.")

    if normalized_genre == "":
        raise ValueError("Поле genre не может быть пустым.")

    return (0, normalized_title, normalized_author, year, normalized_genre)


def create_table(table_name: str) -> str:
    normalized_name = _validate_table_name(table_name)
    if normalized_name in _TABLES:
        raise ValueError(f"Таблица '{normalized_name}' уже существует.")

    _TABLES[normalized_name] = []
    return normalized_name


def list_tables() -> list[str]:
    return list(_TABLES.keys())





def create_record(
    table_name: str,
    book_id: int,
    title: str,
    author: str,
    year: int,
    genre: str,
) -> BookRecord:
    table = _get_table(table_name)

    if any(record[0] == book_id for record in table):
        raise ValueError(f"Запись с id={book_id} уже существует в таблице '{table_name}'.")

    _, normalized_title, normalized_author, normalized_year, normalized_genre = _validate_record_fields(
        title,
        author,
        year,
        genre,
    )

    new_record: BookRecord = (
        book_id,
        normalized_title,
        normalized_author,
        normalized_year,
        normalized_genre,
    )
    table.append(new_record)
    return new_record


def select_record(
    table_name: str,
    book_id: int | None = None,
    title: str | None = None,
    author: str | None = None,
    year: int | None = None,
    genre: str | None = None,
) -> list[BookRecord]:
    table = _get_table(table_name)

    if (
        book_id is None
        and title is None
        and author is None
        and year is None
        and genre is None
    ):
        return table.copy()

    found = []

    for record in table:
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
        found.append(record)

    return found


def update_record(
    table_name: str,
    book_id: int,
    title: str | None = None,
    author: str | None = None,
    year: int | None = None,
    genre: str | None = None,
) -> BookRecord:
    table = _get_table(table_name)

    for index, record in enumerate(table):
        if record[0] != book_id:
            continue

        new_title = record[1] if title is None else title
        new_author = record[2] if author is None else author
        new_year = record[3] if year is None else year
        new_genre = record[4] if genre is None else genre

        _, normalized_title, normalized_author, normalized_year, normalized_genre = _validate_record_fields(
            new_title,
            new_author,
            new_year,
            new_genre,
        )

        updated_record: BookRecord = (
            book_id,
            normalized_title,
            normalized_author,
            normalized_year,
            normalized_genre,
        )
        table[index] = updated_record
        return updated_record

    raise ValueError(f"Запись с id={book_id} не найдена в таблице '{table_name}'.")


def delete_record(table_name: str, book_id: int) -> BookRecord:
    table = _get_table(table_name)

    for index, record in enumerate(table):
        if record[0] == book_id:
            return table.pop(index)


    raise ValueError(f"Запись с id={book_id} не найдена в таблице '{table_name}'.")
