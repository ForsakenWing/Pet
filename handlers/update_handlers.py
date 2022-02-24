import asyncio

from loader import bot
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, ReplyKeyboardRemove
from config import update_stage, answers
from states import Update
from .registr_handlers import Reg_state
from aiogram import Dispatcher
from aiogram import types
from aiogram.dispatcher import FSMContext
from database.db import sql_get_users_id, sql_update
from re import fullmatch


async def callback_update_handler(callback: types.CallbackQuery, state: FSMContext):
    async with state.proxy() as data:

        global lang

        lang = data['language']
        first_name = InlineKeyboardButton(text=update_stage[lang]["first_name"],
                                          callback_data="name")
        email = InlineKeyboardButton(text=update_stage[lang]["email"],
                                     callback_data="email")
        phone_number = InlineKeyboardButton(text=update_stage[lang]["phone_num"],
                                            callback_data="phone_number")
        geo = InlineKeyboardButton(text=update_stage[lang]["geo"],
                                   callback_data="location")
        global keyboard

        keyboard = InlineKeyboardMarkup().add(first_name) \
            .add(email).add(phone_number).add(geo)

        if data['user_id'] in sql_get_users_id():
            await bot.edit_message_text(message_id=callback.message.message_id,
                                        chat_id=callback.message.chat.id,
                                        text=update_stage[lang]["upd_accept"],
                                        reply_markup=keyboard)
        else:
            await callback.answer(update_stage[lang]["upd_decline"], show_alert=True)

        await state.finish()


async def callback_update_name(callback: types.CallbackQuery):
    await Update.name.set()
    await callback.answer(update_stage[lang]['redirect_name'])
    await bot.delete_message(chat_id=callback.message.chat.id,
                             message_id=callback.message.message_id)
    await bot.send_message(chat_id=callback.message.chat.id,
                           text=answers[lang]["entering_name"])


async def update_name(message: types.Message,
                      state: FSMContext):

    if not message.text.isalpha() or len(message.text) < 3:

        await message.answer(answers[lang]['entering_name'])

        return await update_name(message.text, Update.name)

    else:

        async with state.proxy() as data:
            data['first_name'] = message.text.title()
            data['user_id'] = message.from_user.id

            await sql_update(state, "first_name", data['first_name'], data['user_id'])

            await message.answer(update_stage[lang]["successful_name_update"])

        await state.finish()


async def callback_update_phone(callback: types.CallbackQuery):
    await Update.phone.set()
    await callback.answer(update_stage[lang]['redirect_phone'])
    await asyncio.sleep(1)
    await bot.delete_message(chat_id=callback.message.chat.id,
                             message_id=callback.message.message_id)
    await bot.send_message(chat_id=callback.message.chat.id,
                           text=answers[lang]["entering_phone"])


async def update_phone(message: types.Message, state: FSMContext):

    async with state.proxy() as data:
        if bool(fullmatch(r"\+\d{9,20}", message.text)):
            data["phone"] = message.text
            data["user_id"] = message.from_user.id

            await sql_update(state, "phone_number", data["phone"], data["user_id"])

            await message.answer(update_stage[lang]["successful_phone_update"])

        else:

            await message.answer(answers[lang]['validate_phone'])

            return await update_phone(message.text, state)

        await state.finish()


async def callback_update_email(callback: types.CallbackQuery):
    await Update.email.set()
    await callback.answer(update_stage[lang]['redirect_email'])
    await asyncio.sleep(1)
    await bot.delete_message(chat_id=callback.message.chat.id,
                             message_id=callback.message.message_id)
    await bot.send_message(chat_id=callback.message.chat.id,
                           text=answers[lang]["entering_mail"])


async def update_email(message: types.Message, state: FSMContext):

    async with state.proxy() as data:

        if bool(fullmatch(r"^\w[^.\s]{0,10}.??[^.\s]{1,10}.??[^.\s]{0,10}.??[^.\s]"
                          r"{0,10}[^.\s]{0,25}@[a-zA-Z]{1,32}-??\d{0,32}\d{0,32}.\w{1,10}$",
                          message.text)):

            data["email"] = message.text
            data["user_id"] = message.from_user.id

            await sql_update(state, "email", data["email"], data["user_id"])

            await message.answer(update_stage[lang]["successful_email_update"])

        else:

            await message.answer(answers[lang]['try_mail'])

            return await update_email(message.text, state)

        await state.finish()


async def callback_update_location(callback: types.CallbackQuery):
    await Update.location.set()
    location_sending_button = KeyboardButton(update_stage[lang]['location'],
                                             request_location=True)
    location = ReplyKeyboardMarkup(resize_keyboard=True).add(location_sending_button)

    await callback.answer(update_stage[lang]['redirect_location'])
    await asyncio.sleep(1)
    await bot.delete_message(chat_id=callback.message.chat.id,
                             message_id=callback.message.message_id)
    await bot.send_message(chat_id=callback.message.chat.id,
                           text=update_stage[lang]["send_location"],
                           reply_markup=location)


async def update_location(message: types.Message):

    await message.answer(update_stage[lang]["successful_location_update"],
                         reply_markup=ReplyKeyboardRemove())


def reg_update_handlers(dp: Dispatcher):
    dp.register_callback_query_handler(callback_update_handler,
                                       lambda callback: callback.data == "upd",
                                       state=Reg_state.callback)
    dp.register_callback_query_handler(callback_update_name,
                                       lambda callback: callback.data == "name")
    dp.register_callback_query_handler(callback_update_phone,
                                       lambda callback: callback.data == "phone_number")
    dp.register_callback_query_handler(callback_update_email,
                                       lambda callback: callback.data == "email")
    dp.register_callback_query_handler(callback_update_location,
                                       lambda callback: callback.data == "location")
    dp.register_message_handler(update_name, state=Update.name)
    dp.register_message_handler(update_phone, state=Update.phone)
    dp.register_message_handler(update_email, state=Update.email)
    dp.register_message_handler(update_location, state=Update.location,
                                content_types=['location'])
