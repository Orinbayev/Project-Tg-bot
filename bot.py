import asyncio
from aiogram import Bot, Dispatcher, F, types
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.filters import Command
from config import BOT_TOKEN, ADMIN_IDS, SUPER_ADMIN_ID
from db import init_db, get_channels, add_channel, remove_channel
from db_kino import init_kino_db, add_movie, read_db, delete_movie, update_movie, get_all_users, init_users_table
from users_db import get_total_users, get_new_users_in_last_24h, get_active_users_in_last_7d
from states import AddMediaState
from keyboards import (
    admin_panel_keyboard, kino_panel_keyboard, kanal_panel_keyboard,
    confirm_keyboard, broadcast_confirm_keyboard, get_subscribe_keyboard,
    admin_manage_keyboard
)
from states import AdminStates
from db_admins import init_admin_db, add_admin, is_admin, remove_admin, get_all_admins

bot = Bot(BOT_TOKEN)
dp = Dispatcher(storage=MemoryStorage())

# === Subscription check ===
async def check_subscriptions(user_id: int) -> bool:
    channels = await get_channels()
    for channel_id, _, _ in channels:
        try:
            member = await bot.get_chat_member(int(channel_id), user_id)
            if member.status not in ("member", "administrator", "creator"):
                return False
        except:
            return False
    return True

from db_kino import add_user
from users_db import register_user

# === FSM Message Handlers ===
@dp.message(AdminStates.waiting_for_broadcast)
async def confirm_broadcast(message: Message, state: FSMContext):
    await state.update_data(broadcast_msg=message)
    await message.reply("Tasdiqlaysizmi?", reply_markup=broadcast_confirm_keyboard())

@dp.message(AdminStates.waiting_for_channel_username)
async def add_channel_username(message: Message, state: FSMContext):
    text = (message.text or '').strip()
    try:
        if text.startswith("@"):
            chat = await bot.get_chat(text)
            cid = chat.id
            uname = chat.username or "private"
            await add_channel(str(cid), uname, "")
            await message.answer(f"✅ Kanal qo'shildi: @{uname} — `{cid}`", parse_mode="Markdown")
            await state.clear()
        elif text.lstrip("-").isdigit():
            await state.update_data(cid=text)
            await message.answer("🔗 Endi shu kanalning invite linkini yuboring (masalan: https://t.me/+xxxx):")
            await state.set_state(AdminStates.waiting_for_channel_invite_link)
        else:
            await message.answer("❌ Noto'g'ri format! Username yoki kanal ID yuboring.")
    except Exception as e:
        await message.answer(f"⚠️ Xatolik: {e}")
        await state.clear()

@dp.message(AdminStates.waiting_for_channel_invite_link)
async def add_channel_invite_link(message: Message, state: FSMContext):
    data = await state.get_data()
    cid = data.get("cid")
    invite_link = (message.text or '').strip()
    if not (invite_link.startswith("https://t.me/+") or invite_link.startswith("t.me/+")):
        return await message.answer("❌ Noto'g'ri format! Invite link yuboring (masalan: https://t.me/+xxxx).")
    await add_channel(str(cid), "private", invite_link)
    await message.answer(f"✅ Private kanal qo'shildi: {invite_link} — `{cid}`", parse_mode="Markdown")
    await state.clear()

@dp.message(AdminStates.waiting_for_channel_id_to_remove)
async def remove_channel_id(message: Message, state: FSMContext):
    await remove_channel(message.text)
    await message.answer(f"❌ Kanal `{message.text}` o'chirildi.", parse_mode="Markdown")
    await state.clear()

@dp.message(AddMediaState.waiting_for_link)
async def receive_link(message: Message, state: FSMContext):
    await state.update_data(link=message.text)
    await message.answer("📝 Kino tagiga yoziladigan caption matnini yuboring:")
    await state.set_state(AddMediaState.waiting_for_caption)

@dp.message(AddMediaState.waiting_for_caption)
async def receive_caption(message: Message, state: FSMContext):
    await state.update_data(caption=message.text)
    await message.answer("ℹ️ Kino haqida qo'shimcha ma'lumot:")
    await state.set_state(AddMediaState.waiting_for_info)

@dp.message(AddMediaState.waiting_for_info)
async def receive_info(message: Message, state: FSMContext):
    await state.update_data(info=message.text)
    await message.answer("🔢 Kodni kiriting (masalan: 101):")
    await state.set_state(AddMediaState.waiting_for_code)

@dp.message(AddMediaState.waiting_for_code)
async def receive_code(message: Message, state: FSMContext):
    if not message.text.isdigit():
        return await message.answer("❌ Kod faqat raqam bo'lishi kerak!")
    await state.update_data(code=int(message.text))
    data = await state.get_data()
    text = (
        f"🔗 Link: {data['link']}\n"
        f"📝 Caption: {data['caption']}\n"
        f"ℹ️ Info: {data['info']}\n"
        f"🔢 Code: {data['code']}\n\nTasdiqlaysizmi?"
    )
    await message.answer(text, reply_markup=confirm_keyboard())
    await state.set_state(AddMediaState.confirm)

@dp.message(AdminStates.waiting_for_delete_code)
async def delete_media_code(message: Message, state: FSMContext):
    if not message.text.isdigit():
        await message.answer("❌ Kod noto'g'ri.")
    else:
        deleted = delete_movie(int(message.text))
        if deleted:
            await message.answer("✅ Kino o'chirildi!")
        else:
            await message.answer("❌ Bunday kodli kino topilmadi!")
    await state.clear()

@dp.message(AdminStates.waiting_for_edit_code)
async def edit_media_code(message: Message, state: FSMContext):
    if not message.text.isdigit():
        await message.answer("❌ Kod faqat raqam bo'lishi kerak!")
        return
    await state.update_data(code=int(message.text))
    await message.answer("🆕 Yangi caption yuboring:")
    await state.set_state(AdminStates.waiting_for_new_caption)

@dp.message(AdminStates.waiting_for_new_caption)
async def edit_caption(message: Message, state: FSMContext):
    await state.update_data(caption=message.text)
    await message.answer("ℹ️ Yangi info yuboring:")
    await state.set_state(AdminStates.waiting_for_new_info)

@dp.message(AdminStates.waiting_for_new_info)
async def edit_info(message: Message, state: FSMContext):
    await state.update_data(info=message.text)
    await message.answer("🔗 Yangi link yuboring:")
    await state.set_state(AdminStates.waiting_for_new_link)

@dp.message(AdminStates.waiting_for_new_link)
async def edit_link(message: Message, state: FSMContext):
    data = await state.get_data()
    updated = update_movie(data['code'], data['caption'], data['info'], message.text)
    if updated:
        await message.answer("✅ Kino yangilandi!")
    else:
        await message.answer("❌ Yangilash amalga oshmadi. Kod mavjud emas.")
    await state.clear()

@dp.message(AdminStates.waiting_for_new_admin_id)
async def add_new_admin(message: Message, state: FSMContext):
    try:
        if not message.text or not message.text.isdigit():
            await message.answer("❌ Faqat raqamli Telegram ID yuboring!")
            await state.clear()
            return
        new_admin_id = int(message.text)
        result = add_admin(new_admin_id)
        if result:
            await message.answer(f"✅ Yangi admin qo'shildi: <code>{new_admin_id}</code>", parse_mode="HTML")
        else:
            await message.answer(f"⚠️ Bu ID allaqachon admin! <code>{new_admin_id}</code>", parse_mode="HTML")
    except Exception as e:
        await message.answer(f"❌ Xatolik: {e}")
    await state.clear()

@dp.message(AdminStates.waiting_for_remove_admin_id)
async def remove_admin_id(message: Message, state: FSMContext):
    try:
        remove_admin(int(message.text))
        await message.answer(f"❌ Admin o'chirildi: <code>{message.text}</code>", parse_mode="HTML")
    except Exception as e:
        await message.answer(f"❌ Xatolik: {e}")
    await state.clear()

# === Command Handlers ===
@dp.message(Command("start"))
async def start_handler(message: Message, state: FSMContext):
    if not message.from_user:
        return await message.answer("❌ Foydalanuvchi aniqlanmadi. Iltimos, qayta urinib ko‘ring.")
    full_name = message.from_user.full_name or "Foydalanuvchi"

    if not await check_subscriptions(message.from_user.id):
        channels = await get_channels()
        return await message.answer(
            f"👋 Salom, <b>{full_name}</b>!\n\n"
            "🔒 Botdan to‘liq foydalanish uchun quyidagi kanallarga obuna bo‘ling:",
            reply_markup=get_subscribe_keyboard(channels),
            parse_mode="HTML"
        )

    await message.answer(
        f"🎉 Xush kelibsiz, <b>{full_name}</b>!\n\n"
        "Bu bot orqali siz kinolarni maxsus kod orqali topishingiz mumkin.\n"
        "Kodni yuboring va kerakli kinoni ko‘ring!",
        parse_mode="HTML"
    )

@dp.message(Command("admin"))
async def admin_panel(message: Message):
    if not is_admin(message.from_user.id):
        return await message.answer("🚫 Sizda admin panelga kirish huquqi yo‘q.")
    await message.answer(
        "👨‍💻 <b>Admin paneliga xush kelibsiz!</b>\nQuyidagilardan birini tanlang:",
        reply_markup=admin_panel_keyboard(),
        parse_mode="HTML"
    )

@dp.message(F.text.regexp(r"^\d+$"))
async def handle_code(message: Message, state: FSMContext):
    current_state = await state.get_state()
    if current_state:
        return

    if not await check_subscriptions(message.from_user.id):
        channels = await get_channels()
        return await message.answer(
            "📛 Koddan foydalanish uchun avval kanallarga obuna bo'ling!",
            reply_markup=get_subscribe_keyboard(channels)
        )

    for code, caption, info, link in read_db():
        if int(message.text) == code:
            return await message.answer_video(
                video=link,
                caption=f"🎬 <b>{caption}</b>\n\n{info}",
                parse_mode="HTML"
            )

    await message.answer("❌ Kechirasiz, bu kodga mos kino topilmadi.")

# === Callback Query Handlers ===
@dp.callback_query(F.data == "check_subscription")
async def check_subscription_callback(callback: CallbackQuery):
    user_id = callback.from_user.id
    full_name = callback.from_user.full_name

    if await check_subscriptions(user_id):
        await callback.message.answer(
            f"✅ Rahmat, <b>{full_name}</b>! Siz barcha kanallarga obuna bo‘lgansiz.",
            parse_mode="HTML"
        )
    else:
        channels = await get_channels()
        await callback.message.answer(
            "❌ Afsuski, siz hali ham barcha kanallarga obuna bo‘lmadingiz.\n"
            "Iltimos, quyidagi havolalar orqali obuna bo‘ling:",
            reply_markup=get_subscribe_keyboard(channels)
        )
    await callback.answer()

@dp.callback_query(F.data == "kino_panel")
async def kino_panel(callback: CallbackQuery):
    await callback.message.edit_text("🎬 Kino paneli:", reply_markup=kino_panel_keyboard())
    await callback.answer()

@dp.callback_query(F.data == "kanal_panel")
async def kanal_panel(callback: CallbackQuery):
    await callback.message.edit_text("📡 Kanal paneli:", reply_markup=kanal_panel_keyboard())
    await callback.answer()

@dp.callback_query(F.data == "admin_manage")
async def admin_manage_router(callback: CallbackQuery):
    is_superadmin = (callback.from_user.id == SUPER_ADMIN_ID)
    await callback.message.edit_text(
        "👮‍♂️ Admin boshqaruvi bo‘limi:",
        reply_markup=admin_manage_keyboard(is_superadmin)
    )
    await callback.answer()

@dp.callback_query(F.data == "back_admin")
async def back_admin(callback: CallbackQuery):
    await callback.message.edit_text(
        "👨‍💻 Admin panel:",
        reply_markup=admin_panel_keyboard()
    )
    await callback.answer()

@dp.callback_query(F.data == "list_admins")
async def list_admins(callback: CallbackQuery):
    admins = get_all_admins()
    if not admins:
        await callback.message.answer("❌ Hozircha adminlar yo‘q.")
    else:
        text = "👮‍♂️ <b>Adminlar ro‘yxati:</b>\n"
        for admin_id in admins:
            text += f"• <code>{admin_id}</code>\n"
        await callback.message.answer(text, parse_mode="HTML")
    await callback.answer()

@dp.callback_query(F.data == "stats")
async def show_stats(callback: CallbackQuery):
    total = get_total_users()
    last_24h = get_new_users_in_last_24h()
    active = get_active_users_in_last_7d()

    text = (
        "📊 <b>Foydalanuvchilar statistikasi:</b>\n"
        f"• Umumiy foydalanuvchilar: <b>{total}</b>\n"
        f"• Oxirgi 24 soatda qo‘shilganlar: <b>{last_24h}</b>\n"
        f"• So‘nggi 7 kun ichida aktivlar: <b>{active}</b>"
    )
    await callback.message.answer(text, parse_mode="HTML")
    await callback.answer()

@dp.callback_query(F.data == "send_broadcast")
async def send_broadcast(callback: CallbackQuery, state: FSMContext):
    await callback.message.answer("📤 Xabaringizni yuboring:")
    await state.set_state(AdminStates.waiting_for_broadcast)
    await callback.answer()

@dp.callback_query(F.data == "broadcast_confirm")
async def do_broadcast(callback: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    original = data['broadcast_msg']
    users = get_all_users()
    sent = 0
    for uid in users:
        try:
            if original.content_type == "text":
                await bot.send_message(uid, original.text)
            elif original.content_type == "photo":
                await bot.send_photo(uid, original.photo[-1].file_id, caption=original.caption)
            elif original.content_type == "video":
                await bot.send_video(uid, original.video.file_id, caption=original.caption)
            elif original.content_type == "document":
                await bot.send_document(uid, original.document.file_id, caption=original.caption)
            elif original.content_type == "audio":
                await bot.send_audio(uid, original.audio.file_id, caption=original.caption)
            elif original.content_type == "voice":
                await bot.send_voice(uid, original.voice.file_id)
            elif original.content_type == "animation":
                await bot.send_animation(uid, original.animation.file_id, caption=original.caption)
            else:
                await original.copy_to(uid)
            sent += 1
        except Exception as e:
            print(f"❌ Foydalanuvchiga yuborilmadi: {uid}, sabab: {e}")
    await callback.message.edit_text(f"✅ {sent} ta foydalanuvchiga yuborildi.")
    await state.clear()
    await callback.answer()

@dp.callback_query(F.data == "broadcast_cancel")
async def cancel_broadcast(callback: CallbackQuery, state: FSMContext):
    await callback.message.edit_text("❌ Yuborish bekor qilindi.")
    await state.clear()
    await callback.answer()

@dp.callback_query(F.data == "list_codes")
async def send_code_list(callback: CallbackQuery):
    if callback.from_user.id not in ADMIN_IDS:
        return await callback.answer("❌ Siz admin emassiz!", show_alert=True)
    movies = read_db()
    if not movies:
        await callback.message.answer("🎬 Hozircha hech qanday kino qo'shilmagan.")
        return
    filepath = "kino_codes.txt"
    with open(filepath, "w", encoding="utf-8") as file:
        file.write("🎬 Mavjud kinolar ro'yxati:\n\n")
        for code, caption, _, _ in movies:
            file.write(f"🔢 {code} — {caption}\n")
    await bot.send_document(chat_id=callback.from_user.id, document=types.FSInputFile(filepath), caption="📄 Kodlar ro'yxati")
    await callback.answer()

@dp.callback_query(F.data == "list_channels")
async def list_channels(callback: CallbackQuery):
    channels = await get_channels()
    if not channels:
        await callback.message.answer("❌ Hech qanday kanal topilmadi.")
    else:
        text = "📋 Kanal ro'yxati:\n"
        for cid, uname, invite_link in channels:
            if uname and uname != "private":
                text += f"• <b>@{uname}</b> — <code>{cid}</code>\n"
            elif invite_link:
                text += f"• <a href=\"{invite_link}\">Private kanalga obuna bo‘ling</a> — <code>{cid}</code>\n"
            else:
                text += f"• <code>{cid}</code> (private kanal)\n"
        await callback.message.answer(text, parse_mode="HTML")
    await callback.answer()

@dp.callback_query(F.data == "add_channel")
async def ask_channel_username(callback: CallbackQuery, state: FSMContext):
    await callback.message.answer("➕ Kanal username'ini yuboring (@belgisi bilan):")
    await state.set_state(AdminStates.waiting_for_channel_username)
    await callback.answer()

@dp.callback_query(F.data == "remove_channel")
async def ask_channel_id(callback: CallbackQuery, state: FSMContext):
    await callback.message.answer("🗑 O'chirish uchun kanal ID sini yuboring:")
    await state.set_state(AdminStates.waiting_for_channel_id_to_remove)
    await callback.answer()

@dp.callback_query(F.data == "add_media")
async def ask_link(callback: CallbackQuery, state: FSMContext):
    await callback.message.answer("🎥 Kino yoki media faylga havolani yuboring (https://t.me/...):")
    await state.set_state(AddMediaState.waiting_for_link)

@dp.callback_query(F.data == "confirm_add")
async def confirm_add(callback: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    add_movie(data['code'], data['caption'], data['info'], data['link'])
    await callback.message.edit_text("✅ Kino ma'lumotlari saqlandi!")
    await state.clear()
    await callback.answer()

@dp.callback_query(F.data == "cancel_add")
async def cancel_add(callback: CallbackQuery, state: FSMContext):
    await callback.message.edit_text("❌ Bekor qilindi.")
    await state.clear()
    await callback.answer()

@dp.callback_query(F.data == "delete_media")
async def delete_media_start(callback: CallbackQuery, state: FSMContext):
    await callback.message.answer("🗑 O'chirish uchun kino kodini yuboring:")
    await state.set_state(AdminStates.waiting_for_delete_code)
    await callback.answer()

@dp.callback_query(F.data == "edit_media")
async def edit_media_start(callback: CallbackQuery, state: FSMContext):
    await callback.message.answer("✏ Tahrirlash uchun kino kodini yuboring:")
    await state.set_state(AdminStates.waiting_for_edit_code)
    await callback.answer()

@dp.callback_query(F.data == "add_admin")
async def ask_new_admin_id(callback: CallbackQuery, state: FSMContext):
    if callback.from_user.id != SUPER_ADMIN_ID:
        return await callback.answer("❌ Faqat superadmin yangi admin qo'sha oladi!", show_alert=True)
    print("Callback ishladi, state o'rnatiladi")
    await callback.message.answer("➕ Yangi adminning Telegram ID sini yuboring:")
    await state.set_state(AdminStates.waiting_for_new_admin_id)
    await callback.answer()

@dp.callback_query(F.data == "remove_admin")
async def ask_remove_admin_id(callback: CallbackQuery, state: FSMContext):
    if callback.from_user.id != SUPER_ADMIN_ID:
        return await callback.answer("❌ Faqat superadmin admin o'chira oladi!", show_alert=True)
    await callback.message.answer("🗑 O'chirish uchun adminning Telegram ID sini yuboring:")
    await state.set_state(AdminStates.waiting_for_remove_admin_id)
    await callback.answer()

# === Main ===
from users_db import init_users_db

async def main():
    print("🚀 Bot ishga tushdi")
    await init_db()
    init_admin_db()
    init_users_db()
    for admin_id in ADMIN_IDS:
        add_admin(admin_id)
    init_kino_db()
    init_users_table()
    print(f"📡 Router qo'shildi: admin_manage_router")
    print("✅ Bot polling boshlandi")
    await dp.start_polling(bot)

import logging

logging.basicConfig(
    level=logging.INFO,
    filename='logs.txt',
    filemode='a',
    format='%(asctime)s - %(levelname)s - %(message)s'
)

if __name__ == '__main__':
    asyncio.run(main())