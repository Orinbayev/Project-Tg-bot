# handlers/join_requests.py
from aiogram import Router
from aiogram.types import ChatJoinRequest

join_router = Router()

# user_id => {channel_id1, channel_id2, ...}
user_join_requests = {}

@join_router.chat_join_request()
async def handle_join_request(event: ChatJoinRequest):
    user_id = event.from_user.id
    channel_id = str(event.chat.id)

    if user_id not in user_join_requests:
        user_join_requests[user_id] = set()

    user_join_requests[user_id].add(channel_id)

    # ❌ Zayafka qabul qilinmaydi!
    # ❗ faqat foydalanuvchini "zayafka yubordi" deb belgilaymiz
