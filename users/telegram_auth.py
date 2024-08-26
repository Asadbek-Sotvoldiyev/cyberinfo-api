import asyncio
from datetime import datetime
from decouple import config
from django.utils import timezone
import random
from asgiref.sync import sync_to_async
from .models import User, UserConfirmation
from telegram import Update, KeyboardButton, ReplyKeyboardMarkup,ReplyKeyboardRemove
from telegram.ext import Application, CommandHandler, MessageHandler, filters, CallbackContext
from django.db.utils import InterfaceError
from django.db import connections

@sync_to_async
def get_user_by_phone(phone):
    try:
        return User.objects.filter(phone_number=phone).first()
    except InterfaceError:
        connections.close_all()
        return User.objects.filter(phone_number=phone).first()

@sync_to_async
def get_user_by_chat_id(chat_id):
    try:
        return User.objects.filter(chat_id=chat_id).first()
    except InterfaceError:
        connections.close_all()
        return User.objects.filter(chat_id=chat_id).first()

@sync_to_async
def create_user(username, first_name, last_name, phone_number, chat_id):
    return User.objects.create(username=username, first_name=first_name, last_name=last_name, phone_number=phone_number, chat_id=chat_id)

@sync_to_async
def create_user_confirmation(user, code):
    return UserConfirmation.objects.create(user=user, code=code)

@sync_to_async
def get_user_confirmation(user):
    return UserConfirmation.objects.get(user=user)

@sync_to_async
def update_user_confirmation_code(user_confirmation, new_code):
    user_confirmation.code = new_code
    user_confirmation.save()

@sync_to_async
def get_verifies(user, user_confirmation):
    return user.verify_codes.filter(
        expiration_time__gte=timezone.now(),
        code=user_confirmation.code,
        is_confirmed=False
    ).exists()

@sync_to_async
def get_time(user_confirmation):
    return (user_confirmation.expiration_time-timezone.now()).total_seconds()


def generate_code() -> str:
    code = "".join([str(random.randint(0, 10000) % 10) for _ in range(4)])
    return code


async def start(update: Update, context: CallbackContext) -> None:
    chat_id = update.message.chat_id

    result = await get_user_by_chat_id(chat_id)

    if result:
        user_confirmation = await get_user_confirmation(result)
        verifies = await get_verifies(result, user_confirmation)
        minute = await get_time(user_confirmation)//60
        second = await get_time(user_confirmation)%60
        if not verifies:
            new_code = generate_code()
            await update_user_confirmation_code(user_confirmation, new_code)
            await update.message.reply_text(
                f"🔒 Code:\n<code>{new_code}</code>", parse_mode='HTML'
            )
            await update.message.reply_text(
                '🇺🇿Yangi kod olish uchun /login ni bosing\n\n 🇺🇸🔑To get a new code click /login'
            )
        else:
            await update.message.reply_text(
                f"⏳ Eski kodingiz hali ham kuchda! ☝️\n"
                f"<b>{round(minute)}</b> daqiqa <b>{round(second)}</b> sekunddan so'ng yangi kod olishingiz mumkin.",
                parse_mode='HTML'
            )
    else:
        button = KeyboardButton(text="Send / Yuborish", request_contact=True)
        reply_markup = ReplyKeyboardMarkup([[button]], one_time_keyboard=True)
        await update.message.reply_text("""
🇺🇿
<b>Salom 👋</b>
@cyberinfo_uz <b>ning rasmiy botiga xush kelibsiz!</b>

⬇️ Kontaktingizni yuboring (tugmani bosib)

🇺🇸
<b>Hi 👋</b>
<b>Welcome to @cyberinfo_uz's official bot</b>

⬇️ Send your contact (by clicking button)""", reply_markup=reply_markup, parse_mode='HTML')

async def phone_number_received(update: Update, context: CallbackContext) -> None:
    user = update.message.from_user
    phone_number = '+' + update.message.contact.phone_number if update.message.contact else 'N/A'
    chat_id = update.message.chat_id
    result = await get_user_by_phone(phone_number)

    if result:
        user_confirmation = await get_user_confirmation(result)
        verifies = await get_verifies(result, user_confirmation)
        if not verifies:
            new_code = generate_code()
            await update_user_confirmation_code(user_confirmation, new_code)
            await update.message.reply_text(
                f"🔒 Code:\n<code>{new_code}</code>", parse_mode='HTML'
            )
            await update.message.reply_text(
                '🇺🇿Yangi kod olish uchun /login ni bosing\n\n 🇺🇸🔑To get a new code click /login',
                reply_markup=ReplyKeyboardRemove()
            )
        else:
            minute = await get_time(user_confirmation) // 60
            second = await get_time(user_confirmation) % 60
            await update.message.reply_text(
                f"⏳ Eski kodingiz hali ham kuchda! ☝️\n"
                f"<b>{round(minute)}</b> daqiqa <b>{round(second)}</b> sekunddan so'ng yangi kod olishingiz mumkin.",
                parse_mode='HTML'
            )
    else:
        code = generate_code()

        last_name = user.last_name if user.last_name else ""

        new_user = await create_user(phone_number, user.first_name, last_name, phone_number, chat_id)
        await create_user_confirmation(new_user, code)

        await update.message.reply_text(
            f"🔒 Code:\n<code>{code}</code>", parse_mode='HTML'
        )
        await update.message.reply_text(
            '🇺🇿Yangi kod olish uchun /login ni bosing\n\n 🇺🇸🔑To get a new code click /login',
            reply_markup=ReplyKeyboardRemove()
        )


async def login(update: Update, context: CallbackContext) -> None:
    chat_id = update.message.chat_id

    result = await get_user_by_chat_id(chat_id)
    if result:
        user_confirmation = await get_user_confirmation(result)
        verifies = await get_verifies(result, user_confirmation)
        if not verifies:
            new_code = generate_code()
            await update_user_confirmation_code(user_confirmation, new_code)
            await update.message.reply_text(
                f"🔒 Code:\n<code>{new_code}</code>", parse_mode='HTML'
            )
            await update.message.reply_text(
                '🇺🇿Yangi kod olish uchun /login ni bosing\n\n 🇺🇸🔑To get a new code click /login',
                reply_markup=ReplyKeyboardRemove()
            )
        else:
            minute = await get_time(user_confirmation) // 60
            second = await get_time(user_confirmation) % 60
            await update.message.reply_text(
                f"⏳ Eski kodingiz hali ham kuchda! ☝️\n"
                f"<b>{round(minute)}</b> daqiqa <b>{round(second)}</b> sekunddan so'ng yangi kod olishingiz mumkin.",
                parse_mode='HTML'
            )



def auth_telegram():
    application = Application.builder().token(config('BOT_TOKEN')).build()

    application.add_handler(CommandHandler("start", start))
    application.add_handler(MessageHandler(filters.CONTACT, phone_number_received))
    application.add_handler(CommandHandler("login", login))

    application.run_polling()


if __name__ == '__main__':
    loop = asyncio.get_event_loop()
    loop.run_until_complete(auth_telegram())
