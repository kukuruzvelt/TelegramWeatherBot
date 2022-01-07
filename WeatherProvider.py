import json
from abc import ABC, abstractmethod
import requests
from Languages import Languages


class WeatherProvider(ABC):
    @staticmethod
    @abstractmethod
    def getCurrent(city_name, language, params):
        pass

    @staticmethod
    @abstractmethod
    def getForecast(city_name, language, params):
        pass

    @staticmethod
    @abstractmethod
    def isOK(city_name):
        pass


class WeatherioProvider(WeatherProvider):
    API_KEY = "&key=e244662e839949378865f4414b9c6213"
    API_CURRENT = "https://api.weatherbit.io/v2.0/current?&city="
    API_FORECAST = "https://api.weatherbit.io/v2.0/forecast/daily?city="

    @staticmethod
    def isOK(city_name):
        info = requests.get(WeatherioProvider.API_CURRENT + city_name + WeatherioProvider.API_KEY)
        if info.status_code == 200:
            return True
        return False

    @staticmethod
    def getCurrent(city_name, language, params):
        names = Languages.get_message("weather_provider_names", language)
        info = requests.get(
            WeatherioProvider.API_CURRENT + city_name + f"&lang={language}" + WeatherioProvider.API_KEY)
        json_list = json.loads(info.text)["data"][0]
        string = ""
        if params[0]:
            string += f'{names[0]}: {json_list.get("rh")}'
        if params[1]:
            string += f'\n{names[1]}: {json_list.get("temp")}'
        if params[2]:
            string += f'\n{names[2]}: {json_list.get("app_temp")}'
        if params[3]:
            string += f'\n{names[3]}: {json_list.get("wind_spd")}'
        if params[4]:
            string += f'\n{names[4]}: {json_list.get("pres")}'
        if params[5]:
            string += f'\n{names[5]}: {json_list.get("weather").get("description")}'
        return string
    
    @staticmethod
    def getAdvice(city_name, language):
        info = requests.get(
            WeatherioProvider.API_CURRENT + city_name + f"&lang={language}" + WeatherioProvider.API_KEY)
        json_list = json.loads(info.text)["data"][0]
        string = ""
        wind_spd = json_list.get("wind_spd")
        wet = json_list.get("rh")
        temp = json_list.get("temp")

        if wind_spd > 20:
            return Languages.get_message("so_windy", language)

        if temp < -10:
            if wet < 10:
                string += Languages.get_message("less_minus10", language)
            else:
                string += Languages.get_message("less_minus10_wet", language)
            if 5 <= wind_spd < 20:
                string += Languages.get_message("less_minus10_windy", language)

        elif temp < 0:
            if wet < 10:
                string += Languages.get_message("less0", language)
            else:
                string += Languages.get_message("less0_wet", language)
            if 5 <= wind_spd < 20:
                string += Languages.get_message("less0_windy", language)

        elif temp < 10:
            if wet < 10:
                string += Languages.get_message("less10", language)
            else:
                string += Languages.get_message("less10_wet", language)
            if 5 <= wind_spd < 20:
                string += Languages.get_message("less10_windy", language)

        elif temp < 20:
            if wet < 10:
                string += Languages.get_message("less20", language)
            else:
                string += Languages.get_message("less20_wet", language)
            if 5 <= wind_spd < 20:
                string += Languages.get_message("less20_windy", language)

        else:
            if wet < 10:
                string += Languages.get_message("heat", language)
            else:
                string += Languages.get_message("heat_wet", language)
            if 5 <= wind_spd < 20:
                string += Languages.get_message("heat_windy", language)

        return string

    @staticmethod
    def getForecast(city_name, language, params):
        names = Languages.get_message("weather_provider_names", language)
        date = Languages.get_message("weather_provider_date", language)
        info = requests.get(
            WeatherioProvider.API_FORECAST + city_name + f"&lang={language}" + "&days=7" + WeatherioProvider.API_KEY)
        json_list = json.loads(info.text)["data"]
        string = ""
        for i in range(len(json_list)):
            t = json_list[i]
            string += f'{date}: {t.get("datetime")}'
            if params[0]:
                string += f'\n{names[0]}: {t.get("rh")}'
            if params[1]:
                string += f'\n{names[1]}: {t.get("temp")}'
            if params[2]:
                string += f'\n{names[2]}: {t.get("app_temp")}'
            if params[3]:
                string += f'\n{names[3]}: {t.get("wind_spd")}'
            if params[4]:
                string += f'\n{names[4]}: {t.get("pres")}'
            if params[5]:
                string += f'\n{names[5]}: {t.get("weather").get("description")}'
            string += f'\n\n'
        return string

