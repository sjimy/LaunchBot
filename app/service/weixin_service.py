import hashlib
from datetime import datetime
from urllib.parse import urlencode, quote
import requests
from app.models import MenuInfo

sogou_headers = {
    "User-Agent": "Mozilla/5.0 (Linux; Android 6.0; Nexus 5 Build/MRA58N) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/103.0.0.0 Mobile Safari/537.36",
    "Host": "weixin.sogou.com",
    "Cookie": "ssuid=1440888632; SUID=6F73243B3822910A0000000062163639; IPLOC=CN1100; ABTEST=7|1657790000|v1; weixinIndexVisited=1; SUV=00232D5B6A25BB8462CFDE31A88F5271; SNUID=C4FB642B4044A281118F952D41DA37AB; JSESSIONID=aaa7yuXUqHqYMcud0D6dy; ariaDefaultTheme=undefined"
}


def get_today_menu_info() -> MenuInfo or None:
    today = datetime.now()
    address = "昌一"
    data_str = f"{today.year}.{today.month}.{today.day}"
    host = "https://weixin.sogou.com"

    # dbInfo = MenuInfo.get_or_none(MenuInfo.date == data_str)
    # if dbInfo:
    #     logging.info(f"menu info from db, {data_str}")
    #     return dbInfo

    url = None
    for page in range(1, 5):
        query = urlencode({
            "type": "2",
            "s_from": "input",
            "query": f"{address} {data_str} MENU",
            "page": f"{page}"
        })
        request_url = f"{host}/weixin?" + query
        print(f"request_url: {request_url}")
        res = requests.get(request_url, headers=sogou_headers)
        res.encoding = "utf-8"
        if res.status_code != 200:
            return None
        content = res.text
        if "异常访问请求" in content:
            print("访问搜狗查询异常")
            return None
        break_page = False
        for title_index in range(0, 9):
            key_index = content.find(f"article_title_{title_index}")
            if key_index == -1:
                break_page = True
                break
            title = content[key_index:key_index + 150]
            if address in title and data_str in title:
                url = content[key_index - 600:key_index]
                break_page = True
                break
        if break_page:
            break
    if not url:
        return None
    # print(url)
    url = url[url.find("href=\"") + 6:]
    # print(url)
    url = url[:url.find("\"")]
    # print(url)
    url = url.replace("amp;", "")
    url = quote(url, safe='/:?=&', encoding='utf-8')
    if not url or len(url) < 20:
        return None
    redirect_url = f"{host}{url}"

    print(f"redirect_url: {redirect_url}")
    res = requests.get(redirect_url, headers=sogou_headers)
    res.encoding = "utf-8"
    if res.status_code != 200:
        return None
    content_list = res.text.split('\r\n')
    final_url = ""
    for line in content_list:
        if "url +=" in line:
            item = line.replace("url += \'", "").replace("\';", "").strip()
            final_url += item
    if not final_url or len(final_url) < 20:
        return None
    final_url = final_url.replace("@", "")

    print(f"final_url: {final_url}")
    short_url = get_short_url(final_url)
    if short_url is None:
        return None

    print(f"short_url: {short_url}")
    menu_info = MenuInfo()
    menu_info.date = data_str
    menu_info.url = short_url
    menu_info.save()
    return menu_info


def get_short_url(long_url):
    nonce_key = long_url + "joigJIGRFyhr&*5hjIGJHKgirHU%$*gngfgfdfg"
    nonce = hashlib.md5(nonce_key.encode()).hexdigest().upper()
    res = requests.post("http://internal.mij.cc/internal/postShort", json={
        "orignalUrl": long_url,
        "expireTime": "0",
        "config": "mishop",
        "nonce": nonce
    })
    if res.status_code != 200:
        return None
    return res.text
