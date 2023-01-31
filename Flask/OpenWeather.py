import pyowm
from pyowm.utils import timestamps
from pyowm.utils.config import get_default_config_for_subscription_type

class OpenWeather:
    def __init__(self, api_key):
        self.api_key = api_key
        config_dict = get_default_config_for_subscription_type('developer')
        owm = pyowm.OWM(api_key, config_dict)
        self.mgr = owm.weather_manager()

    def get_temperature(self, lat, lon):
        observation = self.mgr.weather_at_coords(lat,lon)
        w = observation.weather
        return w.temperature('celsius')['temp']

    def is_going_to_rain_in_3h(self, lat, lon):
        observation = self.mgr.forecast_at_coords(lat, lon, '3h')
        return observation.will_be_rainy_at(timestamps.next_three_hours())

    def get_humidity(self, lat, lon):
        observation = self.mgr.weather_at_coords(lat, lon)
        w = observation.weather
        return w.humidity



if __name__ == '__main__':
    ow = OpenWeather('2be3598cfb1963158f213a238e5c272e')
    print(ow.get_temperature(44.877120, 10.797592))
    print(ow.is_going_to_rain_in_3h(44.877120, 10.797592))    
    print(ow.get_humidity(44.877120, 10.797592))