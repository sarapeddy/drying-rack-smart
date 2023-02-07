def create_db(cnx, cur):
    query = f"create table rack_user ( " \
            f"	user_name varchar(255) primary key, " \
            f"    pin varchar(255) not null, " \
            f"    lat float not null, " \
            f"    lon float not null, " \
            f"    is_active bool default false, " \
            f"    is_outside bool default true, " \
            f"    check(length(pin)>=8) " \
            f"); "
    cur.execute(query)
    cnx.commit()

    query = f"create table weather_feed ( " \
            f"	id int auto_increment primary key, " \
            f"    content text not null, " \
            f"    user_name varchar(255) not null, " \
            f"    weather_time datetime default current_timestamp not null, " \
            f"    foreign key(user_name) references rack_user(user_name) " \
            f"); "
    cur.execute(query)
    cnx.commit()

    query = f"create table drying_cycle( " \
            f"	id int auto_increment primary key, " \
            f"    start_time datetime not null default current_timestamp, " \
            f"    user_name varchar(255) not null, " \
            f"    is_active bool default true, " \
            f"    foreign key(user_name) references rack_user(user_name) " \
            f"    on delete cascade " \
            f"    on update cascade " \
            f"); "
    cur.execute(query)
    cnx.commit()

    query = f"create table sensor_feed( " \
            f"	id int auto_increment primary key, " \
            f"    sensor_time datetime default current_timestamp not null, " \
            f"    air_humidity int check(air_humidity>=0 and air_humidity<=100), " \
            f"    air_temperature float, " \
            f"    is_raining int, " \
            f"    cloth_humidity float check(cloth_humidity>=0 and cloth_humidity<=100), " \
            f"    cloth_weight int, " \
            f"    cycle_id int not null, " \
            f"    foreign key(cycle_id) references drying_cycle(id) " \
            f"    on delete cascade " \
            f"    on update cascade " \
            f"); "
    cur.execute(query)
    cnx.commit()

    return str(cur.lastrowid)


def insert_base_data(cnx, cur):
    query = "insert into rack_user(user_name, pin, lat, lon)" \
            "values ('cosimo', '12345678', 44.78, 10.94) ;"
    cur.execute(query)
    cnx.commit()


def drop_tables(cnx, cur):
    query = " drop table sensor_feed; " \
            " drop table weather_feed; " \
            " drop table drying_cycle; " \
            " drop table rack_user; "
    cur.execute(query)
    cnx.commit()
