from .backend.memory import DEFAULT_TABLE_NAME, MemoryDatabase


def _print_menu(current_table: str) -> None:
    current_table_label = current_table if current_table else "не выбрана"
    print(f"\n=== База книг | Текущая таблица: {current_table_label} ===")
    print("1. Создать таблицу")
    print("2. Выбрать таблицу")
    print("3. Показать все таблицы")
    print("4. Добавить запись")
    print("5. Показать все записи")
    print("6. Найти записи по фильтру")
    print("7. Обновить запись")
    print("8. Удалить запись")
    print("0. Выход из программы")


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

    for row in records:
        print(row)


def _create_table(database: MemoryDatabase) -> str | None:
    print("\nСоздание таблицы")
    table_name = input("Имя таблицы: ").strip()

    try:
        made_table = database.create_table(table_name)
        print(f"Таблица '{made_table}' создана.")
        return made_table
    except ValueError as error:
        print(f"Ошибка: {error}")
        return None


def _select_table(database: MemoryDatabase) -> str | None:
    tables = database.list_tables()
    if not tables:
        print("\nТаблиц пока нет.")
        return None

    print("\nДоступные таблицы:")
    for table_name in tables:
        print(table_name)

    selected_table = input("Введите имя таблицы: ").strip()
    try:
        database.get_table(selected_table)
        print(f"Текущая таблица изменена на '{selected_table}'.")
        return selected_table
    except ValueError as error:
        print(f"Ошибка: {error}")
        return None


def _show_tables(database: MemoryDatabase) -> None:
    print("\nСписок таблиц")

    tables = database.list_tables()
    if not tables:
        print("Таблиц пока нет.")
        return

    for table_name in tables:
        print(table_name)


def _ensure_table_selected(table_name: str) -> bool:
    if table_name:
        return True

    print("Ошибка: сначала создайте или выберите таблицу.")
    return False


def _add_book(database: MemoryDatabase, table_name: str) -> None:
    if not _ensure_table_selected(table_name):
        return

    print(f"\nДобавление записи в таблицу '{table_name}'")

    book_id = _read_int("id: ")
    title = input("title: ").strip()
    author = input("author: ").strip()
    year = _read_int("year: ")
    genre = input("genre: ").strip()

    try:
        record = database.get_table(table_name).create_record(book_id, title, author, year, genre)
        print(f"Запись добавлена: {record}")
    except ValueError as error:
        print(f"Ошибка: {error}")


def _show_all_books(database: MemoryDatabase, table_name: str) -> None:
    if not _ensure_table_selected(table_name):
        return

    print(f"\nСписок записей таблицы '{table_name}'")
    try:
        _print_records(database.get_table(table_name).select_record())
    except ValueError as error:
        print(f"Ошибка: {error}")


def _find_books_by_filter(database: MemoryDatabase, table_name: str) -> None:
    if not _ensure_table_selected(table_name):
        return

    print(f"\nПоиск в таблице '{table_name}' (Enter = пропустить поле)")

    book_id = _read_optional_int("id: ")
    title = input("title: ").strip() or None
    author = input("author: ").strip() or None
    year = _read_optional_int("year: ")
    genre = input("genre: ").strip() or None

    try:
        result = database.get_table(table_name).select_record(
            book_id=book_id,
            title=title,
            author=author,
            year=year,
            genre=genre,
        )
        _print_records(result)
    except ValueError as error:
        print(f"Ошибка: {error}")


def _update_book(database: MemoryDatabase, table_name: str) -> None:
    if not _ensure_table_selected(table_name):
        return

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
    except ValueError as error:
        print(f"Ошибка: {error}")


def _delete_book(database: MemoryDatabase, table_name: str) -> None:
    if not _ensure_table_selected(table_name):
        return

    print(f"\nУдаление записи из таблицы '{table_name}'")
    book_id = _read_int("id записи: ")

    try:
        record = database.get_table(table_name).delete_record(book_id)
        print(f"Запись удалена: {record}")
    except ValueError as error:
        print(f"Ошибка: {error}")


def run() -> None:
    database = MemoryDatabase()
    current_table = DEFAULT_TABLE_NAME

    while True:
        _print_menu(current_table)
        menu_choice = input("Выберите действие: ").strip()

        if menu_choice == "1":
            made_table = _create_table(database)
            if made_table is not None:
                current_table = made_table
        elif menu_choice == "2":
            selected_table = _select_table(database)
            if selected_table is not None:
                current_table = selected_table
        elif menu_choice == "3":
            _show_tables(database)
        elif menu_choice == "4":
            _add_book(database, current_table)
        elif menu_choice == "5":
            _show_all_books(database, current_table)
        elif menu_choice == "6":
            _find_books_by_filter(database, current_table)
        elif menu_choice == "7":
            _update_book(database, current_table)
        elif menu_choice == "8":
            _delete_book(database, current_table)
        elif menu_choice == "0":
            print("Выход из программы.")
            break
        else:
            print("Неизвестная команда. Повторите ввод.")
