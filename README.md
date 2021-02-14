# Notifier
Telegram feed in custom channel. 
Based on [Pyrogram](https://github.com/pyrogram/pyrogram).

## Russian
Инструкция на русском доступна на [сайте](http://serverchan.ru/Notifier/).

Скрипту нужен только один внешний модуль - Pyrogram.
Установка с помощью PIP - `pip install pyrogram`.  
Скрипт требует данные с [сайта](https://my.telegram.org).

### Настройка скрипта
1. Заполните поля в файле `config.py`, открыв его в любом текстовом редакторе.
2. Заполните REGEX в `main.py`, открыв его в любом текстовом редакторе.
3. Запустите скрипт и авторизуйтесь.

### Настройка ленты
**ОБЯЗАТЕЛЬНО**  
Необходимо создать в телеграмме новый канал и отправить туда команду `>setmainchannel`.
Теперь этот канал - ваша лента.

Для добавления канала в ленту переслать куда либо пост с нужного канала и ответить на него командой
`>addchannel`

Для удаления канала из ленты переслать куда либо пост с нужного канала и ответить на него командой
`>removechannel`

Для просмотра списка каналов написать в любой чат команду
`>list`

## English
The script needs only one external module - pyrogram.
Installation with PIP - `pip install pyrogram`.  
The script requires data from the [site](https://my.telegram.org).

### Script setup
1. Fill in the fields in `config.py` by opening it in any text editor
2. Fill in the REGEX in `main.py` by opening it in any text editor
3. Run script and login.

### Customizing the feed
**IMPORTANT**  
It is necessary to create a new channel in the telegram and send the command `>setmainchannel` there.  
Now that channel is your feed.

To add a channel to the feed, forward the post somewhere from the desired channel and reply to it with the command
`>addchannel`

To remove a channel from the feed, send a post somewhere from the desired channel and reply to it with the command
`>removechannel`

To view the list of channels, write a command to any chat
`>list`
