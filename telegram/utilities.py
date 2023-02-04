import requests

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