#Alcune query di selezione che credo siano utili
#seleziona tutti i sensor feed dell'ultimo ciclo asciugatura di un utente
select * from sensor_feed join drying_cycle 
on(sensor_feed.cycle_id = drying_cycle.id)
where drying_cycle.id >= all( select drying_cycle.id from drying_cycle join rack_user 
							on (drying_cycle.user_name = rack_user.user_name)
							where rack_user.user_name like 'ilVincio');

#seleziona l'ultimo sensor feed dell'ultimo ciclo asciugatura dato un utente
select * from sensor_feed join drying_cycle 
on(sensor_feed.cycle_id = drying_cycle.id)
where drying_cycle.id >= all( select drying_cycle.id from drying_cycle join rack_user 
							on (drying_cycle.user_name = rack_user.user_name)
							where rack_user.user_name like 'ilVincio')
and sensor_feed.id >= all (select sensor_feed.id from sensor_feed join drying_cycle
							on (sensor_feed.cycle_id = drying_cycle.id));

#seleziona l'ultimo weather_feed dato un utente
select * from weather_feed join rack_user
on( weather_feed.user_name like rack_user.user_name)
where weather_feed.id >= all(select weather_feed.user_name from weather_feed join rack_user
							on( weather_feed.user_name = rack_user.user_name)
                            where rack_user.user_name like 'bucci23');

#seleziona tutti i cicli conclusi di un utente (utile per fare medie e statistiche)
select * from drying_cycle
where drying_cycle.user_name like 'ilVincio'
and drying_cycle.is_active is false;

#seleziona il momento di chiusura dell'ultimo ciclo di asciugatura concluso di un dato utente
select * from sensor_feed s join drying_cycle d
on (s.cycle_id = d.id)
where d.user_name like 'ilVincio'
and d.is_active is false
and d.id >=all	(select d1.id from drying_cycle d1
				where d1.user_name like d.user_name
                and d1.is_active is false)
and s.id >=all	(select s1.id from sensor_feed s1
				where s1.cycle_id = d.id);

#seleziona start_time e finish_time di tutti i cicli asciugatura di un utente
select d.start_time, s.sensor_time as finish_time
from drying_cycle d join sensor_feed s on (d.id = s.cycle_id)
where d.user_name like 'ilVincio'
and is_active is false
and s.id >= all(select s1.id from sensor_feed s1 
				where s1.cycle_id = s.cycle_id);

#seleziona start_time, finish_time, umidità iniziale ed umidità finale di tutti i cicli di asciugatura
select d.start_time, s.sensor_time as finish_time, s2.cloth_humidity as start_hum, s.cloth_humidity as finish_hum
from drying_cycle d join sensor_feed s on (d.id = s.cycle_id)
join sensor_feed s2 on (d.id = s2.cycle_id)
where is_active is false
and s.id >= all(select s1.id from sensor_feed s1 
				where s1.cycle_id = s.cycle_id)
and s2.id <= all(select s1.id from sensor_feed s1 
				where s1.cycle_id = s.cycle_id);

#seleziona start_time, finish_time, umidità iniziale ed umidità finale di tutti i cicli di asciugatura di un dato utente
select d.start_time, s.sensor_time as finish_time, s2.cloth_humidity as start_hum, s.cloth_humidity as finish_hum
from drying_cycle d join sensor_feed s on (d.id = s.cycle_id)
join sensor_feed s2 on (d.id = s2.cycle_id)
where is_active is false
and d.user_name like 'ilVincio'
and s.id >= all(select s1.id from sensor_feed s1 
				where s1.cycle_id = s.cycle_id)
and s2.id <= all(select s1.id from sensor_feed s1 
				where s1.cycle_id = s.cycle_id);

#seleziona lo stato (dentro o fuori) degli stendini degli utenti vicini ad un certo utente(<10km)
select r.* from rack_user r join rack_user r1
where r1.user_name like 'ilVincio'
and r.user_name not like 'ilVincio'
and r.is_active is true
and abs(r.lat-r1.lat)<=0.0753
and abs(r.lon-r1.lon)<=0.0753;
#and sqrt((r.lat - r1.lat)*(r.lat - r1.lat) - (r.lon - r1.lon)*(r.lon - r1.lon)) <= 0.1506;

#seleziona le temperature medie di tutti i cicli di asciugatura di un dato utente
select avg(s.air_temperature) as avg_temperature, d.id from  sensor_feed s join drying_cycle d
on (d.id = s.cycle_id)
where d.user_name like 'ilVincio'
group by(s.cycle_id);

#seleziona le temperature medie di tutti i cicli di asciugatura
select avg(s.air_temperature) as avg_temperature, s.cycle_id from sensor_feed
group by(s.cycle_id);

#QUERY DI INSERT
#nuovo utente
insert into rack_user(user_name, pin, lat, lon, is_outside, is_active)
values	('test', '12345678', 44.628997, 10.948450, 0, 0), 
		('LetiLeo', '12345678', 44.629120, 10.947905, 0, 0),
        ('ilVincio', '12345678', 44.629443, 10.949051, 0, 0),
        ('fraGuerra', '12345678', 44.630432, 10.949989, 0, 0);

#nuovo ciclo asciugatura, per fare un bel lavoro bisognerebbe controllare che non ce ne sia nessun altro attivo
insert into drying_cycle(user_name)
values ('LetiLeo');

insert into drying_cycle(user_name)
values ('ilVincio');

insert into drying_cycle(user_name)
values ('fraGuerra');

select * from sensor_feed where cycle_id = 5;

#cambiare lo stato dello stendino  di un dato utente (dentro-fuori, attivo-inattivo)
update rack_user
set is_outside=1
where rack_user.user_name like 'LetiLeo';

update rack_user
set is_active=1
where rack_user.user_name like 'fraGuerra';

#dato un utente ed un id, disattivo il ciclo asciugatura. (non so perchè ma non mi fa selezionare l'ultimo in automatico)
update drying_cycle
set drying_cycle.is_active = 0
where drying_cycle.user_name like 'ilVincio'
and drying_cycle.id =5;


#inserimento di alcuni sensor feed
insert into sensor_feed(air_temperature, is_raining, cloth_weight, cycle_id, cloth_humidity, air_humidity)
values(22, 0, 33, 6, 54, 73);

insert into sensor_feed(air_temperature, is_raining, cloth_weight, cycle_id, cloth_humidity, air_humidity)
values(23, 0, 33, 6, 42, 70);

insert into sensor_feed(air_temperature, is_raining, cloth_weight, cycle_id, cloth_humidity, air_humidity)
values(21, 0, 30, 6, 40, 71);

insert into sensor_feed(air_temperature, is_raining, cloth_weight, cycle_id, cloth_humidity, air_humidity)
values(21, 0, 22, 5, 36, 50);

select * from drying_cycle;
											
        

