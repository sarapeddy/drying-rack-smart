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

    def get_best_moment(self, lat, lon):
        one_call = self.mgr.one_call(lat, lon)
        drying_coefficients = []
        for i in one_call.forecast_hourly:
            drying_coefficients.append((100 - i.humidity)/25 + (1 - i.clouds)/25 + i.temp['temp']) if not any(i.rain) else drying_coefficients.append(0)
        return drying_coefficients.index(max(drying_coefficients))
'''
if __name__ == '__main__':
    ow = OpenWeather('2be3598cfb1963158f213a238e5c272e')
    print(ow.is_going_to_rain_in_3h(55.639060, 12.401471))
    print(ow.get_best_moment(55.639060, 12.401471))
'''