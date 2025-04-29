from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, CallbackContext, CallbackQueryHandler

TELEGRAM_TOKEN = '7579256176:AAFJVdxzsSNftobGvmY0LmT13Ft2stwjKTg'

richieste = {}
crediti = {}
admin_id = None
risposte = {}

def start(update: Update, context: CallbackContext):
    global admin_id
    chat_id = update.effective_chat.id
    if admin_id is None:
        admin_id = chat_id
    update.message.reply_text(
        "👋 Benvenuto su *AI Assistant Express*!\n"
        "Scrivi la tua richiesta per iniziare.\n"
        "- 1 richiesta = 1€\n"
        "- 3 richieste = 2,5€\n"
        "- 10 richieste = 7€\n", parse_mode='Markdown'
    )

def mostra_nuova_richiesta(chat_id, context: CallbackContext):
    if crediti.get(chat_id, 0) > 0:
        btn = [[InlineKeyboardButton("➕ Fai una nuova richiesta", callback_data="nuova_richiesta")]]
        context.bot.send_message(chat_id=chat_id, text=f"Hai {crediti[chat_id]} richieste disponibili.", reply_markup=InlineKeyboardMarkup(btn))

def ricevi_testo(update: Update, context: CallbackContext):
    global risposte
    chat_id = update.effective_chat.id
    text = update.message.text
    if chat_id == admin_id and chat_id in risposte:
        utente = risposte[chat_id]
        context.bot.send_message(chat_id=utente, text=f"✉️ Risposta: {text}")
        mostra_nuova_richiesta(utente, context)
        context.bot.send_message(chat_id=chat_id, text="✅ Risposta inviata.")
        del risposte[chat_id]
    else:
        if crediti.get(chat_id, 0) > 0:
            crediti[chat_id] -= 1
            context.bot.send_message(chat_id=admin_id, text=f"📨 Richiesta:
{text}", reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("✏️ Rispondi", callback_data=f"rispondi_{chat_id}")]]))
        else:
            richieste[chat_id] = text
            btns = [
                [InlineKeyboardButton("1 richiesta (1€)", callback_data="buy_1")],
                [InlineKeyboardButton("3 richieste (2.5€)", callback_data="buy_3")],
                [InlineKeyboardButton("10 richieste (7€)", callback_data="buy_10")]
            ]
            context.bot.send_message(chat_id=chat_id, text="Seleziona un pacchetto per procedere:", reply_markup=InlineKeyboardMarkup(btns))

def gestisci_bottoni(update: Update, context: CallbackContext):
    query = update.callback_query
    data = query.data
    chat_id = query.from_user.id
    if data.startswith("buy_"):
        quanti = int(data.split("_")[1])
        crediti[chat_id] = crediti.get(chat_id, 0) + quanti
        context.bot.send_message(chat_id=chat_id, text=f"✅ Hai acquistato {quanti} richieste.")
    elif data.startswith("rispondi_"):
        utente = int(data.split("_")[1])
        risposte[chat_id] = utente
        context.bot.send_message(chat_id=chat_id, text="✏️ Invia la risposta per l’utente.")
    elif data == "nuova_richiesta":
        context.bot.send_message(chat_id=chat_id, text="✏️ Scrivi la tua nuova richiesta!")

def main():
    updater = Updater(TELEGRAM_TOKEN, use_context=True)
    dp = updater.dispatcher
    dp.add_handler(CommandHandler("start", start))
    dp.add_handler(MessageHandler(Filters.text & ~Filters.command, ricevi_testo))
    dp.add_handler(CallbackQueryHandler(gestisci_bottoni))
    updater.start_polling()
    updater.idle()

if __name__ == '__main__':
    main()
