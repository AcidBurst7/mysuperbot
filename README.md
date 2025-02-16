### Развитие проекта временно остановлено

# Mr. NASA Bot :rocket: :speech_balloon:

## Бот, который отправляет вам картинку из NASA

### Задачи в процессе
- [ ] сделать кнопки вместо команд /today_picture и /calendar сделать "Картинка дня" и "Картинка из календарика"

### Задачи в плане
- [ ] дать пользователю возможность управления расписанием для отправки картинки дня (оптравка на конкретную дату)
- [ ] дать пользователю возможность отключить отправку картинки дня 
- [ ] улучшить вывод результата в консоль при выполнении deploy.py - убрать юникод и лишние пробелы
- [ ] команда /random_picture - присылает рандомную кратинку в период с 1995 года по 2025
- [ ] написать тесты
- [ ] подключить русский язык для календарика
- [ ] перевод перевод заголовка картинки через парсинг google translate

### Сделано
- [x] реализовать автоматическую отправку сообщений по расписанию каждое утро в 8.00
- [x] реализовать календарь который позволит выбрать дату и получить картинку дня
- [x] бот по команде /start приветствует и знакомит с командой /today_picture
- [x] бот по команде /today_picture выдает картинку на сегодня
- [x] файл deploy.py для подключения к удаленному серверу и перезапуска docker'a
- [x] заполнена информация о боте перед командой /start
- [x] сохранение данных о формате, так как это может быть и картинка и видео