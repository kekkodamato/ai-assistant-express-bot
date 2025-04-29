from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, CallbackContext, CallbackQueryHandler
import os

TELEGRAM_TOKEN = '7579256176:AAFJVdxzsSNftobGvmY0LmT13Ft2stwjKTg'
PAYPAL_LINK_1 = 'https://paypal.me/kekkodamato/1'
PAYPAL_LINK_3 = 'https://paypal.me/kekkodamato/2.5'
PAYPAL_LINK_10 = 'https://paypal.me/kekkodamato/7'
ADMIN_CHAT_ID = None

richieste_in_attesa = {}
pagamenti_in_attesa = {}
storico_richieste = {}
crediti = {}
richieste_in_sviluppo = {}
risposte_in_attesa = {}

def get_chat_id(update):
    if update.callback_query:
        return update.callback_query.from_user.id
    elif update.message:
        return update.message.chat.id
    else:
        return None

def start(update: Update, context: CallbackContext):
    global ADMIN_CHAT_ID
    chat_id = get_chat_id(update)
    if ADMIN_CHAT_ID is None and chat_id is not None:
        ADMIN_CHAT_ID = chat_id

    update.message.reply_text(
        "👋 Benvenuto su *AI Assistant Express*!\n\n"
        "Con questo bot puoi usare la potenza di ChatGPT Plus per generare testi, immagini, presentazioni, file PDF e molto altro.\n\n"
        "✅ Nessun abbonamento richiesto\n"
        "✅ Prezzi chiari e semplici:\n"
        "- 1 richiesta = 1€\n"
        "- 3 richieste = 2,5€\n"
        "- 10 richieste = 7€\n\n"
        "Scrivimi la tua prima richiesta per iniziare!", parse_mode='Markdown')

def mostra_bottone_nuova_richiesta(chat_id, context: CallbackContext):
    crediti_restanti = crediti.get(chat_id, 0)
    if crediti_restanti > 0:
        keyboard = [[InlineKeyboardButton("➕ Fai una nuova richiesta", callback_data='nuova_richiesta')]]
        reply_markup = InlineKeyboardMarkup(keyboard)
        context.bot.send_message(chat_id=chat_id, text=f"➕ Ti rimangono {crediti_restanti} richieste disponibili.", reply_markup=reply_markup)

def ricevi_messaggio(update: Update, context: CallbackContext):
    global risposte_in_attesa
    chat_id = get_chat_id(update)
    text = update.message.text

    if chat_id == ADMIN_CHAT_ID and chat_id in risposte_in_attesa:
        utente_id = risposte_in_attesa[chat_id]
        context.bot.send_message(chat_id=utente_id, text=f"📩 Risposta dell'assistente:\n\n{text}")
        mostra_bottone_nuova_richiesta(utente_id, context)
        context.bot.send_message(chat_id=chat_id, text="✅ Risposta inviata con successo!")
        del risposte_in_attesa[chat_id]
    else:
        ricevi_richiesta(update, context)

def ricevi_richiesta(update: Update, context: CallbackContext):
    global ADMIN_CHAT_ID
    chat_id = get_chat_id(update)
    if chat_id is None:
        return

    if ADMIN_CHAT_ID is None:
        ADMIN_CHAT_ID = chat_id

    text = update.message.text

    if chat_id in richieste_in_sviluppo:
        context.bot.send_message(chat_id=chat_id, text="⏳ La tua richiesta precedente è ancora in fase di sviluppo.")
        return

    if crediti.get(chat_id, 0) > 0:
        richieste_in_sviluppo[chat_id] = text
        crediti[chat_id] -= 1
        storico_richieste.setdefault(chat_id, []).append(text)
        keyboard = [[InlineKeyboardButton("✏️ Rispondi subito", callback_data=f"rispondi_{chat_id}")]]
        reply_markup = InlineKeyboardMarkup(keyboard)
        context.bot.send_message(chat_id=ADMIN_CHAT_ID, text=f"📩 Nuova richiesta:\n\n{text}", reply_markup=reply_markup)
    else:
        richieste_in_attesa[chat_id] = {"domanda": text}
        mostra_menu_acquisto(chat_id, context)

def mostra_menu_acquisto(chat_id, context: CallbackContext):
    keyboard = [
        [InlineKeyboardButton("📝 1 richiesta (1€)", callback_data='1')],
        [InlineKeyboardButton("📄 3 richieste (2,5€)", callback_data='3')],
        [InlineKeyboardButton("📚 10 richieste (7€)", callback_data='10')]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    context.bot.send_message(chat_id=chat_id, text="Scegli un pacchetto per continuare:", reply_markup=reply_markup)

def button(update: Update, context: CallbackContext):
    query = update.callback_query
    chat_id = get_chat_id(update)
    data = query.data

    if data.startswith("rispondi_"):
        utente_id = int(data.split("_")[1])
        risposte_in_attesa[chat_id] = utente_id
        context.bot.send_message(chat_id=chat_id, text="✏️ Scrivi ora la risposta da inviare al cliente.")
        return

    if data == 'nuova_richiesta':
        if chat_id not in richieste_in_sviluppo:
            context.bot.send_message(chat_id=chat_id, text="Scrivi la tua nuova richiesta.")
        return

    pacchetti = {'1': (1, 1), '3': (2.5, 3), '10': (7, 10)}
    if data in pacchetti:
        prezzo, quanti = pacchetti[data]
        crediti[chat_id] = crediti.get(chat_id, 0) + quanti
        context.bot.send_message(chat_id=chat_id, text=f"✅ Hai acquistato {quanti} richieste. Invia ora la tua domanda!")

def main():
    updater = Updater(TELEGRAM_TOKEN, use_context=True)
    dp = updater.dispatcher

    dp.add_handler(CommandHandler("start", start))
    dp.add_handler(CallbackQueryHandler(button))
    dp.add_handler(MessageHandler(Filters.text & ~Filters.command, ricevi_messaggio))

    updater.start_polling()
    updater.idle()

if __name__ == '__main__':
    main()
