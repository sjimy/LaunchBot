from peewee import Model, CharField, BooleanField, IntegerField, SqliteDatabase

_client_db = SqliteDatabase('info.db')


class BaseModel(Model):
    class Meta:
        database = _client_db


class TodayInfo(BaseModel):
    date = CharField(default="")  # 日期
    is_off_day = BooleanField(default=False)  # 是否休息日
    is_holiday = BooleanField(default=False)  # 是否节假日
    holiday_name = CharField(default="")  # 节假日名称
    term = CharField(default="")  # 节气
    day_desc = CharField(default="")  # 工作日、周末、节假日
    lunar_month = IntegerField(default=0)  # 农历月
    lunar_date = IntegerField(default=0)  # 农历日


class WeatherInfo(BaseModel):
    date = CharField(default="")  # 日期
    city = CharField(default="")  # 城市
    temperature = CharField(default="")  # 温度
    weather = CharField(default="")  # 天气


class MenuInfo(BaseModel):
    date = CharField(default="")  # 日期
    url = CharField(default="")  # 城市


def init_db():
    _client_db.connect()
    _client_db.create_tables([TodayInfo, WeatherInfo, MenuInfo])
