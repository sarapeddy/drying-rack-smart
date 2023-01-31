from datetime import datetime
import mysql.connector
from configparser import ConfigParser
'''
config = ConfigParser()
config.read('config.ini')
user = config.get('Database', 'user')
password = config.get('Database', 'password')
host = config.get('Database', 'host')
database = config.get('Database', 'database')
raise_on = bool(config.get('Database', 'raise_on_warnings'))
'''
def select_start_finish_time_user(user, cur):
    # seleziona start_time e finish_time di tutti i cicli asciugatura di un utente
    query = f"select d.start_time, s.sensor_time as finish_time " \
            f"from drying_cycle d join sensor_feed s on (d.id = s.cycle_id) " \
            f"where d.user_name like '{user}' " \
            f"and is_active is false " \
            f"and s.id >= all(select s1.id from sensor_feed s1 " \
            f"where s1.cycle_id = s.cycle_id);"
    cur.execute(query)
    result = cur.fetchall()
    return result

def select_start_finish_time(cur):
    # seleziona start_time e finish_time di tutti i cicli asciugatura di un utente
    query = f"select d.start_time, s.sensor_time as finish_time " \
            f"from drying_cycle d join sensor_feed s on (d.id = s.cycle_id) " \
            f"where is_active is false " \
            f"and s.id >= all(select s1.id from sensor_feed s1 " \
            f"where s1.cycle_id = s.cycle_id);"
    cur.execute(query)
    result = cur.fetchall()
    return result

def select_start_finish_time_hum(cur):
    #seleziona start_time, finish_time, umidità iniziale ed umidità finale di tutti i cicli di asciugatura
    query = "select d.start_time, s.sensor_time as finish_time, s2.cloth_humidity as start_hum, s.cloth_humidity as finish_hum \
            from drying_cycle d join sensor_feed s on (d.id = s.cycle_id) \
            join sensor_feed s2 on (d.id = s2.cycle_id) \
            and is_active is false \
            and s.id >= all(select s1.id from sensor_feed s1 \
				            where s1.cycle_id = s.cycle_id) \
            and s2.id <= all(select s1.id from sensor_feed s1 \
				            where s1.cycle_id = s.cycle_id);"
    cur.execute(query)
    result = cur.fetchall()
    result
    return result

def select_start_finish_time_hum_user(user, cur):
    #seleziona start_time, finish_time, umidità iniziale ed umidità finale di tutti i cicli di asciugatura di un dato utente
    query = f"select d.start_time, s.sensor_time as finish_time, s2.cloth_humidity as start_hum, s.cloth_humidity as finish_hum \
            from drying_cycle d join sensor_feed s on (d.id = s.cycle_id) \
            join sensor_feed s2 on (d.id = s2.cycle_id) \
            where d.user_name like {user} \
            and is_active is false \
            and s.id >= all(select s1.id from sensor_feed s1 \
				            where s1.cycle_id = s.cycle_id) \
            and s2.id <= all(select s1.id from sensor_feed s1 \
				            where s1.cycle_id = s.cycle_id);"
    cur.execute(query)
    result = cur.fetchall()
    result
    return result
'''
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
'''
class Statistics:
    def __init__(self, cur):
        self.cur = cur
    def get_mean_cycle_time_user(self, user = None):
        #Ritorna la durata media in secondi dei cicli di asciugatura di un utente (se fornito come argomento) o di tutti (se non si forniscono argomenti)
        if user == None:
            result = select_start_finish_time(cur)
        else:
            result = select_start_finish_time_user(user, cur)
        datediff = 0
        k = 0
        print(result)
        for i in result:
            datediff = datediff +((result[k][1] - result[k][0]).total_seconds())
        return datediff/len(result)

    def get_normalized_mean_cycle_time(self, user = None):
        #Ritorna la durata media in secondi dei cicli di asciugatura, normalizzata alla differenza fra umidità iniziale e finale del vestito
        # di un utente (se fornito come argomento) o di tutti (se non si forniscono argomenti)
        if user == None:
            result = select_start_finish_time_hum(cur)
        else:
            result = select_start_finish_time_hum_user(user, cur)
        datediff = 0
        k = 0
        print(result)
        for i in result:
            datediff = datediff +((result[k][1] - result[k][0]).total_seconds())*100/(result[k][2] - result[k][3])
        return datediff/len(result)

'''
if __name__ == '__main__':
    testdb()
    s = Statistics(cur)
    print(s.get_mean_cycle_time_user())
    print(s.get_normalized_mean_cycle_time())
'''