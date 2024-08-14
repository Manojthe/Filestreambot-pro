import os
import asyncio
import requests as HTTP
from asyncio import TimeoutError
from pyrogram import filters, Client
from pyrogram.errors import FloodWait, UserNotParticipant
from pyrogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton
from Adarsh.bot import StreamBot
from Adarsh.utils.database import Database
from Adarsh.utils.human_readable import humanbytes
from Adarsh.vars import Var
from Adarsh.utils.file_properties import get_name, get_hash, get_media_file_size

# Initialize databases
db = Database(Var.DATABASE_URL, Var.name)
pass_db = Database(Var.DATABASE_URL, "ag_passwords")

# Retrieve the password from environment variables
MY_PASS = os.environ.get("MY_PASS", None)

@StreamBot.on_message((filters.regex("login🔑") | filters.command("login")), group=4)
async def login_handler(c: Client, m: Message):
    try:
        ag = await m.reply_text("Now send me password.\n\n If You don't know check the MY_PASS Variable in heroku \n\n(You can use /cancel command to cancel the process)")
        try:
            _text = await c.listen(m.chat.id, filters=filters.text, timeout=90)
            if _text.text:
                textp = _text.text
                if textp == "/cancel":
                    await ag.edit("Process Cancelled Successfully")
                    return
                if textp == MY_PASS:
                    await pass_db.add_user_pass(m.chat.id, textp)
                    ag_text = "yeah! you entered the password correctly"
                else:
                    ag_text = "Wrong password, try again"
                await ag.edit(ag_text)
            else:
                return
        except TimeoutError:
            await ag.edit("I can't wait more for password, try again")
    except Exception as e:
        print(e)

@StreamBot.on_message((filters.private) & (filters.document | filters.video | filters.audio | filters.photo), group=4)
async def private_receive_handler(c: Client, m: Message):
    if MY_PASS:
        check_pass = await pass_db.get_user_pass(m.chat.id)
        if check_pass is None:
            await m.reply_text("Login first using /login cmd \n don't know the pass? request it from the Developer")
            return
        if check_pass != MY_PASS:
            await pass_db.delete_user(m.chat.id)
            return

    if not await db.is_user_exist(m.from_user.id):
        await db.add_user(m.from_user.id)
        await c.send_message(
            Var.BIN_CHANNEL,
            f"New User Joined! : \n\n Name : [{m.from_user.first_name}](tg://user?id={m.from_user.id}) Started Your Bot!!"
        )

    if Var.UPDATES_CHANNEL != "None":
        try:
            user = await c.get_chat_member(Var.UPDATES_CHANNEL, m.chat.id)
            if user.status == "kicked":
                await c.send_message(
                    chat_id=m.chat.id,
                    text="You are banned!\n\n  **Cᴏɴᴛᴀᴄᴛ Support [Support](https://t.me/Hollywood_in_HindiHD) They Wɪʟʟ Hᴇʟᴘ Yᴏᴜ**",
                    disable_web_page_preview=True
                )
                return
        except UserNotParticipant:
            await c.send_message(
                chat_id=m.chat.id,
                text="""<i>𝙹𝙾𝙸𝙽 UPDATES CHANNEL 𝚃𝙾 𝚄𝚂𝙴 𝙼𝙴 🔐</i>""",
                reply_markup=InlineKeyboardMarkup(
                    [
                        [
                            InlineKeyboardButton("Jᴏɪɴ ɴᴏᴡ 🔓", url=f"https://t.me/{Var.UPDATES_CHANNEL}")
                        ]
                    ]
                ),
            )
            return
        except Exception as e:
            await m.reply_text(e)
            await c.send_message(
                chat_id=m.chat.id,
                text="**Sᴏᴍᴇᴛʜɪɴɢ ᴡᴇɴᴛ Wʀᴏɴɢ. Cᴏɴᴛᴀᴄᴛ ᴍʏ Support** [Support](https://t.me/Hollywood_in_HindiHD)",
                disable_web_page_preview=True
            )
            return

    # New functionality for Terabox links
    if m.text and "teraboxapp.com" in m.text:
        await c.send_chat_action(chat_id=m.chat.id, action="typing")
        ms = m.text
        url = f"https://teraboxvideodownloader.nepcoderdevs.workers.dev/?url={ms}"

        try:
            response = HTTP.get(url)
            if response.status_code == 200:
                data = response.json()
                resolutions = data["response"][0]["resolutions"]
                fast_download_link = resolutions["Fast Download"]
                hd_video_link = resolutions["HD Video"]
                thumbnail_url = data["response"][0]["thumbnail"]
                video_title = data["response"][0]["title"]

                markup = InlineKeyboardMarkup()
                markup.row(
                    InlineKeyboardButton(text='➡️ Fast Download', url=fast_download_link),
                    InlineKeyboardButton(text='▶️ HD Video', url=hd_video_link)
                )
                markup.row(
                    InlineKeyboardButton(text='Developer', url='t.me/Privates_Bots')
                )

                message_text = f"🎬 <b>Title:</b> {video_title}\nMade with ❤️ by @Privates_Bots"

                await c.send_photo(
                    chat_id=m.chat.id,
                    photo=thumbnail_url,
                    caption=message_text,
                    parse_mode="HTML",
                    reply_markup=markup
                )
            else:
                await c.send_message(
                    chat_id=m.chat.id,
                    text="❌ <b>Error fetching data from Terabox API</b>",
                    parse_mode="HTML"
                )
        except Exception as e:
            await c.send_message(
                chat_id=m.chat.id,
                text=f"❌ <b>Error: {str(e)}</b>",
                parse_mode="HTML"
            )

    else:
        # Existing functionality for handling media
        try:
            log_msg = await m.forward(chat_id=Var.BIN_CHANNEL)
            stream_link = f"https://manojthe.github.io?PIN={Var.URL}{str(log_msg.id)}/{quote_plus(get_name(log_msg))}?hash={get_hash(log_msg)}"
            online_link = f"{Var.URL}{str(log_msg.id)}/{quote_plus(get_name(log_msg))}?hash={get_hash(log_msg)}"
            
            msg_text = """<i><u>𝗬𝗼𝘂𝗿 𝗟𝗶𝗻𝗸 𝗚𝗲𝗻𝗲𝗿𝗮𝘁𝗲𝗱 !</u></i>\n\n<b>📂 Fɪʟᴇ ɴᴀᴍᴇ :</b> <i>{}</i>\n\n<b>📦 Fɪʟᴇ ꜱɪᴢᴇ :</b> <i>{}</i>\n\n<b>🚸 Nᴏᴛᴇ : LINK WILL NOT EXPIRE UNTIL I DELETE</b>\n\n<b>🚸 Terabox Download : https://manojthe.github.io/tera</b>"""

            await log_msg.reply_text(
                text=f"**RᴇQᴜᴇꜱᴛᴇᴅ ʙʏ :** [{m.from_user.first_name}](tg://user?id={m.from_user.id})\n**Uꜱᴇʀ ɪᴅ :** `{m.from_user.id}`\n**Stream ʟɪɴᴋ :** {stream_link}",
                disable_web_page_preview=True,
                quote=True
            )
            await m.reply_text(
                text=msg_text.format(get_name(log_msg), humanbytes(get_media_file_size(m)), online_link, stream_link),
                quote=True,
                disable_web_page_preview=True,
                reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("STREAM 🖥 & Dᴏᴡɴʟᴏᴀᴅ📥", url=stream_link)]])
            )
        except FloodWait as e:
            print(f"Sleeping for {str(e.x)}s")
            await asyncio.sleep(e.x)
            await c.send_message(
                chat_id=Var.BIN_CHANNEL,
                text=f"Gᴏᴛ FʟᴏᴏᴅWᴀɪᴛ ᴏғ {str(e.x)}s from [{m.from_user.first_name}](tg://user?id={m.from_user.id})\n\n**𝚄𝚜𝚎𝚛 𝙸𝙳 :** `{str(m.from_user.id)}`",
                disable_web_page_preview=True
            )

@StreamBot.on_message(filters.channel & ~filters.group & (filters.document | filters.video | filters.photo) & ~filters.forwarded, group=-1)
async def channel_receive_handler(bot, broadcast):
    if MY_PASS:
        check_pass = await pass_db.get_user_pass(broadcast.chat.id)
        if check_pass is None:
            await broadcast.reply_text("Login first using /login cmd \n don't know the pass
