import logging
from telegram import Update
from telegram.ext import ApplicationBuilder, ContextTypes, CommandHandler, MessageHandler, ContextTypes, filters
from telegram.ext import ContextTypes, Application
import utilities
from utilities import UNLOGGED, NEED_PASSWORD_LOG, NEED_PASSWORD_REG, NEED_POSITION_REG, NEED_USERNAME_LOG, NEED_USERNAME_REG, LOGGED, CONFIRM_DELETION, CONFIRM_DELETION_CYCLE, NEED_PASSWORD_CHG
BOTKEY = utilities.bot_key_config()
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
        self.last_feed = None
        self.notify_timer_weather = 0
        self.notify_timer_rain = 0
        self.notify_timer_com = 0
        self.cycle_id = -1
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
                                                                            "/current - See the current status of your drying rack\n"\
                                                                            "/forecast - See the best time to dry your clothes\n"\
                                                                            "/notify ON or OFF - turn on or off notifications\n"\
                                                                            "/position IN or OUT - set your drying rack inside or outside\n"\
                                                                            "/delete_user - to delete your account\n"\
                                                                            "/delete_cycle - to delete your last drying cycle\n"\
                                                                            "/ranking - to see who is the best dryier!" \
                                                                            "/editpass - change your password")
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
    elif user_data[c_id].status == CONFIRM_DELETION:
        user_data[c_id].status, response = utilities.delete_rack(user_data[c_id].username, message)
        await context.bot.send_message(chat_id=update.effective_chat.id, text=response)
    elif user_data[c_id].status == CONFIRM_DELETION_CYCLE:
        user_data[c_id].status, response = utilities.delete_cycle(user_data[c_id].username, message)
        await context.bot.send_message(chat_id=update.effective_chat.id, text=response)
    elif user_data[c_id].status == NEED_PASSWORD_CHG:
        user_data[c_id].status, response = utilities.edit_credentials(user_data[c_id].username, message)
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
    elif (user_data[c_id].status  == LOGGED or user_data[c_id].status  == CONFIRM_DELETION) or user_data[c_id].status  == CONFIRM_DELETION_CYCLE:
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
        user_data[c_id].latitude = update.message.location.latitude
        user_data[c_id].longitude = update.message.location.longitude
        user_data[c_id].status = NEED_PASSWORD_REG
        print(user_data[c_id].latitude)
        print(user_data[c_id].longitude)
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
            if user_data[i].notify_timer_weather > 0:
                user_data[i].notify_timer_weather -= 1
            if user_data[i].notify_timer_rain > 0:
                user_data[i].notify_timer_rain -= 1
            if user_data[i].notify_timer_com > 0:
                user_data[i].notify_timer_com -= 1
            if utilities.is_outside(user_data[i].username):              
                if user_data[i].notify_timer_weather == 0:
                    if utilities.get_imminent_rain(user_data[i].username):
                        user_data[i].notify_timer_weather = 5
                        await context.bot.send_message(chat_id=i, text="There is rain incoming in the next three hours!")
                if user_data[i].notify_timer_rain == 0:
                    last_time, rain = utilities.get_actual_rain(user_data[i].username)  
                    print(rain)
                    print(user_data[i].last_feed)
                    if rain and last_time != user_data[i].last_feed:
                        user_data[i].notify_timer_rain = 5
                        await context.bot.send_message(chat_id=i, text="It is raining! Consider taking your rack indoors!")                
                if user_data[i].notify_timer_com == 0:
                    if utilities.get_community(user_data[i].username):
                        user_data[i].notify_timer_com = 5
                        await context.bot.send_message(chat_id=i, text="Some rack users near you has taken his rack inside, maybe you should too!")
            cycle, over = utilities.is_over(user_data[i].username)   
            if user_data[i].cycle_id != cycle and over:
                user_data[i].cycle_id = cycle
                await context.bot.send_message(chat_id=i, text="Good News! Your clothes are dry enough!")


async def set_notify(update: Update, context: ContextTypes.DEFAULT_TYPE):
    #Handler for the /notify command
    c_id = update.effective_chat.id
    if not c_id in user_data.keys():
        user_data[c_id] = user()
    if user_data[c_id].status != LOGGED:
        await context.bot.send_message(chat_id=update.effective_chat.id, text="You need to login to use this command")
        return
    operation = context.args
    if len(operation) != 1:
        await context.bot.send_message(chat_id=update.effective_chat.id, text="Your notifications are ON") if user_data[c_id].notify is True else context.bot.send_message(chat_id=update.effective_chat.id, text="Your notifications are OFF")
        return
    operation = operation[0]
    if 'on' in operation.lower():
        user_data[c_id].notify = True
        await context.bot.send_message(chat_id=update.effective_chat.id, text="Notifications are now ON")
    elif 'off' in operation.lower():
        user_data[c_id].notify = False
        await context.bot.send_message(chat_id=update.effective_chat.id, text="Notifications are now OFF")
    else:
        await context.bot.send_message(chat_id=update.effective_chat.id, text="Your notifications are ON") if user_data[c_id].notify is True else context.bot.send_message(chat_id=update.effective_chat.id, text="Your notifications are OFF")
    
async def set_position(update: Update, context: ContextTypes.DEFAULT_TYPE):
    #Handler for the /position command
    c_id = update.effective_chat.id
    if not c_id in user_data.keys():
        user_data[c_id] = user()
    if user_data[c_id].status != LOGGED:
        await context.bot.send_message(chat_id=update.effective_chat.id, text="You need to login to use this command")
        return
    operation = context.args
    if len(operation) != 1:
        out = utilities.is_outside(user_data[c_id].username)
        if out:
            await context.bot.send_message(chat_id=update.effective_chat.id, text="Your rack is currently OUTSIDE!")
        else:
            await context.bot.send_message(chat_id=update.effective_chat.id, text="Your rack is currently INSIDE!")
        return
    operation = operation[0]
    if 'in' in operation.lower():
        message = utilities.set_position(user_data[c_id].username, False)
    elif 'out' in operation.lower():
        message = utilities.set_position(user_data[c_id].username, True)
    else:
        await context.bot.send_message(chat_id=update.effective_chat.id, text="Invalid argument: Either IN or OUT")
        return
    await context.bot.send_message(chat_id=update.effective_chat.id, text=message)

async def delete_user(update: Update, context: ContextTypes.DEFAULT_TYPE):
    #Handler for the /delete command
    c_id = update.effective_chat.id
    if not c_id in user_data.keys():
        user_data[c_id] = user()
    if user_data[c_id].status != LOGGED and user_data[c_id] != CONFIRM_DELETION:
        await context.bot.send_message(chat_id=update.effective_chat.id, text="You need to login to use this command")
        return
    else:
        user_data[c_id].status = CONFIRM_DELETION
        await context.bot.send_message(chat_id=update.effective_chat.id, text="Are you SURE? All your data will be deleted! [YES, no]")

async def delete_cycle(update: Update, context: ContextTypes.DEFAULT_TYPE):
    #Handler for the /delete_cycle command
    c_id = update.effective_chat.id
    if not c_id in user_data.keys():
        user_data[c_id] = user()
    if user_data[c_id].status != LOGGED and user_data[c_id] != CONFIRM_DELETION_CYCLE:
        await context.bot.send_message(chat_id=update.effective_chat.id, text="You need to login to use this command")
    else:
        user_data[c_id].status = CONFIRM_DELETION_CYCLE
        await context.bot.send_message(chat_id=update.effective_chat.id, text="Are you SURE? Your last drying cycle will be deleted! [YES, no]")

async def ranking(update: Update, context: ContextTypes.DEFAULT_TYPE):
    c_id = update.effective_chat.id
    if not c_id in user_data.keys():
        user_data[c_id] = user()
    if user_data[c_id].status != LOGGED:
        await context.bot.send_message(chat_id=update.effective_chat.id, text="You need to login to use this command")
        return
    response = utilities.get_rankings(user_data[c_id].username)
    await context.bot.send_message(chat_id=update.effective_chat.id, text=response)

async def update_password(update: Update, context: ContextTypes.DEFAULT_TYPE):
    c_id = update.effective_chat.id
    if not c_id in user_data.keys():
        user_data[c_id] = user()
    if user_data[c_id].status != LOGGED and user_data[c_id] != NEED_PASSWORD_CHG:
        await context.bot.send_message(chat_id=update.effective_chat.id, text="You need to login to use this command")
        return
    else:
        user_data[c_id].status = NEED_PASSWORD_CHG
        await context.bot.send_message(chat_id=update.effective_chat.id, text="Please insert your old password, then your new one: [old new]")

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
    set_notify_handler = CommandHandler('notify', set_notify)
    set_position_handler = CommandHandler('position', set_position)
    delete_user_handler = CommandHandler('delete_user', delete_user)
    delete_cycle_handler = CommandHandler('delete_cycle', delete_cycle)
    ranking_handler = CommandHandler('ranking', ranking)
    edit_handler = CommandHandler('editpass', update_password)
    application.add_handlers((start_handler, register_handler,pos_handler, msg_handler, login_handler, logout_handler, stats_handler, help_handler, stats_user_handler, current_handler, forecast_handler, set_notify_handler, set_position_handler, delete_user_handler, delete_cycle_handler, ranking_handler, edit_handler))
    job_queue = application.job_queue
    job_minute = job_queue.run_repeating(callback_minute, interval=120, first=30)
    application.run_polling()
