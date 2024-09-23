from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State

import asyncio
import sys

from aiogram import Bot, Dispatcher, types
from aiogram.client.default import DefaultBotProperties
from aiogram.filters import Command, CommandStart
from aiogram.types import Message, User
from aiogram.enums import ParseMode
from loguru import logger

from classes import UI, BookLoader
from config import books_data
from secret import secret_api_token

API_TOKEN = secret_api_token

# Включаем логирование
logger.add("logfile.log", level="DEBUG")

dp = Dispatcher()
bot = Bot(token=API_TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML))

store = {"chosen_book": [], "current_part": 1}
# user_store = [{"user_id": "", "chosen_book": [], "current_part": 1}]
book_loader = BookLoader()



class UserStatus(StatesGroup):
	picking_book = State()
	picking_symbols = State()
	reading = State()

@dp.message(Command("start"))
async def start(message: Message, state: FSMContext):
	logger.info(f"User {message.from_user.id} started the bot.")
	await message.answer("Добро пожаловать в бот-читалку. Для просмотра списка книг введите команду /open. Для перемещения к следующей части книги введите /next")
	await state.set_state(UserStatus.picking_book)


@dp.message(Command("open"))
async def pick(message: Message, state: FSMContext):
	logger.info(f"User {message.from_user.id} requested book list.")
	await message.answer(UI.show_books_list(books_data))
	await message.answer("Введите номер книги")
	await state.set_state(UserStatus.picking_book)


@dp.message(UserStatus.picking_book)
async def open_book(message: Message, state: FSMContext):
	if message.text.strip() == "/next":
		await message.answer("Cначала выберите книгу")
		logger.warning(f"User {message.from_user.id} tried to skip picking a book.")
	elif not message.text.isdigit():
		await message.answer("Введите только номер")
		logger.warning(f"User {message.from_user.id} entered an invalid book number: {message.text}")
	else:
		index = int(message.text.strip())
		chosen_book_path = ""
		store["current_part"] = 1
		for dictionary in books_data:
			if index == dictionary["index"]:
				chosen_book_path = dictionary["path"]
		if chosen_book_path == "":
			await message.answer("Такого номера нет")
			logger.warning(f"User {message.from_user.id} selected an invalid book number.")
		else:
			logger.info(f"User {message.from_user.id} has opened book #{index}.")
			book_loader.set_path(chosen_book_path)
			await message.answer("Пожалуйста, укажите количество символов, которое вы хотите отображать за раз.")
			await state.set_state(UserStatus.picking_symbols)


@dp.message(UserStatus.picking_symbols)
async def set_symbols_number(message: Message, state: FSMContext):
	if not message.text.strip().isdigit():
		await message.answer("Введите количество символов")
		logger.error(f"User {message.from_user.id} entered an invalid value.")
	else:
		symb_number = int(message.text)
		logger.info(f"User {message.from_user.id} picked {symb_number} length")
		logger.info(f"User {message.from_user.id} started reading part {store["current_part"]}.")
		store["chosen_book"] = book_loader.split_into_given_sb(symb_number)
		await message.answer(f"Часть {store["current_part"]}. \n{store["chosen_book"][store["current_part"] - 1]}")
		store["current_part"] += 1
		await state.set_state(UserStatus.reading)


@dp.message(Command("next"))
async def next_part(message: Message, state: FSMContext):
	if state == UserStatus.picking_book or state == UserStatus.picking_symbols:
		await message.answer("Cначала выберите книгу")
		logger.warning(f"User {message.from_user.id} tried to skip picking a book.")
	elif (store["current_part"] - 1) == len(store["chosen_book"]):
		await message.answer("Книга закончилась, выберите другую")
		logger.warning(f"User {message.from_user.id} finished current book")
	else:
		await message.answer(f"Часть {store["current_part"]}. \n{store["chosen_book"][store["current_part"] - 1]}")
		logger.info(f"User {message.from_user.id} started reading part {store["current_part"]}.")
		store["current_part"] += 1


@dp.message(UserStatus.reading)
async def stop_talking(message: Message):
	await message.answer("Не болтай, а читай. Чтобы перейти к следующему разделу, введи /next. Чтобы вернуться к списку книг, введи /open")


async def main() -> None:
	await dp.start_polling(bot)


asyncio.run(main())