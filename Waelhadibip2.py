import threading
import time
import os
import random
from concurrent.futures import ThreadPoolExecutor, as_completed

ls = []
file = 'nasr1.txt'

def read_file():
    """قراءة البروكسيات من الملف مع تنظيف الأسطر الفارغة والتعليقات وإزالة التكرار."""
    try:
        if not os.path.isfile(file):
            return []
        lines = []
        seen = set()
        with open(file, 'r', encoding='utf-8', errors='ignore') as f:
            for raw in f.read().splitlines():
                line = raw.strip()
                if not line or line.startswith(("#", ";", "//")):
                    continue
                if line in seen:
                    continue
                seen.add(line)
                lines.append(line)
        return lines
    except FileNotFoundError:
        return []

def _normalize_proxy(line: str, default_scheme: str = "http") -> str:
    """
    يدعم صيغ:
      - http://host:port
      - https://user:pass@host:port
      - socks5://host:port
      - host:port
      - user:pass@host:port
      - host:port:user:pass  (بعض القوائم تكتبها هكذا)
      - user:pass:host:port
    """
    s = line.strip()

    if s.startswith(("http://", "https://", "socks5://", "socks4://")):
        return s

    s = s.replace(" ", "")

    if "@" in s and s.count(":") >= 2:
        return f"{default_scheme}://{s}"

    parts = s.split(":")
    if len(parts) == 2 and parts[1].isdigit():
        host, port = parts
        return f"{default_scheme}://{host}:{port}"

    if len(parts) == 4 and parts[3].isdigit():
        user, pwd, host, port = parts
        return f"{default_scheme}://{user}:{pwd}@{host}:{port}"

    if len(parts) == 4 and parts[1].isdigit():
        host, port, user, pwd = parts
        return f"{default_scheme}://{user}:{pwd}@{host}:{port}"

    return f"{default_scheme}://{s}"

def _to_requests_proxies(proxy_url: str) -> dict:
    """تهيئة dict مناسب لـ requests سواء http أو https أو socks."""
    return {"http": proxy_url, "https": proxy_url}

def _build_headers_minimal() -> dict:
    """
    هِدرز خفيفة بدون User-Agent حسب طلبك.
    تُبقي على accept-encoding واللغة والاتصال فقط.
    """
    return {
        "Accept-Encoding": "gzip, deflate",
        "Connection": "Keep-Alive",
        "Accept-Language": "en-US,en;q=0.8,ar;q=0.7",
    }

def process_line(line: str):
    """
    تُرجع (proxies, headers) للاستخدام لاحقًا بدون أي طباعة.
    """
    proxy_url = _normalize_proxy(line, default_scheme="http")
    proxies = _to_requests_proxies(proxy_url)
    headers = _build_headers_minimal()  
    return proxies, headers

def process_lines(lines):
    results = []
    if not lines:
        return results
    with ThreadPoolExecutor(max_workers=10) as executor:
        futures = [executor.submit(process_line, line) for line in lines]
        for future in as_completed(futures):
            results.append(future.result())
    return results

def update_file_loop():
    """
    حلقة تحديث مستمرة: تقرأ الملف كل 120 ثانية وتُجهّز النتائج للاستخدام لاحقًا.
    لا يوجد أي طباعة.
    """
    global ls
    while True:
        new_lines = read_file()
        ls = new_lines
        _ = process_lines(new_lines)
        time.sleep(120)

ls = read_file()
_ = process_lines(ls)

thread = threading.Thread(target=update_file_loop, daemon=True)
thread.start()
def afr(aweme_id,sessionid):
                    global tr,fa,er
                    proxies1=str(random.choice(ls))
                    _rticket = int(time.time() * 1000)
                    ts=str(int(time.time() * 1000))[:10]
                    from uuid import uuid4
                    uid=str(uuid4())
                    install_id = random.randrange(7334285683765348101, 7334285999999999999)
                    device_id=random.randrange(7283928371561793029, 7283929999999999999)
                    openudid = str(binascii.hexlify(os.urandom(8)).decode())
                    tz_name = random.choice(['America/New_York', 'Europe/London', 'Asia/Tokyo', 'Australia/Sydney', 'Asia/Kolkata', 'America/Los_Angeles', 'Europe/Paris', 'Asia/Dubai', 'America/Sao_Paulo', 'Asia/Shanghai'])
                    webcast_language = random.choice(['en', 'es', 'fr', 'de', 'ja', 'pt', 'it', 'ru', 'ar', 'hi'])
                    current_region = random.choice(['US', 'UK', 'CA', 'AU', 'IN', 'BR', 'FR', 'DE', 'IT', 'ES','AB'])
                    region = random.choice(['US', 'UK', 'CA', 'AU', 'IN', 'BR', 'FR', 'DE', 'IT', 'ES'])
                    screen_height = random.randint(600,1080)
                    screen_width = random.randint(800,1920)
                    samsung = ["SM-G975F","SM-G532G","SM-N975F","SM-G988U","SM-G977U","SM-A705FN","SM-A515U1","SM-G955F","SM-A750G","SM-N960F","SM-G960U","SM-J600F","SM-A908B","SM-A705GM","SM-G970U","SM-A307FN","SM-G965U1","SM-A217F","SM-G986B","SM-A207M","SM-A515W","SM-A505G","SM-A315G","SM-A507FN","SM-A505U1","SM-G977T","SM-A025G","SM-J320F","SM-A715W","SM-A908N","SM-A205F","SM-G988B","SM-N986B","SM-A715F","SM-A515F","SM-G965F","SM-G960F","SM-A505F","SM-A207F","SM-A307G","SM-G970F","SM-A107F","SM-G935F","SM-G935A","SM-A310F","SM-J320FN"]
                    oppo =['CPH2359','CPH2457','CPH2349','CPH2145','CPH2293','CPH2343','CPH2127','CPH2197','CPH2173','CPH2371','CPH2269','CPH2005','CPH2185']
                    realme=['RMX3501','RMX3085','RMX1921','RMX3771','RMX3461','RMX3092','RMX3393','RMX3392','RMX1821','RMX1825','RMX3310',]
                    phone=random.choice([samsung,oppo,realme])
                    type1=random.choice(phone)
                    if 'SM' in type1 :
                         brand='samsung'
                         dev=type1.split('-')[1]
                    if 'RMX' in type1:
                         brand='realme'
                         dev=type1.split('X')[1]
                    if 'CPH' in type1:
                         brand='OPPO'
                         dev=type1.split('H')[1]

                    off=int(round((datetime.datetime.now() - datetime.datetime.utcnow()).total_seconds()))
                    if aobsh == '1':
                         time1 = int(datetime.datetime.now().timestamp())
                         
                         reason=str(random.choice(sdsd))
                         pro1=urlencode({'WebIdLastTime': time1,
'aid': '1988', 
'app_language': 'de', 
'app_name': 'tiktok_web', 
'aweme_type':' 0', 
'browser_language':' de', 
'browser_name': 'Mozilla', 
'browser_online': 'true', 
'browser_platform': 'Win32', 
'channel':' tiktok_web', 
'cookie_enabled': 'true', 
'current_region': 'DE', 
'data_collection_enabled': 'true', 
'device_id': 'did', 
'device_platform': 'web_pc',
'focus_state': 'true',
'from_page': 'fyp',
'history_len': '2',
'is_fullscreen': 'false',
'is_page_visible': 'true',
'is_sub_only_video': '0',
'lang': 'ar',
'legal_jurisdiction': 'de',
'logout_reporter_email': '',
'nickname':  nickname,
'object_id': aweme_id,
'object_owner_id':id, 
'odinId': 'odinId', 
'os': 'windows',
'owner_id':  id, 
'screen_width': screen_width,
'lang': webcast_language,
'owner_id':id,
'object_id':aweme_id,
'iid':install_id,
'device_id':device_id,
'device_type':type1,
'device_brand':brand,
'language':webcast_language,
'openudid':openudid,
'_rticket':_rticket,
'current_region':current_region,
"object_id": aweme_id,
"device_id": device_id,
"object_owner_id": id,
"owner_id": id,
"reason": reason,
"target": aweme_id,
"owner_id":id,
'screen_height': screen_height,
'screen_width': screen_width,
'_rticket':_rticket,
'play_mode': 'one_column', 
   "US": "America/New_York",
    "CA": "America/Toronto",
    "GB": "Europe/London",
    "DE": "Europe/Berlin",
    "FR": "Europe/Paris",
    "IT": "Europe/Rome",
    "ES": "Europe/Madrid",
    "RU": "Europe/Moscow",
    "CN": "Asia/Shanghai",
    "JP": "Asia/Tokyo",
    "KR": "Asia/Seoul",
    "IN": "Asia/Kolkata",
    "BR": "America/Sao_Paulo",
    "MX": "America/Mexico_City",
    "AE": "Asia/Dubai",
    "SA": "Asia/Riyadh",
    "EG": "Africa/Cairo",
    "TR": "Europe/Istanbul",
    "AU": "Australia/Sydney",
    "NL": "Europe/Amsterdam",
    "SE": "Europe/Stockholm",
    "CH": "Europe/Zurich",
    "PL": "Europe/Warsaw",
    "NG": "Africa/Lagos",
    "ZA": "Africa/Johannesburg",
    "ID": "Asia/Jakarta",
    "TH": "Asia/Bangkok",
    "MY": "Asia/Kuala_Lumpur",
    "SG": "Asia/Singapore",
    "PH": "Asia/Manila",
    "PK": "Asia/Karachi",
    "AR": "America/Argentina/Buenos_Aires",
    "CO": "America/Bogota",
    "VE": "America/Caracas",
    "IR": "Asia/Tehran",
    "IQ": "Asia/Baghdad",
    "UA": "Europe/Kyiv",
    "BE": "Europe/Brussels",
    "AT": "Europe/Vienna",
    "DK": "Europe/Copenhagen",
    "NO": "Europe/Oslo",
    "FI": "Europe/Helsinki",
    "CZ": "Europe/Prague",
    "PT": "Europe/Lisbon",
    "HU": "Europe/Budapest",
    "GR": "Europe/Athens",
    "IL": "Asia/Jerusalem",
    "NZ": "Pacific/Auckland",
    "CA": "North America",
    "MX": "North America",
    "BR": "South America",
    "AR": "South America",
    "CO": "South America",
    "VE": "South America",
    "GB": "Europe",
    "DE": "Europe",
    "FR": "Europe",
    "IT": "Europe",
    "ES": "Europe",
    "RU": "Europe",
    "UA": "Europe",
    "BE": "Europe",
    "AT": "Europe",
    "NL": "Europe",
    "SE": "Europe",
    "CH": "Europe",
    "PL": "Europe",
    "CZ": "Europe",
    "DK": "Europe",
    "NO": "Europe",
    "FI": "Europe",
    "PT": "Europe",
    "HU": "Europe",
    "GR": "Europe",
    "CN": "Asia",
    "JP": "Asia",
    "KR": "Asia",
    "IN": "Asia",
    "AE": "Asia",
    "SA": "Asia",
    "IR": "Asia",
    "IQ": "Asia",
    "IL": "Asia",
    "ID": "Asia",
    "TH": "Asia",
    "MY": "Asia",
    "SG": "Asia",
    "PH": "Asia",
    "PK": "Asia",
    "EG": "Africa",
    "NG": "Africa",
    "ZA": "Africa",
    "NZ": "Oceania",
    "AU": "Oceania",
'reason': reason,
'referer':' ',
'region': 'de', 
'relevant_law': '', 
'report_desc':' ', 
'report_signature': '', 
'report_type': 'video',
'reporter_id': 'didd',
'screen_height': '1080', 
'screen_width': '1920', 
'submit_type': '1', 
'target': aweme_id,
'trusted_flagger_email': '', 
'tz_name':' Europe/Berlin', 
'user_is_login': 'true', 
'video_id': aweme_id, 
'video_owner': '[object Object]', 
'webcast_language': 'ar', 
'msToken': 'JcZGLqbVFNbTZCdJdKn5u3F-KQCo1RCDKZpx88q01_SKvnIqnunxRRdx1cT-_T0f1YamamErEI4xrmULvPFQ7ZIbHfwtNsy8EQGdhUQs25raLxLNny8_gnVvIpQudM861YvW9mt0Qv1LdQ==',
'X-Bogus': 'DFSzswVLFr0ANVSxCchLEKvVLFS5', 
'X-Gnarly':' M/G6B3TKwfeciheF/-jRLswpvDhkihTdWCiuhFAOmTWVVxOYJ13or1V8QDX/81vSJ/U-nnhvoA9yUhUxxenFNoJbkisqM7WrA/viUCABfuGuUZJ3KmmXHSYpcCOGldRUsYbhILNc83pK57Hcw03awplIDuXcUeppmNwbCKY1/AKlFyAStoqTzwY6Q7ujz5LlEtgt5UvsdRWfnMmkLv8n8fw5t1Q/pkZWLLQnYhzM9F-lndqfk1a-pLXJfRFR7DRTTDJvw2L3l94A',   
'aid': '1988', 
'app_language': 'ar', 
'app_name': 'tiktok_web', 
'aweme_type':' 0', 
'browser_language':' ar-EG', 
'browser_name': 'Mozilla', 
'browser_online': 'true', 
'browser_platform': 'Win32', 
'channel':' tiktok_web', 
'cookie_enabled': 'true', 
'current_region': 'DE', 
'data_collection_enabled': 'true', 
'device_id': 'did', 
'device_platform': 'web_pc',
'focus_state': 'true',
'from_page': 'fyp',
'history_len': '2',
'is_fullscreen': 'false',
'is_page_visible': 'true',
'is_sub_only_video': '0',
'lang': 'ar',
'legal_jurisdiction': 'no',
'logout_reporter_email': '',
'nickname':  nickname,
'object_id': aweme_id,
'object_owner_id':id, 
'odinId': 'odinId', 
'os': 'windows',
'owner_id':  id, 
'play_mode': 'one_column', 
'priority_region': 'DE',
'reason': reason,
'referer':' ',
'region': 'DE', 
'relevant_law': '', 
'report_desc':' ', 
'report_signature': '', 
'report_type': 'video',
'reporter_id': 'didd',
'screen_height': '1080', 
'screen_width': '1920', 
'submit_type': '1', 
'target': aweme_id,
'trusted_flagger_email': '', 
'tz_name':' Europe/Berlin', 
'user_is_login': 'true', 
'video_id': aweme_id, 
'video_owner': '[object Object]', 
'webcast_language': 'ar', 
'msToken': 'JcZGLqbVFNbTZCdJdKn5u3F-KQCo1RCDKZpx88q01_SKvnIqnunxRRdx1cT-_T0f1YamamErEI4xrmULvPFQ7ZIbHfwtNsy8EQGdhUQs25raLxLNny8_gnVvIpQudM861YvW9mt0Qv1LdQ==',
'X-Bogus': 'DFSzswVLFr0ANVSxCchLEKvVLFS5', 
'X-Gnarly':' M/G6B3TKwfeciheF/-jRLswpvDhkihTdWCiuhFAOmTWVVxOYJ13or1V8QDX/81vSJ/U-nnhvoA9yUhUxxenFNoJbkisqM7WrA/viUCABfuGuUZJ3KmmXHSYpcCOGldRUsYbhILNc83pK57Hcw03awplIDuXcUeppmNwbCKY1/AKlFyAStoqTzwY6Q7ujz5LlEtgt5UvsdRWfnMmkLv8n8fw5t1Q/pkZWLLQnYhzM9F-lndqfk1a-pLXJfRFR7DRTTDJvw2L3l94A',
 

                              '_signature': '_02B4Z6wo00001qvYUFwAAIDArHJl-y89yw6r2FTAAMyOac',})
                         url='https://www.tiktok.com/aweme/v2/aweme/feedback/?%s'%(pro1)

                         url='https://www.tiktok.com/aweme/v2/aweme/feedback/?%s'%(pro1)

                         h={

                              'Cookie': f'ttwid={ttwid}; sid_tt='+sessionid+'; sessionid='+sessionid+'; sessionid_ss='+sessionid+';',

                               'Referer': 'https://www.tiktok.com/@'+g+'/video/'+aweme_id,

                              'Sec-Fetch-Site': 'same-origin',

                              'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',}
                         
                    if aobsh == '2':
                         if xxx == '14': 
                              pro=urlencode({
                              'logout_reporter_email':'',
                              'reason':'9013',
                              'enter_from':'homepage_hot',
                              'owner_id':id,
                              'report_type':'video',
                              'object_id':aweme_id,
                              'no_hw':'1',
                              'submit_type':'1',
                              'isFirst':'1',
                              'trusted_flagger_email':'',
                              'report_signature':f'{names.get_last_name()} {names.get_last_name()} {names.get_last_name()}',
                              'extra_log_params':'%7B%22last_from_group_id%22%3A%22'+aweme_id+'%22%2C%22is_ecom%22%3A%220%22%7D',
                              'category':'',
                              'legal_jurisdiction':'dk',
                              'iid':install_id,
                              'device_id':device_id,
                              'ac':'wifi',
                              'channel':'googleplay',
                              'aid':'1233',
                              'app_name':'musical_ly',
                              'version_code':'330304',
                              'version_name':'33.3.4',
                              'device_platform':'android',
                              'os':'android',
                              'ab_version':'33.3.4',
                              'ssmix':'a',
                              'device_type':type1,
                              'device_brand':brand,
                              'language':webcast_language,
                              'os_api':'28',
                              'os_version':'9',
                              'openudid':openudid,
                              'manifest_version_code':'2023303040',
                              'resolution':f'{screen_width}*{screen_height}',
                              'dpi':'191',
                              'update_version_code':'2023303040',
                              '_rticket':_rticket,
                              'is_pad':'0',
                              'current_region':current_region,
                              'app_type':'normal',
                              'sys_region':region,
                              'mcc_mnc':'21890',
                              'timezone_name':tz_name,
                              'residence':current_region,
                              'app_language':webcast_language,
                              'carrier_region':current_region,
                              'ac2':'wifi',
                              'uoo':'0',
                              'op_region':current_region,
                              'timezone_offset':off,
                              'build_number':'33.3.4',
                              'host_abi':'arm64-v8a',
                              'locale':webcast_language,
                              'region':region,
                              'ts':ts,
                              'cdid':uid})
                              
                         else:
                              pro=urlencode({
                              'enter_from':'homepage_hot',
                              'owner_id':id,
                              'report_type':'video',
                              'object_id':aweme_id,
                              'uri':'',
                              'no_hw':'1',
                              'current_video_play_time':'12',
                              'isFirst':'1',
                              'extra_log_params':'%7B%22last_from_group_id%22%3A%22'+aweme_id+'%22%2C%22is_ecom%22%3A%220%22%7D',
                              'report_desc':'',
                              'category':'',
                              'iid':install_id,
                              'device_id':device_id,
                              'ac':'wifi',
                              'channel':'googleplay',
                              'aid':'1233',
                              'app_name':'musical_ly',
                              'version_code':'330304',
                              'version_name':'33.3.4',
                              'device_platform':'android',
                              'os':'android',
                              'ab_version':'33.3.4',
                              'ssmix':'a',
                              'device_type':type1,
                              'device_brand':brand,
                              'language':webcast_language,
                              'os_api':'28',
                              'os_version':'9',
                              'openudid':openudid,
                              'manifest_version_code':'2023303040',
                              'resolution':f'{screen_width}*{screen_height}',
                              'dpi':'191',
                              'update_version_code':'2023303040',
                              '_rticket':_rticket,
                              'is_pad':'0',
                              'current_region':current_region,
                              'app_type':'normal',
                              'sys_region':region,
                              'mcc_mnc':'21890',
                              'timezone_name':tz_name,
                              'residence':current_region,
                              'app_language':webcast_language,
                              'carrier_region':current_region,
                              'ac2':'wifi',
                              'uoo':'0',
                              'op_region':current_region,
                              'timezone_offset':off,
                              'build_number':'33.3.4',
                              'host_abi':'arm64-v8a',
                              'locale':webcast_language,
                              'region':region,
                              'ts':ts,
                              'cdid':uid})
                         u='https://api22-normal-c-useast1a.tiktokv.com/aweme/v2/aweme/feedback/?'
                         url = u+pro
                         payload = f''
                         signed = ttsign(url.split('?')[1], payload, None).get_value()
                         x_gorgon=signed['x-gorgon']
                         x_khronos=signed['x-khronos']
                         xss=signed['x-ss-req-ticket']
                         
                         h={
                         'Cookie':
                         f'sid_tt={sessionid}; sessionid={sessionid}; sessionid_ss={sessionid};',
                        
                         'User-Agent' :f'com.zhiliaoapp.musically/2023306030 (Linux; U; Android 12; {region}; {type1}; Build/NRD90M.{dev}KSU1AQDC;tt-ok/3.12.13.4-tiktok)',#SM-G955N
     
                         'X-Gorgon':x_gorgon,
                         'X-Khronos':x_khronos,
                         'X-SS-REQ-TICKET':xss,
                    }
                    try:
                         r=requests.get(url,headers=h,proxies={'https': f'socks5://{str(random.choice(ls))}','https': f'socks4://{str(random.choice(ls))}','https': f'http://{str(random.choice(ls))}'}).text
                         tr+=1
                         if aweme_id in soso:
                              pass
                         else:
                              soso.append(aweme_id)
                         if sessionid in loop:
                              pass
                         else:
                              loop.append(sessionid)
                         bi = random.choice([F,J,Z,C,B,L,J1,J2,J21,J22,F1,C1,P1])
                         print(bi+f"\r {len(soso)}/{len(tar)} True :{F}[{tr}] {bi}Net :{Z}[{fa}]{bi} {len(loop)}/{len(sisn)}",end=" ");sys.stdout.flush()
                    except:
                         fa +=1
                         bi = random.choice([F,J,Z,C,B,L,J1,J2,J21,J22,F1,C1,P1])
                         print(bi+f"\r {len(soso)}/{len(tar)} True :{F}[{tr}] {bi}Net :{Z}[{fa}]{bi} {len(loop)}/{len(sisn)}",end=" ");sys.stdout.flush()
          

# -*- coding: utf-8 -*-
# NASR — TikTok AR • Per-Session Report Selection • Lists fixed & cleaned

# -*- coding: utf-8 -*-
# NASR — TikTok AR • Per-Session, No-Miss ID Processing with Retries

import os, re, time, sys, threading, gc, random
from concurrent.futures import ThreadPoolExecutor, as_completed
from queue import Queue, Empty
