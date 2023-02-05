import logging
from telegram import Update
from telegram.ext import ApplicationBuilder, ContextTypes, CommandHandler, MessageHandler, ContextTypes, filters
from telegram.ext import ContextTypes, Application
import utilities
from utilities import UNLOGGED, NEED_PASSWORD_LOG, NEED_PASSWORD_REG, NEED_POSITION_REG, NEED_USERNAME_LOG, NEED_USERNAME_REG, LOGGED, get_imminent_rain
BOTKEY = '6152911022:AAHcG-1rkKjBmuv_dZw7iXGrg8jGLbPempM'
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)


#Classe contenente i dati degli utenti
user_data = {}
class user:
    def __init__(self):
        self.username = None
        self.latitude = -1
        self.longitude = -1
        self.status = UNLOGGED
        self.notify = True
        self.notify_timer = 0
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    #Handler del comando /start
    await context.bot.send_message(chat_id=update.effective_chat.id, text="Hi! I am your smart drying rack! please /login or /register to the stendApp Community!")
    c_id = update.effective_chat.id
    if not c_id in user_data.keys():
        user_data[update.effective_chat.id] = user()

async def help(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await context.bot.send_message(chat_id=update.effective_chat.id, text="Hi! I am your smart drying rack! please /login or /register to the stendApp Community!" \
                                                                            "List of commands:\n/start - Start using StendAPP \n"\
                                                                            "/register - Create your new StendAPP account \n"\
                                                                            "/login - Log into your StendAPP account \n"\
                                                                            "/logout - Log out of your StendAPP account\n"\
                                                                            "/stats - See expected drying time\n"\
                                                                            "/mystats - See expected drying time based on your data\n"\
                                                                            "/current - See the current status of your drying rack")
async def register(update: Update, context: ContextTypes.DEFAULT_TYPE):
    #Handler del comando di /register
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
        user_data[c_id].status, response= utilities.insert_new_user(user_data[c_id].username, user_data[c_id].latitude, user_data[c_id].longitude, message)
        await context.bot.send_message(chat_id=update.effective_chat.id, text=response)       
    elif user_data[c_id].status == NEED_USERNAME_LOG:
        user_data[c_id].status = NEED_PASSWORD_LOG
        user_data[c_id].username = message
        await context.bot.send_message(chat_id=update.effective_chat.id, text=f'Hello, {message}! Now please insert your password!')
    elif user_data[c_id].status == NEED_PASSWORD_LOG:
        user_data[c_id].status, response = utilities.check_credentials(user_data[c_id].username, message)
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


async def position_manager(update: Update, context: ContextTypes.DEFAULT_TYPE):
    #Handler della ricezione di posizioni
    c_id = update.effective_chat.id
    if user_data[c_id].status == NEED_POSITION_REG:
        print(update.message.location)
        user_data[c_id].lat = update.message.location.latitude
        user_data[c_id].lon = update.message.location.longitude
        user_data[c_id].status = NEED_PASSWORD_REG
        await context.bot.send_message(chat_id=update.effective_chat.id, text="Thank you! Now please insert your password!")
    else:
        await context.bot.send_message(chat_id=update.effective_chat.id, text="We didn't need that position!")


async def stats(update: Update, context: ContextTypes.DEFAULT_TYPE):
    #Handler per il comando /stats
    c_id = update.effective_chat.id
    if not c_id in user_data.keys():
        user_data[c_id] = user()
    if user_data[c_id].status != LOGGED:
        await context.bot.send_message(chat_id=update.effective_chat.id, text="You need to login to use this command")
        return
    response = utilities.get_stats()
    await context.bot.send_message(chat_id=update.effective_chat.id, text=response)

async def stats_user(update: Update, context: ContextTypes.DEFAULT_TYPE):
    #Handler per il comando /mystats
    c_id = update.effective_chat.id
    if not c_id in user_data.keys():
        user_data[c_id] = user()
    if user_data[c_id].status != LOGGED:
        await context.bot.send_message(chat_id=update.effective_chat.id, text="You need to login to use this command")
        return
    response = utilities.get_stats(user_data[c_id].username)
    await context.bot.send_message(chat_id=update.effective_chat.id, text=response)

async def current_status(update: Update, context: ContextTypes.DEFAULT_TYPE):
    #Handler per il comando /mystats
    c_id = update.effective_chat.id
    if not c_id in user_data.keys():
        user_data[c_id] = user()
    if user_data[c_id].status != LOGGED:
        await context.bot.send_message(chat_id=update.effective_chat.id, text="You need to login to use this command")
        return
    response = utilities.get_status(user_data[c_id].username)
    await context.bot.send_message(chat_id=update.effective_chat.id, text=response)

async def best_time(update: Update, context: ContextTypes.DEFAULT_TYPE):
    #Handler per il comando /best_time
    c_id = update.effective_chat.id
    if not c_id in user_data.keys():
        user_data[c_id] = user()
    if user_data[c_id].status != LOGGED:
        await context.bot.send_message(chat_id=update.effective_chat.id, text="You need to login to use this command")
        return
    response = utilities.get_best_time(user_data[c_id].username)
    await context.bot.send_message(chat_id=update.effective_chat.id, text=response)

async def callback_minute(context: ContextTypes.DEFAULT_TYPE):
    #Handler di messaggi ricorrenti a tutti gli utenti registrati
    for i in user_data.keys():
        if user_data[i].status == LOGGED and user_data[i].notify is True:
            if user_data[i].notify_timer > 0:
                user_data[i].notify_timer -= 1
            if utilities.is_outside(user_data[i].username):
                if get_imminent_rain(user_data[i].username):
                    context.bot.send_message(chat_id=i, text="There is rain incoming in the next three hours!")
                    user_data[i].notify_timer=30

if __name__ == '__main__':
    application = ApplicationBuilder().token(BOTKEY).build()
    start_handler = CommandHandler('start', start)
    register_handler = CommandHandler('register', register)
    login_handler = CommandHandler('login', login)
    msg_handler = MessageHandler(filters.TEXT & (~filters.COMMAND), message_manager)
    pos_handler = MessageHandler(filters.LOCATION, position_manager)
    logout_handler = CommandHandler('logout', logout)
    stats_handler = CommandHandler('stats', stats)
    stats_user_handler = CommandHandler('mystats', stats_user)
    help_handler = CommandHandler('help', help)
    current_handler = CommandHandler('current', current_status)
    forecast_handler = CommandHandler('forecast', best_time)
    application.add_handlers((start_handler, register_handler,pos_handler, msg_handler, login_handler, logout_handler, stats_handler, help_handler, stats_user_handler, current_handler, forecast_handler))
    job_queue = application.job_queue
    job_minute = job_queue.run_repeating(callback_minute, interval=120, first=30)
    application.run_polling()
