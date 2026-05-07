from .backend.memory import (
    DEFAULT_TABLE_NAME,
    create_record,
    create_table,
    delete_record,
    list_tables,
    select_record,
    update_record,
)


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


def _create_table() -> str | None:
    print("\nСоздание таблицы")
    table_name = input("Имя таблицы: ").strip()

    try:
        created_table = create_table(table_name)
        print(f"Таблица '{created_table}' создана.")
        return created_table
    except ValueError as error:
        print(f"Ошибка: {error}")
        return None


def _select_table() -> str | None:
    tables = list_tables()
    if not tables:
        print("\nТаблиц пока нет.")
        return None

    print("\nДоступные таблицы:")
    for table_name in tables:
        print(table_name)

    selected_table = input("Введите имя таблицы: ").strip()
    try:
        select_record(selected_table)
        print(f"Текущая таблица изменена на '{selected_table}'.")
        return selected_table
    except ValueError as error:
        print(f"Ошибка: {error}")
        return None


def _show_tables() -> None:
    print("\nСписок таблиц")

    tables = list_tables()
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


def _add_book(table_name: str) -> None:
    if not _ensure_table_selected(table_name):
        return

    print(f"\nДобавление записи в таблицу '{table_name}'")

    book_id = _read_int("id: ")
    title = input("title: ").strip()
    author = input("author: ").strip()
    year = _read_int("year: ")
    genre = input("genre: ").strip()

    try:
        record = create_record(table_name, book_id, title, author, year, genre)
        print(f"Запись добавлена: {record}")
    except ValueError as error:
        print(f"Ошибка: {error}")


def _show_all_books(table_name: str) -> None:
    if not _ensure_table_selected(table_name):
        return

    print(f"\nСписок записей таблицы '{table_name}'")
    try:
        _print_records(select_record(table_name))
    except ValueError as error:
        print(f"Ошибка: {error}")


def _find_books_by_filter(table_name: str) -> None:
    if not _ensure_table_selected(table_name):
        return

    print(f"\nПоиск в таблице '{table_name}' (Enter = пропустить поле)")

    book_id = _read_optional_int("id: ")
    title = input("title: ").strip() or None
    author = input("author: ").strip() or None
    year = _read_optional_int("year: ")
    genre = input("genre: ").strip() or None

    try:
        result = select_record(
            table_name,
            book_id=book_id,
            title=title,
            author=author,
            year=year,
            genre=genre,
        )
        _print_records(result)
    except ValueError as error:
        print(f"Ошибка: {error}")


def _update_book(table_name: str) -> None:
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
        record = update_record(
            table_name,
            book_id,
            title=title if title != "" else None,
            author=author if author != "" else None,
            year=year,
            genre=genre if genre != "" else None,
        )
        print(f"Запись обновлена: {record}")
    except ValueError as error:
        print(f"Ошибка: {error}")


def _delete_book(table_name: str) -> None:
    if not _ensure_table_selected(table_name):
        return

    print(f"\nУдаление записи из таблицы '{table_name}'")
    book_id = _read_int("id записи: ")

    try:
        record = delete_record(table_name, book_id)
        print(f"Запись удалена: {record}")
    except ValueError as error:
        print(f"Ошибка: {error}")


def run() -> None:
    current_table = DEFAULT_TABLE_NAME

    while True:
        _print_menu(current_table)
        cmd = input("Выберите действие: ").strip()

        if cmd == "1":
            created_table = _create_table()
            if created_table is not None:
                current_table = created_table
        elif cmd == "2":
            selected_table = _select_table()
            if selected_table is not None:
                current_table = selected_table
        elif cmd == "3":
            _show_tables()
        elif cmd == "4":
            _add_book(current_table)
        elif cmd == "5":
            _show_all_books(current_table)
        elif cmd == "6":
            _find_books_by_filter(current_table)
        elif cmd == "7":
            _update_book(current_table)
        elif cmd == "8":
            _delete_book(current_table)
        elif cmd == "0":
            print("Выход из программы.")
            break
        else:
            print("Неизвестная команда. Повторите ввод.")
