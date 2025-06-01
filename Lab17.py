1.
import json
import os
from threading import Lock

class Assistant:
    def __init__(self, filename='notes.json'):
        self.filename = filename
        self.lock = Lock()
        self._ensure_file()

    def _ensure_file(self):
        if not os.path.exists(self.filename) or not self._is_valid_json():
            with open(self.filename, 'w') as f:
                json.dump([], f)

    def _is_valid_json(self):
        try:
            with open(self.filename, 'r') as f:
                json.load(f)
            return True
        except (json.JSONDecodeError, FileNotFoundError):
            return False

    def _read_notes(self):
        with self.lock:
            with open(self.filename, 'r') as f:
                return json.load(f)

    def _write_notes(self, notes):
        with self.lock:
            with open(self.filename, 'w') as f:
                json.dump(notes, f, indent=2)

    def add_note(self, note):
        notes = self._read_notes()
        notes.append(note)
        self._write_notes(notes)

    def list_notes(self):
        return self._read_notes()

    def search_notes(self, keyword):
        return [note for note in self._read_notes() if keyword.lower() in note.lower()]
2.
from assistant import Assistant

def main():
    assistant = Assistant()

    while True:
        command = input("Введіть команду (/add, /list, /search, /exit): ")

        if command == "/add":
            note = input("Введіть нотатку: ")
            assistant.add_note(note)
            print("Нотатку додано.")
        elif command == "/list":
            notes = assistant.list_notes()
            if notes:
                print("Нотатки:")
                for i, note in enumerate(notes, 1):
                    print(f"{i}. {note}")
            else:
                print("Список нотаток порожній.")
        elif command == "/search":
            keyword = input("Введіть ключове слово: ")
            results = assistant.search_notes(keyword)
            if results:
                print("Знайдено нотатки:")
                for note in results:
                    print(f"- {note}")
            else:
                print("Нічого не знайдено.")
        elif command == "/exit":
            break
        else:
            print("Невідома команда.")

if __name__ == "__main__":
    main()

3.
import logging
from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command
from aiogram.types import Message, ReplyKeyboardRemove
from assistant import Assistant

TOKEN = '7540305055:AAE3FhQoJiv8exvAVoVgkcMCwz70uJMtTis'

logging.basicConfig(level=logging.INFO)
bot = Bot(token=TOKEN)
dp = Dispatcher()
assistant = Assistant()

user_state = {}

@dp.message(Command("start"))
async def cmd_start(message: Message):
    await message.answer("Привіт! Я асистент-бот. Використовуйте /add, /list, /search.")

@dp.message(Command("help"))
async def cmd_help(message: Message):
    await message.answer("/add — додати нотатку\n/list — список нотаток\n/search — пошук")

@dp.message(Command("add"))
async def cmd_add(message: Message):
    await message.answer("Введіть текст нотатки:", reply_markup=ReplyKeyboardRemove())
    user_state[message.from_user.id] = "awaiting_note"

@dp.message(Command("list"))
async def cmd_list(message: Message):
    notes = assistant.list_notes()
    if notes:
        text = "\n".join([f"{i+1}. {n}" for i, n in enumerate(notes)])
        await message.answer(text)
    else:
        await message.answer("Список нотаток порожній.")

@dp.message(Command("search"))
async def cmd_search(message: Message):
    await message.answer("Введіть ключове слово для пошуку:", reply_markup=ReplyKeyboardRemove())
    user_state[message.from_user.id] = "awaiting_search"

@dp.message()
async def process_message(message: Message):
    user_id = message.from_user.id
    if user_id in user_state:
        state = user_state[user_id]
        if state == "awaiting_note":
            assistant.add_note(message.text)
            await message.answer("Нотатку збережено.")
            del user_state[user_id]
        elif state == "awaiting_search":
            results = assistant.search_notes(message.text)
            if results:
                await message.answer("\n".join(results))
            else:
                await message.answer("Нічого не знайдено.")
            del user_state[user_id]
    else:
        await message.answer("Я вас не зрозумів. Використовуйте команди: /add, /list, /search.")

if __name__ == "__main__":
    import asyncio
    asyncio.run(dp.start_polling(bot))
