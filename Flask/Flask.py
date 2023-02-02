import json
import mysql.connector
from flask import Flask, request, session, render_template, abort
from flask_restx import Api, Resource
from configparser import ConfigParser
from OpenWeather import OpenWeather
from Stats import Statistics
from Registration import Registration

appname = "Smart Drying-rack"
app = Flask(appname)

config = ConfigParser()
config.read('config.ini')
user = config.get('Database', 'user')
password = config.get('Database', 'password')
host = config.get('Database', 'host')
database = config.get('Database', 'database')
raise_on = bool(config.get('Database', 'raise_on_warnings'))
#print(user, password, host, database, raise_on, type(raise_on))

try:
    cnx = mysql.connector.connect(user=user, password=password, host=host, db=database)
    cur = cnx.cursor()
except Exception as e:
    print(e)

key_weather = config.get('Weather', 'key')

api = Api(app)


@app.route('/')
def hello():
    """
    Home path
    :return: Title
    """
    testdb()
    return '<h1>Smart Drying-Rack<h1>'


def testdb():
    try:
        cur.execute('select * from rack_user')
        result = cur.fetchall()
        print(result)
        return '<h1>Smart Drying-Rack<h1>'
    except Exception as e:
        cnx.close()
        cur.close()
        print("\nThe error:\n" + str(e) + "\n")
        return '<h1>Something is broken.</h1>'


@app.route('/', methods=['PUT'])
def query_records():
    record = json.loads(request.data)
    return record


@app.route('/test')
def hello_name():
    name = request.args.get('name')
    if name is None:
        name = request.cookies.get('name', 'Human')
    response = '<h1>Hello, %s!</h1>' % name
    # return different response according to the user's authentication status
    if 'logged_in' in session:
        response += '[Authenticated]'
    else:
        response += '[Not Authenticated]'
    return response


@app.route('/registration-bot', methods=['POST'])
def add_user():
    data = request.get_json()
    s = check_json(data)
    return s


def check_json(data):
    return data


@app.route('/registration/', methods=['GET', 'POST'])
def add_user_view():
    if request.method == 'POST':
        data = receive_registration_form()
        s = check(data)

        if s:
            create_new_user(data)
            return render_template('afterRegistration.html')
        return render_template('fail.html')
    return render_template('add.html')


def check(data):
    longitude = str(data[3])
    latitude = str(data[2])
    password_utente = str(data[1])
    rack_user = str(data[0])

    print(rack_user, password_utente, latitude, longitude)

    # check credentials with db
    myreg = Registration(cur)
    response1 = myreg.lat_lon_control(latitude, longitude)
    response2 = myreg.check_db(rack_user, password_utente)
    print(response1, response2)
    if response1 == response2:
        return True
    return False


def create_new_user(data):
    query = f"insert into rack_user (`user_name`, pin, lat, lon) " \
            f"values ('{data[0]}', '{data[1]}', {data[2]}, {data[3]}) ;"
    cur.execute(query)
    cnx.commit()
    return str(cur.lastrowid)


def receive_registration_form():
    temp = []
    temp.append(request.form.get("inputName"))
    temp.append(request.form.get("inputPassword"))
    temp.append(request.form.get("lat"))
    temp.append(request.form.get("lon"))
    return temp


@app.route('/credentials', methods=['POST'])
def check_credentials():
    try:
        result = check_rack_user(request.get_json())
        if result:
            return "Login"
    except KeyError:
        return "Uncorrect json format"
    return "Uncorrect username or/and password"


def check_rack_user(user):
    query = f"select user_name, pin from rack_user " \
            f"where pin='{user['password']}' and user_name='{user['username']}';"
    cur.execute(query)
    result = cur.fetchall()
    return result


@app.route('/drying-cycle', methods=['POST'])
def create_new_drying_clycle():
    request_data = request.get_json()
    query = f"insert into drying_cycle (`user_name`) " \
            f"values ('{request_data['user']}');"
    cur.execute(query)
    cnx.commit()
    return str(cur.lastrowid)


@app.route('/sensors/data', methods=['POST'])
def receive_sensor_feed():
    request_data = request.get_json()
    query = f"insert into sensor_feed(`air_temperature`, `is_raining`, `cloth_weight`, `cycle_id`, " \
            f"`cloth_humidity`, `air_humidity`) " \
            f"values({request_data['air_temperature']}, " \
            f"{request_data['is_raining']}, {request_data['cloth_weight']}, " \
            f"{request_data['cycle_id']}, {request_data['cloth_humidity']}, " \
            f"{request_data['air_humidity']});"

    cur.execute(query)
    cnx.commit()
    return str(cur.lastrowid)


@app.route('/stats/', defaults={'user':None})
@app.route('/stats/<string:user>')
def show_stats(user=None):
    mystats = Statistics(cur)
    mean_cycle_time = 0
    normalized_cycle_time = 0
    normalized_cycle_time_temp = 0
    if user is None:
        mean_cycle_time = mystats.get_mean_cycle_time_user()
        normalized_cycle_time = mystats.get_normalized_mean_cycle_time()
        normalized_cycle_time_temp = mystats.get_normalized_cycle_time_per_temp()
        return dict(mean_cycle_time=mean_cycle_time, normalized_cycle_time=normalized_cycle_time,
                    normalized_cycle_time_temp=normalized_cycle_time_temp)
    else:
        mean_cycle_time = mystats.get_mean_cycle_time_user(user)
        normalized_cycle_time = mystats.get_normalized_mean_cycle_time(user)
        normalized_cycle_time_temp = mystats.get_normalized_cycle_time_per_temp(user)
    return dict(mean_cycle_time=mean_cycle_time, normalized_cycle_time=normalized_cycle_time,
                normalized_cycle_time_temp=normalized_cycle_time_temp)


@app.route('/weather_feed/<string:user>', methods=['GET', 'POST'])
def show_weather_info(user):
    if request.method == 'POST':
        return abort(405)
    else:
        myweather = OpenWeather(key_weather)
        result = select_lat_lon(user)
        lat = result[0][0]
        lon = result[0][1]
        temp = myweather.get_temperature(lat, lon)
        rain = myweather.is_going_to_rain_in_3h(lat, lon)
        hum = myweather.get_humidity(lat, lon)
        mydict = dict(temp=temp, rain=rain, hum=hum)
        return json.dumps(mydict, indent=4)


@app.route('/rack_user/<string:user>')
def display(user):
    if user is None:
        return abort(404)

    result = select_last_sensor_feed(user)

    r = [dict((cur.description[i][0], value) for i, value in enumerate(row)) for row in result]
    if 'application/json' in request.headers:
        return json.dumps(r, indent=4, separators=(',', ': '), default=str) if r else None
    else:
        return r if r else None


def select_lat_lon(user):
    # seleziona latitudine e longitudine
    query = f"select lat, lon " \
            f"from rack_user " \
            f"where user_name like " \
            f"'{user}' ;"
    cur.execute(query)
    result = cur.fetchall()
    return result


def select_sensor_feed(user):
    # seleziona tutti i sensor feed dell'ultimo ciclo asciugatura di un utente
    query = f"select * from sensor_feed join drying_cycle on(sensor_feed.cycle_id = drying_cycle.id) " \
            f"where drying_cycle.id >= all( select drying_cycle.id from drying_cycle join rack_user " \
            f"on (drying_cycle.user_name = rack_user.user_name) " \
            f"where rack_user.user_name like '{user}');"
    cur.execute(query)
    result = cur.fetchall()
    return result


def select_last_sensor_feed(user):
    # seleziona l'ultimo sensor feed dell'ultimo ciclo asciugatura dato un utente
    query = f"select * from sensor_feed join drying_cycle on(sensor_feed.cycle_id = drying_cycle.id) " \
            f"where drying_cycle.id >= all(select drying_cycle.id from drying_cycle join rack_user " \
            f"on(drying_cycle.user_name = rack_user.user_name) " \
            f"where rack_user.user_name like '{user}') and sensor_feed.id >= all(select sensor_feed.id " \
            f"from sensor_feed join drying_cycle on(sensor_feed.cycle_id = drying_cycle.id)) ;"

    cur.execute(query)
    result = cur.fetchall()
    return result


def select_last_weather_feed(user):
    # seleziona l'ultimo weather_feed dato un utente
    query = f"select * from weather_feed join rack_user " \
            f"on( weather_feed.user_name like rack_user.user_name) " \
            f"where weather_feed.id >= all(select weather_feed.user_name from weather_feed join rack_user " \
            f"on( weather_feed.user_name = rack_user.user_name) " \
            f" where rack_user.user_name like '{user}') ;"
    cur.execute(query)
    result = cur.fetchall()
    return result


def select_all_cycles(user):
    # seleziona tutti i cicli conclusi di un utente (utile per fare medie e statistiche)
    query = f"select * from drying_cycle " \
            f"where drying_cycle.user_name like '{user}' " \
            f"and drying_cycle.is_active is false ;"
    cur.execute(query)
    result = cur.fetchall()
    return result


def select_closing_time_drying_cycle(user):
    # seleziona il momento di chiusura dell'ultimo ciclo di asciugatura concluso di un dato utente
    query = f"select * from sensor_feed s join drying_cycle d " \
            f"on (s.cycle_id = d.id) " \
            f"where d.user_name like '{user}' " \
            f"and d.is_active is false " \
            f"and d.id >=all	(select d1.id from drying_cycle d1 " \
            f"where d1.user_name like d.user_name " \
            f"and d1.is_active is false) " \
            f"and s.id >=all	(select s1.id from sensor_feed s1 " \
            f"where s1.cycle_id = d.id) ;"
    cur.execute(query)
    result = cur.fetchall()
    return result


def select_start_finish_time(user):
    # seleziona start_time e finish_time di tutti i cicli asciugatura di un utente
    query = f"select d.start_time, s.sensor_time as finish_time " \
            f"from drying_cycle d join sensor_feed s on (d.id = s.cycle_id) " \
            f"where d.user_name like '{user}' " \
            f"and is_active is false " \
            f"and s.id >= all(select s1.id from sensor_feed s1 " \
            f"where s1.cycle_id = s.cycle_id) ;"
    cur.execute(query)
    result = cur.fetchall()
    return result


def select_state(user):
    # seleziona lo stato (dentro o fuori) degli stendini degli utenti vicini ad un certo utente(<10km)
    query = f"select r.* from rack_user r join rack_user r1 " \
            f"where r1.user_name like '{user}' " \
            f"and r.user_name not like '{user}' " \
            f"and r.is_active is true " \
            f"and abs(r.lat-r1.lat)<=0.0753 " \
            f"and abs(r.lon-r1.lon)<=0.0753 " \
            f";"
    cur.execute(query)
    result = cur.fetchall()
    return result


if __name__ == '__main__':
    host = '0.0.0.0'
    port = 80
    app.run(port=port, host=host, debug=True)
