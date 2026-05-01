import unittest
from unittest.mock import patch

from src.db import __main__
from src.db.backend.errors import (
    DuplicateIDError,
    InvalidFieldError,
    RecordNotFoundError,
    TableNotFoundError,
)
from src.db.backend.memory import BookTable, MemoryDatabase
from src.db.tui import (
    _add_book,
    _create_table,
    _delete_book,
    _find_books_by_filter,
    _print_records,
    _read_int,
    _read_optional_int,
    _select_table,
    _show_all_books,
    _show_tables,
    _update_book,
    run,
)


class TestMemoryDatabase(unittest.TestCase):
    def setUp(self) -> None:
        self.database = MemoryDatabase()
        self.table = self.database.get_table("Books")

    def test_default_table_exists(self) -> None:
        self.assertEqual(self.database.list_tables(), ["Books"])

    def test_create_table(self) -> None:
        table_name = self.database.create_table(" Library ")
        self.assertEqual(table_name, "Library")
        self.assertIn("Library", self.database.list_tables())

    def test_create_table_with_empty_name_raises_error(self) -> None:
        with self.assertRaises(InvalidFieldError):
            self.database.create_table("   ")

    def test_create_duplicate_table_raises_error(self) -> None:
        with self.assertRaises(InvalidFieldError):
            self.database.create_table("Books")

    def test_get_missing_table_raises_error(self) -> None:
        with self.assertRaises(TableNotFoundError):
            self.database.get_table("Unknown")

    def test_book_table_name_is_normalized(self) -> None:
        table = BookTable(" Shelf ")
        self.assertEqual(table.name, "Shelf")

    def test_create_record(self) -> None:
        record = self.table.create_record(1, " Clean Code ", " Robert Martin ", 2008, " IT ")
        self.assertEqual(record, (1, "Clean Code", "Robert Martin", 2008, "IT"))

    def test_create_record_with_invalid_fields(self) -> None:
        cases = [
            (1, "", "Author", 2000, "Genre"),
            (1, "Title", "", 2000, "Genre"),
            (1, "Title", "Author", -1, "Genre"),
            (1, "Title", "Author", 2000, ""),
        ]

        for case in cases:
            with self.subTest(case=case):
                with self.assertRaises(InvalidFieldError):
                    self.table.create_record(*case)

    def test_create_record_duplicate_id(self) -> None:
        self.table.create_record(1, "Book 1", "Author 1", 2001, "Drama")

        with self.assertRaises(DuplicateIDError):
            self.table.create_record(1, "Book 2", "Author 2", 2002, "Novel")

    def test_select_record_without_filters(self) -> None:
        self.table.create_record(1, "Book 1", "Author 1", 2001, "Drama")
        self.table.create_record(2, "Book 2", "Author 2", 2002, "Novel")

        self.assertEqual(
            self.table.select_record(),
            [
                (1, "Book 1", "Author 1", 2001, "Drama"),
                (2, "Book 2", "Author 2", 2002, "Novel"),
            ],
        )

    def test_select_record_with_filters(self) -> None:
        test_data = [
            (1, "Book 1", "Author 1", 2001, "Drama"),
            (2, "Book 2", "Author 2", 2002, "Novel"),
            (3, "Book 3", "Author 1", 2003, "Drama"),
        ]
        for record in test_data:
            self.table.create_record(*record)

        self.assertEqual(self.table.select_record(book_id=1), [test_data[0]])
        self.assertEqual(self.table.select_record(title="Book 2"), [test_data[1]])
        self.assertEqual(self.table.select_record(author="Author 1"), [test_data[0], test_data[2]])
        self.assertEqual(self.table.select_record(year=2003), [test_data[2]])
        self.assertEqual(self.table.select_record(genre="Drama"), [test_data[0], test_data[2]])

    def test_update_record(self) -> None:
        self.table.create_record(1, "Old", "Author", 2001, "Drama")

        updated = self.table.update_record(1, title=" New Title ", genre=" Novel ")

        self.assertEqual(updated, (1, "New Title", "Author", 2001, "Novel"))

    def test_update_missing_record_raises_error(self) -> None:
        with self.assertRaises(RecordNotFoundError):
            self.table.update_record(1, title="New")

    def test_delete_record(self) -> None:
        self.table.create_record(1, "Book", "Author", 2001, "Drama")

        deleted = self.table.delete_record(1)

        self.assertEqual(deleted, (1, "Book", "Author", 2001, "Drama"))
        self.assertEqual(self.table.select_record(), [])

    def test_delete_missing_record_raises_error(self) -> None:
        with self.assertRaises(RecordNotFoundError):
            self.table.delete_record(1)


class TestTuiHelpers(unittest.TestCase):
    def setUp(self) -> None:
        self.database = MemoryDatabase()

    @patch("builtins.input", side_effect=["abc", "5"])
    @patch("builtins.print")
    def test_read_int_retries_until_valid(self, mock_print, _mock_input) -> None:
        result = _read_int("id: ")

        self.assertEqual(result, 5)
        mock_print.assert_any_call("Ошибка: введите целое число.")

    @patch("builtins.input", side_effect=["abc", ""])
    @patch("builtins.print")
    def test_read_optional_int_returns_none_for_empty_value(self, mock_print, _mock_input) -> None:
        result = _read_optional_int("year: ")

        self.assertIsNone(result)
        mock_print.assert_any_call("Ошибка: введите целое число или оставьте поле пустым.")

    @patch("src.db.__main__.run")
    def test_main_calls_run(self, mock_run) -> None:
        __main__.main()
        mock_run.assert_called_once_with()

    @patch("builtins.input", return_value="Library")
    @patch("builtins.print")
    def test_create_table_helper(self, mock_print, _mock_input) -> None:
        result = _create_table(self.database)

        self.assertEqual(result, "Library")
        mock_print.assert_any_call("Таблица 'Library' создана.")

    @patch("builtins.input", return_value="Books")
    @patch("builtins.print")
    def test_select_table_helper(self, mock_print, _mock_input) -> None:
        result = _select_table(self.database)

        self.assertEqual(result, "Books")
        mock_print.assert_any_call("Текущая таблица изменена на 'Books'.")

    @patch("builtins.print")
    def test_show_tables_prints_table_names(self, mock_print) -> None:
        self.database.create_table("Library")

        _show_tables(self.database)

        mock_print.assert_any_call("Books")
        mock_print.assert_any_call("Library")

    @patch("builtins.input", side_effect=["1", "Book", "Author", "2024", "Novel"])
    @patch("builtins.print")
    def test_add_book_helper(self, mock_print, _mock_input) -> None:
        _add_book(self.database, "Books")

        self.assertEqual(
            self.database.get_table("Books").select_record(),
            [(1, "Book", "Author", 2024, "Novel")],
        )
        mock_print.assert_any_call("Запись добавлена: (1, 'Book', 'Author', 2024, 'Novel')")

    @patch("builtins.print")
    def test_show_all_books_helper(self, mock_print) -> None:
        self.database.get_table("Books").create_record(1, "Book", "Author", 2024, "Novel")

        _show_all_books(self.database, "Books")

        mock_print.assert_any_call((1, "Book", "Author", 2024, "Novel"))

    @patch("builtins.input", side_effect=["", "", "Author", "", ""])
    @patch("builtins.print")
    def test_find_books_by_filter_helper(self, mock_print, _mock_input) -> None:
        table = self.database.get_table("Books")
        table.create_record(1, "Book 1", "Author", 2020, "Drama")
        table.create_record(2, "Book 2", "Other", 2021, "Novel")

        _find_books_by_filter(self.database, "Books")

        mock_print.assert_any_call((1, "Book 1", "Author", 2020, "Drama"))

    @patch("builtins.input", side_effect=["1", "New Book", "", "", ""])
    @patch("builtins.print")
    def test_update_book_helper(self, mock_print, _mock_input) -> None:
        self.database.get_table("Books").create_record(1, "Old Book", "Author", 2024, "Novel")

        _update_book(self.database, "Books")

        self.assertEqual(
            self.database.get_table("Books").select_record(book_id=1),
            [(1, "New Book", "Author", 2024, "Novel")],
        )
        mock_print.assert_any_call("Запись обновлена: (1, 'New Book', 'Author', 2024, 'Novel')")

    @patch("builtins.input", side_effect=["1"])
    @patch("builtins.print")
    def test_delete_book_helper(self, mock_print, _mock_input) -> None:
        self.database.get_table("Books").create_record(1, "Book", "Author", 2024, "Novel")

        _delete_book(self.database, "Books")

        self.assertEqual(self.database.get_table("Books").select_record(), [])
        mock_print.assert_any_call("Запись удалена: (1, 'Book', 'Author', 2024, 'Novel')")

    @patch("builtins.print")
    def test_print_records_for_empty_list(self, mock_print) -> None:
        _print_records([])
        mock_print.assert_any_call("Записи не найдены.")

    @patch("builtins.input", side_effect=["9", "0"])
    @patch("builtins.print")
    def test_run_handles_unknown_command_and_exit(self, mock_print, _mock_input) -> None:
        run()

        mock_print.assert_any_call("Неизвестная команда. Повторите ввод.")
        mock_print.assert_any_call("Выход из программы.")
