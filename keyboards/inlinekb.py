from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

en_lang_butt = InlineKeyboardButton("English language", callback_data="eng")
rus_lang_butt = InlineKeyboardButton("Русский язык", callback_data="rus")
language = InlineKeyboardMarkup().add(en_lang_butt).add(rus_lang_butt)

eng_reg = InlineKeyboardButton("Register", callback_data="reg")
eng_upd = InlineKeyboardButton("Update data", callback_data="upd")
english_inline = InlineKeyboardMarkup().add(eng_reg).add(eng_upd)


rus_reg = InlineKeyboardButton("Зарегистрироваться", callback_data="reg")
rus_upd = InlineKeyboardButton("Обновить данные", callback_data="upd")
russian_inline = InlineKeyboardMarkup().add(rus_reg).add(rus_upd)

