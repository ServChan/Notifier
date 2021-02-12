from pyrogram import Client, filters
import sqlite3
import config

app=Client(config.session_name, config.api_id, config.api_hash)

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

@app.on_message(filters.command(["addchannel", "добавитьканал"], config.command_prefix)) #Команды можно сменить или добавить, текущая команда - ">addchannel"
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

@app.on_message(filters.regex(".*@LTS_Server.*")) #REGEX фильтры. Простейший фильтр - ".*ЧТОТОЛОВИМ.*", так будут пойманы все сообщения со словом ЧТОТОЛОВИМ
async def mentionmanager(client, message):
    await message.forward(getchannel())
    print("Mention captured")

#REGEX фильтры. Данный фильтр отвечает за ники. ".*" в начале и конце сообщения отвечает за поимку ника в любом месте сообщения.
#Для того, чтобы ловило и с маленькими, и с большими буквами используем [Ss]. Так для бота нет разницы, Server или server.
#Несколько вариантов ника задаем через |, прямую черту.
@app.on_message(filters.regex(".*[Ss]erver-[Cc]han.*|.*[Ss]erver[Cc]han.*"))
async def mentionmanager(client, message):
    if not message.from_user.is_bot:
        await message.forward(getchannel())
        print("Nick captured")

app.run()