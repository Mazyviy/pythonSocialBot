from aiogram.fsm.state import StatesGroup, State

class ClassStateRegistration(StatesGroup):
    role_registration = State()
    name_registration=State()
    date_registration=State()
    number_registration=State()
    adr_registration=State()