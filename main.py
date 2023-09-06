from aiogram import Bot, Dispatcher, executor, types
from aiogram.types import ContentTypes, Message, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.dispatcher import FSMContext
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher.filters.state import State, StatesGroup

import db
import config

bot_token = config.bot_token
api_hash, api_id = config.api_hash, config.api_id

bot = Bot(bot_token)
storage = MemoryStorage()
dp = Dispatcher(bot, storage=storage)

# creating db env
file_number = db.create_db_and_files_table()
voice_number = db.create_voice_table()
db.create_users_table()


# tg part
class Form(StatesGroup):
    first_message = State()
    update = State()


@dp.message_handler(commands=['start'])
async def auth(message: types.Message):
    await bot.send_message(message.chat.id, 'Вы - переводчик? (да/нет)')
    await Form.first_message.set()


@dp.message_handler(state=Form.first_message)
async def auth_answer(message: types.Message, state: FSMContext):
    if message.text.lower() == 'да':
        if message.chat.id not in db.get_users_list():
            db.add_user((message.chat.id, message.chat.username, 1))
            await bot.send_message(message.chat.id, 'Вы добавлены в базу как переводчик')
        else:
            await bot.send_message(message.chat.id, 'Вы уже в базе')
    else:
        if message.chat.id not in db.get_users_list():
            db.add_user((message.chat.id, message.chat.username, 0))
            await bot.send_message(message.chat.id, 'Вы добавлены в базу как пользователь (не переводчик)')
            await bot.send_message(message.chat.id, 'Направьте боту документ, отправляйте "как файл"')
        else:
            await bot.send_message(message.chat.id, 'Вы уже в базе')
    await state.finish()


@dp.message_handler(commands=['update_type'])
async def update(message: types.Message):
    await bot.send_message(message.chat.id, 'Для смены типа пользователя, отправьте боту сообщение с типом\n'
                                            '1 - Переводчик\n'
                                            '0 - Пользователь\n'
                                            'Необходимо направить либо 1, либо 0')
    await Form.update.set()


@dp.message_handler(lambda message: message.text not in ['0', '1'], state=Form.update)
async def update(message: types.Message):
    await bot.send_message(message.chat.id, 'Вы указали неверный тип, попробуйте снова')
    await Form.update.set()


@dp.message_handler(lambda message: message.text in ['0', '1'], state=Form.update)
async def update(message: types.Message, state: FSMContext):
    if message.text == '0':
        db.update_user_status(message.chat.id, 0)
        await bot.send_message(message.chat.id, 'Ваш тип пользователя в базе - пользователь')
    else:
        db.update_user_status(message.chat.id, 1)
        await bot.send_message(message.chat.id, 'Ваш тип пользователя в базе - переводчик')

    await state.finish()


@dp.message_handler(content_types=ContentTypes.DOCUMENT | ContentTypes.AUDIO)
async def doc_handler(message: Message):
    global file_number
    file_name = message.document.file_name.split('.')[0] if message.content_type == 'document' \
        else message.audio.file_name.split('.')[0]
    translator = db.get_translators_id()
    if db.get_translators_id():
        if message.chat.id != translator:
            if file_name not in db.get_files_names():
                await bot.forward_message(translator, message.chat.id, message.message_id)
                file_number += 1
                db.add_file((file_number, message.chat.id, file_name))
                await bot.send_message(message.chat.id, 'Файл направлен переводчику')

                inline_btn_1 = InlineKeyboardButton(f"Взять '{file_name}' в работу", callback_data=file_name)
                inline_kb1 = InlineKeyboardMarkup().add(inline_btn_1)
                await bot.send_message(translator, f"Взять в работу '{file_name}'", reply_markup=inline_kb1)
            else:
                await bot.send_message(message.chat.id, 'Такое название уже используется, поменяйте название'
                                                        'и направьте файл заново')
        else:
            try:
                await bot.forward_message(db.get_receiver_id(file_name), message.chat.id, message.message_id)
                await bot.send_message(message.chat.id, 'Перевод направлен пользователю')
            except TypeError:
                await bot.send_message(message.chat.id, 'Вы назвали файл неверно, попробуйте заново')
    else:
        await bot.send_message(message.chat.id, 'Переводчик не внесен в базу, обратитесь к администратору')


@dp.message_handler(content_types=ContentTypes.VOICE)
async def doc_handler(message: Message):
    global voice_number, file_number
    voice_number += 1
    file_number += 1
    if voice_number == 0:
        voice_name = 'Voice0'
    else:
        voice_name = f'Voice{voice_number}'
    translator = db.get_translators_id()
    if db.get_translators_id():
        if message.chat.id != translator:
            await bot.forward_message(translator, message.chat.id, message.message_id)
            db.add_voice((voice_number, message.chat.id, voice_name))
            db.add_file((file_number, message.chat.id, voice_name))
            await bot.send_message(message.chat.id, 'Файл направлен переводчику')

            inline_btn_1 = InlineKeyboardButton(f"Взять '{voice_name}' в работу", callback_data=voice_name)
            inline_kb1 = InlineKeyboardMarkup().add(inline_btn_1)
            await bot.send_message(translator, f"Взять в работу '{voice_name}'", reply_markup=inline_kb1)

        else:
            try:
                await bot.forward_message(db.get_receiver_id(voice_name), message.chat.id, message.message_id)
                await bot.send_message(message.chat.id, 'Перевод направлен пользователю')
            except TypeError:
                await bot.send_message(message.chat.id, 'Вы назвали файл неверно, попробуйте заново')
    else:
        await bot.send_message(message.chat.id, 'Переводчик не внесен в базу, обратитесь к администратору')


@dp.message_handler(content_types=ContentTypes.TEXT)
async def url_handler(message: Message):
    global file_number
    translator = db.get_translators_id()
    try:
        if message.entities[0].type == 'url':
            if db.get_translators_id():
                if message.chat.id != translator:
                    await bot.forward_message(translator, message.chat.id, message.message_id)
                    file_number += 1
                    file_name = f'url_{file_number}_{message.chat.id}'
                    db.add_file((file_number, message.chat.id, file_name))
                    await bot.send_message(translator, f'Файл с переводом на материал из этой ссылки назовите: '
                                                       f'<b>{file_name}</b>', parse_mode="html")
                    await bot.send_message(message.chat.id, 'Файл направлен переводчику')
            else:
                await bot.send_message(message.chat.id, 'Переводчик не внесен в базу, обратитесь к администратору')
        else:
            await bot.send_message(message.chat.id, 'Вы направили недопустимый формат файла, попробуйте снова')
    except IndexError:
        await bot.send_message(message.chat.id, 'Вы направили недопустимый формат файла, попробуйте снова')


@dp.callback_query_handler(lambda c: c.data)
async def process_callback_kb1btn1(callback_query: types.CallbackQuery):
    file_name = callback_query.data
    receiver = db.get_receiver_id(file_name)
    receiver_text_id = db.get_receiver_text_id(receiver)
    translator = db.get_translators_id()
    await bot.send_message(receiver, f"'{file_name}' взят в работу")
    await bot.send_message(translator, f"Пользователь @{receiver_text_id} уведомлен о взятии в работу '{file_name}'")


if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)
