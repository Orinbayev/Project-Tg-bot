from aiogram.fsm.state import StatesGroup, State

class AdminStates(StatesGroup):
    waiting_for_channel_username = State()
    waiting_for_channel_invite_link = State()
    waiting_for_channel_id_to_remove = State()
    waiting_for_broadcast = State()
    waiting_for_delete_code = State()
    waiting_for_edit_code = State()
    waiting_for_new_caption = State()
    waiting_for_new_info = State()
    waiting_for_new_link = State()
    waiting_for_new_admin_id = State()
    waiting_for_remove_admin_id = State()

class AddMediaState(StatesGroup):
    waiting_for_link = State()
    waiting_for_caption = State()
    waiting_for_info = State()
    waiting_for_code = State()
    confirm = State()