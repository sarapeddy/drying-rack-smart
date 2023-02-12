import random
import requests
from configparser import ConfigParser
def is_going_to_rain(username, config):
    try:
        response = requests.get(f"http://{config.get('Api', 'host')}/weather_feed/{username}")
    except ConnectionError:
        print("Error connecting to api")
        return 0
    try:
        dictionary = response.json()
    except requests.exceptions.JSONDecodeError:
        print(response.text)
        return 'Something went wrong!'
    return 1 if dictionary['rain'] is True else 0

def get_community(username, config):
    try:
        response = requests.get(f"http://{config.get('Api', 'host')}/community/{username}")
    except ConnectionError:
        return 1
    response = response.text
    if 'Inside' in response:
        return 1
    elif 'Outside' in response:
        return 0
    print(response)
    return 1

def get_actual_rain(username, config):
    try:
        response = requests.get(f"http://{config.get('Api', 'host')}/rack_user/{username}")
    except ConnectionError:
        print( 'Connection Error: API probably offline, please retry later')
        return 0
    try:
        dictionary = response.json()
    except requests.exceptions.JSONDecodeError:
        print(response.text)
        return 0
    dictionary = dictionary[0]
    if not any(dictionary):
        return 0
    for i in dictionary.keys():
        dictionary[i] = dictionary[i] if not dictionary[i] is None else 0
    return 1 if dictionary['is_raining'] < 300 else 0

def get_percentage(username, config):
    try:
        response = requests.get(f"http://{config.get('Api', 'host')}/rack_user/{username}")
    except ConnectionError:
        print( 'Connection Error: API probably offline, please retry later')
        return 0
    try:
        dictionary = response.json()
    except requests.exceptions.JSONDecodeError:
        print(response.text)
        return 0
    dictionary = dictionary[0]
    if not any(dictionary):
        return 0
    for i in dictionary.keys():
        dictionary[i] = dictionary[i] if not dictionary[i] is None else 0
    cloth_hum = 100 - dictionary['cloth_humidity'] if dictionary['is_active'] == 1 else 100
    return cloth_hum