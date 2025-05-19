from aiogram.fsm.state import StatesGroup, State

class Reg(StatesGroup):
    code = State()
    name = State()
    group = State()
