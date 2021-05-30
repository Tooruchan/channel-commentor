# -*- encoding: utf-8 -*-
import logging
import asyncio

from pyrogram import Client, filters
from pyrogram.types import Message, User, ChatPermissions

__author__ = "Shamiko Tooru"

# 这里填写你在 BotFather 和 my.telegram.org 获得到的那些参数
app = Client("channel_bot", bot_token="",
             api_hash="", api_id="")


class Timer:
    def __init__(self, callback, timeout):
        # logging.info("Created a schedule interval as " + str(timeout) + " seconds.")
        loop = asyncio.get_event_loop()
        self.callback = callback
        self.timeout = timeout
        self.task = loop.create_task(self.wait())

    async def wait(self):
        await asyncio.sleep(self.timeout)
        # logging.info("Successfully executed a timer schedule.")
        await self.callback

    def stop(self):
        try:
            self.task.cancel()
        except asyncio.CancelledError:
            pass


async def del_remider(client: Client, chat_id, msg: Message):
    await client.delete_messages(chat_id, msg.message_id)


async def ban_user(client: Client, chat_id, user: User):
    await client.kick_chat_member(chat_id, user.id)
    await client.unban_chat_member(chat_id, user.id)
    await client.send_message(chat_id, "检测到用户ID: " + str(user.id) + " 加入频道附属群，已踢出，10s 后自动解封。")


async def unban(client: Client, chat_id, user):
    await client.unban_chat_member(chat_id, user.id)
    await client.send_message(chat_id, "已解封用户 ID:" + str(user.id))


@app.on_message(filters.forwarded & ~filters.edited)
async def gen_poll(client: Client, message: Message):
    await client.send_poll(message.chat.id, "你对本条消息的打分？", ["1", "2", "3", "4", "5"], is_anonymous=True,
                           reply_to_message_id=message.message_id)


@app.on_message(filters.new_chat_members)
async def kick_member(client: Client, message: Message):
    user = message.from_user
    chat_id = message.chat.id
    remind_msg = await message.reply("本群为频道附属评论群，请勿直接加入，此信息为警告信息，30s 后您将会被自动踢出。")
    await client.restrict_chat_member(chat_id, user.id, ChatPermissions())
    Timer(del_remider(client, chat_id, remind_msg), 30)
    Timer(ban_user(client, chat_id, user), 30)
    Timer(unban(client, chat_id, user), 45)
    # 此处上面的 10 是发现用户加群的解封间隔，单位为秒，修改完别忘了把下面的 10s 后自动解封也改了


try:
    app.run()
except KeyboardInterrupt as e:
    quit(0)
except Exception as e:
    print(e)
    quit(-1)
