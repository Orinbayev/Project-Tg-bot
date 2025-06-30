# keyboards.py
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

def get_subscribe_keyboard(channels):
    keyboard = []
    for index, (channel_id, username, invite_link) in enumerate(channels, start=1):
        # Public kanal uchun
        if username and username != "private":
            url = f"https://t.me/{username}"
            text = f"{index}-kanalga obuna bo‘ling"
        # Private kanal uchun
        elif invite_link:
            url = invite_link
            text = f"{index}-kanalga obuna bo‘ling"
        else:
            url = ""
            text = f"{index}-kanal (ID: {channel_id})"
        if url:
            keyboard.append([InlineKeyboardButton(text=text, url=url)])
    keyboard.append([InlineKeyboardButton(text="✅ Tekshirish", callback_data="check_subscription")])
    return InlineKeyboardMarkup(inline_keyboard=keyboard)

def admin_panel_keyboard():
    keyboard = [
        [InlineKeyboardButton(text="🎬 Kino paneli", callback_data="kino_panel")],
        [InlineKeyboardButton(text="📡 Kanal paneli", callback_data="kanal_panel")],
        [InlineKeyboardButton(text="📊 Statistika", callback_data="stats")],
        [InlineKeyboardButton(text="📤 Xabar yuborish", callback_data="send_broadcast")],
        [InlineKeyboardButton(text="📄 Kodlar ro'yxati", callback_data="list_codes")],
        [InlineKeyboardButton(text="👮‍♂️ Admin boshqaruvi", callback_data="admin_manage")],
    ]
    return InlineKeyboardMarkup(inline_keyboard=keyboard)

def admin_manage_keyboard(is_superadmin=False):
    keyboard = [
        [InlineKeyboardButton(text="➕ Admin qo'shish", callback_data="add_admin")],
        [InlineKeyboardButton(text="🗑 Admin o'chirish", callback_data="remove_admin")],
        [InlineKeyboardButton(text="📋 Adminlar ro'yxati", callback_data="list_admins")],
        [InlineKeyboardButton(text="⬅️ Orqaga", callback_data="back_admin")],
    ]
    return InlineKeyboardMarkup(inline_keyboard=keyboard)

def kino_panel_keyboard():
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="\u2795 Kino qo'shish", callback_data="add_media")],
        [InlineKeyboardButton(text="\U0001F5D1 Kino o'chirish", callback_data="delete_media")],
        [InlineKeyboardButton(text="\u270F Kino tahrirlash", callback_data="edit_media")],
        [InlineKeyboardButton(text="\U0001F4CB Kodlar ro'yxati", callback_data="list_codes")],
        [InlineKeyboardButton(text="\u2B05 Orqaga", callback_data="back_admin")],
    ])

def kanal_panel_keyboard():
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="\u2795 Kanal qo'shish", callback_data="add_channel")],
        [InlineKeyboardButton(text="\u2796 Kanal o'chirish", callback_data="remove_channel")],
        [InlineKeyboardButton(text="\U0001F4C3 Qo'shilgan kanallar", callback_data="list_channels")],
        [InlineKeyboardButton(text="\u2B05 Orqaga", callback_data="back_admin")],
    ])

def confirm_keyboard():
    return InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="\u2705 Tasdiqlash", callback_data="confirm_add"),
            InlineKeyboardButton(text="\u274C Bekor qilish", callback_data="cancel_add")
        ]
    ])

def broadcast_confirm_keyboard():
    return InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="\u2705 Yuborish", callback_data="broadcast_confirm"),
            InlineKeyboardButton(text="\u274C Bekor qilish", callback_data="broadcast_cancel")
        ]
    ])

def back_to_admin_panel():
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="⬅️ Orqaga", callback_data="back_admin")]
    ])
