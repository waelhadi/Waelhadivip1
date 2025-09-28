import os
import re
import sys
import time
import json
import random
import threading
import hashlib
import datetime
import binascii
import secrets
import queue
from collections import deque
from urllib.parse import urlencode
from concurrent.futures import ThreadPoolExecutor, as_completed

import requests
import names
import pyfiglet
from termcolor import colored
from colorama import init, Fore, Style

import os, re, json, time, random, threading, queue
from collections import deque

OUTPUT_FILE          = "3.txt"
IMMEDIATE_SAVE_FLUSH = True
REQUEST_TIMEOUT      = 10
RETRY_TOTAL          = 2
UI_REFRESH_SEC       = 0.25
USE_PROXIES          = True

TIKWM_INFO_URL  = "https://www.tikwm.com/api/user/info"
TIKWM_POSTS_URL = "https://www.tikwm.com/api/user/posts"

BR = "\033[1m"
R  = "\033[91m"+BR
G  = "\033[92m"+BR
Y  = "\033[93m"+BR
B  = "\033[94m"+BR
M  = "\033[95m"+BR
C  = "\033[96m"+BR
W  = "\033[97m"+BR
RS = "\033[0m"

def bar(val, vmax, width=30):
    vmax = max(1, int(vmax)); val = max(0, min(int(val), vmax))
    fill = int(width * (val/float(vmax)))
    return "█"*fill + "░"*(width-fill)

try:
    import pyfiglet
except ImportError:
    os.system("pip install pyfiglet >/dev/null 2>&1")
    import pyfiglet

def tiktok_logo_big():
    ascii_banner = pyfiglet.figlet_format("TIKTOK", font="slant")
    lines = ascii_banner.splitlines()
    colors = [C, M, W] 
    colored = []
    for i, line in enumerate(lines):
        col = colors[i % len(colors)]
        colored.append(f"{col}{line}{RS}")
    return "\n".join(colored)

def load_proxies(path="nasr1.txt"):
    arr=[]
    try:
        with open(path,"r",encoding="utf-8") as f:
            for ln in f:
                p=ln.strip()
                if p and not p.startswith("#"): arr.append(p)
    except FileNotFoundError:
        pass
    return arr
PROXIES = load_proxies("nasr1.txt")
def pick_proxy():
    if not (USE_PROXIES and PROXIES): return None
    return random.choice(PROXIES)

_write_q = queue.Queue(maxsize=200000)
_stop_writer = threading.Event()
_seen = set()

def writer_thread(path):
    f = open(path,"a",encoding="utf-8",buffering=1)
    try:
        while not _stop_writer.is_set():
            try: vid = _write_q.get(timeout=0.25)
            except queue.Empty: continue
            f.write(vid+"\n")
            if IMMEDIATE_SAVE_FLUSH: f.flush()
    finally:
        try: f.flush()
        except: pass
        f.close()

def save_id(vid: str):
    if not (vid and vid.isdigit()): return False
    if vid in _seen: return False
    _seen.add(vid)
    try:
        _write_q.put_nowait(vid)
        return True
    except queue.Full:
        return False

def load_existing_ids():
    try:
        with open(OUTPUT_FILE,"r",encoding="utf-8") as f:
            for ln in f:
                s = ln.strip()
                if s.isdigit(): _seen.add(s)
    except FileNotFoundError:
        pass

try:
    import requests
except ImportError:
    os.system("pip install requests >/dev/null 2>&1")
    import requests

def jget(url, headers=None, params=None, timeout=REQUEST_TIMEOUT, proxy=None):
    for attempt in range(1, RETRY_TOTAL+2):
        try:
            r = requests.get(url, headers=headers, params=params, timeout=timeout,
                             proxies={"http":proxy,"https":proxy} if proxy else None)
            if r.ok:
                try: return r.json()
                except: return {}
        except Exception:
            if attempt==RETRY_TOTAL+1: return {}
            time.sleep(0.25*attempt + random.uniform(0,0.2))
    return {}

def tget(url, headers=None, params=None, timeout=REQUEST_TIMEOUT, proxy=None):
    for attempt in range(1, RETRY_TOTAL+2):
        try:
            r = requests.get(url, headers=headers, params=params, timeout=timeout,
                             proxies={"http":proxy,"https":proxy} if proxy else None)
            if r.ok: return r.text
        except Exception:
            if attempt==RETRY_TOTAL+1: return ""
            time.sleep(0.25*attempt + random.uniform(0,0.2))
    return ""

def parse_ids_from_text(text, push):
    if not text: return 0
    got = 0
    for m in re.finditer(r'/video/(\d+)', text):
        if push(m.group(1)): got += 1
    for m in re.finditer(r'"aweme_id"\s*:\s*"(\d+)"', text):
        if push(m.group(1)): got += 1
    return got

def mirror_pull_user(username, push):
    proxy = pick_proxy()
    total = 0
    for base in ("www.tiktok.com","m.tiktok.com"):
        url = f"https://r.jina.ai/http://{base}/@{username}"
        text = tget(url, headers={"User-Agent":"curl/8.5"}, proxy=proxy)
        total += parse_ids_from_text(text, push)
    return total

def tikwm_user_info(username):
    proxy = pick_proxy()
    j = jget(TIKWM_INFO_URL, params={"unique_id":username}, proxy=proxy)
    if j.get("code")==0:
        data = j.get("data") or {}
        return data.get("sec_uid"), data
    return None, {}

def tikwm_posts_by_unique(username, cursor=0, count=200):
    proxy = pick_proxy()
    return jget(TIKWM_POSTS_URL, params={"unique_id":username, "count":str(count), "cursor":str(cursor)}, proxy=proxy)

def tikwm_posts_by_secuid(sec_uid, cursor=0, count=200):
    proxy = pick_proxy()
    return jget(TIKWM_POSTS_URL, params={"sec_uid":sec_uid, "count":str(count), "cursor":str(cursor)}, proxy=proxy)

STATS_LOCK = threading.Lock()
RATE_HIST  = deque(maxlen=600)
START_TS   = time.time()
GLOBAL = {
    "total_found": 0,
    "saved_new":   0,
    "users_total": 0,
    "users_done":  0,
    "per_user":    {}
}
STOP_UI = threading.Event()

def stats_init_user(username):
    with STATS_LOCK:
        GLOBAL["per_user"][username] = {"state":"init","pages":0,"last_got":0,"total":0,"cursor":0,"src":"-"}

def stats_update_user(username, **kw):
    with STATS_LOCK:
        u = GLOBAL["per_user"].get(username, {})
        u.update(kw)
        GLOBAL["per_user"][username] = u

def stats_add_ids(username, ids_count, cursor, src):
    with STATS_LOCK:
        u = GLOBAL["per_user"].get(username, {})
        u["last_got"] = ids_count
        u["total"]    = u.get("total",0) + ids_count
        u["cursor"]   = cursor
        u["src"]      = src
        GLOBAL["per_user"][username] = u
        GLOBAL["total_found"] += ids_count
        GLOBAL["saved_new"]   = len(_seen)
        RATE_HIST.append((time.time(), GLOBAL["total_found"]))

def stats_mark_done(username):
    with STATS_LOCK:
        GLOBAL["users_done"] += 1
        u = GLOBAL["per_user"].get(username, {})
        u["state"]="done"; GLOBAL["per_user"][username]=u

def rate_now_and_avg10s():
    with STATS_LOCK:
        t  = time.time(); tot= GLOBAL["total_found"]; RATE_HIST.append((t, tot))
        if len(RATE_HIST)>=2:
            (t1,v1)=RATE_HIST[-1]; (t0,v0)=RATE_HIST[-2]
            dt=max(1e-6,t1-t0); r_now=(v1-v0)/dt
        else: r_now=0.0
        t_cut=t-10; v_old=None; t_old=None
        for (tx,vx) in reversed(RATE_HIST):
            if tx<=t_cut: v_old=vx; t_old=tx; break
        if v_old is None and RATE_HIST:
            t_old, v_old = RATE_HIST[0]
        dt10=max(1e-6,t-t_old) if t_old else 1.0
        r_avg=(tot-(v_old or 0))/dt10
        return r_now, r_avg

def banner():
    line = "─"*64
    return f"{C}{line}{RS}\n{tiktok_logo_big()}\n{C}{line}{RS}"

def ui_draw():
    try: print("\x1b[H\x1b[2J", end="")
    except: pass
    print(banner())
    elapsed = time.time() - START_TS
    h=int(elapsed//3600); m=int((elapsed%3600)//60); s=int(elapsed%60)
    r_now, r_avg = rate_now_and_avg10s()
    with STATS_LOCK:
        tf = GLOBAL["total_found"]; sv = GLOBAL["saved_new"]
        ud = GLOBAL["users_done"];  ut = GLOBAL["users_total"]
        per = dict(GLOBAL["per_user"])
    print(f"{M}⏱ Time:{RS} {Y}{h:02d}:{m:02d}:{s:02d}{RS}  {C}Now:{RS} {W}{r_now:5.1f}{RS} id/s  {C}Avg(10s):{RS} {W}{r_avg:5.1f}{RS} id/s")
    print(f"{G}Total IDs:{RS} {W}{tf}{RS}   {G}Saved:{RS} {W}{sv}{RS}   {B}Users:{RS} {W}{ud}/{ut}{RS}")
    print(f"{Y}Progress {RS}|{bar(sv, max(tf,1), 42)}| {sv}/{tf}")
    print(f"{C}{'─'*94}{RS}")
    print(f"{W}{'Username':<20}{'State':<10}{'Pages':<8}{'Last':<8}{'Total':<8}{'Cursor':<10}{'Source':<12}{RS}")
    print(f"{C}{'─'*94}{RS}")
    rows = sorted(per.items(), key=lambda kv: kv[1].get("total",0), reverse=True)
    for uname, st in rows:
        state = st.get("state","-"); pages=st.get("pages",0); last=st.get("last_got",0)
        totu  = st.get("total",0);   cur  = st.get("cursor",0); src = st.get("src","-")
        col = G if state=="done" else (Y if state in ("run","tikwm","jina") else M)
        print(f"{W}{uname:<20}{col}{state:<10}{RS}{W}{pages:<8}{last:<8}{totu:<8}{cur:<10}{src:<12}{RS}")
    print()

def ui_loop():
    while not STOP_UI.is_set():
        ui_draw()
        time.sleep(UI_REFRESH_SEC)

def pull_with_tikwm(username):
    stats_update_user(username, state="tikwm", pages=0, last_got=0, total=0, cursor=0, src="tikwm-uid")
    total = 0
    cursor = 0
    while True:
        j = tikwm_posts_by_unique(username, cursor=cursor, count=200)
        if j.get("code") != 0: break
        data = j.get("data") or {}
        vids = data.get("videos") or []
        got = 0
        for v in vids:
            aw = v.get("video_id") or v.get("aweme_id") or v.get("id")
            if aw and str(aw).isdigit():
                if save_id(str(aw)): got += 1
        total += got
        has_more = int(data.get("hasMore") or data.get("has_more") or 0)
        cursor   = int(data.get("cursor") or 0)
        with STATS_LOCK:
            pu = GLOBAL["per_user"][username]; pu["pages"] += 1
        stats_add_ids(username, got, cursor, "tikwm-uid")
        if not has_more or got==0: break
    sec_uid, _ = tikwm_user_info(username)
    if sec_uid:
        cursor=0
        while True:
            j = tikwm_posts_by_secuid(sec_uid, cursor=cursor, count=200)
            if j.get("code") != 0: break
            data = j.get("data") or {}
            vids = data.get("videos") or []
            got = 0
            for v in vids:
                aw = v.get("video_id") or v.get("aweme_id") or v.get("id")
                if aw and str(aw).isdigit():
                    if save_id(str(aw)): got += 1
            total += got
            has_more = int(data.get("hasMore") or data.get("has_more") or 0)
            cursor   = int(data.get("cursor") or 0)
            with STATS_LOCK:
                pu = GLOBAL["per_user"][username]; pu["pages"] += 1
            stats_add_ids(username, got, cursor, "tikwm-sec")
            if not has_more or got==0: break
    return total

def pull_with_mirror(username):
    stats_update_user(username, state="jina", src="jina")
    got = mirror_pull_user(username, lambda vid: save_id(vid))
    stats_add_ids(username, got, 0, "jina")
    return got

def process_user(username):
    stats_init_user(username)
    total = pull_with_tikwm(username)
    if total == 0:
        total += pull_with_mirror(username)
    stats_mark_done(username)
    return total

def main():
    if os.path.exists(OUTPUT_FILE):
        ch = input(f"{Y}Clear {OUTPUT_FILE} before starting? (y/N): {RS}").strip().lower()
        if ch in ("y","yes"):
            open(OUTPUT_FILE,"w",encoding="utf-8").close()
            print(f"{G}[✓]{RS} File cleared.")
    load_existing_ids()
    try:
        n = int(input(f"{W}Enter number of usernames: {RS}").strip())
    except:
        print(f"{R}Invalid number.{RS}"); return
    users = []
    for i in range(n):
        u = input(f"{C}Username #{i+1} (without @): {RS}").strip().lstrip("@")
        if u: users.append(u)
    if not users:
        print(f"{R}No usernames provided.{RS}"); return
    with STATS_LOCK:
        GLOBAL["users_total"] = len(users)
    wt  = threading.Thread(target=writer_thread, args=(OUTPUT_FILE,), daemon=True); wt.start()
    uit = threading.Thread(target=ui_loop, daemon=True); uit.start()
    grand = 0
    for u in users:
        print(f"{W}[>] @{u}{RS} — starting …")
        got = process_user(u)
        print(f"{C}[=] @{u}{RS} — collected {G}{got}{RS} IDs")
        grand += got
    time.sleep(0.3); STOP_UI.set(); time.sleep(0.2); _stop_writer.set(); time.sleep(0.2)
    print("\n" + "═"*60)
    print(f"{G}Done — new total collected: {grand}{RS}")

if __name__ == "__main__":
    main()
import requests,random,datetime,binascii,os,threading,names,secrets,sys
import hashlib
import json
import time
from urllib.parse   import urlencode
import requests,sys,os,time
import requests
import sys
import time
import pyfiglet
from termcolor import colored
from colorama import init, Fore, Style
import requests
from colorama import init, Fore
import re
session = requests.Session()
soso = []
loop = []
tar = []
x_ = []
ls = []
sisn = []  




import os, sys, time, requests
from colorama import init, Fore, Style
init(autoreset=True)

ACCENT1 = Fore.CYAN + Style.BRIGHT   # سماوي
ACCENT2 = Fore.RED  + Style.BRIGHT   # قرمزي
TEXT    = Fore.WHITE + Style.NORMAL
TITLE   = Fore.WHITE + Style.BRIGHT

BAR      = "──────────────────────────────────────────────────────────────────────────────"
WIDE_BAR = "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

session = requests.Session()
soso, loop, tar, x_, ls, sisn = [], [], [], [], [], []

def clear_screen():
    os.system('cls' if os.name == 'nt' else 'clear')

def print_tiktok_logo():
    logo_red = [
        "           ████        ",
        "         ████████      ",
        "        ███    ███     ",
        "        ███            ",
        "        ███   ██████   ",
        "         ███████  ███  ",
        "              ███ ███  ",
    ]
    logo_cyan = [
        "            ████       ",
        "          ████████     ",
        "         ███    ███    ",
        "         ███           ",
        "         ███   ██████  ",
        "          ███████  ███ ",
        "               ███ ███ ",
    ]
    for ln in logo_red:  print(ACCENT2 + " " + ln + Style.RESET_ALL)
    for ln in logo_cyan: print(ACCENT1 + ln + Style.RESET_ALL)
    print(TITLE + "[ NASR // TikTok Reports ]" + Style.RESET_ALL)
    print(TEXT + BAR + Style.RESET_ALL)

def print_lists_only():
    print(TITLE + "[ فئة البلاغات الحساسة والقانونية (1 → 33) ]" + Style.RESET_ALL)
    group_a = [
        (1,  "المحتوى عبارة عن مادة اعتداء جنسي على الأطفال"),
        (2,  "عرض توريد مواد الاعتداء الجنسي على الأطفال وبيعها وتوزيعها"),
        (3,  "المحتوى المتعلق باستمالة طفل أو إغواءه جنسيًا"),
        (4,  "التهديد بالعنف/التحريض على ارتكاب جريمة (جرائم) إرهابية"),
        (5,  "المحتوى المتعلق بالتجنيد والتمويل ودعم الإرهاب"),
        (6,  "تعليمات أو تدريب حول كيفية صنع المتفجرات/الأسلحة/الأسلحة النارية (لأغراض إرهابية)"),
        (7,  "خطاب الكراهية غير القانوني"),
        (8,  "تصوير العنف بشع المنظر"),
        (9,  "المشاركة في منظمة إجرامية"),
        (10, "انتهاكات الخصوصية القائمة على الصور"),
        (11, "انتحال الهوية بشكل غير قانوني"),
        (12, "انتهاكات أخرى للخصوصية"),
        (13, "مشاركة الصور الحميمة أو الخاصة دون موافقة"),
        (14, "المحتوى المرتبط بالاتجار بالبشر (الإعلانات، والمزيد)"),
        (15, "الترويج للدعارة/الاستدراج"),
        (16, "إنتاج العقاقير/المخدرات غير المشروعة أو بيعها أو توريدها أو توزيعه"),
        (17, "المحتوى الذي يروّج للصيد الجائر أو الاتجار غير المشروع بالأحياء البرية"),
        (18, "الاتجار غير المشروع بالأسلحة"),
        (19, "السلع غير القانونية الأخرى"),
        (20, "المضايقات أو التهديدات"),
        (21, "التشهير"),
        (22, "خرق قانون المستهلك"),
        (23, "المنتجات/البضائع غير الآمنة أو الخطر"),
        (24, "التضليل الجنائي"),
        (25, "ازدراء المحكمة أو خرق أمر المحكمة أو التصريح غير القانوني"),
        (26, "إعطاء تعليمات/تشجيع يتعلق بالانتحار"),
        (27, "الاحتيال"),
        (28, "غسيل الأموال"),
        (29, "الابتزاز/الرشوة"),
        (30, "الجرائم المتعلقة بالأمن القومي (الخيانة والتجسس والتخريب وتعريض الأمن الداخلي أو الخارجي للخطر"),
        (31, "محتوى غير قانوني آخر"),
        (32, "عشوائي قانون الأوربي"),
        (33, "بلاغ النسر"),
    ]
    for n, label in group_a:
        print(ACCENT1 + f"  {n:>2} | " + TEXT + label)

    print(TEXT + BAR + Style.RESET_ALL)
    print(TITLE + "[ فئة البلاغات العامة والمساعدة (34 → 63) ]" + Style.RESET_ALL)
    group_b = [
        (34, "بلاغ: الكلام الذي يحض على الكراهية والسلوكيات البغيضة"),
        (35, "بلاغ: لقد تعرضت بنفسي للتنمر أو المضايقة"),
        (36, "تعرض شخص أعرفه للتنمر أو المضايقة "),
        (37, "تعرض أحد المشاهير أو المسؤولين الحكوميين للتنمر أو المضايقة "),
        (38, "تعرض آخرون للتنمر أو المضايقة "),
        (39, "الانتحار وإيذاء النفس"),
        (40, "اضطرابات الأكل وصورة الجسم غير الصحية"),
        (41, "الأنشطة والتحديات الخطرة"),
        (42, "النشاط الجنسي للشباب والاستدراج الجنسي والاستغلال الجنسي"),
        (43, "السلوك الموحي جنسيًا بواسطة الشباب"),
        (44, "النشاط الجنسي للبالغين والخدمات الجنسية والاستدراج الجنسي"),
        (45, "عُري البالغين"),
        (46, "اللغة الجنسية الفاحشة"),
        (47, "المحتوى صادم وبشع المنظر"),
        (48, "معلومات خاطئة عن الانتخابات "),
        (49, "معلومات ضارة مضللة "),
        (50, "التزييف العميق والوسائط التركيبية والوسائط التي تم التلاعب بها"),
        (51, "التفاعل الزائف"),
        (52, "مزعج"),
        (53, "المقامرة"),
        (54, "الكحول والتبغ والمخدرات"),
        (55, "الأسلحة النارية والأسلحة الخطرة"),
        (56, "تجارة السلع والخدمات الأخرى الخاضعة للإرشادات التنظيمية "),
        (57, "الغش والاحتيال"),
        (58, "مشاركة المعلومات الشخصية "),
        (59, "اشتباه في انتهاك الملكية الفكرية لآخرين"),
        (60, "محتوى مرتبط بعلامة تجارية غير معلن عنه "),
        (61, "آخر"),
        (62, "ثغرة رقم 1"),
        (63, "عشوائي عربي"),
    ]
    for n, label in group_b:
        print(ACCENT1 + f"  {n:>2} | " + TEXT + label)

    print(TEXT + BAR + Style.RESET_ALL)

file_path = "1.txt"
if os.path.isfile(file_path):
    with open(file_path, 'r', encoding="utf-8") as f:
        sisn = [line.strip() for line in f if line.strip()]
else:
    sisn = []

GREEN = "\033[92m"
RED = "\033[91m"
TURQUOISE = "\033[38;5;45m"
RESET = "\033[0m"

q1 = sorted(['950111'])
q2 = sorted(['950112'])
q3 = sorted(['950113'])
q4 = sorted(['950121'])
q5 = sorted(['950122'])
q6 = sorted(['950123'])
q7 = sorted(['95013'])
q8 = sorted(['950141'])
q9 = sorted(['950142'])
q10 = sorted(['950151'])
q11 = sorted(['950152'])
q12 = sorted(['950153'])
q13 = sorted(['95016'])
q14 = sorted(['950171'])
q15 = sorted(['950172'])
q16 = sorted(['950173'])
q17 = sorted(['950174'])
q18 = sorted(['950175'])
q19 = sorted(['950176'])
q20 = sorted(['95018'])
q21 = sorted(['95019'])
q22 = sorted(['950201'])
q23 = sorted(['950202'])
q24 = sorted(['950211'])
q25 = sorted(['950212'])
q26 = sorted(['950213'])
q27 = sorted(['950221'])
q28 = sorted(['950222'])
q29 = sorted(['950223'])
q30 = sorted(['950231'])
q31 = sorted(['95024'])
q32 = sorted([
    '950111','950112','950113','950121','950122','950123','95013','950141','950142','950151','950152','950153','95016','950171','950172','950173','950174','950175','95018','95019','950201','950202','950211','950212','950213','950221','950222','950223','950231','95024',
])
q33 = sorted([
    '90012','90013','90014','90015','90016','90017','9002','9007','90061','90063','90064','90084','90085','90086','90087','90088','9005','90111','90115','90116','90191','9010','90114','90034','90037','90032','90038','9004','9018','902112','9013',
    '950111','950112','950113','950121','950122','950123','95013','950141','950142','950151','950152','950153','95016','950171','950172','950173','950174','950175','95018','95019','950201','950202','950211','950212','950213','950221','950222','950223','950231','95024',
    '90012','90013','90014','90015','90016','90017','9002','9007','90061','90063','90064','90084','90085','90086','90087','90088','9005','90111','90115','90116','90191','9010','90114','90034','90037','90032','90038','9004','9018','902112','9013',
])
q34 = sorted(['9002'])
q35 = sorted(['90071'])
q36 = sorted(['90072'])
q37 = sorted(['90073'])
q38 = sorted(['90074'])
q39 = sorted(['90061'])
q40 = sorted(['90063'])
q41 = sorted(['90064'])
q42 = sorted(['90084'])
q43 = sorted(['90085'])
q44 = sorted(['90086'])
q45 = sorted(['90087'])
q46 = sorted(['90088'])
q47 = sorted(['9005'])
q48 = sorted(['90111'])
q49 = sorted(['90115'])
q50 = sorted(['90116'])
q51 = sorted(['90191'])
q52 = sorted(['9010'])
q53 = sorted(['90034'])
q54 = sorted(['90037'])
q55 = sorted(['90032'])
q56 = sorted(['90038'])
q57 = sorted(['9004'])
q58 = sorted(['9018'])
q59 = sorted(['902112'])
q60 = sorted(['90114'])
q61 = sorted(['9013'])
q62 = sorted([
    '9002','950111','950112','950113','950121','950122','950123','95013','950141','950142','950151','950152','950153','95016','950171','950172','950173','950174','950175','95018','95019','950201','950202','950211','950212','950213','950221','950222','950223','950231','95024','90071','950111','950112','950113','950121','950122','950123','95013','950141','950142','950151','950152','950153','95016','950171','950172','950173','950174','950175','95018','95019','950201','950202','950211','950212','950213','950221','950222','950223','950231','95024','90074','950111','950112','950113','950121','950122','950123','95013','950141','950142','950151','950152','950153','95016','950171','950172','950173','950174','950175','95018','95019','950201','950202','950211','950212','950213','950221','950222','950223','950231','95024','90088','950111','950112','950113','950121','950122','950123','95013','950141','950142','950151','950152','950153','95016','950171','950172','950173','950174','950175','95018','95019','950201','950202','950211','950212','950213','950221','950222','950223','950231','95024','9013','950111','950112','950113','950121','950122','950123','95013','950141','950142','950151','950152','950153','95016','950171','950172','950173','950174','950175','95018','95019','950201','950202','950211','950212','950213','950221','950222','950223','950231','95024',
])
q63 = sorted([
    '90012','90013','90014','90015','90016','90017','9002','9007','90061','90063','90064','90084','90085','90086','90087','90088','9005','90111','90115','90116','90191','9010','90114','90034','90037','90032','90038','9004','9018','902112','9013',
])

clear_screen()
print_tiktok_logo()
if sisn:
    print(TEXT + f"تم تحميل {len(sisn)} سيشن من 1.txt" + Style.RESET_ALL)
else:
    print(TEXT + "الملف 1.txt غير موجود أو فارغ" + Style.RESET_ALL)
print(TEXT + BAR + Style.RESET_ALL)

print_lists_only()
choice = input(ACCENT1 + "أدخل رقم الاختيار: " + Style.RESET_ALL).strip()

if choice == '1':
    sdsd = q1
    print(TURQUOISE + "تم اختيار: المحتوى عبارة عن مادة اعتداء جنسي على الأطفال" + RESET)
elif choice == '2':
    sdsd = q2
    print(TURQUOISE + "تم اختيار: عرض توريد مواد الاعتداء الجنسي على الأطفال وبيعها وتوزيعها" + RESET)
elif choice == '3':
    sdsd = q3
    print(TURQUOISE + "تم اختيار: المحتوى المتعلق باستمالة طفل أو إغواءه جنسيًا" + RESET)
elif choice == '4':
    sdsd = q4
    print(TURQUOISE + "تم اختيار: التهديد بالعنف/التحريض على ارتكاب جريمة (جرائم) إرهابية" + RESET)
elif choice == '5':
    sdsd = q5
    print(TURQUOISE + "تم اختيار: المحتوى المتعلق بالتجنيد والتمويل ودعم الإرهاب" + RESET)
elif choice == '6':
    sdsd = q6
    print(TURQUOISE + "تم اختيار: تعليمات أو تدريب حول كيفية صنع المتفجرات/الأسلحة/الأسلحة النارية (لأغراض إرهابية)" + RESET)
elif choice == '7':
    sdsd = q7
    print(TURQUOISE + "تم اختيار: خطاب الكراهية غير القانوني" + RESET)
elif choice == '8':
    sdsd = q8
    print(TURQUOISE + "تم اختيار: تصوير العنف بشع المنظر" + RESET)
elif choice == '9':
    sdsd = q9
    print(TURQUOISE + "تم اختيار: المشاركة في منظمة إجرامية" + RESET)
elif choice == '10':
    sdsd = q10
    print(TURQUOISE + "تم اختيار: انتهاكات الخصوصية القائمة على الصور" + RESET)
elif choice == '11':
    sdsd = q11
    print(TURQUOISE + "تم اختيار: انتحال الهوية بشكل غير قانوني" + RESET)
elif choice == '12':
    sdsd = q12
    print(TURQUOISE + "تم اختيار: انتهاكات أخرى للخصوصية" + RESET)
elif choice == '13':
    sdsd = q13
    print(TURQUOISE + "تم اختيار: مشاركة الصور الحميمة أو الخاصة دون موافقة" + RESET)
elif choice == '14':
    sdsd = q14
    print(TURQUOISE + "تم اختيار: المحتوى المرتبط بالاتجار بالبشر (الإعلانات، والمزيد)" + RESET)
elif choice == '15':
    sdsd = q15
    print(TURQUOISE + "تم اختيار: الترويج للدعارة/الاستدراج" + RESET)
elif choice == '16':
    sdsd = q16
    print(TURQUOISE + "تم اختيار: إنتاج العقاقير/المخدرات غير المشروعة أو بيعها أو توريدها أو توزيعه" + RESET)
elif choice == '17':
    sdsd = q17
    print(TURQUOISE + "تم اختيار: المحتوى الذي يروّج للصيد الجائر أو الاتجار غير المشروع بالأحياء البرية" + RESET)
elif choice == '18':
    sdsd = q18
    print(TURQUOISE + "تم اختيار: الاتجار غير المشروع بالأسلحة" + RESET)
elif choice == '19':
    sdsd = q19
    print(TURQUOISE + "تم اختيار: السلع غير القانونية الأخرى" + RESET)
elif choice == '20':
    sdsd = q20
    print(TURQUOISE + "تم اختيار: المضايقات أو التهديدات" + RESET)
elif choice == '21':
    sdsd = q21
    print(TURQUOISE + "تم اختيار: التشهير" + RESET)
elif choice == '22':
    sdsd = q22
    print(TURQUOISE + "تم اختيار: خرق قانون المستهلك" + RESET)
elif choice == '23':
    sdsd = q23
    print(TURQUOISE + "تم اختيار: المنتجات/البضائع غير الآمنة أو الخطر" + RESET)
elif choice == '24':
    sdsd = q24
    print(TURQUOISE + "تم اختيار: التضليل الجنائي" + RESET)
elif choice == '25':
    sdsd = q25
    print(TURQUOISE + "تم اختيار: ازدراء المحكمة أو خرق أمر المحكمة أو التصريح غير القانوني" + RESET)
elif choice == '26':
    sdsd = q26
    print(TURQUOISE + "تم اختيار: إعطاء تعليمات/تشجيع يتعلق بالانتحار" + RESET)
elif choice == '27':
    sdsd = q27
    print(TURQUOISE + "تم اختيار: الاحتيال" + RESET)
elif choice == '28':
    sdsd = q28
    print(TURQUOISE + "تم اختيار: غسيل الأموال" + RESET)
elif choice == '29':
    sdsd = q29
    print(TURQUOISE + "تم اختيار: الابتزاز/الرشوة" + RESET)
elif choice == '30':
    sdsd = q30
    print(TURQUOISE + "تم اختيار: الجرائم المتعلقة بالأمن القومي (الخيانة والتجسس والتخريب وتعريض الأمن الداخلي أو الخارجي للخطر" + RESET)
elif choice == '31':
    sdsd = q31
    print(TURQUOISE + "تم اختيار: محتوى غير قانوني آخر" + RESET)
elif choice == '32':
    sdsd = q32
    print(TURQUOISE + "تم اختيار: عشوائي قانون الأوربي" + RESET)
elif choice == '33':
    sdsd = q33
    print(TURQUOISE + "تم اختيار: بلاغ النسر" + RESET)
elif choice == '34':
    sdsd = q34
    print(GREEN + "تم اختيار: بلاغ الكراهية والسلوكيات البغيضة" + RESET)
elif choice == '35':
    sdsd = q35
    print(GREEN + "تم اختيار: لقد تعرضت بنفسي للتنمر أو المضايقة" + RESET)
elif choice == '36':
    sdsd = q36
    print(GREEN + "تم اختيار: تعرض شخص أعرفه للتنمر أو المضايقة" + RESET)
elif choice == '37':
    sdsd = q37
    print(GREEN + "تم اختيار: تعرض أحد المشاهير أو المسؤولين الحكوميين للتنمر أو المضايقة" + RESET)
elif choice == '38':
    sdsd = q38
    print(GREEN + "تم اختيار: تعرض آخرون للتنمر أو المضايقة" + RESET)
elif choice == '39':
    sdsd = q39
    print(GREEN + "تم اختيار: الانتحار وإيذاء النفس" + RESET)
elif choice == '40':
    sdsd = q40
    print(GREEN + "تم اختيار: اضطرابات الأكل وصورة الجسم غير الصحية" + RESET)
elif choice == '41':
    sdsd = q41
    print(GREEN + "تم اختيار: الأنشطة والتحديات الخطرة" + RESET)
elif choice == '42':
    sdsd = q42
    print(GREEN + "تم اختيار: النشاط الجنسي للشباب والاستدراج الجنسي والاستغلال الجنسي" + RESET)
elif choice == '43':
    sdsd = q43
    print(GREEN + "تم اختيار: السلوك الموحي جنسيًا بواسطة الشباب" + RESET)
elif choice == '44':
    sdsd = q44
    print(GREEN + "تم اختيار: النشاط الجنسي للبالغين والخدمات الجنسية والاستدراج الجنسي" + RESET)
elif choice == '45':
    sdsd = q45
    print(GREEN + "تم اختيار: عُري البالغين" + RESET)
elif choice == '46':
    sdsd = q46
    print(GREEN + "تم اختيار: اللغة الجنسية الفاحشة" + RESET)
elif choice == '47':
    sdsd = q47
    print(GREEN + "تم اختيار: المحتوى صادم وبشع المنظر" + RESET)
elif choice == '48':
    sdsd = q48
    print(GREEN + "تم اختيار: معلومات خاطئة عن الانتخابات" + RESET)
elif choice == '49':
    sdsd = q49
    print(GREEN + "تم اختيار: معلومات ضارة مضللة" + RESET)
elif choice == '50':
    sdsd = q50
    print(GREEN + "تم اختيار: التزييف العميق والوسائط التركيبية والوسائط التي تم التلاعب بها" + RESET)
elif choice == '51':
    sdsd = q51
    print(GREEN + "تم اختيار: التفاعل الزائف" + RESET)
elif choice == '52':
    sdsd = q52
    print(GREEN + "تم اختيار: مزعج" + RESET)
elif choice == '53':
    sdsd = q53
    print(GREEN + "تم اختيار: المقامرة" + RESET)
elif choice == '54':
    sdsd = q54
    print(GREEN + "تم اختيار: الكحول والتبغ والمخدرات" + RESET)
elif choice == '55':
    sdsd = q55
    print(GREEN + "تم اختيار: الأسلحة النارية والأسلحة الخطرة" + RESET)
elif choice == '56':
    sdsd = q56
    print(GREEN + "تم اختيار: تجارة السلع والخدمات الأخرى الخاضعة للإرشادات التنظيمية" + RESET)
elif choice == '57':
    sdsd = q57
    print(GREEN + "تم اختيار: الغش والاحتيال" + RESET)
elif choice == '58':
    sdsd = q58
    print(GREEN + "تم اختيار: مشاركة المعلومات الشخصية" + RESET)
elif choice == '59':
    sdsd = q59
    print(GREEN + "تم اختيار: اشتباه في انتهاك الملكية الفكرية لآخرين" + RESET)
elif choice == '60':
    sdsd = q60
    print(GREEN + "تم اختيار: محتوى مرتبط بعلامة تجارية غير معلن عنه" + RESET)
elif choice == '61':
    sdsd = q61
    print(GREEN + "تم اختيار: آخر" + RESET)
elif choice == '62':
    sdsd = q62
    print(GREEN + "تم اختيار: ثغرة رقم 1" + RESET)
elif choice == '63':
    sdsd = q63
    print(GREEN + "تم اختيار: عشوائي عربي" + RESET)
else:
    print(RED + "اختيار غير صحيح، تم استخدام بلاغ أوروبي كخيار افتراضي" + RESET)
    sdsd = q32  # افتراضي أوروبي

print(TEXT + WIDE_BAR + Style.RESET_ALL)
print(TEXT + "تم تجهيز قائمة الرموز المختارة (sdsd). يمكنك متابعة المعالجة الأساسية الآن." + Style.RESET_ALL)
tr,fa,er=0,0,0
class ttsign:
    def __init__(self, params: str, data: str, cookies: str) -> None:
        self.params = params
        self.data = data
        self.cookies = cookies
    def hash(self, data: str) -> str:
        return str(hashlib.md5(data.encode()).hexdigest())
    def get_base_string(self) -> str:
        base_str = self.hash(self.params)
        base_str = (
            base_str + self.hash(self.data) if self.data else base_str + str("0" * 32)
        )
        base_str = (
            base_str + self.hash(self.cookies)
            if self.cookies
            else base_str + str("0" * 32)
        )
        return base_str
    def get_value(self) -> json:
        return self.encrypt(self.get_base_string())
    def encrypt(self, data: str) -> json:
        unix = time.time()
        len = 0x14
        key = [

            0xDF,
            0x77,
            0xB9,
            0x40,
            0xB9,
            0x9B,
            0x84,
            0x83,
            0xD1,
            0xB9,
            0xCB,
            0xD1,
            0xF7,
            0xC2,
            0xB9,
            0x85,
            0xC3,
            0xD0,
            0xFB,
            0xC3,
        ]
        param_list = []
        for i in range(0, 12, 4):
            temp = data[8 * i : 8 * (i + 1)]
            for j in range(4):
                H = int(temp[j * 2 : (j + 1) * 2], 16)
                param_list.append(H)
        param_list.extend([0x0, 0x6, 0xB, 0x1C])
        H = int(hex(int(unix)), 16)
        param_list.append((H & 0xFF000000) >> 24)
        param_list.append((H & 0x00FF0000) >> 16)
        param_list.append((H & 0x0000FF00) >> 8)
        param_list.append((H & 0x000000FF) >> 0)
        eor_result_list = []
        for A, B in zip(param_list, key):
            eor_result_list.append(A ^ B)
        for i in range(len):
            C = self.reverse(eor_result_list[i])
            D = eor_result_list[(i + 1) % len]
            E = C ^ D
            F = self.rbit_algorithm(E)
            H = ((F ^ 0xFFFFFFFF) ^ len) & 0xFF
            eor_result_list[i] = H
        result = ""
        for param in eor_result_list:
            result += self.hex_string(param)
        return {
            "x-ss-req-ticket": str(int(unix * 1000)),
            "x-khronos": str(int(unix)),
            "x-gorgon": ("0404b0d30000" + result),
        }

    def rbit_algorithm(self, num):
        result = ""
        tmp_string = bin(num)[2:]
        while len(tmp_string) < 8:
            tmp_string = "0" + tmp_string
        for i in range(0, 8):
            result = result + tmp_string[7 - i]
        return int(result, 2)

    def hex_string(self, num):
        tmp_string = hex(num)[2:]
        if len(tmp_string) < 2:
            tmp_string = "0" + tmp_string
        return tmp_string

    def reverse(self, num):
        tmp_string = self.hex_string(num)
        return int(tmp_string[1:] + tmp_string[:1], 16)
P = '\x1b[1;97m'
B = '\x1b[1;94m'
O = '\x1b[1;96m'
Z = "\033[1;30m"
X = '\033[1;33m' #اصفر
F = '\033[2;32m'
Z = '\033[1;31m' 
L = "\033[1;95m"  #ارجواني
C = '\033[2;35m' #وردي
A = '\033[2;39m' #ازرق
P = "\x1b[38;5;231m" # Putih
J = "\x1b[38;5;208m" # Jingga
J1='\x1b[38;5;202m'
J2='\x1b[38;5;203m' #وردي
J21='\x1b[38;5;204m'
J22='\x1b[38;5;209m'
F1='\x1b[38;5;76m'
C1='\x1b[38;5;120m'
P1='\x1b[38;5;150m'
P2='\x1b[38;5;190m'
def clear():
            import os
from termcolor import colored

def clear():
    os.system('cls' if os.name == 'nt' else 'clear')

print(colored("[3]  أبدء البلاغ", "cyan"))

Get_aobsh = "3"
print(colored(f"تم اختيار رقم {Get_aobsh} تلقائياً ✅", "green"))

clear()
