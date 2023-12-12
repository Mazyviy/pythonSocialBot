from aiogram.fsm.state import StatesGroup, State

class ClassStateRegestration(StatesGroup):
    role_regestration = State()
    name_regestration=State()
    date_regestration=State()
    number_regestration=State()
    adr_regestration=State()