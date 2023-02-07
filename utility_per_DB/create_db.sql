create table rack_user (
	user_name varchar(255) primary key,
    pin varchar(255) not null, 
    lat float not null,
    lon float not null,
    is_active bool default false,
    is_outside bool default true,
    check(length(pin)>=8)
);

create table weather_feed (
	id int auto_increment primary key,
    content text not null,
    user_name varchar(255) not null,
    weather_time datetime default current_timestamp not null,
    foreign key(user_name) references rack_user(user_name)
    on update cascade
	on delete cascade
);

create table drying_cycle(
	id int auto_increment primary key,
    start_time datetime not null default current_timestamp, 
    user_name varchar(255) not null,
    is_active bool default true,
    foreign key(user_name) references rack_user(user_name)
    on delete cascade
	on update cascade
);

create table sensor_feed(
	id int auto_increment primary key,
    sensor_time datetime default current_timestamp not null,
    air_humidity int check(air_humidity>=0 and air_humidity<=100),
    air_temperature float,
    is_raining int, 
    cloth_humidity float check(cloth_humidity>=0 and cloth_humidity<=100),
    cloth_weight int,
    cycle_id int not null,
    foreign key(cycle_id) references drying_cycle(id)
    on delete cascade
	on update cascade
);






