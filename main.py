# -*- encoding: utf-8 -*-
import logging
import asyncio

from pyrogram import Client, filters
from pyrogram.types import Message

__author__ = "Shamiko Tooru"

# 这里填写你在 BotFather 和 my.telegram.org 获得到的那些参数
app = Client("channel_bot", bot_token="",
             api_hash="", api_id="")
logging.basicConfig(level=logging.INFO)


class Timer:
    def __init__(self, callback, timeout):
        logging.info("Created a schedule interval as " + str(timeout) + " seconds.")
        loop = asyncio.get_event_loop()
        self.callback = callback
        self.timeout = timeout
        self.task = loop.create_task(self.wait())

    async def wait(self):
        await asyncio.sleep(self.timeout)
        logging.info("Successfully executed a timer schedule.")
        await self.callback

    def stop(self):
        try:
            self.task.cancel()
        except asyncio.CancelledError:
            pass


async def unban(client: Client, chat_id, user_id):
    await client.unban_chat_member(chat_id, user_id)
    await client.send_message(chat_id, "已解封用户 ID:" + str(user_id))


@app.on_message(filters.forwarded & ~filters.edited)
async def gen_poll(client: Client, message: Message):
    await client.send_poll(message.chat.id, "你对本条消息的打分？", ["1", "2", "3", "4", "5"], is_anonymous=True,
                           reply_to_message_id=message.message_id)


@app.on_message(filters.new_chat_members)
async def kick_member(client: Client, message: Message):
    await client.delete_messages(message.chat.id, message.message_id)
    await client.kick_chat_member(user_id=message.from_user.id, chat_id=message.chat.id)
    Timer(unban(client, message.chat.id, message.from_user.id), 10)
    # 此处上面的 10 是发现用户加群的解封间隔，单位为秒，修改完别忘了把下面的 10s 后自动解封也改了
    await client.send_message(message.chat.id, "检测到用户ID: " + str(message.from_user.id) + " 加入频道附属群，已踢出，10s 后自动解封。")


try:
    app.run()
except KeyboardInterrupt as e:
    quit(0)
except Exception as e:
    print(e)
    quit(-1)
