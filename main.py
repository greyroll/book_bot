from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State

import asyncio
import sys

from aiogram import Bot, Dispatcher, types
from aiogram.client.default import DefaultBotProperties
from aiogram.filters import Command, CommandStart
from aiogram.types import Message, User
from aiogram.enums import ParseMode
import logging

from classes import UI, BookLoader
from config import books_data
from secret import secret_api_token

API_TOKEN = secret_api_token

# Включаем логирование
logging.basicConfig(level=logging.INFO)

dp = Dispatcher()
bot = Bot(token=API_TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML))

store = {"chosen_book": [], "current_part": 1}



class UserStatus(StatesGroup):
	picking = State()
	reading = State()

@dp.message(Command("start"))
async def start(message: Message, state: FSMContext):
	await message.answer("Добро пожаловать в бот-читалку. Для просмотра списка книг введите команду /open. Для перемещения к следующей части книги введите /next")
	await state.set_state(UserStatus.picking)


@dp.message(Command("open"))
async def pick(message: Message, state: FSMContext):
	await message.answer(UI.show_books_list(books_data))
	await message.answer("Введите номер книги")
	await state.set_state(UserStatus.picking)


@dp.message(UserStatus.picking)
async def open_book(message: Message, state: FSMContext):
	if message.text.strip() == "/next":
		await message.answer("Cначала выберите книгу")
	elif not message.text.isdigit():
		await message.answer("Введите только номер")
	else:
		index = int(message.text.strip())
		chosen_book_path = ""
		store["current_part"] = 1
		for dictionary in books_data:
			if index == dictionary["index"]:
				chosen_book_path = dictionary["path"]
		if chosen_book_path == "":
			await message.answer("Такого номера нет")
		book_loader = BookLoader(chosen_book_path)
		store["chosen_book"] = book_loader.split_into_500_sb()
		await message.answer(f"Часть {store["current_part"]}. \n{store["chosen_book"][store["current_part"] - 1]}")
		store["current_part"] += 1
		await state.set_state(UserStatus.reading)


@dp.message(Command("next"))
async def next_part(message: Message, state: FSMContext):
	if state == UserStatus.picking:
		await message.answer("Cначала выберите книгу")
	elif (store["current_part"] - 1) == len(store["chosen_book"]):
		await message.answer("Книга закончилась, выберите другую")
	else:
		await message.answer(f"Часть {store["current_part"]}. \n{store["chosen_book"][store["current_part"] - 1]}")
		store["current_part"] += 1


@dp.message(UserStatus.reading)
async def stop_talking(message: Message):
	await message.answer("Не болтай, а читай. Чтобы перейти к следующему разделу, введи /next. Чтобы вернуться к списку книг, введи /open")

async def main() -> None:
	await dp.start_polling(bot)

logging.basicConfig(level=logging.DEBUG, stream=sys.stdout)
asyncio.run(main())