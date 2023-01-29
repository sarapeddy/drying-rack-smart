#Alcune query di selezione che credo siano utili
#seleziona tutti i sensor feed dell'ultimo ciclo asciugatura di un utente
select * from sensor_feed join drying_cycle 
on(sensor_feed.cycle_id = drying_cycle.id)
where drying_cycle.id >= all( select drying_cycle.id from drying_cycle join rack_user 
							on (drying_cycle.user_name = rack_user.user_name)
							where rack_user.user_name like 'bucci23');

#seleziona l'ultimo sensor feed dell'ultimo ciclo asciugatura dato un utente
select * from sensor_feed join drying_cycle 
on(sensor_feed.cycle_id = drying_cycle.id)
where drying_cycle.id >= all( select drying_cycle.id from drying_cycle join rack_user 
							on (drying_cycle.user_name = rack_user.user_name)
							where rack_user.user_name like 'bucci23')
and sensor_feed.id >= all (select sensor_feed.id from sensor_feed join drying_cycle
							on (sensor_feed.cycle_id = drying_cycle.id));

#seleziona l'ultimo weather_feed dato un utente
select * from weather_feed join rack_user
on( weather_feed.user_name like rack_user.user_name)
where weather_feed.id >= all(select weather_feed.user_name from weather_feed join rack_user
							on( weather_feed.user_name = rack_user.user_name)
                            where rack_user.user_name like 'bucci23');

#seleziona tutti i cicli conclusi di un utente (utile per fare medie e statistiche)
select * from drying_cycle join rack_user 
on (rack_user.user_name like drying_cycle.user_name)
where drying_cycle.user_name like 'bucci23'
and drying_cycle.is_active is true;

#seleziona il momento di chiusura dell'ultimo ciclo di asciugatura concluso di un dato utente
select sensor_feed.sensor_time from sensor_feed join drying_cycle 
on (sensor_feed.cycle_id = drying_cycle.id)
join rack_user on (rack_user.user_name like drying_cycle.user_name)
where rack_user.user_name like 'bucci23'
and drying_cycle.is_active is false
and drying_cycle.id >= all (select drying_cycle.id from drying_cycle join rack_user
							on (drying_cycle.user_name like rack_user.user_name)
                            where rack_user.user_name like 'bucci23'
                            and drying_cycle.is_active is false)
and sensor_feed.id >= all (select sensor_feed.id from sensor_feed join drying_cycle
							on (drying_cycle.id = sensor_feed.cycle_id)
                            where drying_cycle.id >= all (select drying_cycle.id from drying_cycle join rack_user
														on (drying_cycle.user_name like rack_user.user_name)
														where rack_user.user_name like 'bucci23'
														and drying_cycle.is_active is false));

#seleziona start_time e finish_time di tutti i cicli asciugatura di un utente
select d.start_time, s.sensor_time as finish_time
from drying_cycle d join sensor_feed s on (d.id = s.cycle_id)
where d.user_name like 'bucci23'
and is_active is false
and s.id >= all(select s1.id from sensor_feed s1 
				where s1.cycle_id = s.cycle_id);



#seleziona lo stato (dentro o fuori) degli stendini degli utenti vicini ad un certo utente(<10km)
select r.user_name from rack_user r join rack_user r1
where r1.user_name like 'bucci23'
and r.user_name not like 'bucci23'
and sqrt((r.lat - r1.lat)*(r.lat - r1.lat) - (r.lon - r1.lon)*(r.lon - r1.lon)) <= 0.1506;
        

