# keyboards.py
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

def get_subscribe_keyboard(channels):
    keyboard = []
    for index, (channel_id, username) in enumerate(channels, start=1):
        if username != "unknown":
            keyboard.append([
                InlineKeyboardButton(
                    text=f"📢 {index}-kanalga obuna bo‘ling",
                    url=f"https://t.me/{username}"
                )
            ])
    keyboard.append([
        InlineKeyboardButton(text="✅ Tekshirish", callback_data="check_subscription")
    ])
    return InlineKeyboardMarkup(inline_keyboard=keyboard)

def admin_panel_keyboard():
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="\U0001F4FA Kino Paneli", callback_data="kino_panel")],
        [InlineKeyboardButton(text="\U0001F4E1 Kanal Paneli", callback_data="kanal_panel")],
        [InlineKeyboardButton(text="\U0001F4CA Statistika", callback_data="stats")],
        [InlineKeyboardButton(text="\U0001F4E2 Xabar yuborish", callback_data="send_broadcast")],
        # [InlineKeyboardButton(text="👮‍♂️ Adminlar boshqaruvi", callback_data="admin_manage")],
    ])


def admin_manage_keyboard():
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="➕ Admin qo‘shish", callback_data="add_admin_btn")],
        [InlineKeyboardButton(text="➖ Admin o‘chirish", callback_data="remove_admin_btn")],
        [InlineKeyboardButton(text="📋 Adminlar ro‘yxati", callback_data="list_admins_btn")],
        [InlineKeyboardButton(text="⬅️ Orqaga", callback_data="back_admin")],
    ])




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
