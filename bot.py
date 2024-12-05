# 841285032 1087968824
# 7624174806:AAEdh-WlzNAJ2hGfODSOjCXOVKB3SlUqRMA

from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes

# Słownik przechowujący komendy i ich odpowiedzi
commands = {
    "website": "https://devcult.tech/",
    "chart": "https://example.com/chart",
    "ca": "0x1234567890abcdef1234567890abcdef12345678"
}

# Lista administratorów (użytkownicy z uprawnieniami do zarządzania komendami)
ADMINS = [1087968824]  # Zastąp swoją ID Telegram

# Funkcja dla komendy start
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Witaj! Podaj komendę, aby otrzymać odpowiedź.")

# Funkcja do obsługi komend
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_input = update.message.text.lower()
    if user_input in commands:
        await update.message.reply_text(commands[user_input])
    # Jeśli komenda nie jest rozpoznana, bot ignoruje wiadomość
    return

# Funkcja do dodawania nowej komendy (dla administratorów)
async def add_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id not in ADMINS:
        await update.message.reply_text("Nie masz uprawnień do tej akcji.")
        return

    if len(context.args) < 2:
        await update.message.reply_text("Użycie: /add <komenda> <odpowiedź>")
        return

    command = context.args[0].lower()
    response = " ".join(context.args[1:])
    commands[command] = response
    await update.message.reply_text(f"Komenda '{command}' została dodana.")

# Funkcja do usuwania komendy (dla administratorów)
async def remove_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id not in ADMINS:
        await update.message.reply_text("Nie masz uprawnień do tej akcji.")
        return

    if len(context.args) != 1:
        await update.message.reply_text("Użycie: /remove <komenda>")
        return

    command = context.args[0].lower()
    if command in commands:
        del commands[command]
        await update.message.reply_text(f"Komenda '{command}' została usunięta.")
    else:
        await update.message.reply_text("Taka komenda nie istnieje.")

# Funkcja do wyświetlenia wszystkich komend
async def list_commands(update: Update, context: ContextTypes.DEFAULT_TYPE):
    commands_list = "\n".join([f"{cmd}: {resp}" for cmd, resp in commands.items()])
    await update.message.reply_text(f"Dostępne komendy:\n{commands_list}")

# Główna funkcja uruchamiająca bota
def main():
    TOKEN = "7624174806:AAEdh-WlzNAJ2hGfODSOjCXOVKB3SlUqRMA"  # Wprowadź swój token bota
    application = Application.builder().token(TOKEN).build()

    # Handlery
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("add", add_command))
    application.add_handler(CommandHandler("remove", remove_command))
    application.add_handler(CommandHandler("list", list_commands))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    # Uruchomienie bota
    application.run_polling()

if __name__ == "__main__":
    main()
