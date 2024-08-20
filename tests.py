import pytest

from classes import BookLoader, UI
from config import books_data

book_loader = BookLoader("books_txt/Labkovskiy.txt")



def test_split_into_500_sb():
	split_text = book_loader.split_into_500_sb()
	for i, split_text in enumerate(split_text):
		print(f"Часть {i + 1}: {split_text}\n")


def test_show_books_list():
	print(UI.show_books_list(books_data))
