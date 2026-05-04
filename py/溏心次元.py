import requests
import re
import json
import html
import urllib3
from bs4 import BeautifulSoup
from base.spider import Spider

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
#txcy2users@gmail.com
xurl = "https://txcy-online.buzz"

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8',
    'accept-language': 'zh-CN,zh;q=0.9',
    'referer': xurl
}

class Spider(Spider):
    def getName(self):
        return "溏心次元"

    def init(self, extend):
        pass

    def isVideoFormat(self, url):
        pass

    def manualVideoCheck(self):
        pass

    def get_page_with_dynamic_cookie(self, target_url, method='GET', data=None):
        session = requests.Session()
        session.headers.update(headers)
        session.verify = False
        try:
            if method.upper() == 'POST':
                resp = session.post(target_url, data=data, timeout=10)
            else:
                resp = session.get(target_url, timeout=10)
            
            if resp.status_code == 200:
                return resp.text
            return ""
        except Exception as e:
            return ""

    def homeContent(self, filter):
        result = {}
        classes = [
            {"type_id": "4", "type_name": "MD系列"},
            {"type_id": "5", "type_name": "导演系列"},
            {"type_id": "6", "type_name": "MDS系列"},
            {"type_id": "7", "type_name": "MDX系列"},
            {"type_id": "8", "type_name": "MDXS系列"},
            {"type_id": "46", "type_name": "MDL系列"},
            {"type_id": "50", "type_name": "MMZ系列"},
            {"type_id": "53", "type_name": "MAD系列"},
            {"type_id": "58", "type_name": "MDWP系列"},
            {"type_id": "64", "type_name": "MSD系列"},
            {"type_id": "74", "type_name": "MDM恋爱咖啡"},
            {"type_id": "78", "type_name": "MDUS系列"},
            {"type_id": "79", "type_name": "MXJ系列"},
            {"type_id": "87", "type_name": "MKY系列"},
            {"type_id": "89", "type_name": "MAN系列"},
            {"type_id": "96", "type_name": "MCY系列"},
            {"type_id": "100", "type_name": "MDAG系列"},
            {"type_id": "101", "type_name": "MDHT系列"},
            {"type_id": "115", "type_name": "BLX系列"},
            {"type_id": "116", "type_name": "MPG系列"},
            {"type_id": "10", "type_name": "兔子先生"},
            {"type_id": "11", "type_name": "果冻传媒"},
            {"type_id": "12", "type_name": "皇家华人"},
            {"type_id": "13", "type_name": "吴梦梦无套系列"},
            {"type_id": "14", "type_name": "PsychoPorn色控"},
            {"type_id": "15", "type_name": "蜜桃影像传媒"},
            {"type_id": "45", "type_name": "天美传媒"},
            {"type_id": "52", "type_name": "91制片厂"},
            {"type_id": "65", "type_name": "MSM性梦者"},
            {"type_id": "71", "type_name": "叮叮映画"},
            {"type_id": "72", "type_name": "涩会"},
            {"type_id": "75", "type_name": "豚豚创媒"},
            {"type_id": "76", "type_name": "爱妃传媒"},
            {"type_id": "80", "type_name": "辣椒原创"},
            {"type_id": "81", "type_name": "O-STAR"},
            {"type_id": "91", "type_name": "肉肉传媒"},
            {"type_id": "95", "type_name": "渡边传媒"},
            {"type_id": "97", "type_name": "葵心娱乐"},
            {"type_id": "103", "type_name": "红斯灯影像"},
            {"type_id": "105", "type_name": "蝌蚪传媒"},
            {"type_id": "106", "type_name": "Pussy Hunter"},
            {"type_id": "108", "type_name": "桃花源"},
            {"type_id": "17", "type_name": "大鸟十八"},
            {"type_id": "18", "type_name": "疯拍系列"},
            {"type_id": "19", "type_name": "KISS糖果屋"},
            {"type_id": "20", "type_name": "小鹏奇啪行"},
            {"type_id": "22", "type_name": "30天解密麻豆"},
            {"type_id": "23", "type_name": "突袭女优计划"},
            {"type_id": "24", "type_name": "女神羞羞研究所"},
            {"type_id": "27", "type_name": "小哥哥艾理"},
            {"type_id": "31", "type_name": "情趣K歌房"},
            {"type_id": "40", "type_name": "淫欲游戏王"},
            {"type_id": "41", "type_name": "麻豆不回家"},
            {"type_id": "42", "type_name": "女优淫娃培训营"},
            {"type_id": "54", "type_name": "狼人插"},
            {"type_id": "55", "type_name": "女优擂台摔角狂热"},
            {"type_id": "61", "type_name": "恋爱巴士"},
            {"type_id": "66", "type_name": "男女优生死斗"},
            {"type_id": "67", "type_name": "情人劫密室逃脱"},
            {"type_id": "68", "type_name": "换妻"},
            {"type_id": "69", "type_name": "你好同学"},
            {"type_id": "77", "type_name": "禁欲小屋"},
            {"type_id": "84", "type_name": "鲍鱼的胜利"},
            {"type_id": "88", "type_name": "性爱自修室"},
            {"type_id": "92", "type_name": "春游记"},
            {"type_id": "93", "type_name": "心动的性号"},
            {"type_id": "94", "type_name": "情趣大富翁"},
            {"type_id": "99", "type_name": "寻宝吧女神"},
            {"type_id": "102", "type_name": "男优练习生"},
            {"type_id": "110", "type_name": "女神体育祭"},
            {"type_id": "111", "type_name": "麻豆高校"},
            {"type_id": "112", "type_name": "野外露初"},
            {"type_id": "33", "type_name": "乌鸦传媒"},
            {"type_id": "34", "type_name": "精东影业"},
            {"type_id": "36", "type_name": "SWAG"},
            {"type_id": "47", "type_name": "星空无限传媒"},
            {"type_id": "48", "type_name": "大象传媒"},
            {"type_id": "59", "type_name": "大象传媒"},
            {"type_id": "62", "type_name": "MINI传媒"},
            {"type_id": "73", "type_name": "糖心vlog"},
            {"type_id": "82", "type_name": "葫芦影业"},
            {"type_id": "83", "type_name": "天马传媒"},
            {"type_id": "90", "type_name": "CCAV成人头条"},
            {"type_id": "109", "type_name": "性视界传媒"},
            {"type_id": "113", "type_name": "SA国际传媒"},
            {"type_id": "114", "type_name": "香蕉传媒"},
            {"type_id": "117", "type_name": "91茄子"},
            {"type_id": "118", "type_name": "EDmosaic"},
            {"type_id": "39", "type_name": "国产精品"}
        ]
        result['class'] = classes
        return result

    def categoryContent(self, cid, pg, filter, ext):
        page = int(pg) if pg else 1
        target_url = f'{xurl}/vodtype/{cid}-{page}/'
        
        html_content = self.get_page_with_dynamic_cookie(target_url)
        doc = BeautifulSoup(html_content, 'lxml')
        videos = []
        
        for item in doc.select('a.img-box.bo-r5'):
            vod_id = item.get('href')
            vod_name = item.get('title')
            img = item.select_one('img')
            if not img: 
                continue
                
            vod_pic = img.get('data-original') or img.get('src')
            remark_span = item.select_one('.item-auxiliary')
            vod_remarks = remark_span.text.strip() if remark_span else ''
            
            if vod_id and vod_name:
                videos.append({
                    "vod_id": vod_id,
                    "vod_name": vod_name,
                    "vod_pic": vod_pic,
                    "vod_remarks": vod_remarks
                })
                
        return {'list': videos, 'page': page, 'pagecount': 9999, 'limit': 90, 'total': 999999}

    def detailContent(self, ids):
        did = ids[0]
        if not did.startswith('http'):
            did = xurl + did
            
        html_content = self.get_page_with_dynamic_cookie(did)
        doc = BeautifulSoup(html_content, 'lxml')
        
        h1 = doc.select_one('h1')
        vod_name = h1.text.strip() if h1 else ""
        
        img = doc.select_one('.detail-image-wrapper img')
        vod_pic = img['src'] if img else ""
        
        play_btn = doc.select_one('a.tx-btn.tx-bg.f-18')
        play_url = play_btn['href'] if play_btn else ids[0]
        
        vod_play_from = "溏心专线"
        vod_play_url = f"播放${play_url}"
        
        video = {
            "vod_id": ids[0],
            "vod_name": vod_name,
            "vod_pic": vod_pic,
            "vod_play_from": vod_play_from,
            "vod_play_url": vod_play_url,
            "vod_content": "溏心次元为您播送：" + vod_name
        }
        
        return {'list': [video]}

    def playerContent(self, flag, id, vipFlags):
        if not id.startswith('http'):
            id = xurl + id
            
        html_content = self.get_page_with_dynamic_cookie(id)
        
        play_url = ""
        match = re.search(r'var player_data=(.*?)</script>', html_content)
        if match:
            try:
                data = json.loads(match.group(1))
                play_url = data.get('url', '').replace('\\/', '/')
            except Exception:
                pass
                
        return {
            "parse": 0,
            "playUrl": "",
            "url": play_url,
            "header": headers
        }

    def searchContent(self, key, quick, pg="1"):
        url = f"{xurl}/vodsearch/-------------/"
        data = {"wd": key}
        html_content = self.get_page_with_dynamic_cookie(url, method='POST', data=data)
        doc = BeautifulSoup(html_content, 'lxml')
        videos = []
        
        for item in doc.select('a.img-box.bo-r5'):
            vod_id = item.get('href')
            vod_name = item.get('title')
            img = item.select_one('img')
            if not img: 
                continue
                
            vod_pic = img.get('data-original') or img.get('src')
            remark_span = item.select_one('.item-auxiliary')
            vod_remarks = remark_span.text.strip() if remark_span else ''
            
            if vod_id and vod_name:
                videos.append({
                    "vod_id": vod_id,
                    "vod_name": vod_name,
                    "vod_pic": vod_pic,
                    "vod_remarks": vod_remarks
                })
                
        return {'list': videos, 'page': 1, 'pagecount': 1, 'limit': 90, 'total': len(videos)}

    def localProxy(self, params):
        if params['type'] == "m3u8":
            return self.proxyM3u8(params)
        elif params['type'] == "media":
            return self.proxyMedia(params)
        elif params['type'] == "ts":
            return self.proxyTs(params)
        return None
