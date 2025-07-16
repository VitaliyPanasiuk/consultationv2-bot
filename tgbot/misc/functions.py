from aiogram import Router, Bot, types
from aiogram.types import Message, FSInputFile
from tgbot.config import load_config
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup

from db.db import get_pool_func

import datetime
import asyncio

config = load_config(".env")

# async with db_pool.acquire() as connection:

async def reg_user(user_id, name, username):
    db_pool = await get_pool_func()
    async with db_pool.acquire() as connection:
        user = await connection.fetchrow(f"SELECT user_id FROM users WHERE user_id = {user_id}")

        if user:
            return 
        else:
            await connection.execute(f"INSERT INTO users (user_id, user_name, name) VALUES ({user_id}, '@{username}', '{name}')")
            

async def update_lang(user_id, lang):
    db_pool = await get_pool_func()
    async with db_pool.acquire() as connection:     
        await connection.execute(f"UPDATE users set lang = '{lang}' where user_id = {user_id}")       
            
async def get_lang(user_id):
    db_pool = await get_pool_func()
    async with db_pool.acquire() as connection:
        lang = await connection.fetchrow(f"SELECT lang FROM users WHERE user_id = {user_id}")            
    return  lang[0]     

async def update_user(user_id, phone, name, comp_name, links, target):
    db_pool = await get_pool_func()
    async with db_pool.acquire() as connection:   
        if comp_name and links:
            print('comp_name and links')
            await connection.execute(f"UPDATE users set phone = '{phone}',name = '{name}',company_name = '{comp_name}',links = '{links}',target = '{target}'  where user_id = {user_id}") 
        elif comp_name:
            print('comp_name')
            await connection.execute(f"UPDATE users set phone = '{phone}',name = '{name}',company_name = '{comp_name}',target = '{target}'  where user_id = {user_id}")
        elif links:
            print('links')
            await connection.execute(f"UPDATE users set phone = '{phone}',name = '{name}',links = '{links}',target = '{target}'  where user_id = {user_id}")
        else:
            print('nothing')
            await connection.execute(f"UPDATE users set phone = '{phone}',name = '{name}',target = '{target}'  where user_id = {user_id}")
            
            
async def get_user_data(user_id):
    db_pool = await get_pool_func()
    async with db_pool.acquire() as connection:
        data = await connection.fetchrow(f"SELECT phone,name,company_name,links,target FROM users WHERE user_id = {user_id}")            
    return  data