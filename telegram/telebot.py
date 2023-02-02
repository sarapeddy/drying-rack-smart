import logging
from telegram import Update
from telegram.ext import ApplicationBuilder, ContextTypes, CommandHandler, MessageHandler, ContextTypes, filters
import requests

BOTKEY = '6152911022:AAHcG-1rkKjBmuv_dZw7iXGrg8jGLbPempM'
API_LOCATION = 'http://localhost:80'
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)
UNLOGGED = 0
NEED_USERNAME_REG = 1
NEED_PASSWORD_REG = 2
NEED_POSITION_REG = 3

NEED_USERNAME_LOG = 4
NEED_PASSWORD_LOG = 5

LOGGED = 6

user_data = {}
class user:
    def __init__(self):
        self.username = None
        self.latitude = -1
        self.longitude = -1
        self.status = UNLOGGED

def check_username(username):
    return True
def check_credentials(username, password):
    dictionary = {}
    dictionary['username'] = username
    dictionary['password'] = password
    response = requests.post(f'{API_LOCATION}/credentials', json = dictionary)
    if 'Login' in response.text:
        return True
    else:
        return False

def insert_new_user(username,lat, lon, password):
    dictionary = {}
    dictionary['username'] = username
    dictionary['password'] = password
    dictionary['latitude'] = lat
    dictionary['longitude'] = lon
    response = requests.post(f'{API_LOCATION}/registration-bot', json = dictionary)
    print(response.text)
    test = 'signed up' in response.text
    return test

def parse_coordinates(text):
    coord = text.split(',')
    if len(coord) != 2:
        return -1, -1
    lat = float(coord[0])
    lon = float(coord[1])
    if not((lat >=0 and lat <=90) and(lon >=0 and lon<=90)):
        return -1, -1
    return lat, lon

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await context.bot.send_message(chat_id=update.effective_chat.id, text="Hi! I am your smart drying rack! please /login or /register to the stendApp Community!")
    user_data[update.effective_chat.id] = user()

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
        await context.bot.send_message(chat_id=update.effective_chat.id, text="Again, please insert your position!")
    elif user_data[c_id].status  == LOGGED:
        await context.bot.send_message(chat_id=update.effective_chat.id, text="You are alredy logged in, to log out type /logout")
    else:
        await context.bot.send_message(chat_id=update.effective_chat.id, text="You were logging, finish that procedure before trying something else!")
async def message_manager(update: Update, context: ContextTypes.DEFAULT_TYPE):
    c_id = update.effective_chat.id
    message = update.message.text
    if not c_id in user_data.keys():
        user_data[c_id] = user()
    if user_data[c_id].status == UNLOGGED:
        await context.bot.send_message(chat_id=update.effective_chat.id, text="Use /login or /register to join the stendAPP community")
    elif user_data[c_id].status == NEED_USERNAME_REG:
        if not check_username(message):
            await context.bot.send_message(chat_id=update.effective_chat.id, text="Sorry, username alredy taken, please retry!")
            return
        user_data[c_id].status = NEED_POSITION_REG
        user_data[c_id].username = message
        await context.bot.send_message(chat_id=update.effective_chat.id, text=f'Hello, {message}! Now please insert your position lat, lon')
    elif user_data[c_id].status == NEED_POSITION_REG:
        lat, lon = parse_coordinates(message)
        if lat == -1 or lon == -1: 
            await context.bot.send_message(chat_id=update.effective_chat.id, text=f'Sorry, {message}! you have inserted invalid coordinates, try again!')
            return
        user_data[c_id].latitude = lat
        user_data[c_id].longitude = lon
        user_data[c_id].status = NEED_PASSWORD_REG
        await context.bot.send_message(chat_id=update.effective_chat.id, text=f'Thank you, your position is {lat}, {lon}, now choose a password!')
    elif user_data[c_id].status == NEED_PASSWORD_REG:
        if insert_new_user(user_data[c_id].username, user_data[c_id].latitude, user_data[c_id].longitude, message) is True:
            user_data[c_id].status = LOGGED
            await context.bot.send_message(chat_id=update.effective_chat.id, text=f'Hello, {user_data[c_id].username}! You are now part of the StendAPP community!')
        else:
            await context.bot.send_message(chat_id=update.effective_chat.id, text='Sorry, something went wrong! try again /login or /register')
            user_data[c_id].status = UNLOGGED
    elif user_data[c_id].status == NEED_USERNAME_LOG:
        user_data[c_id].status = NEED_PASSWORD_LOG
        user_data[c_id].username = message
        await context.bot.send_message(chat_id=update.effective_chat.id, text=f'Hello, {message}! Now please insert your password!')
    elif user_data[c_id].status == NEED_PASSWORD_LOG:
        if check_credentials(user_data[c_id].username, message) is True:
            user_data[c_id].status = LOGGED
            await context.bot.send_message(chat_id=update.effective_chat.id, text=f'Hello, {user_data[c_id].username}! You are successfully logged in!')
        else:
            user_data[c_id].status = UNLOGGED
            await context.bot.send_message(chat_id=update.effective_chat.id, text=f'Sorry, Username or password incorrect, try again /login or /register')
            
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
if __name__ == '__main__':
    application = ApplicationBuilder().token(BOTKEY).build()
    
    start_handler = CommandHandler('start', start)
    register_handler = CommandHandler('register', register)
    login_handler = CommandHandler('login', login)
    msg_handler = MessageHandler(filters.TEXT & (~filters.COMMAND), message_manager)
    application.add_handler(start_handler)
    application.add_handler(register_handler)
    application.add_handler(msg_handler)
    application.add_handler(login_handler)
    application.run_polling()