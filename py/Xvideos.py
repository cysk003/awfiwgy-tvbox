import json
import re
import sys
from pyquery import PyQuery as pq
from base64 import b64decode, b64encode
from requests import Session
sys.path.append('..')
from base.spider import Spider

class Spider(Spider):
    def init(self, extend=""):
        self.headers['referer'] = f'{self.host}/'
        self.session = Session()
        self.session.headers.update(self.headers)
        pass

    def getName(self):
        pass

    def isVideoFormat(self, url):
        pass

    def manualVideoCheck(self):
        pass

    def destroy(self):
        pass

    host = "https://www.xvideos.com"

    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/133.0.0.0 Safari/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
        'sec-ch-ua': '"Not(A:Brand";v="99", "Google Chrome";v="133", "Chromium";v="133"',
        'sec-ch-ua-mobile': '?0',
        'sec-ch-ua-full-version': '"133.0.6943.98"',
        'sec-ch-ua-arch': '"x86"',
        'sec-ch-ua-platform': '"Windows"',
        'sec-ch-ua-platform-version': '"19.0.0"',
        'sec-ch-ua-model': '""',
        'sec-ch-ua-full-version-list': '"Not(A:Brand";v="99.0.0.0", "Google Chrome";v="133.0.6943.98", "Chromium";v="133.0.6943.98"',
        'dnt': '1',
        'upgrade-insecure-requests': '1',
        'sec-fetch-site': 'none',
        'sec-fetch-mode': 'navigate',
        'sec-fetch-user': '?1',
        'sec-fetch-dest': 'document',
        'accept-language': 'zh-CN,zh;q=0.9,en;q=0.8',
        'priority': 'u=0, i'
    }

    def homeContent(self, filter):
        result = {}
        cateManual = {
            "频道": "/channels-index",
            "标签": "/tags",
            "明星": "/pornstars-index",
            "中文": "/lang/chinese",
            "阿拉伯": "/c/Arab-159",
            "成熟": "/c/Mature-38",
            "出轨背叛": "/c/Cuckold-237",
            "调教": "/c/Femdom-235",
            "肛交": "/c/Anal-12",
            "褐发": "/c/Brunette-25",
            "黑人": "/c/Black_Woman-30",
            "红发": "/c/Redhead-31",
            "家庭乱搞": "/c/Fucked_Up_Family-81",
            "金发": "/c/Blonde-20",
            "巨屌": "/c/Big_Cock-34",
            "巨乳": "/c/Big_Tits-23",
            "巨臀": "/c/Big_Ass-24",
            "口交": "/c/Blowjob-15",
            "拉丁裔": "/c/Latina-16",
            "辣妈": "/c/Milf-19",
            "裂开": "/c/Gapes-167",
            "美臀": "/c/Ass-14",
            "男同": "/gay",
            "女同": "/c/Lesbian-26",
            "胖女": "/c/bbw-51",
            "喷出": "/c/Squirting-56",
            "拳交": "/c/Fisting-165",
            "群交": "/c/Gangbang-69",
            "人妖": "/shemale",
            "少女": "/c/Teen-13",
            "射颜": "/c/Cumshot-18",
            "摄像头": "/c/Cam_Porn-58",
            "双性恋": "/c/Bi_Sexual-62",
            "丝袜": "/c/Stockings-28",
            "涂油": "/c/Oiled-22",
            "性感内衣": "/c/Lingerie-83",
            "亚洲": "/c/Asian_Woman-32",
            "业余": "/c/Amateur-65",
            "异族": "/c/Interracial-27",
            "印度": "/c/Indian-89",
            "中出": "/c/Creampie-40",
            "自慰": "/c/Solo_and_Masturbation-33",
            "AI": "/c/AI-239",
            "ASMR": "/c/ASMR-229"
        }
        classes = []
        for k in cateManual:
            classes.append({
                'type_name': k,
                'type_id': cateManual[k]
            })
        result['class'] = classes
        return result

    def homeVideoContent(self):
        data = self.getpq()
        return {'list': self.getlist(data(".mozaique .frame-block"))}

    def categoryContent(self, tid, pg, filter, extend):
        vdata = []
        result = {}
        page = f"/{int(pg) - 1}" if str(pg) != '1' else ''
        result['page'] = pg
        result['pagecount'] = 9999
        result['limit'] = 90
        result['total'] = 999999
        
        if tid == '/new' or 'tags_click' in tid or tid.startswith('/c/') or tid.startswith('/lang/') or tid in ['/gay', '/shemale']:
            if 'tags_click' in tid:
                tid = tid.split('click_')[-1]
            data = self.getpq(f'{tid}{page}')
            vdata = self.getlist(data(".mozaique .frame-block"))
        elif tid == '/best':
            if str(pg) == '1':
                self.path = self.session.get(f'{self.host}{tid}', headers=self.headers, allow_redirects=False).headers['Location']
            data = self.getpq(f'{self.path}{page}')
            vdata = self.getlist(data(".mozaique .frame-block"))
        elif tid == '/channels-index' or tid == '/pornstars-index':
            data = self.getpq(f'{tid}{page}')
            vhtml = data(".mozaique .thumb-block")
            for i in vhtml.items():
                a = i('.thumb-inside .thumb a')
                match = re.search(r'src="([^"]+)"', a('script').text())
                img = ''
                if match:
                    img = match.group(1).strip()
                vdata.append({
                    'vod_id': f"channels_click_{'/channels' if tid == '/channels-index' else ''}" + a.attr('href'),
                    'vod_name': a('.profile-name').text() or i('.profile-name').text().replace('\xa0', '/'),
                    'vod_pic': img,
                    'vod_tag': 'folder',
                    'vod_remarks': i('.thumb-under .profile-counts').text(),
                    'style': {'ratio': 1.33, 'type': 'rect'}
                })
        elif tid == '/tags':
            result['pagecount'] = pg
            vhtml = self.getpq(tid)
            vhtml = vhtml('.tags-list')
            for d in vhtml.items():
                for i in d('li a').items():
                    vdata.append({
                        'vod_id': "tags_click_" + i.attr('href'),
                        'vod_name': i.attr('title') or i('b').text(),
                        'vod_pic': '',
                        'vod_tag': 'folder',
                        'vod_remarks': i('.navbadge').text(),
                        'style': {'ratio': 1.33, 'type': 'rect'}
                    })
        elif 'channels_click' in tid:
            tid = tid.split('click_')[-1]
            headers = self.session.headers.copy()
            headers.update({'Accept': 'application/json, text/javascript, */*; q=0.01'})
            vhtml = self.post(f'{self.host}{tid}/videos/best/{int(pg) - 1}', headers=headers).json()
            for i in vhtml['videos']:
                vdata.append({
                    'vod_id': i.get('u'),
                    'vod_name': i.get('tf'),
                    'vod_pic': i.get('il'),
                    'vod_year': i.get('n'),
                    'vod_remarks': i.get('d'),
                    'style': {'ratio': 1.33, 'type': 'rect'}
                })
        
        result['list'] = vdata
        return result

    def detailContent(self, ids):
        url = f"{self.host}{ids[0]}"
        data = self.getpq(ids[0])
        vn = data('meta[property="og:title"]').attr('content')
        dtext = data('.main-uploader a')
        href = dtext.attr('href')
        pdtitle = ''
        if href and href.count('/') < 2:
            href = f'/channels{href}'
            pdtitle = '[a=cr:' + json.dumps({'id': 'channels_click_' + href, 'name': dtext('.name').text()}) + '/]' + dtext('.name').text() + '[/a]'
        vod = {
            'vod_name': vn,
            'vod_director': pdtitle,
            'vod_remarks': data('.page-title').text().replace(vn, ''),
            'vod_play_from': '书生玩剣ⁱ·*₁＇',
            'vod_play_url': ''
        }
        js_content = data("#video-player-bg script")
        jstr = ''
        for script in js_content.items():
            content = script.text()
            if 'setVideoUrlLow' in content and 'html5player' in content:
                jstr = content
                break
        plist = [f"{vn}${self.e64(f'{1}@@@@{url}')}"]
        
        def extract_video_urls(js_content):
            try:
                low = re.search(r'setVideoUrlLow\([\'"]([^\'"]+)[\'"]\)', js_content)
                high = re.search(r'setVideoUrlHigh\([\'"]([^\'"]+)[\'"]\)', js_content)
                hls = re.search(r'setVideoHLS\([\'"]([^\'"]+)[\'"]\)', js_content)

                return {
                    'hls': hls.group(1) if hls else None,
                    'high': high.group(1) if high else None,
                    'low': low.group(1) if low else None
                }
            except Exception as e:
                return {}
        
        if jstr:
            try:
                urls = extract_video_urls(jstr)
                plist = [
                    f"{quality}${self.e64(f'{0}@@@@{url}')}"
                    for quality, url in urls.items()
                    if url
                ]
            except Exception as e:
                pass
        vod['vod_play_url'] = '#'.join(plist)
        return {'list': [vod]}

    def searchContent(self, key, quick, pg="1"):
        data = self.getpq(f'/?k={key}&p={int(pg) - 1}')
        return {'list': self.getlist(data(".mozaique .frame-block")), 'page': pg}

    def playerContent(self, flag, id, vipFlags):
        headers = {
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/109.0.5410.0 Safari/537.36',
            'pragma': 'no-cache',
            'cache-control': 'no-cache',
            'sec-ch-ua-platform': '"Windows"',
            'sec-ch-ua': '"Not(A:Brand";v="99", "Google Chrome";v="133", "Chromium";v="133"',
            'dnt': '1',
            'sec-ch-ua-mobile': '?0',
            'origin': self.host,
            'sec-fetch-site': 'cross-site',
            'sec-fetch-mode': 'cors',
            'sec-fetch-dest': 'empty',
            'referer': f'{self.host}/',
            'accept-language': 'zh-CN,zh;q=0.9,en;q=0.8',
            'priority': 'u=1, i',
        }
        ids = self.d64(id).split('@@@@')
        return {'parse': int(ids[0]), 'url': ids[1], 'header': headers}

    def localProxy(self, param):
        pass

    def e64(self, text):
        try:
            text_bytes = text.encode('utf-8')
            encoded_bytes = b64encode(text_bytes)
            return encoded_bytes.decode('utf-8')
        except Exception as e:
            return ""

    def d64(self, encoded_text):
        try:
            encoded_bytes = encoded_text.encode('utf-8')
            decoded_bytes = b64decode(encoded_bytes)
            return decoded_bytes.decode('utf-8')
        except Exception as e:
            return ""

    def getlist(self, data):
        vlist = []
        for i in data.items():
            a = i('.thumb-inside .thumb a')
            b = i('.thumb-under .title a')
            vlist.append({
                'vod_id': a.attr('href'),
                'vod_name': b('a').attr('title') or b.attr('title'),
                'vod_pic': a('img').attr('data-src'),
                'vod_year': a('.video-hd-mark').text(),
                'vod_remarks': b('.duration').text(),
                'style': {'ratio': 1.33, 'type': 'rect'}
            })
        return vlist

    def getpq(self, path=''):
        response = self.session.get(f'{self.host}{path}').text
        try:
            return pq(response)
        except Exception as e:
            return pq(response.encode('utf-8'))
