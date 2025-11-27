from telegram import InlineKeyboardButton, InlineKeyboardMarkup

def build_menu():
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("➕ Cộng", callback_data="add"),
         InlineKeyboardButton("➖ Trừ", callback_data="sub")],
        [InlineKeyboardButton("📅 Hôm nay", callback_data="today"),
         InlineKeyboardButton("📊 Tổng", callback_data="total")],
        [InlineKeyboardButton("📈 Biểu đồ", callback_data="chart"),
         InlineKeyboardButton("📉 Thống kê", callback_data="stat")],
    ])

def build_admin_menu():
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("➕ Thêm user", callback_data="admin_add_user")],
        [InlineKeyboardButton("❌ Xoá user", callback_data="admin_del_user")],
        [InlineKeyboardButton("📜 Danh sách user", callback_data="admin_list_user")],
    ])
