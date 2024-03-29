from datetime import datetime
from typing import Iterable
import mysql.connector
from configparser import ConfigParser
import Queries
'''
config = ConfigParser()
config.read('config.ini')
user = config.get('Database', 'user')
password = config.get('Database', 'password')
host = config.get('Database', 'host')
database = config.get('Database', 'database')
raise_on = bool(config.get('Database', 'raise_on_warnings'))

def testdb():
    global cnx, cur
    try:
        cnx = mysql.connector.connect(user=user, password=password, host=host, db=database)
        cur = cnx.cursor()
        cur.execute('select * from rack_user')
        result = cur.fetchall()
        return '<h1>Smart Drying-Rack<h1>'
    except Exception as e:
        cnx.close()
        cur.close()
        print("\nThe error:\n" + str(e) + "\n")
        return '<h1>Something is broken.</h1>'
'''
class Statistics:
    #Per usare la classe Statistics: passare al costruttore direttamente il cursore di una connessione a mysql già stabilita
    def __init__(self, cur):
        self.cur = cur
    def get_mean_cycle_time_user(self, user = None):
        #Ritorna la durata media in secondi dei cicli di asciugatura di un utente (se fornito come argomento) o di tutti (se non si forniscono argomenti)
        if user == None:
            result = Queries.select_start_finish_time(self.cur)
        else:
            result = Queries.select_start_finish_time_user(user, self.cur)
        datediff = 0
        k = 0
        for i in result:
            datediff = datediff +((result[k][1] - result[k][0]).total_seconds())
            k=k+1
        if len(result) == 0:
            return datediff
        datediff = datediff/len(result)
        return abs(datediff/60/60)

    def get_normalized_mean_cycle_time(self, user = None):
        #Ritorna la durata media in secondi dei cicli di asciugatura, normalizzata alla differenza fra umidità iniziale e finale del vestito
        # di un utente (se fornito come argomento) o di tutti (se non si forniscono argomenti)
        if user == None:
            result = Queries.select_start_finish_time_hum(self.cur)
        else:
            result = Queries.select_start_finish_time_hum_user(user, self.cur)
        datediff = 0
        k = 0
        for i in result:
            if i[2] != i[3]:
                datediff = datediff +((result[k][1] - result[k][0]).total_seconds())*100/abs(i[2] - i[3])
            k=k+1
        if len(result) == 0:
            return datediff
        datediff = datediff/len(result)
        return abs(datediff/60/60/4)

    def get_normalized_cycle_time_per_temp(self, user = None):
        #ritorna la durata media in secondi dei cicli di asciugatura divisi per temperatura: temp>25, 15<temp<25, temp<15 in una list
        if user == None:
            result = Queries.select_avg_tmp(self.cur)
            result2 = Queries.select_start_finish_time_hum(self.cur)
        else:
            result = Queries.select_avg_tmp_user(user, self.cur)
            result2 = Queries.select_start_finish_time_hum_user(user, self.cur)  
        datediff = [0, 0, 0]
        k = [0, 0, 0]
        for i in result:
            for j in result2:
                if i[1] == j[4]:
                    if(j[2] != j[3]):
                        if i[0] < 15:
                            datediff[0] = datediff[0] +((j[1] - j[0]).total_seconds())*100/abs(j[2] - j[3])
                            k[0] +=1
                        elif i[0] > 25:
                            datediff[2] = datediff[2] +((j[1] - j[0]).total_seconds())*100/abs(j[2] - j[3])
                            k[2] +=1
                        else:
                            datediff[1] = datediff[1] +((j[1] - j[0]).total_seconds())*100/abs(j[2] - j[3])
                            k[1] +=1
        datediff[0] /=28800
        datediff[1] /=28800
        datediff[2] /=28800
        if len(result) == 0:
            return datediff
        if k[0] != 0:
            datediff[0] /=k[0]
        if k[1] != 0:
            datediff[1] /=k[1]
        if k[2] != 0:
            datediff[2] /=k[2]
        return datediff
    def get_total_cycles_user(self, user = None):
        if user == None:
            result = Queries.select_total_cycles_last_month(self.cur)
        else:
            result = Queries.select_total_cycles_last_month(self.cur)

'''
if __name__ == '__main__':
    testdb()
    s = Statistics(cur)
    print(s.get_mean_cycle_time_user('mariorossi'))
    print(s.get_normalized_mean_cycle_time())
    print(s.get_normalized_cycle_time_per_temp())
'''