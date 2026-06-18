import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, InputFile
from telegram.ext import (
    Application,
    CommandHandler,
    CallbackQueryHandler,
    MessageHandler,
    filters,
    ContextTypes,
    ConversationHandler
)
import json
import os
from datetime import datetime, timedelta
import random
import asyncio
from pathlib import Path
import shutil

# ================= CONFIG =================
BOT_TOKEN = "8887346898:AAEYlqMssdZg_wi_MXTE-c3KwKqienX7Ba8"
ADMIN_ID = 8170952537
CHANNEL_LINK = "https://t.me/Rayyan_Hacks"
SUPPORT_USERNAME = "@Narendra_Modih"

# States
(SENDING_KEY, ADMIN_MSG_USER, ADMIN_MSG_TEXT, REBRAND_NAME, REBRAND_LOGO, 
 REBRAND_PRICE, RESELL_PRICE, ADD_APK, REMOVE_APK, APK_LINK, 
 PRICE_REBRAND, PRICE_RESELL, BROADCAST_MSG, UPLOAD_APK_FILE, 
 EDIT_APK_NAME, EDIT_APK_LINK, BAN_USER, UNBAN_USER, CUSTOM_KEY_DURATION,
 ADD_PLAN, REMOVE_PLAN, SCHEDULE_BROADCAST) = range(23)

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', 
    level=logging.INFO,
    handlers=[
        logging.FileHandler('bot.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# ================= DATABASE =================
class Database:
    def __init__(self, filename="data.json"):
        self.filename = filename
        self.load_data()
        self.setup_directories()
    
    def setup_directories(self):
        """Create necessary directories"""
        directories = ['apks', 'backups', 'logs', 'media']
        for dir_name in directories:
            Path(dir_name).mkdir(exist_ok=True)
    
    def load_data(self):
        if os.path.exists(self.filename):
            with open(self.filename, 'r') as f:
                self.data = json.load(f)
        else:
            self.data = {
                "users": {},
                "banned_users": [],
                "admins": [ADMIN_ID],
                "stats": {
                    "total_approved": 0,
                    "total_rejected": 0,
                    "keys_sold": 0,
                    "keys_generated": 0,
                    "total_referrals": 0,
                    "total_balance": 0,
                    "total_apk_downloads": 0,
                    "daily_users": [],
                    "weekly_users": [],
                    "monthly_users": [],
                    "revenue_by_plan": {},
                    "daily_stats": {}
                },
                "settings": {
                    "bot_name": "ROLEX X PREMIUM",
                    "bot_logo": "✨",
                    "welcome_text": "Welcome to the best hack bot!",
                    "ads": [],
                    "rebrand_price": {"session": 3000, "monthly": 1800, "single": 400},
                    "resell_price": {"unlimited_balance": 500},
                    "trial_price": {"5_hour": 100, "12_hour": 150, "24_hour": 200},
                    "plans": {
                        "1h": {"name": "1 Hour", "price": 50, "duration": "1h"},
                        "5h": {"name": "5 Hours Trial", "price": 100, "duration": "5h"},
                        "12h": {"name": "12 Hours", "price": 150, "duration": "12h"},
                        "1d": {"name": "1 Day", "price": 200, "duration": "1d"},
                        "3d": {"name": "3 Days", "price": 400, "duration": "3d"},
                        "7d": {"name": "7 Days", "price": 600, "duration": "7d"},
                        "15d": {"name": "15 Days", "price": 900, "duration": "15d"},
                        "30d": {"name": "30 Days", "price": 1200, "duration": "30d"}
                    },
                    "apks": [
                        {"id": "apk_1", "name": "X Silent", "active": True, "link": "", "version": "2.1.0", "changelog": "Fixed stability issues", "file_path": ""},
                        {"id": "apk_2", "name": "Rolex Mod", "active": True, "link": "", "version": "3.0.0", "changelog": "New features added", "file_path": ""},
                        {"id": "apk_3", "name": "Ztrax", "active": True, "link": "", "version": "1.8.5", "changelog": "Performance improved", "file_path": ""},
                        {"id": "apk_4", "name": "Mars Loader", "active": True, "link": "", "version": "2.4.0", "changelog": "Security updates", "file_path": ""}
                    ],
                    "broadcasts": [],
                    "ai_messages": [
                        "How can I help you?",
                        "Need a key?",
                        "Check latest APK updates.",
                        "Contact support anytime.",
                        "View available plans.",
                        "Ready to purchase?",
                        "Need help with setup?"
                    ],
                    "referral_bonus": 20
                },
                "referrals": {},
                "resell_keys": {},
                "keys": {},
                "broadcasts": [],
                "purchase_history": [],
                "rebrand_purchases": []
            }
            self.save_data()
    
    def save_data(self):
        with open(self.filename, 'w') as f:
            json.dump(self.data, f, indent=4)
    
    def get_user(self, user_id):
        uid = str(user_id)
        if uid not in self.data["users"]:
            self.data["users"][uid] = {
                "name": "",
                "keys": [],
                "balance": 0,
                "refs": 0,
                "ref_code": uid,
                "joined": datetime.now().isoformat(),
                "resell_keys": [],
                "is_banned": False,
                "history": [],
                "downloads": 0,
                "last_active": datetime.now().isoformat()
            }
            self.save_data()
        return self.data["users"][uid]
    
    def add_key(self, user_id, key, duration, plan_type):
        uid = str(user_id)
        user = self.get_user(user_id)
        key_data = {
            "key": key,
            "duration": duration,
            "plan_type": plan_type,
            "issued_at": datetime.now().isoformat(),
            "expires_at": (datetime.now() + timedelta(days=duration)).isoformat(),
            "is_active": True,
            "used_count": 0
        }
        user["keys"].append(key_data)
        self.data["stats"]["keys_sold"] += 1
        self.data["stats"]["keys_generated"] += 1
        self.save_data()
        return key_data
    
    def add_referral(self, user_id, ref_by):
        user = self.get_user(user_id)
        bonus = self.data["settings"]["referral_bonus"]
        user["refs"] += 1
        user["balance"] += bonus
        self.data["stats"]["total_referrals"] += 1
        self.data["stats"]["total_balance"] += bonus
        self.save_data()
    
    def is_user_banned(self, user_id):
        return str(user_id) in self.data["banned_users"]
    
    def ban_user(self, user_id):
        uid = str(user_id)
        if uid not in self.data["banned_users"]:
            self.data["banned_users"].append(uid)
            self.save_data()
            return True
        return False
    
    def unban_user(self, user_id):
        uid = str(user_id)
        if uid in self.data["banned_users"]:
            self.data["banned_users"].remove(uid)
            self.save_data()
            return True
        return False
    
    def get_apk_by_id(self, apk_id):
        for apk in self.data["settings"]["apks"]:
            if apk["id"] == apk_id:
                return apk
        return None
    
    def add_apk(self, name, link="", version="1.0.0", changelog=""):
        apk_id = f"apk_{len(self.data['settings']['apks']) + 1}"
        apk_data = {
            "id": apk_id,
            "name": name,
            "active": True,
            "link": link,
            "version": version,
            "changelog": changelog,
            "file_path": ""
        }
        self.data["settings"]["apks"].append(apk_data)
        self.save_data()
        return apk_data
    
    def get_daily_stats(self):
        today = datetime.now().date().isoformat()
        if today not in self.data["stats"]["daily_stats"]:
            self.data["stats"]["daily_stats"][today] = {
                "users": 0,
                "keys_sold": 0,
                "revenue": 0,
                "downloads": 0
            }
        return self.data["stats"]["daily_stats"][today]
    
    def update_daily_stats(self, key_type="users"):
        today = datetime.now().date().isoformat()
        stats = self.get_daily_stats()
        if key_type == "users":
            stats["users"] += 1
        elif key_type == "keys_sold":
            stats["keys_sold"] += 1
        elif key_type == "revenue":
            stats["revenue"] += 1
        elif key_type == "downloads":
            stats["downloads"] += 1
        self.save_data()
    
    def backup_data(self):
        backup_name = f"backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        backup_path = f"backups/{backup_name}"
        shutil.copy2(self.filename, backup_path)
        return backup_path

db = Database()

# ================= AI ASSISTANT =================
class AIAssistant:
    def __init__(self):
        self.message_index = 0
        self.last_message_time = {}
        self.is_enabled = True
    
    def get_next_message(self):
        messages = db.data["settings"]["ai_messages"]
        if self.message_index >= len(messages):
            self.message_index = 0
        msg = messages[self.message_index]
        self.message_index += 1
        return msg
    
    def should_send_message(self, user_id):
        if not self.is_enabled:
            return False
        current_time = datetime.now()
        last_time = self.last_message_time.get(user_id)
        if last_time is None or (current_time - last_time) > timedelta(minutes=1):
            self.last_message_time[user_id] = current_time
            return True
        return False

ai_assistant = AIAssistant()

# ================= KEYBOARDS =================
def get_verification_keyboard():
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("📢 Join Channel", url=CHANNEL_LINK)],
        [InlineKeyboardButton("✅ Verify", callback_data="verify_channel")]
    ])

def get_main_keyboard():
    keyboard = InlineKeyboardMarkup([
        [InlineKeyboardButton("🛒 Buy Keys", callback_data="buy"), 
         InlineKeyboardButton("🔑 My Keys", callback_data="mykeys")],
        [InlineKeyboardButton("🎁 Referral", callback_data="ref"), 
         InlineKeyboardButton("📞 Support", callback_data="support")],
        [InlineKeyboardButton("👑 Contact Owner", callback_data="contact_owner")],
        [InlineKeyboardButton("💸 Resell Keys", callback_data="resell_menu")],
        [InlineKeyboardButton("📊 Live Stats", callback_data="live_stats")],
        [InlineKeyboardButton("📱 APK Download", callback_data="apk_download")]
    ])
    return keyboard

def get_admin_keyboard():
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("👥 Users", callback_data="admin_users"),
         InlineKeyboardButton("📊 Stats", callback_data="admin_stats")],
        [InlineKeyboardButton("📢 Broadcast", callback_data="bc"),
         InlineKeyboardButton("🔑 Manage Keys", callback_data="manage_keys")],
        [InlineKeyboardButton("🎨 Rebrand", callback_data="rebrand_menu"),
         InlineKeyboardButton("💰 Price Settings", callback_data="price_settings")],
        [InlineKeyboardButton("💸 Resell Settings", callback_data="resell_settings")],
        [InlineKeyboardButton("📱 Manage APKs", callback_data="manage_apks")],
        [InlineKeyboardButton("🚫 Ban/Unban User", callback_data="ban_user")],
        [InlineKeyboardButton("📋 Purchase History", callback_data="purchase_history")],
        [InlineKeyboardButton("💾 Backup Data", callback_data="backup_data")],
        [InlineKeyboardButton("🔄 Refresh", callback_data="admin_ref")]
    ])

def get_back_keyboard():
    return InlineKeyboardMarkup([[InlineKeyboardButton("🔙 Back", callback_data="back_start")]])

# ================= VERIFICATION =================
async def verify_channel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    user_id = query.from_user.id
    
    try:
        # Check if user is member of channel
        chat_member = await context.bot.get_chat_member(CHANNEL_LINK.split('/')[-1], user_id)
        if chat_member.status in ['member', 'administrator', 'creator']:
            await query.message.edit_text(
                "✅ *Verification Successful!*\n\nWelcome to the bot!",
                parse_mode="Markdown"
            )
            await start(update, context)
        else:
            await query.answer("❌ Please join the channel first!", show_alert=True)
    except Exception as e:
        logger.error(f"Verification error: {e}")
        await query.answer("❌ Verification failed. Please try again or contact support.", show_alert=True)

# ================= START =================
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    user_id = user.id
    
    # Check if user is banned
    if db.is_user_banned(user_id):
        await update.message.reply_text("🚫 You have been banned from using this bot.")
        return
    
    user_data = db.get_user(user_id)
    user_data["name"] = user.first_name
    user_data["last_active"] = datetime.now().isoformat()
    db.save_data()
    
    # Check referral
    if context.args and context.args[0].isdigit() and int(context.args[0]) != user_id:
        ref_by = context.args[0]
        if str(ref_by) in db.data["users"] and str(ref_by) != str(user_id):
            if not db.data["users"][str(user_id)].get("referred_by"):
                db.add_referral(user_id, ref_by)
                db.data["users"][str(user_id)]["referred_by"] = str(ref_by)
                db.save_data()
                await update.message.reply_text(f"🎉 *You joined with a referral! +₹{db.data['settings']['referral_bonus']} added to your wallet!*", parse_mode="Markdown")
    
    settings = db.data["settings"]
    
    # Show verification first
    if not context.args:
        welcome_text = (
            f"{settings['bot_logo']} *{settings['bot_name']}*\n\n"
            f"👋 *Welcome, {user.first_name}*\n\n"
            f"⚠️ *Please join our channel first to continue!*"
        )
        await update.message.reply_text(welcome_text, reply_markup=get_verification_keyboard(), parse_mode="Markdown")
        return
    
    # Main menu after verification
    welcome_text = (
        f"{settings['bot_logo']} *{settings['bot_name']}*\n\n"
        f"👋 *Welcome, {user.first_name}*\n\n"
        f"✨ *PREMIUM FEATURES*\n"
        f"╰ 🎯 180° Bullet Track\n"
        f"╰ 🪄 Magic Bullet High DMG\n"
        f"╰ ⚡ Ultra Aim Assist\n"
        f"╰ 💎 Smooth ESP (Internal)\n\n"
        f"🚀 *Status:* `Undetected` | *Server:* `Stable`\n"
        f"👥 *Referrals:* {user_data['refs']} | 💰 *Balance:* ₹{user_data['balance']}"
    )
    
    if update.message:
        await update.message.reply_text(welcome_text, reply_markup=get_main_keyboard(), parse_mode="Markdown")
    else:
        await update.callback_query.message.edit_text(welcome_text, reply_markup=get_main_keyboard(), parse_mode="Markdown")

# ================= BUY =================
async def buy_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    plans = db.data["settings"]["plans"]
    
    keyboard = []
    for plan_id, plan_data in plans.items():
        keyboard.append([
            InlineKeyboardButton(
                f"{plan_data['name']} - ₹{plan_data['price']}", 
                callback_data=f"p_{plan_id}"
            )
        ])
    
    keyboard.append([InlineKeyboardButton("🔙 Back", callback_data="back_start")])
    
    await query.message.edit_text(
        "💎 *SELECT YOUR PLAN*\n\n"
        "Choose from our premium packages:",
        reply_markup=InlineKeyboardMarkup(keyboard),
        parse_mode="Markdown"
    )

async def plan_confirm(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    plan_id = query.data.split("_")[1]
    plan_data = db.data["settings"]["plans"].get(plan_id)
    
    if not plan_data:
        await query.answer("❌ Plan not found!", show_alert=True)
        return
    
    context.user_data['temp_plan'] = {"id": plan_id, **plan_data}
    
    text = (
        f"🧾 *ORDER CONFIRMATION*\n\n"
        f"👤 *Client:* {query.from_user.first_name}\n"
        f"📋 *Plan:* {plan_data['name']}\n"
        f"⏳ *Duration:* {plan_data['duration']}\n"
        f"💰 *Amount:* ₹{plan_data['price']}\n\n"
        f"Click below to generate payment QR."
    )
    keyboard = [
        [InlineKeyboardButton("💳 Pay Now", callback_data="pay_now")], 
        [InlineKeyboardButton("❌ Cancel", callback_data="buy")]
    ]
    await query.message.edit_text(text, reply_markup=InlineKeyboardMarkup(keyboard), parse_mode="Markdown")

async def pay_now(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    plan = context.user_data.get('temp_plan')
    if not plan:
        await query.answer("❌ Please select a plan first!", show_alert=True)
        return
    
    text = (
        f"✨ *PAYMENT GATEWAY*\n\n"
        f"👤 *User:* {query.from_user.first_name}\n"
        f"💰 *Amount:* ₹{plan['price']}\n\n"
        f"⚠️ *Step 1:* Send payment to\n"
        f"📱 UPI: `example@upi`\n"
        f"📱 Bank: `XXXX-XXXX-XXXX`\n\n"
        f"⚠️ *Step 2:* Send **Screenshot** here\n\n"
        f"Admin will verify and send your key instantly."
    )
    await query.message.delete()
    await context.bot.send_photo(
        chat_id=query.message.chat_id, 
        photo="https://kommodo.ai/i/qF4FLWL7wK3SjLsyNmH1", 
        caption=text, 
        parse_mode="Markdown"
    )

# ================= SCREENSHOT =================
async def handle_screenshot(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    plan = context.user_data.get('temp_plan')
    
    if db.is_user_banned(user.id):
        await update.message.reply_text("🚫 You are banned from using this bot.")
        return
    
    if not plan:
        await update.message.reply_text("⚠️ Please start buying process first! /start")
        return
    
    await update.message.reply_text("⏳ *Payment Sent for Verification...*", parse_mode="Markdown")
    
    # Update daily stats
    db.update_daily_stats("keys_sold")
    
    # Generate a unique key
    key = f"ROLX-{random.randint(1000, 9999)}-{random.randint(1000, 9999)}-{random.randint(1000, 9999)}"
    duration = 1  # Default 1 day
    
    # Send to admin
    admin_kb = [
        [InlineKeyboardButton("✅ Approve", callback_data=f"adm_app_{user.id}_{plan['id']}"), 
         InlineKeyboardButton("❌ Reject", callback_data=f"adm_rej_{user.id}")]
    ]
    
    admin_text = (
        f"💸 *NEW PAYMENT*\n\n"
        f"👤 ID: `{user.id}`\n"
        f"👤 Name: {user.first_name}\n"
        f"📅 Plan: {plan['name']}\n"
        f"💰 Price: ₹{plan['price']}\n"
        f"🔑 Generated Key: `{key}`"
    )
    
    await context.bot.send_photo(
        chat_id=ADMIN_ID, 
        photo=update.message.photo[-1].file_id, 
        caption=admin_text, 
        reply_markup=InlineKeyboardMarkup(admin_kb), 
        parse_mode="Markdown"
    )

# ================= ADMIN =================
async def admin_panel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    
    if user_id not in db.data["admins"]:
        if update.message:
            await update.message.reply_text("❌ Unauthorized!")
        else:
            await update.callback_query.answer("❌ Unauthorized!", show_alert=True)
        return
    
    stats = db.data["stats"]
    daily_stats = db.get_daily_stats()
    
    stats_text = (
        f"🛠 *ADMIN CONTROL PANEL*\n\n"
        f"👥 Total Users: {len(db.data['users'])}\n"
        f"✅ Approved: {stats['total_approved']}\n"
        f"❌ Rejected: {stats['total_rejected']}\n"
        f"🔑 Keys Sold: {stats['keys_sold']}\n"
        f"🎁 Total Referrals: {stats['total_referrals']}\n"
        f"💰 Total Revenue: ₹{stats['total_balance']}\n"
        f"📱 APK Downloads: {stats['total_apk_downloads']}\n\n"
        f"📈 *Today's Stats*\n"
        f"👥 New Users: {daily_stats['users']}\n"
        f"🔑 Keys Sold: {daily_stats['keys_sold']}\n"
        f"💰 Revenue: ₹{daily_stats['revenue']}\n"
        f"📱 Downloads: {daily_stats['downloads']}\n\n"
        f"📌 *Select an option:*"
    )
    
    if update.message:
        await update.message.reply_text(stats_text, reply_markup=get_admin_keyboard(), parse_mode="Markdown")
    else:
        await update.callback_query.message.edit_text(stats_text, reply_markup=get_admin_keyboard(), parse_mode="Markdown")

# ================= ADMIN CALLBACKS =================
async def admin_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    data = query.data
    user_id = query.from_user.id
    
    if user_id not in db.data["admins"]:
        await query.answer("❌ Unauthorized!", show_alert=True)
        return
    
    if data.startswith("adm_app_"):
        parts = data.split("_")
        target_id = parts[2]
        plan_id = parts[3] if len(parts) > 3 else None
        context.user_data['target_id'] = target_id
        context.user_data['plan_id'] = plan_id
        await query.message.reply_text(f"📝 Paste the **KEY** for user `{target_id}`:\n(Or type 'auto' for auto-generate)")
        return SENDING_KEY
    
    elif data.startswith("adm_rej_"):
        target_id = data.split("_")[2]
        db.data["stats"]["total_rejected"] += 1
        db.save_data()
        try:
            await context.bot.send_message(
                target_id, 
                "❌ *Payment Rejected:* Screenshot invalid or payment not received.\n\nPlease try again or contact support.", 
                parse_mode="Markdown"
            )
        except:
            pass
        await query.message.reply_text("✅ Rejected successfully.")
    
    elif data == "admin_stats":
        stats = db.data["stats"]
        text = (
            f"📊 *FULL STATISTICS*\n\n"
            f"👥 Total Users: {len(db.data['users'])}\n"
            f"✅ Approved: {stats['total_approved']}\n"
            f"❌ Rejected: {stats['total_rejected']}\n"
            f"🔑 Keys Sold: {stats['keys_sold']}\n"
            f"🔑 Keys Generated: {stats['keys_generated']}\n"
            f"🎁 Referrals: {stats['total_referrals']}\n"
            f"💰 Revenue: ₹{stats['total_balance']}\n"
            f"📱 APK Downloads: {stats['total_apk_downloads']}\n\n"
            f"🚫 Banned Users: {len(db.data['banned_users'])}"
        )
        await query.message.edit_text(
            text, 
            reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔙 Back", callback_data="admin_panel")]]), 
            parse_mode="Markdown"
        )
    
    elif data == "admin_users":
        users = list(db.data["users"].items())
        text = "👥 *USER LIST*\n\n"
        for uid, udata in users[:10]:
            key_count = len(udata.get('keys', []))
            is_banned = "🚫" if uid in db.data["banned_users"] else "✅"
            text += f"{is_banned} 🆔 `{uid}` - {udata['name']} - Keys: {key_count}\n"
        if len(users) > 10:
            text += f"\n... and {len(users)-10} more"
        text += f"\n\nTotal: {len(users)} users"
        await query.message.edit_text(
            text, 
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("🔙 Back", callback_data="admin_panel")],
                [InlineKeyboardButton("📋 Full List", callback_data="export_users")]
            ]), 
            parse_mode="Markdown"
        )
    
    elif data == "manage_keys":
        keyboard = [
            [InlineKeyboardButton("📤 Generate Key", callback_data="gen_key")],
            [InlineKeyboardButton("📋 View All Keys", callback_data="view_keys")],
            [InlineKeyboardButton("🚫 Ban Key", callback_data="ban_key")],
            [InlineKeyboardButton("🔙 Back", callback_data="admin_panel")]
        ]
        await query.message.edit_text(
            "🔑 *KEY MANAGEMENT*\n\n"
            "Manage all keys here:",
            reply_markup=InlineKeyboardMarkup(keyboard),
            parse_mode="Markdown"
        )
    
    elif data == "gen_key":
        keyboard = []
        for plan_id, plan_data in db.data["settings"]["plans"].items():
            keyboard.append([
                InlineKeyboardButton(
                    f"{plan_data['name']} - {plan_data['duration']}", 
                    callback_data=f"gen_{plan_id}"
                )
            ])
        keyboard.append([InlineKeyboardButton("🔙 Back", callback_data="manage_keys")])
        await query.message.edit_text(
            "🔑 *GENERATE KEY*\n\n"
            "Select plan duration:",
            reply_markup=InlineKeyboardMarkup(keyboard),
            parse_mode="Markdown"
        )
    
    elif data.startswith("gen_"):
        plan_id = data.split("_")[1]
        plan_data = db.data["settings"]["plans"].get(plan_id)
        
        if not plan_data:
            await query.answer("❌ Plan not found!", show_alert=True)
            return
        
        # Generate key
        key = f"ROLX-{random.randint(1000, 9999)}-{random.randint(1000, 9999)}-{random.randint(1000, 9999)}"
        
        duration_map = {
            "1h": 0.04, "5h": 0.2, "12h": 0.5, "1d": 1,
            "3d": 3, "7d": 7, "15d": 15, "30d": 30
        }
        duration_days = duration_map.get(plan_data.get("duration", "1d"), 1)
        
        db.add_key(0, key, duration_days, plan_id)
        
        await query.message.edit_text(
            f"✅ *Key Generated*\n\n"
            f"🔑 Key: `{key}`\n"
            f"📋 Plan: {plan_data['name']}\n"
            f"⏳ Duration: {plan_data['duration']}\n\n"
            f"Send this key to the user.",
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("🔙 Back", callback_data="manage_keys")]
            ]),
            parse_mode="Markdown"
        )
    
    elif data == "bc":
        await query.message.reply_text(
            "📢 *BROADCAST*\n\n"
            "Send your broadcast message:\n"
            "• Type /schedule to schedule\n"
            "• Send message now for immediate broadcast",
            parse_mode="Markdown"
        )
        return BROADCAST_MSG
    
    elif data == "ban_user":
        await query.message.reply_text(
            "🚫 *BAN/UNBAN USER*\n\n"
            "Send the user ID to ban/unban:\n"
            "Example: `8170952537`\n\n"
            "Type `/unban USER_ID` to unban.",
            parse_mode="Markdown"
        )
        return BAN_USER
    
    elif data == "purchase_history":
        history = db.data["purchase_history"][-20:]  # Last 20 purchases
        if not history:
            text = "📋 No purchase history yet."
        else:
            text = "📋 *PURCHASE HISTORY*\n\n"
            for entry in history:
                text += f"👤 {entry.get('user_name', 'Unknown')} - {entry.get('plan', 'Unknown')} - ₹{entry.get('price', 0)}\n"
        
        await query.message.edit_text(
            text,
            reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔙 Back", callback_data="admin_panel")]]),
            parse_mode="Markdown"
        )
    
    elif data == "backup_data":
        backup_path = db.backup_data()
        await query.message.reply_text(f"✅ Data backed up successfully!\n📁 File: {backup_path}")

async def deliver_key(update: Update, context: ContextTypes.DEFAULT_TYPE):
    target_id = context.user_data.get('target_id')
    plan_id = context.user_data.get('plan_id')
    key_input = update.message.text.strip()
    
    if key_input.lower() == "auto":
        # Auto-generate key
        plan_data = db.data["settings"]["plans"].get(plan_id, {"duration": "1d"})
        duration_map = {
            "1h": 0.04, "5h": 0.2, "12h": 0.5, "1d": 1,
            "3d": 3, "7d": 7, "15d": 15, "30d": 30
        }
        duration_days = duration_map.get(plan_data.get("duration", "1d"), 1)
        
        key = f"ROLX-{random.randint(1000, 9999)}-{random.randint(1000, 9999)}-{random.randint(1000, 9999)}"
        db.add_key(target_id, key, duration_days, plan_id)
        
        await context.bot.send_message(
            target_id, 
            f"🎉 *PURCHASE SUCCESSFUL*\n\n"
            f"🔑 Key: `{key}`\n"
            f"📋 Plan: {plan_data.get('name', 'Premium')}\n"
            f"⏳ Duration: {plan_data.get('duration', '1 Day')}\n\n"
            f"Enjoy your hack!",
            parse_mode="Markdown"
        )
        
        db.data["stats"]["total_approved"] += 1
        db.save_data()
        await update.message.reply_text(f"✅ Key auto-generated and delivered successfully!\n🔑 Key: `{key}`", parse_mode="Markdown")
    else:
        # Manual key input
        db.add_key(target_id, key_input, 1, "manual")
        await context.bot.send_message(
            target_id, 
            f"🎉 *PURCHASE SUCCESSFUL*\n\n🔑 Key: `{key_input}`\n\nEnjoy your hack!",
            parse_mode="Markdown"
        )
        await update.message.reply_text("✅ Key Delivered Successfully!")
    
    return ConversationHandler.END

# ================= BROADCAST =================
async def broadcast_send(update: Update, context: ContextTypes.DEFAULT_TYPE):
    msg = update.message.text
    users = list(db.data["users"].keys())
    sent = 0
    failed = 0
    
    # Save broadcast
    db.data["broadcasts"].append({
        "message": msg,
        "sent_at": datetime.now().isoformat(),
        "sent_to": len(users),
        "successful": 0
    })
    
    await update.message.reply_text(f"📢 Broadcasting to {len(users)} users...")
    
    for uid in users:
        try:
            await context.bot.send_message(uid, f"📢 *ANNOUNCEMENT*\n\n{msg}", parse_mode="Markdown")
            sent += 1
            await asyncio.sleep(0.1)  # Rate limiting
        except:
            failed += 1
    
    db.data["broadcasts"][-1]["successful"] = sent
    db.save_data()
    
    await update.message.reply_text(f"✅ Broadcast sent to {sent} users! ({failed} failed)")
    return ConversationHandler.END

# ================= REBRAND =================
async def rebrand_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    if user_id not in db.data["admins"]:
        await update.callback_query.answer("Unauthorized!", show_alert=True)
        return
    
    keyboard = [
        [InlineKeyboardButton("📝 Change Name", callback_data="rebrand_name")],
        [InlineKeyboardButton("🎨 Change Logo", callback_data="rebrand_logo")],
        [InlineKeyboardButton("📄 Change Welcome Text", callback_data="rebrand_welcome")],
        [InlineKeyboardButton("💰 Rebrand Price", callback_data="rebrand_price")],
        [InlineKeyboardButton("🔙 Back", callback_data="admin_panel")]
    ]
    await update.callback_query.message.edit_text(
        "🎨 *REBRAND SETTINGS*\n\n"
        "Customize your bot:", 
        reply_markup=InlineKeyboardMarkup(keyboard), 
        parse_mode="Markdown"
    )

async def rebrand_name_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.callback_query.message.reply_text("📝 Send new bot name:")
    return REBRAND_NAME

async def rebrand_name_save(update: Update, context: ContextTypes.DEFAULT_TYPE):
    db.data["settings"]["bot_name"] = update.message.text
    db.save_data()
    await update.message.reply_text("✅ Bot name updated successfully!")
    return ConversationHandler.END

async def rebrand_logo_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.callback_query.message.reply_text("🎨 Send new bot logo (emoji or text):")
    return REBRAND_LOGO

async def rebrand_logo_save(update: Update, context: ContextTypes.DEFAULT_TYPE):
    db.data["settings"]["bot_logo"] = update.message.text
    db.save_data()
    await update.message.reply_text("✅ Bot logo updated successfully!")
    return ConversationHandler.END

# ================= PRICE SETTINGS =================
async def price_settings(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    if user_id not in db.data["admins"]:
        await update.callback_query.answer("Unauthorized!", show_alert=True)
        return
    
    prices = db.data["settings"]["rebrand_price"]
    keyboard = [
        [InlineKeyboardButton(f"Session: ₹{prices['session']}", callback_data="price_rebrand_session")],
        [InlineKeyboardButton(f"Monthly: ₹{prices['monthly']}", callback_data="price_rebrand_monthly")],
        [InlineKeyboardButton(f"Single 10 Day: ₹{prices['single']}", callback_data="price_rebrand_single")],
        [InlineKeyboardButton("📋 Manage Plans", callback_data="manage_plans")],
        [InlineKeyboardButton("🔙 Back", callback_data="admin_panel")]
    ]
    await update.callback_query.message.edit_text(
        "💰 *PRICE SETTINGS*\n\n"
        "Manage prices for all products:", 
        reply_markup=InlineKeyboardMarkup(keyboard), 
        parse_mode="Markdown"
    )

async def price_rebrand_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    context.user_data['price_type'] = query.data.split("_")[2]
    await query.message.reply_text(f"💰 Send new price for {context.user_data['price_type']}:")
    return PRICE_REBRAND

async def price_rebrand_save(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        price = int(update.message.text)
        price_type = context.user_data['price_type']
        db.data["settings"]["rebrand_price"][price_type] = price
        db.save_data()
        await update.message.reply_text(f"✅ {price_type} price updated to ₹{price}!")
    except:
        await update.message.reply_text("❌ Please send a valid number!")
    return ConversationHandler.END

# ================= RESELL =================
async def resell_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [InlineKeyboardButton("💸 Buy Resell Key", callback_data="resell_buy")],
        [InlineKeyboardButton("📋 My Resell Keys", callback_data="resell_my")],
        [InlineKeyboardButton("🔙 Back", callback_data="back_start")]
    ]
    await update.callback_query.message.edit_text(
        "💸 *RESELL SYSTEM*\n\n"
        "Buy and manage resell keys here:", 
        reply_markup=InlineKeyboardMarkup(keyboard), 
        parse_mode="Markdown"
    )

async def resell_buy(update: Update, context: ContextTypes.DEFAULT_TYPE):
    resell_price = db.data["settings"]["resell_price"]["unlimited_balance"]
    keyboard = [
        [InlineKeyboardButton(f"Unlimited Balance - ₹{resell_price}", callback_data="resell_unlimited")],
        [InlineKeyboardButton("🔙 Back", callback_data="resell_menu")]
    ]
    await update.callback_query.message.edit_text(
        f"💎 *RESELL PACKAGE*\n\n"
        f"• Unlimited Balance: ₹{resell_price}\n"
        f"• Generate unlimited keys\n"
        f"• Perfect for resellers\n\n"
        f"💰 *Price:* ₹{resell_price}",
        reply_markup=InlineKeyboardMarkup(keyboard), 
        parse_mode="Markdown"
    )

async def resell_settings(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    if user_id not in db.data["admins"]:
        await update.callback_query.answer("Unauthorized!", show_alert=True)
        return
    
    current = db.data["settings"]["resell_price"]["unlimited_balance"]
    await update.callback_query.message.reply_text(
        f"💰 *RESELL PRICE SETTINGS*\n\n"
        f"Current price: ₹{current}\n\n"
        f"Send new price:"
    )
    return RESELL_PRICE

async def resell_price_save(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        price = int(update.message.text)
        db.data["settings"]["resell_price"]["unlimited_balance"] = price
        db.save_data()
        await update.message.reply_text(f"✅ Resell price updated to ₹{price}!")
    except:
        await update.message.reply_text("❌ Please send a valid number!")
    return ConversationHandler.END

# ================= APK MANAGEMENT =================
async def manage_apks(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    if user_id not in db.data["admins"]:
        await update.callback_query.answer("Unauthorized!", show_alert=True)
        return
    
    apks = db.data["settings"]["apks"]
    keyboard = []
    for apk in apks:
        status = "✅" if apk["active"] else "❌"
        keyboard.append([
            InlineKeyboardButton(
                f"{status} {apk['name']} v{apk.get('version', '1.0')}", 
                callback_data=f"apk_detail_{apk['id']}"
            )
        ])
    
    keyboard.extend([
        [InlineKeyboardButton("➕ Add APK", callback_data="add_apk")],
        [InlineKeyboardButton("📤 Upload APK File", callback_data="upload_apk")],
        [InlineKeyboardButton("🔙 Back", callback_data="admin_panel")]
    ])
    
    await update.callback_query.message.edit_text(
        "📱 *MANAGE APKs*\n\n"
        "Total APKs: " + str(len(apks)),
        reply_markup=InlineKeyboardMarkup(keyboard),
        parse_mode="Markdown"
    )

async def apk_detail(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    apk_id = query.data.split("_")[2]
    apk = db.get_apk_by_id(apk_id)
    
    if not apk:
        await query.answer("APK not found!", show_alert=True)
        return
    
    text = (
        f"📱 *{apk['name']}*\n\n"
        f"📌 ID: `{apk['id']}`\n"
        f"📌 Version: {apk.get('version', '1.0.0')}\n"
        f"📌 Status: {'✅ Active' if apk['active'] else '❌ Inactive'}\n"
        f"📌 Changelog: {apk.get('changelog', 'No changelog')}\n"
        f"📌 Link: {apk.get('link', 'Not set')}\n\n"
    )
    
    keyboard = [
        [InlineKeyboardButton("✅ Toggle Status", callback_data=f"apk_toggle_{apk_id}")],
        [InlineKeyboardButton("✏️ Edit Name", callback_data=f"apk_edit_name_{apk_id}")],
        [InlineKeyboardButton("🔗 Edit Link", callback_data=f"apk_edit_link_{apk_id}")],
        [InlineKeyboardButton("📝 Edit Changelog", callback_data=f"apk_changelog_{apk_id}")],
        [InlineKeyboardButton("🗑️ Delete APK", callback_data=f"apk_delete_{apk_id}")],
        [InlineKeyboardButton("🔙 Back", callback_data="manage_apks")]
    ]
    
    await query.message.edit_text(text, reply_markup=InlineKeyboardMarkup(keyboard), parse_mode="Markdown")

async def apk_toggle(update: Update, context: ContextTypes.DEFAULT_TYPE):
    apk_id = update.callback_query.data.split("_")[2]
    apk = db.get_apk_by_id(apk_id)
    
    if apk:
        apk["active"] = not apk["active"]
        db.save_data()
        await update.callback_query.answer("APK toggled!", show_alert=True)
        await apk_detail(update, context)

async def add_apk_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.callback_query.message.reply_text(
        "📝 *ADD APK*\n\n"
        "Send APK name:"
    )
    return ADD_APK

async def add_apk_save(update: Update, context: ContextTypes.DEFAULT_TYPE):
    name = update.message.text
    db.add_apk(name)
    await update.message.reply_text(f"✅ APK '{name}' added successfully!")
    return ConversationHandler.END

async def upload_apk_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.callback_query.message.reply_text(
        "📤 *UPLOAD APK FILE*\n\n"
        "Select the APK to upload:\n\n"
        "List of APKs:\n"
        + "\n".join([f"• {apk['name']} (ID: {apk['id']})" for apk in db.data["settings"]["apks"]]) +
        "\n\nSend the APK ID:"
    )
    return UPLOAD_APK_FILE

async def upload_apk_file(update: Update, context: ContextTypes.DEFAULT_TYPE):
    apk_id = update.message.text.strip()
    apk = db.get_apk_by_id(apk_id)
    
    if not apk:
        await update.message.reply_text("❌ APK not found! Please send a valid APK ID.")
        return UPLOAD_APK_FILE
    
    context.user_data['uploading_apk_id'] = apk_id
    await update.message.reply_text(
        f"📤 Upload APK file for '{apk['name']}'\n\n"
        "Send the APK file (max 50MB):"
    )
    return UPLOAD_APK_FILE

async def handle_apk_file(update: Update, context: ContextTypes.DEFAULT_TYPE):
    apk_id = context.user_data.get('uploading_apk_id')
    apk = db.get_apk_by_id(apk_id)
    
    if not apk:
        await update.message.reply_text("❌ APK not found!")
        return ConversationHandler.END
    
    document = update.message.document
    if document and document.mime_type == 'application/vnd.android.package-archive':
        # Save the file
        file_path = f"apks/{apk_id}.apk"
        file = await context.bot.get_file(document.file_id)
        await file.download_to_drive(file_path)
        
        apk["file_path"] = file_path
        db.save_data()
        
        await update.message.reply_text(f"✅ APK file uploaded successfully for '{apk['name']}'!")
    else:
        await update.message.reply_text("❌ Please send a valid APK file (.apk)")
        return UPLOAD_APK_FILE
    
    return ConversationHandler.END

# ================= APK DOWNLOAD =================
async def apk_download(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    apks = db.data["settings"]["apks"]
    active_apks = [apk for apk in apks if apk["active"]]
    
    if not active_apks:
        await query.message.edit_text(
            "❌ No APKs available currently. Check back later!", 
            reply_markup=get_back_keyboard(), 
            parse_mode="Markdown"
        )
        return
    
    keyboard = []
    for apk in active_apks:
        version = apk.get('version', '1.0')
        has_file = "📱" if apk.get('file_path') and os.path.exists(apk.get('file_path', '')) else "🔗"
        keyboard.append([
            InlineKeyboardButton(
                f"{has_file} {apk['name']} v{version}", 
                callback_data=f"apk_dl_{apk['id']}"
            )
        ])
    keyboard.append([InlineKeyboardButton("🔙 Back", callback_data="back_start")])
    
    # Update stats
    db.update_daily_stats("downloads")
    db.data["stats"]["total_apk_downloads"] += 1
    db.save_data()
    
    await query.message.edit_text(
        "📱 *APK DOWNLOAD*\n\n"
        "Select an APK to download:",
        reply_markup=InlineKeyboardMarkup(keyboard),
        parse_mode="Markdown"
    )

async def apk_download_link(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    apk_id = query.data.split("_")[2]
    apk = db.get_apk_by_id(apk_id)
    
    if not apk:
        await query.answer("APK not found!", show_alert=True)
        return
    
    # Update user download count
    user_data = db.get_user(query.from_user.id)
    user_data["downloads"] += 1
    db.save_data()
    
    text = (
        f"📱 *{apk['name']}*\n\n"
        f"📌 Version: {apk.get('version', '1.0.0')}\n"
        f"📝 Changelog:\n{apk.get('changelog', 'No changelog available')}\n\n"
    )
    
    keyboard = []
    
    # Check if file exists locally
    if apk.get('file_path') and os.path.exists(apk.get('file_path', '')):
        keyboard.append([InlineKeyboardButton("📥 Download File", callback_data=f"apk_file_{apk_id}")])
    
    if apk.get('link'):
        keyboard.append([InlineKeyboardButton("🔗 Download Link", url=apk['link'])])
    
    if not keyboard:
        text += "❌ No download links available for this APK."
        keyboard.append([InlineKeyboardButton("🔙 Back", callback_data="apk_download")])
    else:
        keyboard.append([InlineKeyboardButton("🔙 Back", callback_data="apk_download")])
    
    await query.message.edit_text(
        text,
        reply_markup=InlineKeyboardMarkup(keyboard),
        parse_mode="Markdown"
    )

async def apk_file_download(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    apk_id = query.data.split("_")[2]
    apk = db.get_apk_by_id(apk_id)
    
    if not apk or not apk.get('file_path') or not os.path.exists(apk.get('file_path', '')):
        await query.answer("File not found!", show_alert=True)
        return
    
    try:
        with open(apk['file_path'], 'rb') as f:
            await context.bot.send_document(
                chat_id=query.message.chat_id,
                document=InputFile(f, filename=f"{apk['name']}.apk"),
                caption=f"📱 *{apk['name']}*\nVersion: {apk.get('version', '1.0.0')}",
                parse_mode="Markdown"
            )
    except Exception as e:
        logger.error(f"File download error: {e}")
        await query.answer("Error downloading file!", show_alert=True)

# ================= BAN USER =================
async def ban_user_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    if user_id not in db.data["admins"]:
        await update.message.reply_text("❌ Unauthorized!")
        return
    
    try:
        target_id = int(update.message.text)
        if db.ban_user(target_id):
            await update.message.reply_text(f"✅ User {target_id} banned successfully!")
            try:
                await context.bot.send_message(target_id, "🚫 You have been banned from using this bot.")
            except:
                pass
        else:
            await update.message.reply_text(f"❌ User {target_id} is already banned.")
    except ValueError:
        await update.message.reply_text("❌ Please send a valid user ID.")
    
    return ConversationHandler.END

async def unban_user_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    if user_id not in db.data["admins"]:
        await update.message.reply_text("❌ Unauthorized!")
        return
    
    try:
        target_id = int(update.message.text.split()[1])
        if db.unban_user(target_id):
            await update.message.reply_text(f"✅ User {target_id} unbanned successfully!")
            try:
                await context.bot.send_message(target_id, "✅ You have been unbanned. You can now use the bot.")
            except:
                pass
        else:
            await update.message.reply_text(f"❌ User {target_id} is not banned.")
    except (IndexError, ValueError):
        await update.message.reply_text("❌ Usage: /unban USER_ID")
    
    return ConversationHandler.END

# ================= AI ASSISTANT =================
async def ai_assistant_task(context: ContextTypes.DEFAULT_TYPE):
    """Background task to send AI messages"""
    for user_id in list(db.data["users"].keys()):
        try:
            user_id_int = int(user_id)
            if ai_assistant.should_send_message(user_id_int) and not db.is_user_banned(user_id_int):
                msg = ai_assistant.get_next_message()
                await context.bot.send_message(
                    user_id_int,
                    f"🤖 *AI Assistant*\n\n{msg}\n\nNeed help? Just reply!",
                    parse_mode="Markdown"
                )
                await asyncio.sleep(0.5)  # Rate limiting
        except Exception as e:
            logger.error(f"AI message error for {user_id}: {e}")

# ================= CONTACT OWNER =================
async def contact_owner(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    keyboard = [
        [InlineKeyboardButton("📞 WhatsApp", url="https://wa.me/8170952537")],
        [InlineKeyboardButton("💬 Telegram", url="https://t.me/RayyanDevx")],
        [InlineKeyboardButton("📧 Email", callback_data="email_owner")],
        [InlineKeyboardButton("🔙 Back", callback_data="back_start")]
    ]
    await query.message.edit_text(
        "👑 *CONTACT OWNER*\n\n"
        "📱 *Direct Contact:*\n"
        "• Telegram: @RayyanDevx\n"
        "• WhatsApp: +91 8170952537\n\n"
        "⏰ *Response Time:* Within 24 hours",
        reply_markup=InlineKeyboardMarkup(keyboard),
        parse_mode="Markdown"
    )

# ================= LIVE STATS =================
async def live_stats(update: Update, context: ContextTypes.DEFAULT_TYPE):
    stats = db.data["stats"]
    daily_stats = db.get_daily_stats()
    
    text = (
        f"📊 *LIVE STATISTICS*\n\n"
        f"👥 Total Users: {len(db.data['users'])}\n"
        f"✅ Approved Payments: {stats['total_approved']}\n"
        f"❌ Rejected Payments: {stats['total_rejected']}\n"
        f"🔑 Keys Sold: {stats['keys_sold']}\n"
        f"🎁 Total Referrals: {stats['total_referrals']}\n"
        f"💰 Revenue Generated: ₹{stats['total_balance']}\n"
        f"📱 APK Downloads: {stats['total_apk_downloads']}\n\n"
        f"📈 *Today's Activity*\n"
        f"👥 New Users: {daily_stats['users']}\n"
        f"🔑 Keys Sold: {daily_stats['keys_sold']}\n"
        f"💰 Revenue: ₹{daily_stats['revenue']}\n"
        f"📱 Downloads: {daily_stats['downloads']}\n\n"
        f"🔄 *Last Updated:* {datetime.now().strftime('%d/%m/%Y %H:%M')}"
    )
    await update.callback_query.message.edit_text(
        text, 
        reply_markup=get_back_keyboard(), 
        parse_mode="Markdown"
    )

# ================= OTHER HANDLERS =================
async def my_keys(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    user_id = query.from_user.id
    user_data = db.get_user(user_id)
    keys = user_data["keys"]
    
    text = "🔑 *Your Keys:*\n\n"
    if keys:
        for k in keys:
            expires = k.get('expires_at', 'N/A')
            status = "✅ Active" if k.get('is_active', True) else "❌ Expired"
            text += f"• `{k['key']}` - {status}\n"
    else:
        text += "No keys found. Purchase a key to get started!"
    
    await query.message.edit_text(
        text, 
        reply_markup=get_back_keyboard(), 
        parse_mode="Markdown"
    )

async def referral(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    user = query.from_user
    user_data = db.get_user(user.id)
    bot_username = (await context.bot.get_me()).username
    link = f"https://t.me/{bot_username}?start={user.id}"
    bonus = db.data["settings"]["referral_bonus"]
    
    text = (
        f"🎁 *REFERRAL PROGRAM*\n\n"
        f"🔗 *Your Link:*\n`{link}`\n\n"
        f"👥 *Referrals:* {user_data['refs']}\n"
        f"💰 *Earned:* ₹{user_data['balance']}\n"
        f"💎 *Bonus per Referral:* ₹{bonus}\n\n"
        f"💡 *How it works:*\n"
        f"• Share your link with friends\n"
        f"• Get ₹{bonus} for each referral\n"
        f"• Unlimited earning potential!"
    )
    await query.message.edit_text(
        text, 
        reply_markup=InlineKeyboardMarkup([
            [InlineKeyboardButton("📤 Share Link", url=f"https://t.me/share/url?url={link}&text=Join this amazing bot!")],
            [InlineKeyboardButton("🔙 Back", callback_data="back_start")]
        ]), 
        parse_mode="Markdown"
    )

async def support(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = (
        f"📞 *SUPPORT CENTER*\n\n"
        f"• Payment Issues\n"
        f"• Setup Guide\n"
        f"• Key Replacement\n"
        f"• Technical Help\n\n"
        f"💬 Admin: {SUPPORT_USERNAME}\n"
        f"⏰ Response: 24/7"
    )
    await update.callback_query.message.edit_text(
        text, 
        reply_markup=get_back_keyboard(), 
        parse_mode="Markdown"
    )

# ================= MAIN =================
def main():
    app = Application.builder().token(BOT_TOKEN).build()
    
    # Admin Conversation
    admin_conv = ConversationHandler(
        entry_points=[
            CallbackQueryHandler(admin_callback, pattern="adm_"),
            CommandHandler("admin", admin_panel)
        ],
        states={
            SENDING_KEY: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, deliver_key)
            ],
            BROADCAST_MSG: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, broadcast_send)
            ],
            BAN_USER: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, ban_user_handler)
            ],
            UPLOAD_APK_FILE: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, upload_apk_file),
                MessageHandler(filters.Document.APK, handle_apk_file)
            ],
        },
        fallbacks=[CommandHandler("start", start)]
    )
    
    # Rebrand Conversations
    rebrand_conv = ConversationHandler(
        entry_points=[CallbackQueryHandler(rebrand_name_start, pattern="rebrand_name")],
        states={REBRAND_NAME: [MessageHandler(filters.TEXT & ~filters.COMMAND, rebrand_name_save)]},
        fallbacks=[CommandHandler("start", start)]
    )
    
    rebrand_logo_conv = ConversationHandler(
        entry_points=[CallbackQueryHandler(rebrand_logo_start, pattern="rebrand_logo")],
        states={REBRAND_LOGO: [MessageHandler(filters.TEXT & ~filters.COMMAND, rebrand_logo_save)]},
        fallbacks=[CommandHandler("start", start)]
    )
    
    # Price Conversations
    price_rebrand_conv = ConversationHandler(
        entry_points=[CallbackQueryHandler(price_rebrand_start, pattern="price_rebrand_")],
        states={PRICE_REBRAND: [MessageHandler(filters.TEXT & ~filters.COMMAND, price_rebrand_save)]},
        fallbacks=[CommandHandler("start", start)]
    )
    
    # Resell Conversations
    resell_price_conv = ConversationHandler(
        entry_points=[CallbackQueryHandler(resell_settings, pattern="resell_settings")],
        states={RESELL_PRICE: [MessageHandler(filters.TEXT & ~filters.COMMAND, resell_price_save)]},
        fallbacks=[CommandHandler("start", start)]
    )
    
    # APK Conversations
    add_apk_conv = ConversationHandler(
        entry_points=[CallbackQueryHandler(add_apk_start, pattern="add_apk")],
        states={ADD_APK: [MessageHandler(filters.TEXT & ~filters.COMMAND, add_apk_save)]},
        fallbacks=[CommandHandler("start", start)]
    )
    
    upload_apk_conv = ConversationHandler(
        entry_points=[CallbackQueryHandler(upload_apk_start, pattern="upload_apk")],
        states={
            UPLOAD_APK_FILE: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, upload_apk_file),
                MessageHandler(filters.Document.APK, handle_apk_file)
            ]
        },
        fallbacks=[CommandHandler("start", start)]
    )
    
    # Add all handlers
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("unban", unban_user_handler))
    app.add_handler(admin_conv)
    app.add_handler(rebrand_conv)
    app.add_handler(rebrand_logo_conv)
    app.add_handler(price_rebrand_conv)
    app.add_handler(resell_price_conv)
    app.add_handler(add_apk_conv)
    app.add_handler(upload_apk_conv)
    
    # Callback handlers
    app.add_handler(CallbackQueryHandler(verify_channel, pattern="verify_channel"))
    app.add_handler(CallbackQueryHandler(buy_menu, pattern="buy"))
    app.add_handler(CallbackQueryHandler(plan_confirm, pattern="p_"))
    app.add_handler(CallbackQueryHandler(pay_now, pattern="pay_now"))
    app.add_handler(CallbackQueryHandler(my_keys, pattern="mykeys"))
    app.add_handler(CallbackQueryHandler(referral, pattern="ref"))
    app.add_handler(CallbackQueryHandler(support, pattern="support"))
    app.add_handler(CallbackQueryHandler(start, pattern="back_start"))
    app.add_handler(CallbackQueryHandler(contact_owner, pattern="contact_owner"))
    app.add_handler(CallbackQueryHandler(resell_menu, pattern="resell_menu"))
    app.add_handler(CallbackQueryHandler(resell_buy, pattern="resell_buy"))
    app.add_handler(CallbackQueryHandler(live_stats, pattern="live_stats"))
    app.add_handler(CallbackQueryHandler(admin_panel, pattern="admin_panel"))
    app.add_handler(CallbackQueryHandler(rebrand_menu, pattern="rebrand_menu"))
    app.add_handler(CallbackQueryHandler(price_settings, pattern="price_settings"))
    app.add_handler(CallbackQueryHandler(manage_apks, pattern="manage_apks"))
    app.add_handler(CallbackQueryHandler(apk_detail, pattern="apk_detail_"))
    app.add_handler(CallbackQueryHandler(apk_toggle, pattern="apk_toggle_"))
    app.add_handler(CallbackQueryHandler(apk_download, pattern="apk_download$"))
    app.add_handler(CallbackQueryHandler(apk_download_link, pattern="apk_dl_"))
    app.add_handler(CallbackQueryHandler(apk_file_download, pattern="apk_file_"))
    app.add_handler(CallbackQueryHandler(admin_callback, pattern="admin_"))
    
    # Message handlers
    app.add_handler(MessageHandler(filters.PHOTO, handle_screenshot))
    app.add_handler(MessageHandler(filters.Document.APK, handle_apk_file))
    
    # AI Assistant background task
    job_queue = app.job_queue
    if job_queue:
        job_queue.run_repeating(ai_assistant_task, interval=60, first=10)
    
    print("🚀 Advanced Rolex Premium Bot V2.0 Started Successfully!")
    print(f"👤 Admin ID: {ADMIN_ID}")
    print(f"📊 Total Users: {len(db.data['users'])}")
    print(f"📱 Features: Advanced Management, AI Assistant, APK System")
    print(f"🔄 AI Assistant Active (every 1 minute)")
    app.run_polling()

if __name__ == "__main__":
    main()