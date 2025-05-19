import re

# Проверка имени
def validate_full_name(name: str) -> tuple[bool, str]:
    """
    Валидирует ФИО
    
    Returns:
        tuple: (is_valid, error_message)
    """
    name = name.strip()
    
    # Проверка на пустоту
    if not name:
        return False, "ФИО не может быть пустым"
    
    # Проверка длины
    if len(name) < 5:
        return False, "ФИО слишком короткое (минимум 5 символов)"
    
    if len(name) > 100:
        return False, "ФИО слишком длинное (максимум 100 символов)"
    
    # Проверка на допустимые символы
    if not re.match(r'^[а-яёА-ЯЁa-zA-Z\s\-]+$', name):
        return False, "ФИО может содержать только буквы, пробелы и дефисы"
    
    # Проверка на количество слов
    words = name.split()
    if len(words) < 2:
        return False, "Введите как минимум имя и фамилию"
    
    if len(words) > 4:
        return False, "ФИО содержит слишком много слов"
    
    # Проверка на минимальную длину каждого слова
    for word in words:
        if len(word) < 2:
            return False, f"Слово '{word}' слишком короткое"
    
    return True, ""
