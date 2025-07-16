from aiogram.utils.keyboard import ReplyKeyboardBuilder, InlineKeyboardButton, InlineKeyboardBuilder
from aiogram import Bot, types
from aiogram.filters.callback_data import CallbackData
from typing import Optional

from tgbot.misc.text import buttons


class ServiceCallback(CallbackData, prefix="fabnum"):
    # castom class for callback_data
    action: str
    service_id: Optional[int]

def lang_button():
    example = InlineKeyboardBuilder()
    example.add(types.InlineKeyboardButton(
        text='Українська',
        callback_data='ua'
    ))
    example.add(types.InlineKeyboardButton(
        text='Русский',
        callback_data='ru'
    ))
    return example

def main_menu_button(lang):
    example = InlineKeyboardBuilder()
    example.add(types.InlineKeyboardButton(
        text=buttons[lang]['start'][0],
        callback_data='consult'
    ))
    example.add(types.InlineKeyboardButton(
        text=buttons[lang]['start'][1],
        callback_data='price'
    ))
    example.adjust(1, 1)
    return example

def phone_button(lang):
    home_buttons = ReplyKeyboardBuilder()
    home_buttons.add(
        types.KeyboardButton(text=buttons[lang]['phone'], request_contact=True)
    )
    home_buttons.adjust(1)
    return home_buttons

def skip_comp_button(lang):
    example = InlineKeyboardBuilder()
    example.add(types.InlineKeyboardButton(
        text=buttons[lang]['skip'],
        callback_data='skip_comp'
    ))
    return example

def skip_links_button(lang):
    example = InlineKeyboardBuilder()
    example.add(types.InlineKeyboardButton(
        text=buttons[lang]['skip'],
        callback_data='skip_links'
    ))
    return example

def service_button(lang):
    example = InlineKeyboardBuilder()
    a = 1
    for i in buttons[lang]['service']:
        example.button(
            text=i,
            callback_data=ServiceCallback(action='select_service', service_id=a)
        )
        a += 1
    
    example.adjust(1, 1, 1, 1, 1, 1, 1, 1)
    return example
