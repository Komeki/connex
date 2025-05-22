# Connex b01

## TODO
- [ ] Автоматическая смена актуальности мероприятия (1 -> 0)
- [ ] Кнопочная регистрация
- [ ] Все факультеты
- [ ] Указание создателя ивента
- [ ] ...
```
def deactivate_finished_events()
```

## Изменения
Переработана система администратора
Добавлены декораторы (@admin_required, @user) и теперь не нужно в каждой функции проверять на админа по типу:
```
if not is_admin(message.from_user.id)
    return
```
#### CALLBACKS
Перенос хендлеров с коллбеками в отдельную папку для коллбеков. 
- handlers/..._callbacks.py -> callbacks/..._callb.py

#### DB Tables
Изменены все связи с БД, особенно по отношению к таблице events.
##### Users:
- user_id
- telegram - @username
- full_name
- course
- faculty
- group_num
- organisation - организация
- registration_date
- curator (0/1) - является куратором или нет

##### events:
- id
- name
- description
- start_date - начало
- duration - длительность (end_date будет вычисляться путем сложения)
- location
- valid - актуально ли мероприятие; после окончания актуальности должно быть 0
- image_id
- curator_id

##### registrations:
- id
- user_id
- event_id
- registration_date
- attended (0/1) - присутствовал ли на самом деле
- points

##### admins:
- user_id
- full_name
- status_text
