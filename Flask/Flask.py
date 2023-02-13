import json
import mysql.connector
from flask import Flask, request, session, render_template, abort
from flask_restx import Api
from configparser import ConfigParser
from OpenWeather import OpenWeather
from Stats import Statistics
from Registration import Registration
from flasgger import Swagger, LazyString, LazyJSONEncoder
from flask_cors import CORS
from werkzeug.middleware.proxy_fix import ProxyFix
import Queries
import Creation

appname = "Smart Drying-rack"
application = Flask(appname)
CORS(application)
application.json_encoder = LazyJSONEncoder

config = ConfigParser()
config.read('config.ini')
user = config.get('Database', 'user')
password = config.get('Database', 'password')
host = config.get('Database', 'host')
database = config.get('Database', 'database')
raise_on = bool(config.get('Database', 'raise_on_warnings'))


swagger_template = dict(
    info={
        'title': LazyString(lambda: 'Smart Drying Rack'),
        'version': LazyString(lambda: '1.0'),
        'description': LazyString(lambda: 'This is the documentation about Flask Smart Drying Rack project Apis'),
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

swagger = Swagger(application, template=swagger_template, config=swagger_config)

try:
    cnx = mysql.connector.connect(user=user, password=password, host=host, db=database)
    cur = cnx.cursor()
except Exception as e:
    print(e)

key_weather = config.get('Weather', 'key')

CREATE = 0  # variabile per la creazione del db su AWS
INSERT = 0  # variabile per inserire dati di prova nel db su AWS

api = Api(application)


@application.route('/')
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


@application.route('/', methods=['PUT'])
def query_records():
    record = json.loads(request.data)
    return record


@application.route('/test')
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


@application.route('/registration-bot', methods=['POST'])
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
    produces:
      - text/plain
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


@application.route('/registration/', methods=['GET', 'POST'])
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
    produces:
      - text/html
    """
    if request.method == 'POST':
        data = dict(request.form)
        print(request.form)
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


@application.route('/credentials', methods=['POST'])
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
            schema:
                type: string
                example: Login
        400:
            description: Client Error
        500:
            description: Internal Server Error
    produces:
      - text/plain
    """
    try:
        result = Queries.check_rack_user(request.get_json(), cur)
        if result:
            return "Login"
    except KeyError:
        return "Uncorrect json format"
    return "Uncorrect username or/and password"


@application.route('/credentials/password', methods=['PUT'])
def recover_change_credentials():
    """
    ---
    summary: Change password
    description: Change password of a logged user
    parameters:
      - name: User
        in: body
        required: true
        schema:
            type: object
            properties:
                password:
                    type: string
                    required: false
                    example: 12345678
                new_password:
                    type: string
                    required: false
                    example: 87654321
                username:
                    type: string
                    example: mariorossi
    responses:
        200:
            description: OK
            schema:
                type: string
                example: Password changed
        400:
            description: Client Error
        500:
            description: Internal Server Error
    produces:
      - text/plain
    """
    try:
        request_data = request.get_json()
        if len(str(request_data['new_password'])) < 8:
            return 'At least 8 characters needed'
        result = Queries.check_rack_user(request_data, cur)
        print(result)
        if result:
            Queries.update_password(request_data, cur, cnx)
            return "Password changed"
    except KeyError:
        return "Uncorrect json format"
    return "Uncorrect username or/and password"


@application.route('/credentials/password/<string:user>')
def recover_password(user=None):
    """
    ---
    summary: Recover password
    description: Recover password of a user
    parameters:
      - name: User
        in: string
        required: true
        schema:
            type: string
            example: mariorossi
    responses:
        200:
            description: OK
            schema:
                type: string
                example: 12345678
        400:
            description: Client Error
        500:
            description: Internal Server Error
    produces:
      - text/plain
    """
    if user is None:
        return 'user is required to recover password'
    result = Queries.select_user(user, cur)
    if not result:
        return 'Invalid username'
    return result[0][1]


@application.route('/drying-cycle', methods=['POST'])
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
            schema:
                type: string
                example: 50
        400:
            description: Client Error
        500:
            description: Internal Server Error
    produces:
      - text/plain
    """
    request_data = request.get_json()
    result = Queries.select_user(request_data['user'], cur)
    if not result:
        return 'Invalid username'
    return Queries.create_new_drying_cycle(request_data, cur, cnx)


@application.route('/sensors/data', methods=['POST'])
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
                    example: 50
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
            schema:
                type: string
                example: 54
        400:
            description: Client Error
        500:
            description: Internal Server Error
    produces:
      - text/plain
    """
    return Queries.create_new_sensor_feed(request.get_json(), cur, cnx)


@application.route('/<int:drying_cycle>/inactive', methods=['PUT'])
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
            schema:
                type: string
                example: 30
        400:
            description: Client Error
        500:
            description: Internal Server Error
    produces:
      - text/plain
    """
    return str(Queries.update_status_drying_cycle(drying_cycle, cnx, cur))


@application.route('/drying-rack/position', methods=['PUT'])
def set_drying_rack_position():
    """
    ---
    summary: Update the drying rack position
    description: Update the drying rack position. The drying rack is set outside by default. If this API is called it is possible to change the drying-rack position passing an object.
    parameters:
      - name: UpdateDryingCycle
        in: body
        required: true
        schema:
            type: object
            properties:
                username:
                    type: string
                    example: mariorossi
                is_outside:
                    type: bool
                    example: 0
    responses:
        200:
            description: OK
            schema:
                type: string
                example: Correct Operation
        400:
            description: Client Error
        500:
            description: Internal Server Error
    produces:
      - text/plain
    """
    return Queries.update_drying_rack_position(request.get_json(), cur, cnx)


@application.route('/stats/', defaults={'user': None})
@application.route('/stats/<string:user>')
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
            schema:
                type: object
                properties:
                    mean_cycle_time:
                        type: number
                        format: float
                        example: 50.5
                    normalized_cycle_time:
                        type: number
                        format: float
                        exaqmple: 66.3
                    normalized_cycle_time_temp:
                        type: number
                        format: float
                        example: 57.3
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


@application.route('/weather_feed', defaults={'user': None})
@application.route('/weather_feed/<string:user>', methods=['GET', 'POST'])
def show_weather_info(user=None):
    """
    ---
    summary: Give a weather feed based on the position given in the registration phase.
    description: Give a weather feed based on the position given in the registration phase.
    parameters:
      - name: User
        in: path
        required: false
        schema:
            type: string
            example: mariorossi
    responses:
        200:
            description: OK
            schema:
                type: object
                properties:
                    temp:
                        type: number
                        format: float
                        example: 21.3
                    rain:
                        type: bool
                        example: true
                    hum:
                        type: number
                        format: float
                        example: 50.2
                    best_time:
                        type: string
                        example: 9:30
        400:
            description: Client Error
        500:
            description: Internal Server Error
    """
    if request.method == 'POST':
        return abort(405)
    elif user is None:
        return 'Insert a username to view information'
    else:
        myweather = OpenWeather(key_weather)
        result = Queries.select_lat_lon(user, cur)
        if len(result) == 0:
            return 'Invalid username'
        lat = result[0][0]
        lon = result[0][1]
        temp = myweather.get_temperature(lat, lon)
        rain = myweather.is_going_to_rain_in_3h(lat, lon)
        hum = myweather.get_humidity(lat, lon)
        best_time = myweather.get_best_moment(lat, lon)
        mydict = dict(temp=temp, rain=rain, hum=hum, best_time=best_time)
        return json.dumps(mydict, indent=4)


@application.route('/rack_user/<string:user>')
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
            schema:
                type: object
                properties:
                    id:
                        type: number
                        example: 64
                    user_name:
                        type: string
                        example: mariorossi
                    sensor_time:
                        type: string
                        format: date-time
                        example: 2023-02-10 11:26:59
                    air_humidity:
                        type: float
                        example: 30.00
                    air_temperature:
                        type: float
                        example: 19.00
                    cloth_humidity:
                        type: int64
                        example: 50
                    cloth_weight:
                        type: int64
                        example: 600
                    is_raining:
                        type: number
                        example: 1011
                    start_time:
                        type: string
                        format: date-time
                        example: 2023-02-10 11:26:56
                    cycle_id:
                        type: int64
                        example: 64
                    is_active:
                        type: bool
                        example: true
        400:
            description: Client Error
        500:
            description: Internal Server Error
    """
    if user is None:
        return abort(404)

    result = Queries.select_last_sensor_feed(user, cur)

    if len(result) == 0:
        return json.dumps([{}])

    r = [dict((cur.description[i][0], value) for i, value in enumerate(row)) for row in result]
    if 'application/json' in request.headers:
        return json.dumps(r, indent=4, separators=(',', ': '), default=str) if r else None
    else:
        return r if r else None


@application.route('/database')
def create_database():
    if CREATE:
        Creation.create_db(cnx, cur)
    if INSERT:
        Creation.insert_base_data(cnx, cur)

    cur.execute('select user_name from rack_user')
    result = cur.fetchall()
    if not result:
        return "Database created"
    return result


@application.route('/deletion/drying_cycle/<string:user>', methods=['DELETE'])
def cancel_last_cycle(user):
    """
 ---
    summary: Delete the last drying cycle of a user
    description: The drying cycle and the data are being deleted. If this API is called it is possible to delete the drying cycle and sensor data associated with it.
    parameters:
      - name: User
        in: string
        required: true
        schema:
            type: string
            properties:
                username:
                    type: string
                    example: mariorossi
    responses:
        200:
            description: OK
            schema:
                type: string
                example: mariorossi last drying cycle deleted
        400:
            description: Client Error
        500:
            description: Internal Server Error
    produces:
      - text/plain
    """
    result = Queries.select_last_drying_cycle(user, cur)
    if not result:
        return 'Username invalid'

    #print(result, result[0][0], result[0][1])
    username = result[0][0]
    id = result[0][1]
    try:
        Queries.delete_sensor_feed(id, cur)
        Queries.delete_last_drying_cycle(id, cur)
        cnx.commit()
    except Exception as e:
        print(e)
        return ' Deletion gone wrong'

    return str(username) + ' last drying cycle deleted'


@application.route('/deletion/<string:user>', methods=['DELETE'])
def cancel_all(user):
    """
     ---
    summary: Delete a user
    description: Delete all information related to a user.
    parameters:
      - name: User
        in: string
        required: true
        schema:
            type: string
            properties:
                username:
                    type: string
                    example: mariorossi
    responses:
        200:
            description: OK
            schema:
                type: string
                example: mariorossi deleted
        400:
            description: Client Error
        500:
            description: Internal Server Error
    produces:
      - text/plain
    """
    result = Queries.select_user(user, cur)
    if not result:
        return 'Username invalid'
    username = result[0][0]
    try:
        Queries.delete_user(user, cur)
        cnx.commit()
        print(username)
    except Exception as e:
        print(e)
        return ' Deletion gone wrong'

    return str(username) + ' deleted'


@application.route('/ranking')
def build_ranking():
    """
     ---
    summary: Create ranking based on number of close drying cycle
    description: Create ranking based on number of close drying cycle
    responses:
        200:
            description: OK
            schema:
                type: array
                example:
                  - (42, mariorossi)
                  - (17, lucabianchi)
                  - (8, giacomoverdi)]
        400:
            description: Client Error
        500:
            description: Internal Server Error
    """
    return Queries.create_ranking_number_of_drying_cycle(cur)


@application.route('/profile/<string:user>')
def show_user_info(user):
    """
     ---
    summary: Give profile information about the user
    description: Give profile information about the user and its drying-rack
    parameters:
      - name: User
        in: string
        required: true
        schema:
            type: string
            example: mariorossi
    responses:
        200:
            description: OK
            schema:
                type: object
                properties:
                    username:
                        type: string
                        example: mariorossi
                    latitude:
                        type: number
                        format: float
                        example: 40.6
                    longitude:
                        type: number
                        format: float
                        example: 10.5
                    place:
                        type: string
                        example: outside
                    active:
                        type: bool
                        example: true
        400:
            description: Client Error
        500:
            description: Internal Server Error
    """
    result = Queries.select_profile_info(user, cur)
    if not result:
        return 'Username invalid'
    if result[0][3]:
        place = 'outside'
    else: 
        place = 'inside'
    mydict = dict(username=result[0][0], latitude=result[0][1], longitude=result[0][2],
                  place=place, active=result[0][4])
    return json.dumps(mydict, indent=4)


@application.route('/community/<string:user>')
def control_com(user):
    """
     ---
    summary: Give information about the community
    description: Give information about the community in order to see if the drying rack is inside or outside
    parameters:
      - name: User
        in: string
        required: true
        schema:
            type: string
            example: mariorossi
    responses:
        200:
            description: OKù
            schema:
                type: string
                example: Outside
        400:
            description: Client Error
        500:
            description: Internal Server Error
    produces:
      - text/plain
    """
    result = Queries.select_state(user, cur)
    if not result:
        return 'Error'
    #print(result)

    result2 = Queries.select_state_all(user, cur)
    if not result2:
        return 'Error'
    #print(result2)

    len_inside = len(result)
    len_outside = len(result2)
    if len_inside/len_outside > 0.5:
        return 'Inside'
    return 'Outside'


if __name__ == '__main__':
    host = '0.0.0.0'
    port = 80
    # application.wsgi_app = ProxyFix(app.wsgi_app, x_for=1, x_proto=1, x_host=1, x_prefix=1)
    application.run(port=port, host=host, debug=True)
