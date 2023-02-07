import requests
import datetime
from datetime import datetime
API_LOCATION = 'http://localhost:80'

#POSSIBILI STATI DI UN UTENTE:
UNLOGGED = 0
NEED_USERNAME_REG = 1
NEED_PASSWORD_REG = 2
NEED_POSITION_REG = 3

NEED_USERNAME_LOG = 4
NEED_PASSWORD_LOG = 5

LOGGED = 6

def check_credentials(username, password):
    #Funzione di verifica credenziali in fase di login
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

def insert_new_user(username,lat, lon, password):
    #Insert tramite api di un nuovo utente
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
        response = requests.get(f'{API_LOCATION}/stats/{username}')
    except ConnectionError:
        return 'Connection Error: API probably offline, please retry later'
    try:
        dictionary = response.json()
    except requests.exceptions.JSONDecodeError:
        print(response.text)
        return 'Something went wrong!'
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

def get_status(username):
    try:
        response = requests.get(f'{API_LOCATION}/rack_user/{username}')
    except ConnectionError:
        return 'Connection Error: API probably offline, please retry later'
    try:
        dictionary = response.json()
    except requests.exceptions.JSONDecodeError:
        print(response.text)
        return 'Something went wrong!'
    dictionary = dictionary[0]
    if not any(dictionary):
        return "You don't have any sensor feed yet. Activate a new drying cycle to get some!"
    for i in dictionary.keys():
        dictionary[i] = dictionary[i] if not dictionary[i] is None else 0
    ret_string = "*Here is the current status of your drying rack:*\n"
    status = "-You have an ongoing drying cycle\n" if dictionary['is_active'] == 1 else "-Your drying cycle is finished.\n"
    rain = "-It is raining" if dictionary['is_raining'] < 300 else "-It is *not* raining \n"
    hum_and_t = f"-The temperature is: {dictionary['air_temperature']}, the air humidity is {dictionary['air_humidity']}% \n"
    cloth_hum = f"-The drying is {100 - dictionary['cloth_humidity']}% done" if dictionary['is_active'] == 1 else ""
    return f"{ret_string}{status}{rain}{hum_and_t}{cloth_hum}"

def get_best_time(username):
    try:
        response = requests.get(f'{API_LOCATION}/weather_feed/{username}')
    except ConnectionError:
        return 'Connection Error: API probably offline, please retry later'
    try:
        dictionary = response.json()
    except requests.exceptions.JSONDecodeError:
        print(response.text)
        return 'Something went wrong!'
    now = datetime.timestamp(datetime.now())
    best = now + dictionary['best_time'] * 3600
    best = datetime.fromtimestamp(best)
    return f"The best time to dry your clothes will be {dictionary['best_time']} hours from now, at {best}"

def get_imminent_rain(username):
    try:
        response = requests.get(f'{API_LOCATION}/weather_feed/{username}')
    except ConnectionError:
        return False
    try:
        dictionary = response.json()
    except requests.exceptions.JSONDecodeError:
        print(response.text)
        return 'Something went wrong!'
    return dictionary['rain']

def is_outside(username):
    return True

def set_position(username, pos):
    dictionary = {}
    dictionary['is_outside'] = pos
    dictionary['username'] = username
    try:
        response = requests.put(f'{API_LOCATION}/drying-rack/position', json = dictionary)
    except ConnectionError:
        return False
    if response.status_code != 200:
        print(response.text)
        return 'Something went wrong!'
    return 'Your rack is now set outside' if pos else 'Your rack is now set inside'

def get_actual_rain(username):
    try:
        response = requests.get(f'{API_LOCATION}/rack_user/{username}')
    except ConnectionError:
        return 'Connection Error: API probably offline, please retry later'
    try:
        dictionary = response.json()
    except requests.exceptions.JSONDecodeError:
        print(response.text)
        return 'Something went wrong!'
    dictionary = dictionary[0]
    if not any(dictionary):
        return "You don't have any sensor feed yet. Activate a new drying cycle to get some!"
    for i in dictionary.keys():
        dictionary[i] = dictionary[i] if not dictionary[i] is None else 0
    print(dictionary['sensor_time'])
    return dictionary['sensor_time'], True if dictionary['is_raining'] < 300 else False

def get_community(username):
    return True