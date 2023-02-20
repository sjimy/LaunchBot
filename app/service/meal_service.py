from app.config import START_TYPE_LUNCH, TRAIN_TICKETS_PRE_SALE_DATE, FS_CHAT_IDS, TRAIN_TICKETS_ENABLE
from app.service.feishu_service import get_tenant_access_token, send_fs_chat_msg
from app.service.juhe_service import get_day_info, get_tomorrow_weather_info
from app.service.weixin_service import get_today_menu_info


def send_meal_msg(meal_type):
    today_info = get_day_info(0)
    tomorrow_info = get_day_info(1)
    message = None
    menu_info = None
    if today_info:
        if tomorrow_info and tomorrow_info.term == "除夕":  # 除夕前一天已放假，不提醒
            pass
        elif today_info.is_off_day:  # 休息日
            if meal_type == START_TYPE_LUNCH:
                if today_info.term == "春节":
                    message = "祝福群里的小伙伴新的一年里身体健康，工作顺利，胃口好吃嘛嘛香"
            else:
                train_msg = get_tomorrow_buy_train_tickets_msg()
                if train_msg:
                    message = f"购票提醒，{train_msg}"
        else:  # 正常工作日提醒
            if meal_type == START_TYPE_LUNCH:
                message = "走，吃午饭去"
                if today_info.term and today_info.holiday_name:
                    message += f"，今天是{today_info.term}和{today_info.holiday_name}"
                elif today_info.term:
                    message += f"，今天是{today_info.term}"
                elif today_info.holiday_name:
                    message += f"，今天是{today_info.holiday_name}"
            else:
                message = "走，吃晚饭去"
                weather_info = get_tomorrow_weather_info()
                train_msg = get_tomorrow_buy_train_tickets_msg()
                if weather_info:
                    message += f"，明天{weather_info.weather} {weather_info.temperature}"
                    if tomorrow_info and tomorrow_info.is_off_day:
                        message += f"，明天是{tomorrow_info.day_desc}，要好好休息呀"
                    if train_msg:
                        message += f"，{train_msg}"
            menu_info = get_today_menu_info()
    if message:
        token = get_tenant_access_token()
        post_content = [
            [{"tag": "text", "text": message}]
        ]
        if menu_info:
            post_content[0].append({"tag": "text", "text": ", "})
            post_content[0].append({"tag": "a", "href": menu_info.url, "text": "今日菜单"})
        for chat_id in FS_CHAT_IDS:
            send_fs_chat_msg(token, chat_id, "", post_content)


# 火车票信息
def get_tomorrow_buy_train_tickets_msg():
    if not TRAIN_TICKETS_ENABLE:
        return None
    days = []
    start_day = TRAIN_TICKETS_PRE_SALE_DATE - 3
    end_day = TRAIN_TICKETS_PRE_SALE_DATE + 4
    for index in range(start_day, end_day):
        days.append(get_day_info(index))
    msg = None
    cur_day = days[3]
    if not cur_day.is_holiday and days[4].is_holiday:  # or days[5].is_holiday or days[6].is_holiday
        day = 0
        if days[4].is_holiday:
            day = 1
        # elif days[5].is_holiday:
        #    day = 2
        # elif days[6].is_holiday:
        #    day = 3
        msg = f"明天可买节日前{day}天的火车票"
    # elif not days[2].is_holiday and cur_day.is_holiday:
    #     msg = "明天可买节日第1天的火车票"
    # elif cur_day.is_holiday and not days[4].is_holiday:
    #     msg = "明天可买节日最后1天的火车票"
    # elif not cur_day.is_holiday and (days[2].is_holiday or days[1].is_holiday or days[0].is_holiday):
    #     day = 0
    #     if days[2].is_holiday:
    #         day = 1
    #     elif days[1].is_holiday:
    #         day = 2
    #     elif days[0].is_holiday:
    #         day = 3
    #     msg = f"明天可买节日后{day}天的火车票"
    return msg

