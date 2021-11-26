import json
from abc import ABC, abstractmethod
import requests


class WeatherProvider(ABC):
    @staticmethod
    @abstractmethod
    def getCurrent(city_name, language):
        pass

    @staticmethod
    @abstractmethod
    def getForecast(city_name, language):
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
    def getCurrent(city_name, language):
        # todo должен возвращать текущую погоду, в зависимости от параметров(должны передаваться в конструкторе)
        info = requests.get(
            WeatherioProvider.API_CURRENT + city_name + f"&lang={language}" + WeatherioProvider.API_KEY)
        json_list = json.loads(info.text)["data"][0]
        string = f'humidity: {json_list.get("rh")}, temp: {json_list.get("temp")}, ' \
                 f'feels like: {json_list.get("app_temp")}, wind speed: {json_list.get("wind_spd")}, ' \
                 f'Pressure: {json_list.get("pres")}, description: {json_list.get("weather").get("description")}'
        return string



    @staticmethod
    def getForecast(city_name, language):
        # todo должен возвращать прогноз погоды, в зависимости от параметров(должны передаваться в конструкторе)
        info = requests.get(
            WeatherioProvider.API_FORECAST + city_name + f"&lang={language}" + WeatherioProvider.API_KEY)

