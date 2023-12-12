from aiogram.fsm.state import StatesGroup, State

class ClassStateTaskProducts(StatesGroup):
    list_products = State()
    task_urgency_products = State()

class ClassStateTaskMedicines(StatesGroup):
    list_medicines = State()
    task_urgency_medicines = State()

class ClassStateTaxi(StatesGroup):
    first_adress_taxi = State()
    second_adress_taxi = State()
    task_urgency_taxi = State()

class ClassStateDoctor(StatesGroup):
    health_complaint = State()
    task_urgency_doctor = State()