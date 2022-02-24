from asyncio import sleep
from re import fullmatch

from aiogram import Dispatcher
from aiogram import types
from aiogram.dispatcher import FSMContext
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton
from aiogram.types import ReplyKeyboardRemove

from config import answers
from database import db
from states import Registration
from keyboards import english_inline
from keyboards import russian_inline, language
from loader import bot

Reg_state = Registration()


async def start_handler(message: types.Message):
    await message.answer(text="Choose one of two \nappropriate languages",
                         reply_markup=language)

    await Reg_state.start.set()


async def eng_reg(callback: types.CallbackQuery, state: FSMContext):
    await bot.edit_message_text(text="Choose one of two options",
                                message_id=callback.message.message_id,
                                reply_markup=english_inline,
                                chat_id=callback.message.chat.id)

    async with state.proxy() as data:
        data['language'] = 'English'
        data['user_id'] = int(callback.from_user.id)

    await Reg_state.next()

    await callback.answer("Language was successfully changed")


async def rus_reg(callback: types.CallbackQuery, state: FSMContext):
    await bot.edit_message_text(text="Выберите одну из двух опций",
                                message_id=callback.message.message_id,
                                reply_markup=russian_inline,
                                chat_id=callback.message.chat.id)

    async with state.proxy() as data:
        data['language'] = 'Russian'
        data['user_id'] = int(callback.from_user.id)

    await Reg_state.next()

    await callback.answer("Язык был успешно изменён")


async def reg_name(callback: types.CallbackQuery, state: FSMContext):
    await bot.delete_message(chat_id=callback.message.chat.id,
                             message_id=callback.message.message_id)

    async with state.proxy() as data:
        get_contact = KeyboardButton(answers[f"{data['language']}"]['share_contact'], request_contact=True)
        name_and_phone = ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True).add(get_contact)
        await bot.send_message(chat_id=callback.message.chat.id,
                               reply_markup=name_and_phone,
                               text=answers[f"{data['language']}"]['reg_name'])

    await Reg_state.next()


async def reg_contact_or_name(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        if message.contact:
            contact_dict = message.contact
            data['first_name'] = str(contact_dict['first_name']).title()
            data['phone_number'] = contact_dict['phone_number']
            msg = await message.answer(answers[f"{data['language']}"]['reg_contact_or_name'])
            await sleep(2)
            await msg.delete()
            await message.delete()
            await message.answer(answers[f"{data['language']}"]['entering_mail'])
            await Reg_state.email.set()
        else:
            if not message.text.isalpha() or len(message.text) < 3:

                await message.answer(answers[f"{data['language']}"]['entering_name'])

                await reg_contact_or_name(message.text, state=Reg_state.name)

            else:
                data['first_name'] = message.text.title()
                msg = await message.answer(answers[f"{data['language']}"]['valid_name'],
                                           reply_markup=ReplyKeyboardRemove())
                await sleep(2)
                await msg.delete()
                await message.delete()
                await message.answer(answers[f"{data['language']}"]['entering_phone'])
                await Reg_state.next()


async def phone_reg(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        if bool(fullmatch(r"\+\d{9,20}", message.text)):
            data["phone"] = message.text

            nextz = KeyboardButton(answers[f"{data['language']}"]['continue'])
            back = KeyboardButton(answers[f"{data['language']}"]['back'])
            reply = ReplyKeyboardMarkup(resize_keyboard=True,
                                        one_time_keyboard=True).add(nextz).add(back)

            await message.answer(answers[f"{data['language']}"]['successful_phone'],
                                 reply_markup=reply)
        else:
            await message.answer(answers[f"{data['language']}"]['validate_phone'])
            await phone_reg(message.text, state=Reg_state.phone)

    await Reg_state.next()


async def choose(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        if message.text == answers[f"{data['language']}"]['back']:
            await message.answer(answers[f"{data['language']}"]['entering_phone'],
                                 reply_markup=ReplyKeyboardRemove())
            await Registration.previous()
        elif message.text == answers[f"{data['language']}"]['continue']:
            msg = await message.answer(answers[f"{data['language']}"]['mail_continue'],
                                       reply_markup=ReplyKeyboardRemove())
            await sleep(1)
            await msg.delete()
            await message.answer(answers[f"{data['language']}"]['valid_email'])
        elif message.text == answers[f"{data['language']}"]['to_start']:
            await state.finish()
            return await start_handler(message.text)

        await Registration.next()


async def email_reg(message: types.Message, state: FSMContext, default=0):
    async with state.proxy() as data:
        if bool(fullmatch(
                r"^\w[^.\s]{0,10}.??[^.\s]{1,10}.??[^.\s]{0,10}.??[^.\s]"
                r"{0,10}[^.\s]{0,25}@[a-zA-Z]{1,32}-??\d{0,32}\d{0,32}.\w{1,10}$",
                message.text)):

            nextz = KeyboardButton(answers[f"{data['language']}"]['continue'])
            back = KeyboardButton(answers[f"{data['language']}"]['back'])
            reply = ReplyKeyboardMarkup(resize_keyboard=True,
                                        one_time_keyboard=True).add(nextz).add(back)

            await message.answer(answers[f"{data['language']}"]['successful_mail'],
                                 reply_markup=reply)
            data['email'] = message.text
            await Reg_state.next()
        else:
            default += 1
            if default > 3:
                return await message.answer(answers[f"{data['language']}"]['mail_errors'])

            await message.answer(answers[f"{data['language']}"]['try_mail'],
                                 disable_web_page_preview=True)


async def last_choose(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        if message.text == answers[f"{data['language']}"]['continue']:
            geo_button = KeyboardButton(answers[f"{data['language']}"]['sending_location'], request_location=True)
            geo_loc = ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True).add(geo_button)
            await message.answer(answers[f"{data['language']}"]['location_step'],
                                 reply_markup=geo_loc)
            await Reg_state.next()
        elif message.text == answers[f"{data['language']}"]['back']:
            msg = await message.answer(answers[f"{data['language']}"]['mail_returning'])
            await sleep(1)
            await msg.delete()
            await message.answer(answers[f"{data['language']}"]['entering_mail'])
            await Reg_state.previous()
        elif message.text == answers[f"{data['language']}"]['to_start']:
            await state.finish()
            return await start_handler(message.text)


async def geo_location(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        location = message.location
        data['latitude'] = location['latitude']
        data['longitude'] = location['longitude']

    if not await db.sql_add(state):

        yes_button = InlineKeyboardButton(answers[data['language']]['YES'],
                                          callback_data="confirm")
        no_button = InlineKeyboardButton(answers[data['language']]['NO'],
                                         callback_data="decline")

        inline_confirm = InlineKeyboardMarkup().add(yes_button).add(no_button)

        await message.answer(answers[data['language']]['user_id_indb'],
                             reply_markup=inline_confirm)

        await Reg_state.next()

    else:

        await message.answer(answers[f"{data['language']}"]['congratulations'],
                             reply_markup=ReplyKeyboardRemove())

        await state.finish()


async def confirm(callback: types.CallbackQuery, state: FSMContext):
    async with state.proxy() as data:
        await bot.delete_message(chat_id=callback.message.chat.id,
                                 message_id=callback.message.message_id)

        await bot.send_message(chat_id=callback.message.chat.id,
                               text=answers[data['language']]['record'],
                               reply_markup=ReplyKeyboardRemove())

    await db.sql_del(state)
    await db.sql_add(state)

    await state.finish()


async def decline(callback: types.CallbackQuery, state: FSMContext):
    async with state.proxy() as data:
        await bot.delete_message(chat_id=callback.message.chat.id,
                                 message_id=callback.message.message_id)

        await bot.send_message(chat_id=callback.message.chat.id,
                               text=answers[data['language']]['decline'],
                               reply_markup=ReplyKeyboardRemove())

    await state.finish()


def regisration_handlers(dp: Dispatcher):
    dp.register_message_handler(start_handler, commands=["start", "language"], state='*')
    dp.register_callback_query_handler(eng_reg, lambda x: x.data == "eng", state=Reg_state.start)
    dp.register_callback_query_handler(rus_reg, lambda x: x.data == "rus", state=Reg_state.start)
    dp.register_callback_query_handler(reg_name, lambda x: x.data == "reg", state=Reg_state.callback)
    dp.register_message_handler(reg_contact_or_name, content_types=["contact", "text"], state=Reg_state.name)
    dp.register_message_handler(phone_reg, state=Reg_state.phone)
    dp.register_message_handler(choose, state=Reg_state.choose)
    dp.register_message_handler(email_reg, state=Reg_state.email)
    dp.register_message_handler(last_choose, state=Reg_state.second_choose)
    dp.register_message_handler(geo_location, state=Reg_state.location, content_types="location")
    dp.register_callback_query_handler(confirm, lambda x: x.data == "confirm", state=Reg_state.finish)
    dp.register_callback_query_handler(decline, lambda x: x.data == "decline", state=Reg_state.finish)
