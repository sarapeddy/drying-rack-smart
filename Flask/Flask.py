import json
import mysql.connector
from flask import Flask, request, session, render_template
from flask_restx import Api, Resource

appname = "Smart Drying-rack"
app = Flask(appname)
#api = Api(app)

config = {
  'user': 'cosimo',
  'password': '123',
  'host': '25.46.183.67',
  'database': 'stendini_smart',
  'raise_on_warnings': True
}

@app.route('/')
def hello():
    testdb()
    return '<h1>Smart Drying-Rack<h1>'

def testdb():
    global cnx, cur
    try:
        cnx = mysql.connector.connect(**config)
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

if __name__ == '__main__':
    host = '0.0.0.0'
    port = 80
    app.run(port=port, host=host)