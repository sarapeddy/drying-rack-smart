import json
import mysql.connector
from flask import Flask, request, session, render_template, abort
from flask_restx import Api
from configparser import ConfigParser
from OpenWeather import OpenWeather
from Stats import Statistics
from Registration import Registration
from flasgger import Swagger, LazyString, LazyJSONEncoder, swag_from
import Queries

appname = "Smart Drying-rack"
app = Flask(appname)
app.json_encoder = LazyJSONEncoder

config = ConfigParser()
config.read('config.ini')
user = config.get('Database', 'user')
password = config.get('Database', 'password')
host = config.get('Database', 'host')
database = config.get('Database', 'database')
raise_on = bool(config.get('Database', 'raise_on_warnings'))
# print(user, password, host, database, raise_on, type(raise_on))

swagger_template = dict(
    info={
        'title': LazyString(lambda: 'Drying Rack Smart'),
        'version': LazyString(lambda: '1.0'),
        'description': LazyString(lambda: 'This is the documentations about Flask Drying Rack Smart project Apis'),
    },
    host=LazyString(lambda: request.host)
)
swagger_config = {
    "headers": [],
    "specs": [
        {
            "endpoint": 'drying-rack',
            "route": '/drying-rack.json',
            "rule_filter": lambda rule: True,
            "model_filter": lambda tag: True,
        }
    ],
    "static_url_path": "/flasgger_static",
    "swagger_ui": True,
    "specs_route": "/apidocs/"
}

swagger = Swagger(app, template=swagger_template, config=swagger_config)

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
    ---
    responses:
        200:
            description: Check if the connection to the mysql db is correct
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
    if s == 'True':
        create_new_user_json(data)
        return data['username'] + ' signed up'
    return data['username'] + ' ' + s


def check_json(data):
    print(data)
    myreg = Registration(cur)
    response1 = myreg.lat_lon_control(data['latitude'], data['longitude'])
    if response1 != 'True':
        return response1
    response2 = myreg.check_db(data['username'], data['password'])
    if response2 != 'True':
        return response2
    print(response1, response2)
    if response1 == response2:
        return 'True'
    return response1 + ' ' + response2


def create_new_user_json(request_data):
    query = f"insert into rack_user (`user_name`, pin, lat, lon) " \
            f"values ('{request_data['username']}', '{request_data['password']}', {request_data['latitude']}, " \
            f" {request_data['longitude']}) ;"
    cur.execute(query)
    cnx.commit()
    return str(cur.lastrowid)


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
    """
    ---
    responses:
        200:
            description: OK
        400:
            description: Client Error
        500:
            description: Internal Server Error
    """
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


@app.route('/<int:drying_cycle>/inactive')
def set_drying_cycle_inactive(drying_cycle):
    return str(Queries.update_status_drying_cycle(drying_cycle, cnx, cur))


@app.route('/stats/', defaults={'user': None})
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
        result = Queries.select_lat_lon(user, cur)
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

    result = Queries.select_last_sensor_feed(user, cur)

    r = [dict((cur.description[i][0], value) for i, value in enumerate(row)) for row in result]
    if 'application/json' in request.headers:
        return json.dumps(r, indent=4, separators=(',', ': '), default=str) if r else None
    else:
        return r if r else None


if __name__ == '__main__':
    host = '0.0.0.0'
    port = 80
    app.run(port=port, host=host, debug=True)