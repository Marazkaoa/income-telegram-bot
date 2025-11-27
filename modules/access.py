import json

def load_cfg():
    return json.load(open("config.json"))

def is_allowed(uid):
    cfg = load_cfg()
    return uid == cfg["owner_id"] or uid in cfg["allowed_users"]

async def owner_only(update, context):
    uid = update.effective_user.id
    cfg = load_cfg()
    if uid != cfg["owner_id"]:
        await update.message.reply_text("❌ Bạn không phải owner.")
        raise SystemExit
    return True

def list_allowed():
    cfg = load_cfg()
    text = "📜 Danh sách user được cấp quyền:\n"
    for u in cfg["allowed_users"]:
        text += f"• {u}\n"
    return text
