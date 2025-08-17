import sqlite3,asyncio
from pyrogram import Client,filters
import config

DB_PATH="Notifier.db"
app=Client(config.session_name,config.api_id,config.api_hash)
CHANNELS=set()

def _conn():
    c=sqlite3.connect(DB_PATH)
    c.execute("PRAGMA journal_mode=WAL")
    c.execute("PRAGMA foreign_keys=ON")
    return c

def ensure_schema():
    with _conn() as c:
        c.execute("CREATE TABLE IF NOT EXISTS settings (notifychannel_id INTEGER)")
        c.execute("CREATE TABLE IF NOT EXISTS channels (channel_id INTEGER PRIMARY KEY)")
        cur=c.execute("SELECT COUNT(1) FROM settings")
        if cur.fetchone()[0]==0:
            c.execute("INSERT INTO settings(notifychannel_id) VALUES (NULL)")

def get_notify_channel():
    with _conn() as c:
        cur=c.execute("SELECT notifychannel_id FROM settings LIMIT 1")
        row=cur.fetchone()
        return row[0] if row else None

def set_notify_channel(cid:int):
    with _conn() as c:
        c.execute("UPDATE settings SET notifychannel_id=?", (cid,))

def add_channel(cid:int):
    with _conn() as c:
        c.execute("INSERT OR IGNORE INTO channels(channel_id) VALUES(?)",(cid,))
    CHANNELS.add(cid)

def remove_channel(cid:int):
    with _conn() as c:
        c.execute("DELETE FROM channels WHERE channel_id=?",(cid,))
    CHANNELS.discard(cid)

def list_channel_ids():
    with _conn() as c:
        return [r[0] for r in c.execute("SELECT channel_id FROM channels ORDER BY channel_id")]

def refresh_channels():
    global CHANNELS
    CHANNELS=set(list_channel_ids())

ensure_schema()
refresh_channels()

@app.on_message(filters.command(["addchannel","добавитьканал"],config.command_prefix))
async def cmd_addchannel(client,message):
    if not message.from_user or not message.from_user.is_self: return
    if not message.reply_to_message or not getattr(message.reply_to_message,"forward_from_chat",None): 
        await message.reply_text("Нужно ответить на пересланное сообщение из канала.")
        return
    ch=message.reply_to_message.forward_from_chat
    try:
        add_channel(int(ch.id))
        await message.delete()
        await message.reply_text(f"Канал <b>{ch.title}</b> добавлен в ленту.",parse_mode="HTML")
    except Exception:
        await message.reply_text("Ошибка добавления канала.")

@app.on_message(filters.command(["removechannel","удалитьканал"],config.command_prefix))
async def cmd_removechannel(client,message):
    if not message.from_user or not message.from_user.is_self: return
    if not message.reply_to_message or not getattr(message.reply_to_message,"forward_from_chat",None):
        await message.reply_text("Нужно ответить на пересланное сообщение из канала.")
        return
    ch=message.reply_to_message.forward_from_chat
    try:
        remove_channel(int(ch.id))
        await message.delete()
        await message.reply_text(f"Канал <b>{ch.title}</b> удалён из ленты.",parse_mode="HTML")
    except Exception:
        await message.reply_text("Ошибка удаления канала.")

@app.on_message(filters.command(["list","список"],config.command_prefix))
async def cmd_list(client,message):
    if not message.from_user or not message.from_user.is_self: return
    ids=list(CHANNELS)
    if not ids:
        await message.reply_text("Список каналов пуст.")
        return
    text="Текущий список каналов для ленты:\n"
    i=1
    for cid in ids:
        title=f"ID {cid}"
        try:
            chat=await client.get_chat(cid)
            title=chat.title or title
        except Exception:
            pass
        text+=f"<b>[{i}]</b> {title}\n"
        i+=1
    await message.reply_text(text,parse_mode="HTML")

@app.on_message(filters.command(["setmainchannel","установитьглавканал"],config.command_prefix))
async def cmd_setmain(client,message):
    try:
        cid=int(message.chat.id)
        set_notify_channel(cid)
        await message.delete()
        await message.reply_text("Этот канал установлен как лента.",parse_mode="HTML")
    except Exception:
        await message.reply_text("Ошибка установки ленты.")

@app.on_message(filters.channel & ~filters.service)
async def channel_forwarder(client,message):
    try:
        if int(message.sender_chat.id) not in CHANNELS: return
        dst=get_notify_channel()
        if not dst: return
        await message.forward(int(dst))
    except Exception:
        pass

app.run()
