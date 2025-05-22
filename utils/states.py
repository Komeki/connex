from aiogram.fsm.state import StatesGroup, State

# Регистрация студента
class Reg(StatesGroup):
    code = State()
    name = State()
    course = State()
    major = State()
    group = State()

# Регистрация админа
class AdminReg(StatesGroup):
    waiting_for_fullname = State()
    waiting_for_status = State()

# Создание мероприятия
class CreateEvent(StatesGroup):
    name = State()
    description = State()
    start_time = State()
    end_time = State()
    location = State()
    image = State()
