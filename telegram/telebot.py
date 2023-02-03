import logging
from telegram import Update
from telegram.ext import ApplicationBuilder, ContextTypes, CommandHandler, MessageHandler, ContextTypes, filters
import requests
from telegram.ext import ContextTypes, Application

BOTKEY = '6152911022:AAHcG-1rkKjBmuv_dZw7iXGrg8jGLbPempM'
API_LOCATION = 'http://localhost:80'
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)

#POSSIBILI STATI DI UN UTENTE:
UNLOGGED = 0
NEED_USERNAME_REG = 1
NEED_PASSWORD_REG = 2
NEED_POSITION_REG = 3

NEED_USERNAME_LOG = 4
NEED_PASSWORD_LOG = 5

LOGGED = 6

#Classe contenente i dati degli utenti
user_data = {}
class user:
    def __init__(self):
        self.username = None
        self.latitude = -1
        self.longitude = -1
        self.status = UNLOGGED

#Funzione di verifica credenziali in fase di login
def check_credentials(username, password):
    dictionary = {}
    dictionary['username'] = username
    dictionary['password'] = password
    try:
        response = requests.post(f'{API_LOCATION}/credentials', json = dictionary)
    except ConnectionError:
        return UNLOGGED, 'Connection Error: api probably offline, please retry later!'
    if 'Login' in response.text:
        return LOGGED, f'Welcome {username}, you successfully logged in!'
    else:
        return UNLOGGED, 'Username and or password incorrect, /login to try again or /register if you don\'t have an account!'

#Insert tramite api di un nuovo utente
def insert_new_user(username,lat, lon, password):
    dictionary = {}
    dictionary['username'] = username
    dictionary['password'] = password
    dictionary['latitude'] = lat
    dictionary['longitude'] = lon
    try:
        response = requests.post(f'{API_LOCATION}/registration-bot', json = dictionary)
    except ConnectionError:
        return UNLOGGED, 'Connection Error: API probably offline, please retry later!'
    print(response.text)
    if 'signed up' in response.text:
        return LOGGED, f'Welcome {username}! You are now part of the stendAPP community'
    if 'password' in response.text:
        return NEED_PASSWORD_REG, 'Sorry, the password was not suitable: try again (at least 8 characters)'
    if 'Username' in response.text:
        return UNLOGGED, 'The username was alredy taken, /login if that is you, or /register to try a new one'

def get_stats(username = ''):
    try:
        response = requests.get(f'{API_LOCATION}/stats/')
    except ConnectionError:
        return 'Connection Error: API probably offline, please retry later'
    dictionary = response.json()
    global_avg = round(dictionary['mean_cycle_time'] /60 /60, 2)
    normalized_global_avg = round(dictionary['normalized_cycle_time'] /60 /60, 2)
    normalized_avg15 = round(dictionary['normalized_cycle_time_temp'][0] /60 /60, 2)
    normalized_avg20 = round(dictionary['normalized_cycle_time_temp'][1] /60 /60, 2)
    normalized_avg25 = round(dictionary['normalized_cycle_time_temp'][2] /60/60, 2)
    return f"Here are the global drying time expectations:\n" \
            f"-Expected drying time (not normalized): {global_avg} hours\n" \
            f"-Expected drying time (normalized): {normalized_global_avg} hours\n"\
            f"-Expected drying time during the winter: {normalized_avg15} hours\n"\
            f"-Expected drying time indoor: {normalized_avg20} hours \n"\
            f"-Expected drying time during the summer: {normalized_avg25} hours\n"
#Handler del comando /start
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    #Comando iniziale, inizializza il proprio chat.id
    await context.bot.send_message(chat_id=update.effective_chat.id, text="Hi! I am your smart drying rack! please /login or /register to the stendApp Community!")
    user_data[update.effective_chat.id] = user()
    print('ciao')

#Handler del comando di /register
async def register(update: Update, context: ContextTypes.DEFAULT_TYPE):
    #Inizia il processo di registrazione
    c_id = update.effective_chat.id
    if not c_id in user_data.keys():
        user_data[update.effective_chat.id] = user()
    if user_data[c_id].status  == UNLOGGED:
        user_data[c_id].status = NEED_USERNAME_REG
        await context.bot.send_message(chat_id=update.effective_chat.id, text="Please insert your username!")
    elif user_data[c_id].status  == NEED_USERNAME_REG:
        await context.bot.send_message(chat_id=update.effective_chat.id, text="Again, please insert your username!")
    elif user_data[c_id].status  == NEED_PASSWORD_REG:
        await context.bot.send_message(chat_id=update.effective_chat.id, text="Again, please insert your password!")
    elif user_data[c_id].status  == NEED_POSITION_REG:
        await context.bot.send_message(chat_id=update.effective_chat.id, text="Again, please send your position!")
    elif user_data[c_id].status  == LOGGED:
        await context.bot.send_message(chat_id=update.effective_chat.id, text="You are alredy logged in, to log out type /logout")
    else:
        await context.bot.send_message(chat_id=update.effective_chat.id, text="You were logging, finish that procedure before trying something else!")

#Gestore dei messaggi: (tutto ciò che non è comando)
async def message_manager(update: Update, context: ContextTypes.DEFAULT_TYPE):
    c_id = update.effective_chat.id
    message = update.message.text
    if not c_id in user_data.keys():
        user_data[c_id] = user()
    if user_data[c_id].status == UNLOGGED:
        await context.bot.send_message(chat_id=update.effective_chat.id, text="Use /login or /register to join the stendAPP community")
    elif user_data[c_id].status == NEED_USERNAME_REG:
        user_data[c_id].status = NEED_POSITION_REG
        user_data[c_id].username = message
        await context.bot.send_message(chat_id=update.effective_chat.id, text=f'Hello, {message}! Now please send your position!')
    elif user_data[c_id].status == NEED_POSITION_REG:
        await context.bot.send_message(chat_id=update.effective_chat.id, text=f'Again, please send your position!')
    elif user_data[c_id].status == NEED_PASSWORD_REG:
        user_data[c_id].status, response= insert_new_user(user_data[c_id].username, user_data[c_id].latitude, user_data[c_id].longitude, message)
        await context.bot.send_message(chat_id=update.effective_chat.id, text=response)       
    elif user_data[c_id].status == NEED_USERNAME_LOG:
        user_data[c_id].status = NEED_PASSWORD_LOG
        user_data[c_id].username = message
        await context.bot.send_message(chat_id=update.effective_chat.id, text=f'Hello, {message}! Now please insert your password!')
    elif user_data[c_id].status == NEED_PASSWORD_LOG:
        user_data[c_id].status, response = check_credentials(user_data[c_id].username, message)
        await context.bot.send_message(chat_id=update.effective_chat.id, text=response)

#Handler del comando login       
async def login(update: Update, context: ContextTypes.DEFAULT_TYPE):
    c_id = update.effective_chat.id
    if not c_id in user_data.keys():
        user_data[c_id] = user()
    if user_data[c_id].status  == UNLOGGED:
        user_data[c_id].status = NEED_USERNAME_LOG
        await context.bot.send_message(chat_id=update.effective_chat.id, text="Please insert your username!")
    elif user_data[c_id].status  == NEED_USERNAME_LOG:
        await context.bot.send_message(chat_id=update.effective_chat.id, text="Again, please insert your username!")
    elif user_data[c_id].status  == NEED_PASSWORD_LOG:
        await context.bot.send_message(chat_id=update.effective_chat.id, text="Again, please insert your password!")
    elif user_data[c_id].status  == LOGGED:
        await context.bot.send_message(chat_id=update.effective_chat.id, text="You are alredy logged in, to log out type /logout")
    else:
        await context.bot.send_message(chat_id=update.effective_chat.id, text="You were registering, finish that procedure before trying something else!")

#Handler del comando /logout
async def logout(update: Update, context: ContextTypes.DEFAULT_TYPE):
    c_id = update.effective_chat.id
    if not c_id in user_data.keys():
        user_data[c_id] = user()
    if user_data[c_id].status != LOGGED:
        await context.bot.send_message(chat_id=update.effective_chat.id, text="You don't need to log out, you are not even logged in!")
    else:
        user_data[c_id].status = UNLOGGED
        await context.bot.send_message(chat_id=update.effective_chat.id, text="You are now logged out, use /login or /register")

#Handler della ricezione di posizioni
async def position_manager(update: Update, context: ContextTypes.DEFAULT_TYPE):
    c_id = update.effective_chat.id
    if user_data[c_id].status == NEED_POSITION_REG:
        print(update.message.location)
        user_data[c_id].lat = update.message.location.latitude
        user_data[c_id].lon = update.message.location.longitude
        user_data[c_id].status = NEED_PASSWORD_REG
        await context.bot.send_message(chat_id=update.effective_chat.id, text="Thank you! Now please insert your password!")
    else:
        await context.bot.send_message(chat_id=update.effective_chat.id, text="We didn't need that position!")

#Handler per il comando /stats
async def stats(update: Update, context: ContextTypes.DEFAULT_TYPE):
    c_id = update.effective_chat.id
    if not c_id in user_data.keys():
        user_data[c_id] = user()
    if user_data[c_id].status != LOGGED:
        await context.bot.send_message(chat_id=update.effective_chat.id, text="You need to login to use this command")
        return
    response = get_stats()
    await context.bot.send_message(chat_id=update.effective_chat.id, text=response)

#Handler di messaggi ricorrenti a tutti gli utenti registrati
async def callback_minute(context: ContextTypes.DEFAULT_TYPE):
    for i in user_data.keys():
        if user_data[i].status == LOGGED:
            await context.bot.send_message(chat_id=i, text='Hello!')

if __name__ == '__main__':
    application = ApplicationBuilder().token(BOTKEY).build()
    start_handler = CommandHandler('start', start)
    register_handler = CommandHandler('register', register)
    login_handler = CommandHandler('login', login)
    msg_handler = MessageHandler(filters.TEXT & (~filters.COMMAND), message_manager)
    pos_handler = MessageHandler(filters.LOCATION, position_manager)
    logout_handler = CommandHandler('logout', logout)
    stats_handler = CommandHandler('stats', stats)
    application.add_handlers((start_handler, register_handler,pos_handler, msg_handler, login_handler, logout_handler, stats_handler))
    job_queue = application.job_queue
    job_minute = job_queue.run_repeating(callback_minute, interval=120, first=30)
    application.run_polling()
