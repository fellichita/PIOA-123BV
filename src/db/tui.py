from .backend.errors import DatabaseError
from .backend.memory import DEFAULT_TABLE_NAME, MemoryDatabase


def _print_menu(current_table: str) -> None:
    print(f"\n=== База книг | Текущая таблица: {current_table} ===")
    print("1. Создать таблицу")
    print("2. Выбрать таблицу")
    print("3. Показать все таблицы")
    print("4. Добавить запись")
    print("5. Показать все записи")
    print("6. Найти записи по фильтру")
    print("7. Обновить запись")
    print("8. Удалить запись")
    print("0. Выход")


def _read_int(prompt: str) -> int:
    while True:
        raw = input(prompt).strip()
        try:
            return int(raw)
        except ValueError:
            print("Ошибка: введите целое число.")


def _read_optional_int(prompt: str) -> int | None:
    while True:
        raw = input(prompt).strip()
        if raw == "":
            return None
        try:
            return int(raw)
        except ValueError:
            print("Ошибка: введите целое число или оставьте поле пустым.")


def _print_records(records: list[tuple[int, str, str, int, str]]) -> None:
    if not records:
        print("Записи не найдены.")
        return

    for record in records:
        print(record)


def _create_table(database: MemoryDatabase) -> str | None:
    print("\nСоздание таблицы")
    table_name = input("Имя таблицы: ").strip()

    try:
        created_table = database.create_table(table_name)
        print(f"Таблица '{created_table}' создана.")
        return created_table
    except DatabaseError as error:
        print(f"Ошибка: {error}")
        return None


def _select_table(database: MemoryDatabase) -> str | None:
    print("\nДоступные таблицы:")
    for table_name in database.list_tables():
        print(table_name)

    selected_table = input("Введите имя таблицы: ").strip()
    try:
        database.get_table(selected_table)
        print(f"Текущая таблица изменена на '{selected_table}'.")
        return selected_table
    except DatabaseError as error:
        print(f"Ошибка: {error}")
        return None


def _show_tables(database: MemoryDatabase) -> None:
    print("\nСписок таблиц")
    for table_name in database.list_tables():
        print(table_name)


def _add_book(database: MemoryDatabase, table_name: str) -> None:
    print(f"\nДобавление записи в таблицу '{table_name}'")

    book_id = _read_int("id: ")
    title = input("title: ").strip()
    author = input("author: ").strip()
    year = _read_int("year: ")
    genre = input("genre: ").strip()

    try:
        record = database.get_table(table_name).create_record(
            book_id,
            title,
            author,
            year,
            genre,
        )
        print(f"Запись добавлена: {record}")
    except DatabaseError as error:
        print(f"Ошибка: {error}")


def _show_all_books(database: MemoryDatabase, table_name: str) -> None:
    print(f"\nСписок записей таблицы '{table_name}'")
    try:
        _print_records(database.get_table(table_name).select_record())
    except DatabaseError as error:
        print(f"Ошибка: {error}")


def _find_books_by_filter(database: MemoryDatabase, table_name: str) -> None:
    print(f"\nПоиск в таблице '{table_name}' (Enter = пропустить поле)")

    book_id = _read_optional_int("id: ")
    title = input("title: ").strip() or None
    author = input("author: ").strip() or None
    year = _read_optional_int("year: ")
    genre = input("genre: ").strip() or None

    try:
        records = database.get_table(table_name).select_record(
            book_id=book_id,
            title=title,
            author=author,
            year=year,
            genre=genre,
        )
        _print_records(records)
    except DatabaseError as error:
        print(f"Ошибка: {error}")


def _update_book(database: MemoryDatabase, table_name: str) -> None:
    print(f"\nОбновление записи в таблице '{table_name}'")
    print("Оставьте поле пустым, если не хотите его менять.")

    book_id = _read_int("id записи: ")
    title = input("title: ").strip()
    author = input("author: ").strip()
    year = _read_optional_int("year: ")
    genre = input("genre: ").strip()

    try:
        record = database.get_table(table_name).update_record(
            book_id,
            title=title if title != "" else None,
            author=author if author != "" else None,
            year=year,
            genre=genre if genre != "" else None,
        )
        print(f"Запись обновлена: {record}")
    except DatabaseError as error:
        print(f"Ошибка: {error}")


def _delete_book(database: MemoryDatabase, table_name: str) -> None:
    print(f"\nУдаление записи из таблицы '{table_name}'")
    book_id = _read_int("id записи: ")

    try:
        record = database.get_table(table_name).delete_record(book_id)
        print(f"Запись удалена: {record}")
    except DatabaseError as error:
        print(f"Ошибка: {error}")


def run() -> None:
    database = MemoryDatabase()
    current_table = DEFAULT_TABLE_NAME

    while True:
        _print_menu(current_table)
        action = input("Выберите действие: ").strip()

        if action == "1":
            created_table = _create_table(database)
            if created_table is not None:
                current_table = created_table
        elif action == "2":
            selected_table = _select_table(database)
            if selected_table is not None:
                current_table = selected_table
        elif action == "3":
            _show_tables(database)
        elif action == "4":
            _add_book(database, current_table)
        elif action == "5":
            _show_all_books(database, current_table)
        elif action == "6":
            _find_books_by_filter(database, current_table)
        elif action == "7":
            _update_book(database, current_table)
        elif action == "8":
            _delete_book(database, current_table)
        elif action == "0":
            print("Выход из программы.")
            break
        else:
            print("Неизвестная команда. Повторите ввод.")
