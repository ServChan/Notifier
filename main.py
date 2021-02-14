from pyrogram import Client, filters
import sqlite3
import config

app = Client(config.session_name, config.api_id, config.api_hash)


def database_connect(command):
    conn = sqlite3.connect("Notifier.db")
    cursor = conn.cursor()
    try:
        cursor.execute(command)
    except Exception as Ex:
        print(Ex)
    results = cursor.fetchall()
    conn.commit()
    conn.close()
    return results

# Команды можно сменить или добавить, текущая команда - ">addchannel"
# Commands can be changed or added, the current command is ">addchannel"
@app.on_message(filters.command(["addchannel", "добавитьканал"], config.command_prefix))
async def addchannel(client, message):
    if message.reply_to_message and message.from_user.is_self:
        try:
            database_connect(f"INSERT INTO channels (channel_id) VALUES (\'{message.reply_to_message.forward_from_chat.id}\')")
            await message.delete()
            await message.reply_text(f"Обновления канала <b>{message.reply_to_message.forward_from_chat.title}</b> будут показаны в ленте.", parse_mode="HTML")
        except Exception as Ex:
            await message.reply_text(f"Ошибка добавления канала")


@app.on_message(filters.command(["removechannel", "удалитьканал"], config.command_prefix))
async def addchannel(client, message):
    if message.reply_to_message and message.from_user.is_self:
        try:
            database_connect(f"DELETE FROM channels WHERE channel_id={message.reply_to_message.forward_from_chat.id}")
            await message.delete()
            await message.reply_text(f"Обновления канала <b>{message.reply_to_message.forward_from_chat.title}</b> больше не будут показаны в ленте.", parse_mode="HTML")
        except Exception as Ex:
            await message.reply_text(f"Ошибка удаления канала")


@app.on_message(filters.command(["list", "список"], config.command_prefix))
async def channellist(client, message):
    if message.from_user.is_self:
        data = database_connect("SELECT * FROM channels")
        text = "Текущий список каналов для ленты:\n"
        i = 1
        for element in data:
            chat = await client.get_chat(element["channel_id"])
            chatname = chat.title
            text = text + f"<b>[{i}]</b> {chatname}\n"
            i = i+1
        await message.reply_text(text)


@app.on_message(filters.command(["setmainchannel", "установитьглавканал"], config.command_prefix))
async def setchannel(client, message):
    chat_id = message.sender_chat.id
    database_connect(f"DELETE FROM settings")
    database_connect(f"INSERT INTO settings (notifychannel_id) VALUES (\'{chat_id}\')")
    await message.delete()
    await message.reply_text(f"Данный канал установлен как лента.", parse_mode="HTML")


def getchannel():
    data = database_connect(f"SELECT * FROM settings")
    return data[0][0]


@app.on_message(filters.channel)
async def channelmanager(client, message):
    data = database_connect(f"SELECT * FROM channels WHERE channel_id={message.sender_chat.id}")
    try:
        if message.sender_chat.id == data[0][0]:
            await message.forward(int(getchannel()))
            print("Channel post captured")
        else:
            pass
    except IndexError:
        pass


# REGEX фильтры. Простейший фильтр - ".*ЧТОТОЛОВИМ.*", так будут пойманы все сообщения со словом ЧТОТОЛОВИМ
# REGEX filters. The simplest filter is ".*WHAT'S CAPTURE.*", So all messages with the word WHAT'S CAPTURE will be caught
# Раскомментируйте строки ниже, если вы хотите получать уведомление, когда упоминают ваш юзернейм
# Uncomment the lines below if you want to be notified when your username is mentioned
#@app.on_message(filters.regex(".*@LTS_Server.*"))
#async def mentionmanager(client, message):
#    if message.chat.username:
#        chat_id = message.chat.username
#    else:
#        chat_id = f"c/{str(message.chat.id)[4:]}"
#    await app.send_message(getchannel(), text=f"Пинг в чате {message.chat.title} от {message.from_user.first_name}\n<a href = \'t.me/{chat_id}/{message.message_id}\'>Перейти</a>", parse_mode="HTML")
#    await message.forward(getchannel())
#    print("Mention captured")


# REGEX фильтры. Данный фильтр отвечает за ники. ".*" в начале и конце сообщения отвечает за поимку ника в любом месте сообщения.
# Для того, чтобы ловило и с маленькими, и с большими буквами используем [Ss]. Так для бота нет разницы, Server или server.
# Несколько вариантов ника задаем через |, прямую черту.
# REGEX filters. This filter is responsible for nicknames. The ".*" at the beginning and end of the message is responsible for catching the nickname anywhere in the message.
# In order to catch both small and large letters use [Ss]. So for the bot there is no difference, Server or server.
# Several variants of the nickname are set through |, a straight line.
# Раскомментируйте строки ниже, если вы хотите получать уведомление, когда упоминают ваш ник
# Uncomment the lines below if you want to be notified when your nickname is mentioned
#@app.on_message(filters.regex(".*[Ss]erver-[Cc]han.*|.*[Ss]erver[Cc]han.*"))
#async def mentionmanager(client, message):
#    if not message.from_user.is_bot:
#        if message.chat.username:
#            chat_id = message.chat.username
#        else:
#            chat_id = f"c/{str(message.chat.id)[4:]}"
#        await app.send_message(getchannel(), text=f"Упоминание в чате {message.chat.title} от {message.from_user.first_name}\n<a href = \'t.me/{chat_id}/{message.message_id}\'>Перейти</a>", parse_mode="HTML")
#        await message.forward(getchannel())
#        print("Nick captured")

app.run()