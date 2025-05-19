from aiogram.fsm.state import StatesGroup, State

# Регистрация студента
class Reg(StatesGroup):
    code = State()
    name = State()
    group = State()

# Создание мероприятия и его перенос в БД
class CreateEvent(StatesGroup):
    name = State()
    description = State()
    time = State()
    location = State()
    image = State()
