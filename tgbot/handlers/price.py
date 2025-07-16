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

from tgbot.keyboards.inlineBtn import ServiceCallback, main_menu_button, phone_button, skip_comp_button, skip_links_button, service_button
# CastomCallback.filter(F.action == "") // callback_query: types.CallbackQuery, callback_data: SellersCallbackFactory, state: FSMContext

from db.db import get_pool_func
from logs.logs import initlogging
from tgbot.misc.functions import reg_user, update_lang, get_lang, update_user,get_user_data
from tgbot.misc.text import mess
from tgbot.misc.states import price_state


price_router = Router()
config = load_config(".env")
bot = Bot(token=config.tg_bot.token,
        default=DefaultBotProperties(parse_mode='HTML'))

services_arr = ['SMM', 'PR', 'Digital-реклама (таргет, PPC, SEO)', 'Створення мерчу, прес-пака', 'Створення стенду', 'Брендинг / неймінг', 'Трафік. Influence-маркетинг', 'Трафік. Медійна відеореклама в YouTube / Instagram']

@price_router.callback_query(F.data == "price")
async def user_start(callback_query: types.callback_query, state: FSMContext):    
    user_id = callback_query.from_user.id
    lang = await get_lang(user_id)
    
    user_data = await get_user_data(user_id)
    
    if not user_data['phone']:
        btn = phone_button(lang)
        await bot.send_message(user_id, mess[lang]['phone'], reply_markup=btn.as_markup(resize_keyboard=True))
        await state.set_state(price_state.phone)
    elif user_data['phone'] and user_data['company_name'] and user_data['links']:
        await state.update_data(phone = user_data["phone"])
        await state.update_data(name = user_data["name"])
        await state.update_data(comp_name = user_data["company_name"])
        await state.update_data(links = user_data["links"])
        await state.update_data(target = user_data["target"])
        
        btn = service_button(lang)
        await bot.send_message(user_id, mess[lang]['service'], reply_markup=btn.as_markup())
        await state.set_state(price_state.service)
    elif not user_data['company_name']:
        await state.update_data(phone = user_data["phone"])
        await state.update_data(name = user_data["name"])
        
        btn = skip_comp_button(lang)
        await bot.send_message(user_id, mess[lang]['company'], reply_markup=btn.as_markup())
        await state.set_state(price_state.comp_name)
    elif not user_data['links']:
        await state.update_data(phone = user_data["phone"])
        await state.update_data(name = user_data["name"])
        await state.update_data(comp_name = user_data["company_name"])
        
        btn = skip_links_button(lang)
        await bot.send_message(user_id, mess[lang]['links'], reply_markup=btn.as_markup())
        await state.set_state(price_state.links)
        
        
@price_router.message(F.contact , price_state.phone)
async def contacts(message: Message, state: FSMContext):
    user_id = message.from_user.id
    phone_number = message.contact.phone_number
    lang = await get_lang(user_id)
    await state.update_data(phone = phone_number)
    
    await bot.send_message(user_id, mess[lang]['name'], reply_markup=types.ReplyKeyboardRemove())
    await state.set_state(price_state.name)
    
@price_router.message(F.text , price_state.name)
async def contacts(message: Message, state: FSMContext):
    user_id = message.from_user.id
    text = message.text
    lang = await get_lang(user_id)
    await state.update_data(name = text)
    
    btn = skip_comp_button(lang)
    await bot.send_message(user_id, mess[lang]['company'], reply_markup=btn.as_markup())
    await state.set_state(price_state.comp_name)
    
@price_router.message(F.text , price_state.comp_name)
async def contacts(message: Message, state: FSMContext):
    user_id = message.from_user.id
    text = message.text
    lang = await get_lang(user_id)
    await state.update_data(comp_name = text)
    
    btn = skip_links_button(lang)
    await bot.send_message(user_id, mess[lang]['links'], reply_markup=btn.as_markup())
    await state.set_state(price_state.links)
    
@price_router.callback_query(F.data == "skip_comp", price_state.comp_name)
async def user_start(callback_query: types.callback_query, state: FSMContext):    
    user_id = callback_query.from_user.id
    lang = await get_lang(user_id)
    await state.update_data(comp_name = '')
    
    btn = skip_links_button(lang)
    await bot.send_message(user_id, mess[lang]['links'], reply_markup=btn.as_markup())
    await state.set_state(price_state.links)
    
@price_router.message(F.text , price_state.links)
async def contacts(message: Message, state: FSMContext):
    user_id = message.from_user.id
    text = message.text
    lang = await get_lang(user_id)
    await state.update_data(links = text)
    
    await bot.send_message(user_id, mess[lang]['target'])
    await state.set_state(price_state.target)
    
@price_router.callback_query(F.data == "skip_links", price_state.links)
async def user_start(callback_query: types.callback_query, state: FSMContext):    
    user_id = callback_query.from_user.id
    lang = await get_lang(user_id)
    await state.update_data(links = '')
    
    await bot.send_message(user_id, mess[lang]['target'])
    await state.set_state(price_state.target)
    
@price_router.message(F.text , price_state.target)
async def contacts(message: Message, state: FSMContext):
    user_id = message.from_user.id
    text = message.text
    lang = await get_lang(user_id)
    await state.update_data(target = text)
    
    btn = service_button(lang)
    await bot.send_message(user_id, mess[lang]['service'], reply_markup=btn.as_markup())
    await state.set_state(price_state.service)
    
@price_router.callback_query(ServiceCallback.filter(F.action == "select_service"))
async def user_start(callback_query: types.CallbackQuery,callback_data: ServiceCallback,state: FSMContext,):
    user_id = callback_query.from_user.id    
    service = callback_data.service_id
    lang = await get_lang(user_id)
    
    if service == 1:
        photo = FSInputFile(f"tgbot/docs/smm_{lang}.pdf")
        await bot.send_document(user_id, photo)
        
        await bot.send_message(user_id, mess[lang]['thanks'])
        photo = FSInputFile("tgbot/docs/thanks.gif")
        await bot.send_animation(user_id, photo)
    elif service == 2:
        photo = FSInputFile(f"tgbot/docs/pr_{lang}.pdf")
        await bot.send_document(user_id, photo)
        
        await bot.send_message(user_id, mess[lang]['thanks'])
        photo = FSInputFile("tgbot/docs/thanks.gif")
        await bot.send_animation(user_id, photo)
    elif service == 3:
        photo = FSInputFile(f"tgbot/docs/digital_{lang}.pdf")
        await bot.send_document(user_id, photo)
        
        await bot.send_message(user_id, mess[lang]['thanks'])
        photo = FSInputFile("tgbot/docs/thanks.gif")
        await bot.send_animation(user_id, photo)
    elif service == 4:
        photo = FSInputFile(f"tgbot/docs/merch_{lang}.pdf")
        await bot.send_document(user_id, photo)
        
        await bot.send_message(user_id, mess[lang]['thanks'])
        photo = FSInputFile("tgbot/docs/thanks.gif")
        await bot.send_animation(user_id, photo)
    elif service == 5:
        photo = FSInputFile(f"tgbot/docs/expo_{lang}.pdf")
        await bot.send_document(user_id, photo)
        
        await bot.send_message(user_id, mess[lang]['thanks'])
        photo = FSInputFile("tgbot/docs/thanks.gif")
        await bot.send_animation(user_id, photo)
    elif service == 6:
        photo = FSInputFile(f"tgbot/docs/branding_{lang}.pdf")
        await bot.send_document(user_id, photo)
        
        await bot.send_message(user_id, mess[lang]['thanks'])
        photo = FSInputFile("tgbot/docs/thanks.gif")
        await bot.send_animation(user_id, photo)
    elif service == 7:
        photo = FSInputFile(f"tgbot/docs/influence_{lang}.pdf")
        await bot.send_document(user_id, photo)
        
        await bot.send_message(user_id, mess[lang]['thanks'])
        photo = FSInputFile("tgbot/docs/thanks.gif")
        await bot.send_animation(user_id, photo)
    elif service == 8:
        photo = FSInputFile(f"tgbot/docs/media_ads_{lang}.pdf")
        await bot.send_document(user_id, photo)
        
        await bot.send_message(user_id, mess[lang]['thanks'])
        photo = FSInputFile("tgbot/docs/thanks.gif")
        await bot.send_animation(user_id, photo)
    
    data = await state.get_data()
    service = service - 1
    message=f'''Пользователь: @{callback_query.from_user.username}
Тип: узнать прайс
Имя: {data["name"]}
Телефон: {data["phone"]}
Название компании: {data["comp_name"]}
Ссылки: {data["links"]}
Цель: {data["target"]}
Услуга: {services_arr[service]}
'''    
    await update_user(user_id,data["phone"],data["name"],data["comp_name"],data["links"],data["target"])
    await bot.send_message(config.tg_bot.chat, message)    
    await state.clear()
    