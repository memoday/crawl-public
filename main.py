import requests
from bs4 import BeautifulSoup
import re
import json
import time

start = time.time()

nickname = '넴촉'
icon = [None,None,'리부트','리부트2','오로라','레드','이노시스','유니온','스카니아','루나','제니스','크로아','베라','엘리시움','아케인','노바']
w_num = {
    '리부트': 1,
    '리부트2': 2,
    '오로라': 3,
    '레드': 4,
    '이노시스': 5,
    '유니온': 6,
    '스카니아': 7,
    '루나': 8,
    '제니스': 9,
    '크로아': 10,
    '베라': 11,
    '엘리시움': 12,
    '아케인': 13,
    '노바': 14
}

header = {'User-Agent' : 'Mozilla/5.0 (Windows NT 10.0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/108.0.0.0 Whale/3.18.154.13 Safari/537.36'}

def get_icon_name_from_url(url):
    match = re.search(r'icon_(\d+)\.png', url)
    if match:
        icon_number = int(match.group(1))
        if 0 <= icon_number < len(icon):
            return icon[icon_number]
    return None

def getBasic(nick): #인기도, 직업, 월드, 레벨, 경험치, 길드, 전체랭킹, 월드랭킹까지 가져올 수 있음
    url = f"https://maplestory.nexon.com/N23Ranking/World/Total?c={nick}&w=0"
    r = requests.get(url, headers = header)
    if r.status_code == 200:
        html = BeautifulSoup(r.text,"html.parser")
        chk = html.select_one("#container > div > div > div:nth-child(4) > div.rank_table_wrap > table > tbody > tr.search_com_chk")

        try: 
            image_url = chk.select_one("td.left > span > img:nth-child(1)")['src']
            world = chk.select_one("td.left > dl > dt > a > img")["src"]
            world= get_icon_name_from_url(world)
            job = chk.select_one("td.left > dl > dd").text
            typeOfJob, job = job.split(' / ')
            level = chk.select_one("td:nth-child(3)").text
            exp = chk.select_one("td:nth-child(4)").text
            fame = chk.select_one("td:nth-child(5)").text
            guild = chk.select_one("td:nth-child(6)").text
            rank = chk.select_one("td:nth-child(1) > p").text.strip() #p.ranking_other이 아닌 이유는 웹사이트 코드 구조 오류로 p.'ranking_other'로 되어있음
            if rank == '':
                try:
                    rank = chk.select_one("td:nth-child(1) > p > img")["alt"].strip('등')
                except:
                    rank = None

            world = chk.select_one("td.left > dl > dt > a > img")["src"]
            world= get_icon_name_from_url(world)
            world_num = w_num[world]

            url = f"https://maplestory.nexon.com/N23Ranking/World/Total?c={nick}&w={world_num}"
            r = requests.get(url, headers = header)
            html = BeautifulSoup(r.text,"html.parser")
            chk = html.select_one("#container > div > div > div:nth-child(4) > div.rank_table_wrap > table > tbody > tr.search_com_chk")
            world_rank = chk.select_one("td:nth-child(1) > p").text.strip()
            if world_rank == '':
                try:
                    world_rank = chk.select_one("td:nth-child(1) > p > img")["alt"].strip('등')
                except:
                    world_rank = None

            basic = {
                'character_image': image_url,
                'world': world,
                'class': job,
                'level': level,
                'exp': exp,
                'fame': fame,
                'guild': guild,
                'overall_rank' : rank,
                'world_rank' : world_rank
            }

        except AttributeError as e:
            print(e)
            basic = None
    else:
        basic = {
            'message' : '서버 오류가 발생했습니다',
            'status_code' : r.status_code,
        }

    return basic

def getUnion(nick): #유니온 랭킹/유니온 레벨/공격대 전투력
    url = f"https://maplestory.nexon.com/N23Ranking/World/Union?c={nick}&w=0"
    r = requests.get(url, headers = header)
    if r.status_code == 200:
        html = BeautifulSoup(r.text,"html.parser")
        chk = html.select_one("#container > div > div > div:nth-child(4) > table > tbody > tr.search_com_chk")

        if chk != None:
            rank = chk.select_one("td:nth-child(1) > p").text.strip()
            if rank == '':
                try:
                    rank = chk.select_one("td:nth-child(1) > p > img")["alt"].strip('등')
                except:
                    rank = None
            union_level = chk.select_one("td:nth-child(3)").text
            legion_raid_power = chk.select_one("td:nth-child(4)").text

            #월드랭킹 확인
            world = chk.select_one("td.left > dl > dt > a > img")["src"]
            world= get_icon_name_from_url(world)
            world_num = w_num[world]

            url = f"https://maplestory.nexon.com/N23Ranking/World/Union?c={nick}&w={world_num}"
            r = requests.get(url, headers = header)
            html = BeautifulSoup(r.text,"html.parser")
            chk = html.select_one("#container > div > div > div:nth-child(4) > table > tbody > tr.search_com_chk")
            world_rank = chk.select_one("td:nth-child(1) > p").text.strip()
            if world_rank == '':
                try:
                    world_rank = chk.select_one("td:nth-child(1) > p > img")["alt"].strip('등')
                except:
                    world_rank = None
        
        elif chk == None:
            return None
        
        union = {
            'overall_rank' : rank,
            'world_rank' : world_rank,
            'level' : union_level,
            'union_combat_power' : legion_raid_power
        }
    else:
        union = None

    return union

def getMulung(nick): #무릉, 데이터는 지난주 기록을 가져옴 (주 1회 갱신 예정)
    
    url = f"https://maplestory.nexon.com/N23Ranking/Contents/Dojang/LastWeek?c={nick}&t=2&w=0"
    r = requests.get(url, headers = header)
    if r.status_code == 200:
        html = BeautifulSoup(r.text,"html.parser")
        chk = html.select_one("#container > div > div > div:nth-child(4) > div.rank_table_wrap > table > tbody > tr.search_com_chk")

        if chk != None:
            rank = chk.select_one("td:nth-child(1) > p").text.strip()
            if rank == '':
                try:
                    rank = chk.select_one("td:nth-child(1) > p > img")["alt"].strip('등')
                except:
                    rank = None
            job = chk.select_one("td.left > dl > dd").text
            typeOfJob, job = job.split(' / ')
            level = chk.select_one("td:nth-child(3)").text
            floor = chk.select_one("td:nth-child(4)").text
            clear_time = chk.select_one("td:nth-child(5)").text

            #월드랭킹 확인
            world = chk.select_one("td.left > dl > dt > a > img")["src"]
            world= get_icon_name_from_url(world)
            world_num = w_num[world]

            url = f"https://maplestory.nexon.com/N23Ranking/Contents/Dojang/LastWeek?c={nick}&t=2&w={world_num}"
            r = requests.get(url, headers = header)
            html = BeautifulSoup(r.text,"html.parser")
            chk = html.select_one("#container > div > div > div:nth-child(4) > div.rank_table_wrap > table > tbody > tr.search_com_chk")
            world_rank = chk.select_one("td:nth-child(1) > p").text.strip()
            if world_rank == '':
                try:
                    world_rank = chk.select_one("td:nth-child(1) > p > img")["alt"].strip('등')
                except:
                    world_rank = None
        
        elif chk == None:
            return None
        

        mulung = {
            'overall_rank' : rank,
            'world_rank' : world_rank,
            'class_at_completion' : job,
            'levet_at_completion' : level,
            'floor' : floor,
            'complete_time' : clear_time
        }
    else:
        mulung = None

    return mulung

def getAchievement(nick): #업적
    url = f"https://maplestory.nexon.com/N23Ranking/Contents/Achievement?c={nick}"
    r = requests.get(url, headers = header)
    if r.status_code == 200:
        html = BeautifulSoup(r.text,"html.parser")
        chk = html.select_one("#container > div > div > div:nth-child(4) > div.rank_table > table > tbody > tr.search_com_chk")

        if chk != None:
            rank = chk.select_one("td:nth-child(1) > p").text.strip()
            if rank == '':
                try:
                    rank = chk.select_one("td:nth-child(1) > p > img")["alt"].strip('등').lstrip('0') #업적 alt 정보는 01등, 02등, 03등으로 나타나서 lstrip 추가
                except:
                    rank = None
            points = chk.select_one("td:nth-child(4)").text
            grade = chk.select_one("td.ach_img > span").text
            grade_img = chk.select_one("td.ach_img > img")['src']
        
        elif chk == None:
            return None

        achievement = {
            'overall_rank': rank,
            'world_rank' : None, #업적은 월드랭킹이 따로 없어 순위표를 모두 긁어와야 함
            'score': points,
            'rate': grade,
            'rate_img': grade_img
        }
    else:
        achievement = None


    return achievement

def getCharInfo(nick):

    basic = getBasic(nick)
    mulung = getMulung(nick)
    union = getUnion(nick)
    if union == None:
        achievement = None
    else:
        achievement = getAchievement(nick)

    nickInfo = {
        'nickname': nick,
        'basic': basic,
        'union': union,
        'mulung': mulung,
        'achievement': achievement
    }
    
    return nickInfo


if __name__ == "__main__":
    result = getCharInfo(nickname)
    print(json.dumps(result, ensure_ascii=False, indent=3))
    print("time:", time.time() - start )

