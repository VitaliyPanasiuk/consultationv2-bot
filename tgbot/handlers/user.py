from aiogram import Router, Bot, types
from aiogram.client.bot import DefaultBotProperties
from aiogram.filters import Command, StateFilter
from aiogram.types import Message, FSInputFile
from tgbot.config import load_config
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram import F


import time
from datetime import datetime
import requests
import asyncio

from tgbot.services.del_message import delete_message

from tgbot.keyboards.inlineBtn import lang_button, main_menu_button, phone_button, skip_comp_button, skip_links_button
# CastomCallback.filter(F.action == "") // callback_query: types.CallbackQuery, callback_data: SellersCallbackFactory, state: FSMContext

from db.db import get_pool_func
from logs.logs import initlogging
from tgbot.misc.functions import reg_user, update_lang, get_lang, update_user,get_user_data
from tgbot.misc.text import mess
from tgbot.misc.states import consult_state


user_router = Router()
config = load_config(".env")
bot = Bot(token=config.tg_bot.token,
        default=DefaultBotProperties(parse_mode='HTML'))

# db_pool = await get_pool_func()
#     async with db_pool.acquire() as connection:
db_logger, bot_logger = initlogging()

@user_router.message(Command("start"))
async def user_start(message: Message):
    user_id = message.from_user.id  
    name = message.from_user.first_name
    user_name = message.from_user.username
    await reg_user(user_id, name, user_name)
    
    btn = lang_button()
    await bot.send_message(user_id, "Привет! 👋Выбери, пожалуйста, язык", reply_markup=btn.as_markup())
    
    
@user_router.callback_query(F.data == "ua")
async def user_start(callback_query: types.callback_query, state: FSMContext):    
    user_id = callback_query.from_user.id
    
    await update_lang(user_id, "ua")
    lang = await get_lang(user_id)
    
    btn = main_menu_button(lang)
    await bot.send_message(user_id, mess[lang]['greeting'], reply_markup=btn.as_markup())
    
@user_router.callback_query(F.data == "ru")
async def user_start(callback_query: types.callback_query, state: FSMContext):    
    user_id = callback_query.from_user.id
    
    await update_lang(user_id, "ru")
    lang = await get_lang(user_id)
    btn = main_menu_button(lang)
    await bot.send_message(user_id, mess[lang]['greeting'], reply_markup=btn.as_markup())
    
@user_router.callback_query(F.data == "consult")
async def user_start(callback_query: types.callback_query, state: FSMContext):    
    user_id = callback_query.from_user.id
    lang = await get_lang(user_id)
    
    user_data = await get_user_data(user_id)
    
    if not user_data['phone']:
        btn = phone_button(lang)
        await bot.send_message(user_id, mess[lang]['phone'], reply_markup=btn.as_markup(resize_keyboard=True))
        await state.set_state(consult_state.phone)
    elif user_data['phone'] and user_data['company_name'] and user_data['links']:
        message=f'''Пользователь: @{callback_query.from_user.username}
Тип: консультация
Имя: {user_data["name"]}
Телефон: {user_data["phone"]}
Название компании: {user_data["company_name"]}
Ссылки: {user_data["links"]}
Цель: {user_data["target"]}
'''
        await bot.send_message(config.tg_bot.chat, message)
        
        await bot.send_message(user_id, mess[lang]['thanks'])
        photo = FSInputFile("tgbot/docs/thanks.gif")
        await bot.send_animation(user_id, photo)
        await state.clear()
    elif not user_data['company_name']:
        await state.update_data(phone = user_data["phone"])
        await state.update_data(name = user_data["name"])
        
        btn = skip_comp_button(lang)
        await bot.send_message(user_id, mess[lang]['company'], reply_markup=btn.as_markup())
        await state.set_state(consult_state.comp_name)
    elif not user_data['links']:
        await state.update_data(phone = user_data["phone"])
        await state.update_data(name = user_data["name"])
        await state.update_data(comp_name = user_data["company_name"])
        
        btn = skip_links_button(lang)
        await bot.send_message(user_id, mess[lang]['links'], reply_markup=btn.as_markup())
        await state.set_state(consult_state.links)
    
    
@user_router.message(F.contact , consult_state.phone)
async def contacts(message: Message, state: FSMContext):
    user_id = message.from_user.id
    phone_number = message.contact.phone_number
    lang = await get_lang(user_id)
    await state.update_data(phone = phone_number)
    
    await bot.send_message(user_id, mess[lang]['name'], reply_markup=types.ReplyKeyboardRemove())
    await state.set_state(consult_state.name)
    
@user_router.message(F.text , consult_state.name)
async def contacts(message: Message, state: FSMContext):
    user_id = message.from_user.id
    text = message.text
    lang = await get_lang(user_id)
    await state.update_data(name = text)
    
    btn = skip_comp_button(lang)
    await bot.send_message(user_id, mess[lang]['company'], reply_markup=btn.as_markup())
    await state.set_state(consult_state.comp_name)
    
@user_router.message(F.text , consult_state.comp_name)
async def contacts(message: Message, state: FSMContext):
    user_id = message.from_user.id
    text = message.text
    lang = await get_lang(user_id)
    await state.update_data(comp_name = text)
    
    btn = skip_links_button(lang)
    await bot.send_message(user_id, mess[lang]['links'], reply_markup=btn.as_markup())
    await state.set_state(consult_state.links)
    
@user_router.callback_query(F.data == "skip_comp", consult_state.comp_name)
async def user_start(callback_query: types.callback_query, state: FSMContext):    
    user_id = callback_query.from_user.id
    lang = await get_lang(user_id)
    await state.update_data(comp_name = '')
    
    btn = skip_links_button(lang)
    await bot.send_message(user_id, mess[lang]['links'], reply_markup=btn.as_markup())
    await state.set_state(consult_state.links)
    
@user_router.message(F.text , consult_state.links)
async def contacts(message: Message, state: FSMContext):
    user_id = message.from_user.id
    text = message.text
    lang = await get_lang(user_id)
    await state.update_data(links = text)
    
    await bot.send_message(user_id, mess[lang]['target'])
    await state.set_state(consult_state.target)
    
@user_router.callback_query(F.data == "skip_links", consult_state.links)
async def user_start(callback_query: types.callback_query, state: FSMContext):    
    user_id = callback_query.from_user.id
    lang = await get_lang(user_id)
    await state.update_data(links = '')
    
    await bot.send_message(user_id, mess[lang]['target'])
    await state.set_state(consult_state.target)
    
@user_router.message(F.text , consult_state.target)
async def contacts(message: Message, state: FSMContext):
    user_id = message.from_user.id
    text = message.text
    lang = await get_lang(user_id)
    await state.update_data(target = text)
    
    data = await state.get_data()
    message=f'''Пользователь: @{message.from_user.username}
Тип: консультация
Имя: {data["name"]}
Телефон: {data["phone"]}
Название компании: {data["comp_name"]}
Ссылки: {data["links"]}
Цель: {data["target"]}
'''
    await update_user(user_id,data["phone"],data["name"],data["comp_name"],data["links"],data["target"])
    await bot.send_message(config.tg_bot.chat, message)
    
    await bot.send_message(user_id, mess[lang]['thanks'])
    photo = FSInputFile("tgbot/docs/thanks.gif")
    await bot.send_animation(user_id, photo)
    await state.clear()
    
    