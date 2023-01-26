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
on( weather_feed.user_name = rack_user.user_name)
where weather_feed.id >= all(select weather_feed.user_name from weather_feed join rack_user
							on( weather_feed.user_name = rack_user.user_name)
                            where rack_user.user_name like 'bucci23');


