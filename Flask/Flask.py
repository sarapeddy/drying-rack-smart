import json
import mysql.connector
from flask import Flask, request, session, render_template
from flask_restx import Api, Resource
from configparser import ConfigParser

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

#api = Api(app)


@app.route('/')
def hello():
    """
    Home path
    :return: Title
    """
    testdb()
    return '<h1>Smart Drying-Rack<h1>'


def testdb():
    global cnx, cur
    try:
        cnx = mysql.connector.connect(user=user, password=password, host=host, db=database)
        cur = cnx.cursor()
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


@app.route('/new_user')
def add_user_view():
    return render_template('add.html')


@app.route('/show')
def show():
    # TODO
    # select, read elements
    return 0


@app.route('/edit/<user>')
def edit():
    # TODO
    # edit form where user updates information
    return 0


@app.route('/update/user', methods=['POST'])
def update_user():
    # TODO
    # update user information
    return 0


@app.route('/update/data', methods=['POST'])
def update_data():
    # TODO
    # update data
    return 0


@app.route('/delete')
def delete():
    # TODO
    # delete information or user
    return 0


@app.route('/sensors')
def func1():
    # TODO
    # visione sensori, nomi, dati, statistiche,...
    return "Sensors --> DHT11, ..."


@app.route('/sensors/data', methods=['POST'])
def receive_json():
    request_data = request.get_json()
    print(request_data)
    # TODO
    # inserire dati dei sensori nel db
    return request_data


@app.route('/<string:user>')
def display(user):
    result = select_sensor_feed(user)
    return json.loads(result)


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
    query = f"select * from sensor_feed join drying_cycle on(sensor_feed.cycle_id = drying_cycle.id)" \
            f"where drying_cycle.id >= all(select drying_cycle.id from drying_cycle join rack_user " \
            f"on(drying_cycle.user_name = rack_user.user_name) " \
            f"where rack_user.user_name like '{user}') and sensor_feed.id >= all(select sensor_feed.id " \
            f"from sensor_feed join drying_cycle on(sensor_feed.cycle_id = drying_cycle.id));"

    cur.execute(query)
    result = cur.fetchall()
    return result


def select_last_weather_feed(user):
    # seleziona l'ultimo weather_feed dato un utente
    query = f"select * from weather_feed join rack_user " \
            f"on( weather_feed.user_name like rack_user.user_name) ù" \
            f"where weather_feed.id >= all(select weather_feed.user_name from weather_feed join rack_user " \
            f"on( weather_feed.user_name = rack_user.user_name)" \
            f"where rack_user.user_name like '{user}');"
    cur.execute(query)
    result = cur.fetchall()
    return result


def select_all_cycles(user):
    # seleziona tutti i cicli conclusi di un utente (utile per fare medie e statistiche)
    query = f"select * from drying_cycle " \
            f"where drying_cycle.user_name like '{user}'" \
            f"and drying_cycle.is_active is false;"
    cur.execute(query)
    result = cur.fetchall()
    return result


def select_closing_time_drying_cycle(user):
    # seleziona il momento di chiusura dell'ultimo ciclo di asciugatura concluso di un dato utente
    query = f"select * from sensor_feed s join drying_cycle d" \
            f"on (s.cycle_id = d.id)" \
            f"where d.user_name like '{user}'" \
            f"and d.is_active is false" \
            f"and d.id >=all	(select d1.id from drying_cycle d1" \
            f"where d1.user_name like d.user_name" \
            f"and d1.is_active is false)" \
            f"and s.id >=all	(select s1.id from sensor_feed s1" \
            f"where s1.cycle_id = d.id);"
    cur.execute(query)
    result = cur.fetchall()
    return result


def select_start_finish_time(user):
    # seleziona start_time e finish_time di tutti i cicli asciugatura di un utente
    query = f"select d.start_time, s.sensor_time as finish_time " \
            f"from drying_cycle d join sensor_feed s on (d.id = s.cycle_id)" \
            f"where d.user_name like '{user}'" \
            f"and is_active is false" \
            f"and s.id >= all(select s1.id from sensor_feed s1" \
            f"where s1.cycle_id = s.cycle_id);"
    cur.execute(query)
    result = cur.fetchall()
    return result


def select_state(user):
    # seleziona lo stato (dentro o fuori) degli stendini degli utenti vicini ad un certo utente(<10km)
    query = f"select r.* from rack_user r join rack_user r1" \
            f"where r1.user_name like '{user}'" \
            f"and r.user_name not like '{user}'" \
            f"and r.is_active is true" \
            f"and abs(r.lat-r1.lat)<=0.0753 " \
            f"and abs(r.lon-r1.lon)<=0.0753" \
            f";"
    cur.execute(query)
    result = cur.fetchall()
    return result


if __name__ == '__main__':
    host = '0.0.0.0'
    port = 80
    app.run(port=port, host=host, debug=True)
