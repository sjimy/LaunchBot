from datetime import date, timedelta
import logging
import requests
from app.config import JH_HOLIDAY_URL, JH_HOLIDAY_KEY, JH_WEATHER_URL, JH_WEATHER_KEY, JH_WEATHER_CITY
from app.models import TodayInfo, WeatherInfo


def get_day_info(days=0) -> TodayInfo or None:
    try:
        queryDate = (date.today() + timedelta(days=days)).strftime("%Y-%m-%d")
        dbInfo = TodayInfo.get_or_none(TodayInfo.date == queryDate)
        if dbInfo:
            logging.info(f"day info from db, {queryDate}")
            return dbInfo
        url = JH_HOLIDAY_URL
        params = {
            "key": JH_HOLIDAY_KEY,
            "date": queryDate,
            "detail": 1
        }
        res = requests.get(url=url, params=params).json()
        if res['error_code'] == 0:
            result = res['result']
            todayInfo = TodayInfo()
            todayInfo.date = queryDate
            if 'statusDesc' in result:
                todayInfo.day_desc = result['statusDesc']
                todayInfo.is_off_day = todayInfo.day_desc != '工作日'
                todayInfo.is_holiday = todayInfo.day_desc == '节假日'
            if 'value' in result:
                todayInfo.holiday_name = result['value']
            if 'term' in result:
                todayInfo.term = result['term']
            if 'lunarMonth' in result:
                todayInfo.lunar_month = result['lunarMonth']
            if 'lunarDate' in result:
                todayInfo.lunar_date = result['lunarDate']
            todayInfo.save()
            return todayInfo
    except Exception as ex:
        logging.error(ex)
    return None


def get_tomorrow_weather_info() -> WeatherInfo or None:
    try:
        tomorrow_date = (date.today() + timedelta(days=1)).strftime("%Y-%m-%d")
        dbInfo = WeatherInfo.get_or_none(WeatherInfo.date == tomorrow_date)
        if dbInfo:
            logging.info(f"tomorrow weather from db, {tomorrow_date}")
            return dbInfo
        url = JH_WEATHER_URL
        params = {
            "key": JH_WEATHER_KEY,
            "city": JH_WEATHER_CITY
        }
        res = requests.get(url=url, params=params).json()
        if res['error_code'] == 0:
            city = res['result']['city']
            future_list = res['result']['future']
            if future_list and len(future_list) > 1:
                future = future_list[1]
                weather_info = WeatherInfo()
                weather_info.date = tomorrow_date
                weather_info.city = city
                weather_info.weather = future['weather']
                weather_info.temperature = future['temperature']
                weather_info.save()
                return weather_info
    except Exception as ex:
        logging.error(ex)
    return None
