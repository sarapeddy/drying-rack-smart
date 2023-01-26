create table rack_user (
	user_name varchar(255) primary key,
    pin varchar(255) not null, 
    lat float not null,
    lon float not null,
    check(length(pin)>=8)
);

create table weather_feed (
	id int auto_increment primary key,
    content text not null,
    user_name varchar(255) not null,
    foreign key(user_name) references rack_user(user_name)
);

create table drying_cycle(
	id int auto_increment primary key,
    start_time datetime not null default current_timestamp, 
    user_name varchar(255) not null,
    foreign key(user_name) references rack_user(user_name)
);

create table sensor_feed(
	id int auto_increment primary key,
    sensor_time datetime default current_timestamp not null,
    air_humidity float check(air_humidity>0 and air_humidity<=100),
    air_temperature float,
    is_raining int, 
    cloth_humidity int check(cloth_humidity>0 and cloth_humidity<=100),
    cloth_weight int,
    cycle_id int not null,
    foreign key(cycle_id) references drying_cycle(id)
);

<<<<<<< Updated upstream
=======
alter table weather_feed
add column weather_time datetime default current_timestamp not null;

>>>>>>> Stashed changes

