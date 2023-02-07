def select_start_finish_time_user(user, cur):
    # seleziona start_time e finish_time di tutti i cicli asciugatura di un utente
    query = f"select d.start_time, s.sensor_time as finish_time " \
            f"from drying_cycle d join sensor_feed s on (d.id = s.cycle_id) " \
            f"where d.user_name like '{user}' " \
            f"and d.is_active is false " \
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
            where d.user_name like '{user}' \
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
    query = f"select avg(s.air_temperature) as avg_temperature, d.id from  sensor_feed s join drying_cycle d \
            on (d.id = s.cycle_id) \
            where d.user_name like '{user}' \
            group by(s.cycle_id); "
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


def update_status_drying_cycle(cycle_id, cnx, cur):
    query = f"update drying_cycle set drying_cycle.is_active = 0 " \
            f"where drying_cycle.id = {cycle_id};"
    cur.execute(query)
    cnx.commit()
    return cur.lastrowid


def select_state(user, cur):
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


def select_closing_time_drying_cycle(user, cur):
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


def select_all_cycles(user, cur):
    # seleziona tutti i cicli conclusi di un utente (utile per fare medie e statistiche)
    query = f"select * from drying_cycle " \
            f"where drying_cycle.user_name like '{user}' " \
            f"and drying_cycle.is_active is false ;"
    cur.execute(query)
    result = cur.fetchall()
    return result


def select_last_weather_feed(user, cur):
    # seleziona l'ultimo weather_feed dato un utente
    query = f"select * from weather_feed join rack_user " \
            f"on( weather_feed.user_name like rack_user.user_name) " \
            f"where weather_feed.id >= all(select weather_feed.user_name from weather_feed join rack_user " \
            f"on( weather_feed.user_name = rack_user.user_name) " \
            f" where rack_user.user_name like '{user}') ;"
    cur.execute(query)
    result = cur.fetchall()
    return result


def select_last_sensor_feed(user, cur):
    # seleziona l'ultimo sensor feed dell'ultimo ciclo asciugatura dato un utente
    query = f"select * from sensor_feed s join drying_cycle d on(s.cycle_id = d.id) " \
            f"where d.user_name like '{user}' " \
            f"and s.id >= all(select s1.id from sensor_feed s1 join drying_cycle d1 on (s1.cycle_id = d1.id) " \
            f"where d1.user_name like '{user}');"

    cur.execute(query)
    result = cur.fetchall()
    return result


def select_sensor_feed(user, cur):
    # seleziona tutti i sensor feed dell'ultimo ciclo asciugatura di un utente
    query = f"select * from sensor_feed join drying_cycle on(sensor_feed.cycle_id = drying_cycle.id) " \
            f"where drying_cycle.id >= all( select drying_cycle.id from drying_cycle join rack_user " \
            f"on (drying_cycle.user_name = rack_user.user_name) " \
            f"where rack_user.user_name like '{user}');"
    cur.execute(query)
    result = cur.fetchall()
    return result


def select_lat_lon(user, cur):
    # seleziona latitudine e longitudine
    query = f"select lat, lon " \
            f"from rack_user " \
            f"where user_name like " \
            f"'{user}' ;"
    cur.execute(query)
    result = cur.fetchall()
    return result


def check_rack_user(user, cur):
    query = f"select user_name, pin from rack_user " \
            f"where pin='{user['password']}' and user_name='{user['username']}';"
    cur.execute(query)
    result = cur.fetchall()
    return result


def create_new_user_json(request_data, cur, cnx):
    query = f"insert into rack_user (`user_name`, pin, lat, lon) " \
            f"values ('{request_data['username']}', '{request_data['password']}', {request_data['latitude']}, " \
            f" {request_data['longitude']}) ;"
    cur.execute(query)
    cnx.commit()
    return str(cur.lastrowid)


def create_new_drying_cycle(request_data, cur, cnx):
    query = f"insert into drying_cycle (`user_name`) " \
            f"values ('{request_data['user']}');"
    cur.execute(query)
    cnx.commit()
    return str(cur.lastrowid)


def create_new_sensor_feed(request_data, cur, cnx):
    query = f"insert into sensor_feed(`air_temperature`, `is_raining`, `cloth_weight`, `cycle_id`, " \
            f"`cloth_humidity`, `air_humidity`) " \
            f"values({request_data['air_temperature']}, " \
            f"{request_data['is_raining']}, {request_data['cloth_weight']}, " \
            f"{request_data['cycle_id']}, {request_data['cloth_humidity']}, " \
            f"{request_data['air_humidity']});"

    cur.execute(query)
    cnx.commit()
    return str(cur.lastrowid)


def update_drying_rack_position(data, cur, cnx):
    query = f"update rack_user set is_outside = {data['is_outside']} " \
            f"where user_name = '{data['username']}';"
    cur.execute(query)
    cnx.commit()
    return "Correct Operation"


def select_last_drying_cycle(user, cur):
    query = f"select user_name, id " \
            f"from drying_cycle " \
            f"where user_name = '{user}' " \
            f"and id = (select max(id) " \
            f"	      from drying_cycle " \
            f"		  where user_name = '{user}') " \
            f"; "

    cur.execute(query)
    result = cur.fetchall()
    return result


def delete_last_drying_cycle(id, cur):
    query = f"delete from drying_cycle where " \
            f"id = {id} " \
            f"; "
    cur.execute(query)
    return id


def delete_all_drying_cycle(user, cur):
    query = f"delete from drying_cycle where " \
            f"user_name = '{user}' " \
            f"; "
    cur.execute(query)
    return user


def delete_weather_feed(user, cur):
    query = f"delete from weather_feed where " \
            f"user_name = '{user}' " \
            f"; "
    cur.execute(query)
    return user


def delete_sensor_feed(cycle_id, cur):
    query = f"delete from sensor_feed where " \
            f"cycle_id = {cycle_id} " \
            f"; "
    cur.execute(query)
    return cycle_id


def delete_user(user, cur):
    query = f"delete from rack_user where " \
            f"user_name = '{user}' " \
            f"; "
    cur.execute(query)
    return user
