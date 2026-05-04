import sys
import re
import json
import urllib.parse
from base.spider import Spider

class Spider(Spider):
    def __init__(self):
        self.name = '追剧网'
        self.host = 'https://www.sxnycy.com'
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36',
            'Referer': self.host
        }
        self.classes = [
            {'type_id': 'dianying', 'type_name': '电影'},
            {'type_id': 'dianshiju', 'type_name': '电视剧'},
            {'type_id': 'zongyi', 'type_name': '综艺'},
            {'type_id': 'dongman', 'type_name': '动漫'},
            {'type_id': 'donghuapian', 'type_name': '动画片'},
            {'type_id': 'duanju', 'type_name': '短剧'}
        ]

    def getName(self):
        return self.name

    def init(self, extend=""):
        pass

    def isVideoFormat(self, url):
        return False

    def manualVideoCheck(self):
        return False

    def _get_filters(self):
        year_list = [{'n': '全部', 'v': ''}] + [{'n': str(y), 'v': str(y)} for y in range(2026, 1999, -1)]
        area_list = [{'n': '全部', 'v': ''}, {'n': '大陆', 'v': '大陆'}, {'n': '香港', 'v': '香港'}, {'n': '台湾', 'v': '台湾'}, {'n': '美国', 'v': '美国'}, {'n': '韩国', 'v': '韩国'}, {'n': '日本', 'v': '日本'}, {'n': '泰国', 'v': '泰国'}, {'n': '英国', 'v': '英国'}, {'n': '法国', 'v': '法国'}, {'n': '其他', 'v': '其他'}]
        lang_list = [{'n': '全部', 'v': ''}, {'n': '国语', 'v': '国语'}, {'n': '英语', 'v': '英语'}, {'n': '粤语', 'v': '粤语'}, {'n': '闽南语', 'v': '闽南语'}, {'n': '韩语', 'v': '韩语'}, {'n': '日语', 'v': '日语'}, {'n': '其它', 'v': '其它'}]
        by_list = [{'n': '按时间', 'v': 'time'}, {'n': '按人气', 'v': 'hits'}, {'n': '按评分', 'v': 'score'}]

        def make_cls(classes):
            return [{'n': '全部', 'v': ''}] + [{'n': c, 'v': c} for c in classes]

        return {
            'dianying': [
                {'key': 'class', 'name': '剧情', 'value': make_cls(['喜剧','爱情','恐怖','动作','科幻','剧情','战争','警匪','犯罪','动画','奇幻','武侠','冒险','枪战','悬疑','惊悚','经典','青春','文艺','微电影','古装','历史','运动','农村','儿童','网络电影'])},
                {'key': 'area', 'name': '地区', 'value': area_list},
                {'key': 'year', 'name': '年份', 'value': year_list},
                {'key': 'lang', 'name': '语言', 'value': lang_list},
                {'key': 'by', 'name': '排序', 'value': by_list}
            ],
            'dianshiju': [
                {'key': 'class', 'name': '剧情', 'value': make_cls(['古装','战争','青春偶像','喜剧','家庭','犯罪','动作','奇幻','剧情','历史','经典','乡村','情景','商战','网剧','其他'])},
                {'key': 'area', 'name': '地区', 'value': area_list},
                {'key': 'year', 'name': '年份', 'value': year_list},
                {'key': 'lang', 'name': '语言', 'value': lang_list},
                {'key': 'by', 'name': '排序', 'value': by_list}
            ],
            'zongyi': [
                {'key': 'class', 'name': '剧情', 'value': make_cls(['选秀','情感','访谈','播报','旅游','音乐','美食','纪实','曲艺','生活','游戏互动','财经','求职'])},
                {'key': 'area', 'name': '地区', 'value': area_list},
                {'key': 'year', 'name': '年份', 'value': year_list},
                {'key': 'lang', 'name': '语言', 'value': lang_list},
                {'key': 'by', 'name': '排序', 'value': by_list}
            ],
            'dongman': [
                {'key': 'class', 'name': '剧情', 'value': make_cls(['科幻','热血','推理','搞笑','冒险','萝莉','校园','动作','机战','运动','战争','少年','少女','社会','原创','亲子','益智','励志','其他'])},
                {'key': 'area', 'name': '地区', 'value': area_list},
                {'key': 'year', 'name': '年份', 'value': year_list},
                {'key': 'lang', 'name': '语言', 'value': lang_list},
                {'key': 'by', 'name': '排序', 'value': by_list}
            ],
            'donghuapian': [
                {'key': 'area', 'name': '地区', 'value': area_list},
                {'key': 'year', 'name': '年份', 'value': year_list},
                {'key': 'lang', 'name': '语言', 'value': lang_list},
                {'key': 'by', 'name': '排序', 'value': by_list}
            ],
            'duanju': [
                {'key': 'class', 'name': '剧情', 'value': make_cls(['女频恋爱','反转爽剧','年代穿越','脑洞悬疑','现代都市','古装仙侠','热血剧情'])},
                {'key': 'area', 'name': '地区', 'value': area_list},
                {'key': 'year', 'name': '年份', 'value': year_list},
                {'key': 'by', 'name': '排序', 'value': by_list}
            ]
        }

    def homeContent(self, filter):
        return {'class': self.classes, 'filters': self._get_filters()}

    def homeVideoContent(self):
        res = self.fetch(self.host, headers=self.headers)
        pattern = r'href="/voddetail/([^.]+)\.html"\s+title="([^"]+)"\s+data-original="([^"]+)".*?<span class="pic-text text-right">([^<]*)</span>'
        matches = re.findall(pattern, res.text, re.S)
        videos = []
        for m in matches:
            videos.append({
                'vod_id': m[0],
                'vod_name': m[1],
                'vod_pic': m[2] if m[2].startswith('http') else self.host + m[2],
                'vod_remarks': m[3].strip()
            })
        return {'list': videos}

    def categoryContent(self, tid, pg, filter, extend):
        area = urllib.parse.quote(extend.get('area', ''))
        by = extend.get('by', 'time')
        cls = urllib.parse.quote(extend.get('class', ''))
        lang = urllib.parse.quote(extend.get('lang', ''))
        letter = extend.get('letter', '')
        year = extend.get('year', '')
        url = f"{self.host}/vodshow/{tid}-{area}-{by}-{cls}-{lang}-{letter}---{pg}---{year}.html"
        res = self.fetch(url, headers=self.headers)
        pattern = r'href="/voddetail/([^.]+)\.html"\s+title="([^"]+)"\s+data-original="([^"]+)".*?<span class="pic-text text-right">([^<]*)</span>'
        matches = re.findall(pattern, res.text, re.S)
        videos = []
        for m in matches:
            videos.append({
                'vod_id': m[0],
                'vod_name': m[1],
                'vod_pic': m[2] if m[2].startswith('http') else self.host + m[2],
                'vod_remarks': m[3].strip()
            })
        return {'list': videos}

    def detailContent(self, ids):
        bid = ids[0]
        url = f"{self.host}/voddetail/{bid}.html"
        res = self.fetch(url, headers=self.headers)
        html = res.text
        vod = {'vod_id': bid}
        
        title_match = re.search(r'<h1 class="title">([^<]+)</h1>', html)
        if title_match:
            vod['vod_name'] = title_match.group(1).strip()
            
        pic_match = re.search(r'<a class="stui-vodlist__thumb[^>]+data-original="([^"]+)"', html)
        if not pic_match:
            pic_match = re.search(r'data-original="([^"]+)"', html)
        if pic_match:
            pic_url = pic_match.group(1)
            vod['vod_pic'] = pic_url if pic_url.startswith('http') else self.host + pic_url
            
        actor_match = re.search(r'<p class="data"><span class="text-muted">主演：</span>(.*?)</p>', html, re.S)
        if actor_match:
            vod['vod_actor'] = re.sub(r'<[^>]+>', '', actor_match.group(1)).strip()
            
        director_match = re.search(r'<p class="data"><span class="text-muted">导演：</span>(.*?)</p>', html, re.S)
        if director_match:
            vod['vod_director'] = re.sub(r'<[^>]+>', '', director_match.group(1)).strip()
            
        content_match = re.search(r'id="desc".*?<p class="col-pd">(.*?)</p>', html, re.S)
        if content_match:
            vod['vod_content'] = re.sub(r'<[^>]+>', '', content_match.group(1)).strip()

        panels = re.findall(r'class="stui-pannel-box b playlist mb"(.*?)</ul>', html, re.S)
        play_froms = []
        play_urls = []
        
        for panel in panels:
            title_match = re.search(r'<h3 class="title">.*?<img[^>]*>([^<]+)</h3>', panel, re.S)
            title = title_match.group(1).strip() if title_match else "默认线路"
            play_froms.append(title)
            
            links = re.findall(r'<a[^>]*href="([^"]+)"[^>]*>([^<]+)</a>', panel)
            ep_list = [f"{t.strip()}${l}" for l, t in links]
            play_urls.append('#'.join(ep_list))
            
        vod['vod_play_from'] = '$$$'.join(play_froms)
        vod['vod_play_url'] = '$$$'.join(play_urls)
        
        return {'list': [vod]}

    def searchContent(self, key, quick, pg="1"):
        key_enc = urllib.parse.quote(key)
        url = f"{self.host}/vodsearch/{key_enc}----------{pg}---.html"
        res = self.fetch(url, headers=self.headers)
        pattern = r'href="/voddetail/([^.]+)\.html"\s+title="([^"]+)"\s+data-original="([^"]+)".*?<span class="pic-text text-right">([^<]*)</span>'
        matches = re.findall(pattern, res.text, re.S)
        videos = []
        for m in matches:
            videos.append({
                'vod_id': m[0],
                'vod_name': m[1],
                'vod_pic': m[2] if m[2].startswith('http') else self.host + m[2],
                'vod_remarks': m[3].strip()
            })
        return {'list': videos}

    def playerContent(self, flag, id, vipFlags):
        url = self.host + id if id.startswith('/') else id
        res = self.fetch(url, headers=self.headers)
        match = re.search(r'var player_[a-zA-Z0-9]+=(.*?);?</script>', res.text)
        if match:
            try:
                player_data = json.loads(match.group(1))
                play_url = player_data.get('url', '')
                if play_url:
                    return {'parse': 0, 'url': play_url, 'header': self.headers}
            except Exception:
                pass
        return {'parse': 1, 'playUrl': '', 'url': url, 'header': self.headers}

    def destroy(self):
        pass

    def localProxy(self, param):
        return None
