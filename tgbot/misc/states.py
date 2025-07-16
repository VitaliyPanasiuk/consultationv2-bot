from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup


class consult_state(StatesGroup):
    phone = State()
    name = State()
    comp_name = State()
    links = State()
    target = State()
    
class price_state(StatesGroup):
    phone = State()
    name = State()
    comp_name = State()
    links = State()
    target = State()
    service = State()
