import mysql.connector


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
    # seleziona start_time, finish_time, umidit� iniziale ed umidit� finale di tutti i cicli di asciugatura
    query = "select d.start_time, s.sensor_time as finish_time, s2.cloth_humidity as start_hum, s.cloth_humidity as finish_hum, d.id \
            from drying_cycle d join sensor_feed s on (d.id = s.cycle_id) \
            join sensor_feed s2 on (d.id = s2.cycle_id) \
            and is_active is false \
            and s.id >= all(select s1.id from sensor_feed s1 \
				            where s1.cycle_id = s.cycle_id) \
            and s2.id <= all(select s1.id from sensor_feed s1 \
				            where s1.cycle_id = s.cycle_id);"
    cur.execute(query)
    result = cur.fetchall()
    return result


def select_start_finish_time_hum_user(user, cur):
    # seleziona start_time, finish_time, umidit� iniziale ed umidit� finale di tutti i cicli di asciugatura di un dato utente
    query = f"select d.start_time, s.sensor_time as finish_time, s2.cloth_humidity as start_hum, s.cloth_humidity as finish_hum, d.id \
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
    return result


def select_avg_tmp_user(user, cur):
    # seleziona le temperature medie di tutti i cicli di asciugatura di un dato utente
    query = f'select avg(s.air_temperature) as avg_temperature, d.id from  sensor_feed s join drying_cycle d \
            on (d.id = s.cycle_id) \
            where d.user_name like {user} \
            group by(s.cycle_id); '
    cur.execute(query)
    result = cur.fetchall()
    return result


def select_avg_tmp(cur):
    # seleziona le temperature medie di tutti i cicli di asciugatura di un dato utente
    query = 'select avg(s.air_temperature) as avg_temperature, s.cycle_id from  sensor_feed s \
            group by(s.cycle_id); '
    cur.execute(query)
    result = cur.fetchall()
    return result


def select_total_cycles_last_month(cur):
    # seleziona il numero di cicli effettuati da ciascun utente nell'ultimo mese
    query = f'select count(distinct d.id) as total_cycles, d.user_name from drying_cycle d \
            where timestampdiff(day, d.start_time, now()) < 30 \
            group by d.user_name \
            order by 1 desc;'
    cur.execute(query)
    result = cur.fetchall()
    return result
