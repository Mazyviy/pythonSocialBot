from datetime import datetime
import re
async def check_address_format(address, check_adr_3_words=False):
    pattern = r'^[А-Яа-яЁё\s]+,\s*[\d\s]?[А-Яа-яЁё\s]+\s*\d*,\s*\d+\s*[а-яА-Я]?\s*,\s*\d+\s*[а-яА-Я]?$'
    if check_adr_3_words == True:
        pattern = r'^[А-Яа-яЁё\s]+,\s*[\d\s]?[А-Яа-яЁё\s]+\s*\d*,\s*\d+\s*[а-яА-Я]?\s*?$'

    if re.match(pattern, address):
        return True
    else:
        return False

# Функция для проверки корректности введеной даты рождения от пользователя
async def validate_date(date_string):
    try:
        date_obj = datetime.strptime(date_string, '%d.%m.%Y')
        current_date = datetime.now()

        if date_obj < current_date:
            return True, date_obj
        else:
            return False, None
    except ValueError:
        return False, None