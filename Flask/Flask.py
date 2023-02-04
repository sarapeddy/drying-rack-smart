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
    """
    ---
    summary: User registration with Telegram Bot
    description: User registration made by Telegram Bot
    parameters:
      - name: User
        in: body
        required: true
        schema:
            type: object
            properties:
                username:
                    type: string
                    example: mariorossi
                password:
                    type: string
                    example: 12345678
                latitude:
                    type: string
                    example: numeri da vedere
                longitude:
                    type: string
                    example: numeri da vedere
    responses:
        200:
            description: OK
            schema:
                type: string
                example: mariorossi signed up
        400:
            description: Client Error
        500:
            description: Internal Server Error
    """
    data = request.get_json()
    s = check_json(data)
    if s == 'True':
        Queries.create_new_user_json(data, cur, cnx)
        return data['username'] + ' signed up'
    return data['username'] + ' ' + s


def check_json(data):
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


@app.route('/registration/', methods=['GET', 'POST'])
def add_user_view():
    """
    ---
    summary: User registration
    description: User registration made by web page
    parameters:
      - name: UserWeb
        in: body
        required: true
        schema:
            type: object
            properties:
                inputName:
                    type: string
                    example: mariorossi
                inputPassword:
                    type: string
                    example: 12345678
                lat:
                    type: int64
                    example: 42.6
                lon:
                    type: int64
                    example: 10.8
    responses:
        200:
            description: OK
        400:
            description: Client Error
        500:
            description: Internal Server Error
    """
    if request.method == 'POST':
        data = dict(request.form)
        s = check(data)

        if s:
            Queries.create_new_user_json(data, cur, cnx)
            return render_template('afterRegistration.html')
        return render_template('fail.html')
    return render_template('add.html')


def check(data):
    # check credentials with db
    myreg = Registration(cur)
    response1 = myreg.lat_lon_control(data["latitude"], data["longitude"])
    response2 = myreg.check_db(data["username"], data["password"])
    if response1 == response2:
        return True
    return False


@app.route('/credentials', methods=['POST'])
def check_credentials():
    """
    ---
    summary: Check if an user exists
    description: Check if an user exists. It is an API called by the bridge to log in the Smart Drying Rack
    parameters:
      - name: UserCheck
        in: body
        required: true
        schema:
            type: object
            properties:
                password:
                    type: string
                    example: 12345678
                username:
                    type: string
                    example: mariorossi
    responses:
        200:
            description: OK
        400:
            description: Client Error
        500:
            description: Internal Server Error
    """
    try:
        result = Queries.check_rack_user(request.get_json(), cur)
        if result:
            return "Login"
    except KeyError:
        return "Uncorrect json format"
    return "Uncorrect username or/and password"


@app.route('/drying-cycle', methods=['POST'])
def create_new_drying_clycle():
    """
    ---
    summary: Create a new Drying Cycle
    description: Create a new Drying Cycle. It's called when on the Arduino is tapped the button and the RGB led is green
    parameters:
      - name: NewDryingCycle
        in: body
        required: true
        schema:
            type: object
            properties:
                user:
                    type: string
                    example: mariorossi
    responses:
        200:
            description: OK
        400:
            description: Client Error
        500:
            description: Internal Server Error
    """
    return Queries.create_new_drying_cycle(request.get_json(), cur, cnx)


@app.route('/sensors/data', methods=['POST'])
def receive_sensor_feed():
    """
    ---
    summary: Create a new sensor feed
    description: Create a new sensor feed. It is called by the bridge to send the sensor feeds.
    parameters:
      - name: NewDryingCycle
        in: body
        required: true
        schema:
            type: object
            properties:
                air_humidity:
                    type: float
                    example: 30.00
                air_temperature:
                    type: float
                    example: 19.00
                cloth_humidity:
                    type: int64
                    example: 300
                cloth_weight:
                    type: int64
                    example: 600
                is_raining:
                    type: bool
                    example: false
                cycle_id:
                    type: int64
                    example: 57
    responses:
        200:
            description: OK
        400:
            description: Client Error
        500:
            description: Internal Server Error
    """
    return Queries.create_new_sensor_feed(request.get_json(), cur, cnx)


@app.route('/<int:drying_cycle>/inactive')
def set_drying_cycle_inactive(drying_cycle):
    """
    ---
    summary: Set inactive a Drying Cycle
    description: Set inactive a Drying Cycle. It is called by the bridge if the Arduino button is pressed and the RGB led is red.
    parameters:
      - name: DryingCycle
        description: It is the Drying Cycle ID
        in: path
        required: true
        schema:
            type: int
            example: 57
    responses:
        200:
            description: OK
        400:
            description: Client Error
        500:
            description: Internal Server Error
    """
    return str(Queries.update_status_drying_cycle(drying_cycle, cnx, cur))


@app.route('/stats/', defaults={'user': None})
@app.route('/stats/<string:user>')
def show_stats(user=None):
    """
    ---
    summary: Returns the Statistics about the Drying Cycles
    description: Returns the Statistics about the Drying Cycles. If it is given the user, the stats are calculated only on his data
    parameters:
      - name: UserID
        in: path
        required: false
        schema:
            type: string
            example: mariorossi
    responses:
        200:
            description: OK
        400:
            description: Client Error
        500:
            description: Internal Server Error
    """
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
    """
    ---
    summary: Give a wheated feed based on the position given in the registration phase.
    description: Give a wheated feed based on the position given in the registration phase.
    parameters:
      - name: User
        in: path
        required: true
        schema:
            type: string
            example: mariorossi
    responses:
        200:
            description: OK
        400:
            description: Client Error
        500:
            description: Internal Server Error
    """
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
    """
    ---
    summary: Give the last sensor feed made on the Drying Rack
    description: Give the last sensor feed made on the Drying Rack
    parameters:
      - name: User
        in: path
        required: true
        schema:
            type: string
            example: mariorossi
    responses:
        200:
            description: OK
        400:
            description: Client Error
        500:
            description: Internal Server Error
    """
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