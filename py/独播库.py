import sys, re, json, urllib.parse
from base.spider import Spider

class Spider(Spider):
    def __init__(self):
        self.name = '独播库'
        self.host = 'https://www.dbku.tv'
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Referer': self.host
        }
        self.video_cache = {}
        self.category_cache = {'4': '动漫', '2': '剧集', '1': '电影', '3': '综艺'}

    def getName(self):
        return self.name

    def init(self, extend=""):
        pass

    def isVideoFormat(self, url):
        return False

    def manualVideoCheck(self):
        return False

    def destroy(self):
        pass

    def localProxy(self, param):
        return None

    def homeContent(self, filter):
        result = {'class': [{'type_id': k, 'type_name': v} for k, v in self.category_cache.items()]}
        if filter:
            result['filters'] = self._get_filters()
        return result

    def homeVideoContent(self):
        try:
            rsp = self.fetch(self.host, headers=self.headers)
            return {'list': self._parse_video_list(rsp.text)}
        except:
            return {'list': []}

    def categoryContent(self, tid, pg, filter, extend):
        try:
            page_num = int(pg)
            if page_num == 1 and not extend:
                url = f"{self.host}/vodtype/{tid}.html"
                cat_id = str(tid)
            else:
                cat_id = str(extend.get('tid', tid))
                area = urllib.parse.quote(extend.get('area', '')) if extend.get('area') else ''
                by = urllib.parse.quote(extend.get('by', '')) if extend.get('by') else ''
                class_name = urllib.parse.quote(extend.get('class', '')) if extend.get('class') else ''
                lang = urllib.parse.quote(extend.get('lang', '')) if extend.get('lang') else ''
                letter = extend.get('letter', '')
                year = urllib.parse.quote(extend.get('year', '')) if extend.get('year') else ''
                params = [cat_id, area, by, class_name, lang, letter, "", "", str(page_num), "", year, ""]
                url = f"{self.host}/vodshow/{'-'.join(params)}.html"
            
            rsp = self.fetch(url, headers=self.headers)
            videos = self._parse_video_list(rsp.text)
            pagecount = self._parse_pagecount(rsp.text, cat_id)
            return {'list': videos, 'page': page_num, 'pagecount': pagecount, 'limit': 20, 'total': len(videos) * pagecount}
        except:
            return {'list': []}

    def detailContent(self, ids):
        try:
            vid = ids[0]
            url = f"{self.host}/voddetail/{vid}.html"
            rsp = self.fetch(url, headers=self.headers)
            html = rsp.text
            name = self._extract_detail(html, r'<h1[^>]*>([^<]+)</h1>')
            pic = self._extract_detail(html, r'data-original="([^"]+)"')
            content = self._extract_detail(html, r'<span[^>]*class="data"[^>]*>(.*?)</span>', default='暂无简介')
            year = self._extract_detail(html, r'年份：</span><a[^>]*>(\d+)</a>')
            area = self._extract_detail(html, r'地区：</span><a[^>]*>([^<]+)</a>')
            director = self._extract_detail(html, r'导演：</span>(.*?)</p>')
            if not director:
                director = self._extract_detail(html, r'导演：</span><a[^>]*>([^<]+)</a>')
            if director:
                director = re.sub(r'<[^>]+>', '', director).strip()
            actor = self._extract_detail(html, r'主演：</span>(.*?)</p>')
            if not actor:
                actor = self._extract_detail(html, r'主演：</span><a[^>]*>([^<]+)</a>')
            if actor:
                actor = re.sub(r'<[^>]+>', '', actor).strip()
            
            play_url = []
            playlist_patterns = [
                r'<ul[^>]*class="[^"]*myui-content__list[^"]*"[^>]*>(.*?)</ul>',
                r'<div[^>]*class="[^"]*myui-panel_bd[^"]*"[^>]*>(.*?)</div>'
            ]
            for pattern in playlist_patterns:
                playlist_match = re.search(pattern, html, re.S)
                if playlist_match:
                    episode_matches = re.findall(r'<a[^>]*href="([^"]+)"[^>]*>([^<]+)</a>', playlist_match.group(1))
                    for ep_url, ep_title in episode_matches:
                        play_url.append(f"{ep_title}${self._make_full_url(ep_url)}")
                    if play_url:
                        break
            
            if not play_url:
                episode_matches = re.findall(r'<a[^>]*href="([^"]+)"[^>]*title="([^"]+)"[^>]*>', html)
                for ep_url, ep_title in episode_matches:
                    if '/vodplay/' in ep_url or '/play/' in ep_url:
                        play_url.append(f"{ep_title}${self._make_full_url(ep_url)}")
            
            vod = {
                'vod_id': vid,
                'vod_name': name,
                'vod_pic': pic,
                'vod_year': year,
                'vod_area': area,
                'vod_actor': actor if actor else "未知",
                'vod_director': director if director else "未知",
                'vod_content': content,
                'vod_play_from': '独播库',
                'vod_play_url': '#'.join(play_url) if play_url else ""
            }
            return {'list': [vod]}
        except Exception as e:
            return {'list': []}

    def searchContent(self, key, quick, pg="1"):
        try:
            page_num = int(pg)
            if page_num == 1:
                url = f"{self.host}/vodsearch/-------------.html?wd={urllib.parse.quote(key)}"
            else:
                url = f"{self.host}/vodsearch/{urllib.parse.quote(key)}------------{page_num}---.html"
            rsp = self.fetch(url, headers=self.headers)
            videos = self._parse_video_list(rsp.text)
            return {'list': videos, 'page': page_num, 'pagecount': 10}
        except:
            return {'list': []}

    def playerContent(self, flag, id, vipFlags):
        return {'parse': 1, 'url': id, 'header': self.headers}

    def _parse_video_list(self, html):
        videos = []
        pattern = r'<a[^>]*class="[^"]*myui-vodlist__thumb[^"]*"[^>]*href="/voddetail/(\d+)\.html"[^>]*title="([^"]*)"[^>]*data-original="([^"]*)"'
        for match in re.finditer(pattern, html):
            vid, name, pic = match.groups()
            remark = ""
            end_pos = match.end()
            snippet = html[end_pos:end_pos+500]
            remark_match = re.search(r'<span[^>]*class="pic-text[^"]*"[^>]*>([^<]*)</span>', snippet)
            if remark_match:
                remark = remark_match.group(1).strip()
            videos.append({'vod_id': vid, 'vod_name': name, 'vod_pic': pic, 'vod_remarks': remark})
        return videos

    def _parse_pagecount(self, html, tid):
        page_patterns = [
            r'href="/vodshow/' + re.escape(tid) + r'-+(\d+)---\.html"',
            r'page=(\d+)',
            r'(\d+)</a>\s*</li>\s*<li[^>]*><a[^>]*>下一页'
        ]
        max_page = 1
        for pattern in page_patterns:
            pages = re.findall(pattern, html)
            if pages:
                try:
                    max_page = max(max_page, max(int(p) for p in pages if p.isdigit()))
                except:
                    pass
        return max_page

    def _extract_detail(self, html, pattern, default=''):
        match = re.search(pattern, html, re.S)
        return match.group(1).strip() if match else default

    def _make_full_url(self, url):
        if url.startswith('http'):
            return url
        return f"{self.host}{url}" if url.startswith('/') else f"{self.host}/{url}"

    def _get_filters(self):
        return {
            "1": [
                {"key": "class", "name": "剧情", "value": [{"n": "全部", "v": ""}, {"n": "喜剧", "v": "喜剧"}, {"n": "爱情", "v": "爱情"}, {"n": "恐怖", "v": "恐怖"}, {"n": "动作", "v": "动作"}, {"n": "科幻", "v": "科幻"}, {"n": "剧情", "v": "剧情"}, {"n": "警匪", "v": "警匪"}, {"n": "战争", "v": "战争"}, {"n": "犯罪", "v": "犯罪"}, {"n": "动画", "v": "动画"}, {"n": "奇幻", "v": "奇幻"}, {"n": "武侠", "v": "武侠"}, {"n": "冒险", "v": "冒险"}, {"n": "悬疑", "v": "悬疑"}, {"n": "惊悚", "v": "惊悚"}, {"n": "古装", "v": "古装"}, {"n": "同性", "v": "同性"}]},
                {"key": "area", "name": "地区", "value": [{"n": "全部", "v": ""}, {"n": "大陆", "v": "大陆"}, {"n": "香港", "v": "香港"}, {"n": "台湾", "v": "台湾"}, {"n": "韩国", "v": "韩国"}, {"n": "英国", "v": "英国"}, {"n": "法国", "v": "法国"}, {"n": "加拿大", "v": "加拿大"}, {"n": "澳大利亚", "v": "澳大利亚"}]},
                {"key": "year", "name": "年份", "value": [{"n": "全部", "v": ""}, {"n": "2026", "v": "2026"}, {"n": "2025", "v": "2025"}, {"n": "2024", "v": "2024"}, {"n": "2023", "v": "2023"}, {"n": "2022", "v": "2022"}, {"n": "2020", "v": "2020"}, {"n": "2019", "v": "2019"}]},
                {"key": "lang", "name": "语言", "value": [{"n": "全部", "v": ""}, {"n": "国语", "v": "国语"}, {"n": "粤语", "v": "粤语"}, {"n": "韩语", "v": "韩语"}, {"n": "英语", "v": "英语"}, {"n": "法语", "v": "法语"}]},
                {"key": "letter", "name": "字母", "value": [{"n": "全部", "v": ""}, {"n": "A", "v": "A"}, {"n": "B", "v": "B"}, {"n": "C", "v": "C"}, {"n": "D", "v": "D"}, {"n": "E", "v": "E"}, {"n": "F", "v": "F"}, {"n": "G", "v": "G"}, {"n": "H", "v": "H"}, {"n": "I", "v": "I"}, {"n": "J", "v": "J"}, {"n": "K", "v": "K"}, {"n": "L", "v": "L"}, {"n": "M", "v": "M"}, {"n": "N", "v": "N"}, {"n": "O", "v": "O"}, {"n": "P", "v": "P"}, {"n": "Q", "v": "Q"}, {"n": "R", "v": "R"}, {"n": "S", "v": "S"}, {"n": "T", "v": "T"}, {"n": "U", "v": "U"}, {"n": "V", "v": "V"}, {"n": "W", "v": "W"}, {"n": "X", "v": "X"}, {"n": "Y", "v": "Y"}, {"n": "Z", "v": "Z"}, {"n": "0~9", "v": "0~9"}]},
                {"key": "by", "name": "排序", "value": [{"n": "时间", "v": ""}, {"n": "人气", "v": "人气"}, {"n": "评分", "v": "评分"}]}
            ],
            "2": [
                {"key": "tid", "name": "类型", "value": [{"n": "全部", "v": "2"}, {"n": "陆剧", "v": "13"}, {"n": "日韩剧", "v": "15"}, {"n": "短剧", "v": "21"}, {"n": "台泰剧", "v": "14"}, {"n": "港剧", "v": "20"}]},
                {"key": "class", "name": "剧情", "value": [{"n": "全部", "v": ""}, {"n": "悬疑", "v": "悬疑"}, {"n": "武侠", "v": "武侠"}, {"n": "科幻", "v": "科幻"}, {"n": "都市", "v": "都市"}, {"n": "爱情", "v": "爱情"}, {"n": "古装", "v": "古装"}, {"n": "战争", "v": "战争"}, {"n": "青春", "v": "青春"}, {"n": "偶像", "v": "偶像"}, {"n": "喜剧", "v": "喜剧"}, {"n": "家庭", "v": "家庭"}, {"n": "奇幻", "v": "奇幻"}, {"n": "剧情", "v": "剧情"}, {"n": "乡村", "v": "乡村"}, {"n": "年代", "v": "年代"}, {"n": "警匪", "v": "警匪"}, {"n": "谍战", "v": "谍战"}, {"n": "历险", "v": "历险"}, {"n": "罪案", "v": "罪案"}, {"n": "宫廷", "v": "宫廷"}, {"n": "经典", "v": "经典"}, {"n": "动作", "v": "动作"}, {"n": "惊悚", "v": "惊悚"}, {"n": "历史", "v": "历史"}, {"n": "穿越", "v": "穿越"}, {"n": "同性", "v": "同性"}]},
                {"key": "area", "name": "地区", "value": [{"n": "全部", "v": ""}, {"n": "大陆", "v": "大陆"}, {"n": "香港", "v": "香港"}, {"n": "台湾", "v": "台湾"}, {"n": "韩国", "v": "韩国"}, {"n": "日本", "v": "日本"}, {"n": "新加坡", "v": "新加坡"}, {"n": "泰国", "v": "泰国"}]},
                {"key": "year", "name": "年份", "value": [{"n": "全部", "v": ""}, {"n": "2026", "v": "2026"}, {"n": "2025", "v": "2025"}, {"n": "2024", "v": "2024"}, {"n": "2023", "v": "2023"}, {"n": "2022", "v": "2022"}, {"n": "2021", "v": "2021"}, {"n": "2020", "v": "2020"}, {"n": "2019", "v": "2019"}, {"n": "2018", "v": "2018"}, {"n": "2017", "v": "2017"}, {"n": "更早", "v": "更早"}]},
                {"key": "lang", "name": "语言", "value": [{"n": "全部", "v": ""}, {"n": "国语", "v": "国语"}, {"n": "粤语", "v": "粤语"}, {"n": "韩语", "v": "韩语"}, {"n": "泰语", "v": "泰语"}, {"n": "日语", "v": "日语"}]},
                {"key": "letter", "name": "字母", "value": [{"n": "全部", "v": ""}, {"n": "A", "v": "A"}, {"n": "B", "v": "B"}, {"n": "C", "v": "C"}, {"n": "D", "v": "D"}, {"n": "E", "v": "E"}, {"n": "F", "v": "F"}, {"n": "G", "v": "G"}, {"n": "H", "v": "H"}, {"n": "I", "v": "I"}, {"n": "J", "v": "J"}, {"n": "K", "v": "K"}, {"n": "L", "v": "L"}, {"n": "M", "v": "M"}, {"n": "N", "v": "N"}, {"n": "O", "v": "O"}, {"n": "P", "v": "P"}, {"n": "Q", "v": "Q"}, {"n": "R", "v": "R"}, {"n": "S", "v": "S"}, {"n": "T", "v": "T"}, {"n": "U", "v": "U"}, {"n": "V", "v": "V"}, {"n": "W", "v": "W"}, {"n": "X", "v": "X"}, {"n": "Y", "v": "Y"}, {"n": "Z", "v": "Z"}, {"n": "0~9", "v": "0~9"}]},
                {"key": "by", "name": "排序", "value": [{"n": "时间", "v": ""}, {"n": "人气", "v": "人气"}, {"n": "评分", "v": "评分"}]}
            ],
            "3": [
                {"key": "class", "name": "剧情", "value": [{"n": "全部", "v": ""}, {"n": "真人秀", "v": "真人秀"}, {"n": "选秀", "v": "选秀"}, {"n": "竞演", "v": "竞演"}, {"n": "情感", "v": "情感"}, {"n": "旅游", "v": "旅游"}, {"n": "音乐", "v": "音乐"}, {"n": "美食", "v": "美食"}, {"n": "纪实", "v": "纪实"}, {"n": "生活", "v": "生活"}, {"n": "游戏互动", "v": "游戏互动"}, {"n": "竞技", "v": "竞技"}, {"n": "搞笑", "v": "搞笑"}, {"n": "脱口秀", "v": "脱口秀"}]},
                {"key": "area", "name": "地区", "value": [{"n": "全部", "v": ""}, {"n": "大陆", "v": "大陆"}, {"n": "韩国", "v": "韩国"}]},
                {"key": "year", "name": "年份", "value": [{"n": "全部", "v": ""}, {"n": "2026", "v": "2026"}, {"n": "2025", "v": "2025"}, {"n": "2024", "v": "2024"}, {"n": "2023", "v": "2023"}, {"n": "2022", "v": "2022"}, {"n": "2021", "v": "2021"}, {"n": "2020", "v": "2020"}, {"n": "2019", "v": "2019"}, {"n": "更早", "v": "更早"}]},
                {"key": "lang", "name": "语言", "value": [{"n": "全部", "v": ""}, {"n": "国语", "v": "国语"}, {"n": "韩语", "v": "韩语"}]},
                {"key": "letter", "name": "字母", "value": [{"n": "全部", "v": ""}, {"n": "A", "v": "A"}, {"n": "B", "v": "B"}, {"n": "C", "v": "C"}, {"n": "D", "v": "D"}, {"n": "E", "v": "E"}, {"n": "F", "v": "F"}, {"n": "G", "v": "G"}, {"n": "H", "v": "H"}, {"n": "I", "v": "I"}, {"n": "J", "v": "J"}, {"n": "K", "v": "K"}, {"n": "L", "v": "L"}, {"n": "M", "v": "M"}, {"n": "N", "v": "N"}, {"n": "O", "v": "O"}, {"n": "P", "v": "P"}, {"n": "Q", "v": "Q"}, {"n": "R", "v": "R"}, {"n": "S", "v": "S"}, {"n": "T", "v": "T"}, {"n": "U", "v": "U"}, {"n": "V", "v": "V"}, {"n": "W", "v": "W"}, {"n": "X", "v": "X"}, {"n": "Y", "v": "Y"}, {"n": "Z", "v": "Z"}, {"n": "0~9", "v": "0~9"}]},
                {"key": "by", "name": "排序", "value": [{"n": "时间", "v": ""}, {"n": "人气", "v": "人气"}, {"n": "评分", "v": "评分"}]}
            ],
            "4": [
                {"key": "class", "name": "剧情", "value": [{"n": "全部", "v": ""}, {"n": "武侠", "v": "武侠"}, {"n": "科幻", "v": "科幻"}, {"n": "热血", "v": "热血"}, {"n": "推理", "v": "推理"}, {"n": "爆笑", "v": "爆笑"}, {"n": "冒险", "v": "冒险"}, {"n": "校园", "v": "校园"}, {"n": "动作", "v": "动作"}, {"n": "机战", "v": "机战"}, {"n": "竞技", "v": "竞技"}, {"n": "少女", "v": "少女"}, {"n": "格斗", "v": "格斗"}, {"n": "恋爱", "v": "恋爱"}, {"n": "魔幻", "v": "魔幻"}]},
                {"key": "area", "name": "地区", "value": [{"n": "全部", "v": ""}, {"n": "大陆", "v": "大陆"}, {"n": "日本", "v": "日本"}, {"n": "法国", "v": "法国"}, {"n": "美国", "v": "美国"}]},
                {"key": "year", "name": "年份", "value": [{"n": "全部", "v": ""}, {"n": "2026", "v": "2026"}, {"n": "2025", "v": "2025"}, {"n": "2024", "v": "2024"}, {"n": "2023", "v": "2023"}, {"n": "2022", "v": "2022"}, {"n": "2021", "v": "2021"}, {"n": "2020", "v": "2020"}, {"n": "2019", "v": "2019"}, {"n": "2018", "v": "2018"}, {"n": "2017", "v": "2017"}, {"n": "2015", "v": "2015"}]},
                {"key": "lang", "name": "语言", "value": [{"n": "全部", "v": ""}, {"n": "国语", "v": "国语"}, {"n": "日语", "v": "日语"}, {"n": "英语", "v": "英语"}]},
                {"key": "letter", "name": "字母", "value": [{"n": "全部", "v": ""}, {"n": "A", "v": "A"}, {"n": "B", "v": "B"}, {"n": "C", "v": "C"}, {"n": "D", "v": "D"}, {"n": "E", "v": "E"}, {"n": "F", "v": "F"}, {"n": "G", "v": "G"}, {"n": "H", "v": "H"}, {"n": "I", "v": "I"}, {"n": "J", "v": "J"}, {"n": "K", "v": "K"}, {"n": "L", "v": "L"}, {"n": "M", "v": "M"}, {"n": "N", "v": "N"}, {"n": "O", "v": "O"}, {"n": "P", "v": "P"}, {"n": "Q", "v": "Q"}, {"n": "R", "v": "R"}, {"n": "S", "v": "S"}, {"n": "T", "v": "T"}, {"n": "U", "v": "U"}, {"n": "V", "v": "V"}, {"n": "W", "v": "W"}, {"n": "X", "v": "X"}, {"n": "Y", "v": "Y"}, {"n": "Z", "v": "Z"}, {"n": "0~9", "v": "0~9"}]},
                {"key": "by", "name": "排序", "value": [{"n": "时间", "v": ""}, {"n": "人气", "v": "人气"}, {"n": "评分", "v": "评分"}]}
            ]
        }
