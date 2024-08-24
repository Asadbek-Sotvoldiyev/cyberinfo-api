import asyncio
from decouple import config
from django.utils import timezone
import random
from asgiref.sync import sync_to_async
from .models import User, UserConfirmation
from telegram import Update, KeyboardButton, ReplyKeyboardMarkup,ReplyKeyboardRemove
from telegram.ext import Application, CommandHandler, MessageHandler, filters, CallbackContext

@sync_to_async
def get_user_by_username(username):
    return User.objects.filter(username=username).first()

@sync_to_async
def create_user(username, first_name, last_name, phone_number):
    return User.objects.create(username=username, first_name=first_name, last_name=last_name, phone_number=phone_number)

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


def generate_code() -> str:
    code = "".join([str(random.randint(0, 10000) % 10) for _ in range(4)])
    return code


async def start(update: Update, context: CallbackContext) -> None:
    user = update.message.from_user
    username = user.username

    result = await get_user_by_username(username)

    if result:
        user_confirmation = await get_user_confirmation(result)
        verifies = await get_verifies(result, user_confirmation)
        if not verifies:
            new_code = generate_code()
            await update_user_confirmation_code(user_confirmation, new_code)
            await update.message.reply_text(f"Salom! Sizning yangi kodingiz: {new_code}")
        else:
            await update.message.reply_text(f"Eski kodingiz hali ham kuchda ☝️")
    else:
        button = KeyboardButton(text="Telefon raqam yuborish", request_contact=True)
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
    phone_number = update.message.contact.phone_number if update.message.contact else 'N/A'

    result = await get_user_by_username(user.username)

    if result:
        user_confirmation = await get_user_confirmation(result)
        verifies = await get_verifies(result, user_confirmation)
        if not verifies:
            new_code = generate_code()
            await update_user_confirmation_code(user_confirmation, new_code)
            await update.message.reply_text(f"Salom! Sizning yangi kodingiz: {new_code}")
            await update.message.reply_text(
                '🇺🇿Yangi kod olish uchun /login ni bosing\n\n 🇺🇸🔑To get a new code click /login',
                reply_markup=ReplyKeyboardRemove()
            )
        else:
            await update.message.reply_text(f"Eski kodingiz hali ham kuchda ☝️")
    else:
        code = generate_code()

        last_name = user.last_name if user.last_name else ""

        new_user = await create_user(user.username, user.first_name, last_name, phone_number)
        await create_user_confirmation(new_user, code)

        await update.message.reply_text(
            f"🔒 Code:\n<code>{code}</code>", parse_mode='HTML'
        )
        await update.message.reply_text(
            '🇺🇿Yangi kod olish uchun /login ni bosing\n\n 🇺🇸🔑To get a new code click /login',
            reply_markup=ReplyKeyboardRemove()
        )


async def login(update: Update, context: CallbackContext) -> None:
    user = update.message.from_user

    result = await get_user_by_username(user.username)
    if result:
        user_confirmation = await get_user_confirmation(result)
        verifies = await get_verifies(result, user_confirmation)
        if not verifies:
            new_code = generate_code()
            await update_user_confirmation_code(user_confirmation, new_code)
            await update.message.reply_text(f"Yangi kodingiz: <code>{new_code}</code>", parse_mode='HTML')
        else:
            await update.message.reply_text(f"Eski kodingiz hali ham kuchda ☝️")




def auth_telegram():
    application = Application.builder().token(config('BOT_TOKEN')).build()

    application.add_handler(CommandHandler("start", start))
    application.add_handler(MessageHandler(filters.CONTACT, phone_number_received))
    application.add_handler(CommandHandler("login", login))

    application.run_polling()


if __name__ == '__main__':
    loop = asyncio.get_event_loop()
    loop.run_until_complete(auth_telegram())
