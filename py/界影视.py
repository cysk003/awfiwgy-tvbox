import hashlib
import re
import sys
import time
import requests
sys.path.append('..')
from base.spider import Spider

class Spider(Spider):
    def getName(self):
        return "JieYingShi"

    def init(self, extend):
        self.home_url = 'https://m.jiabaide.cn'
        self.error_url = 'https://json.doube.eu.org/error/4gtv/index.m3u8'
        self.headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36",
        }

    def getDependence(self):
        return []

    def isVideoFormat(self, url):
        pass

    def manualVideoCheck(self):
        pass

    def homeContent(self, filter):
        classes = [
            {'type_id': '4', 'type_name': '动漫'},
            {'type_id': '2', 'type_name': '电视剧'},
            {'type_id': '1', 'type_name': '电影'},
            {'type_id': '3', 'type_name': '综艺'}
        ]
        filters = {
            "1": [{"key": "type", "name": "类型", "value": [{"n": "全部", "v": ""}, {"n": "喜剧", "v": "22"}, {"n": "动作", "v": "23"}, {"n": "科幻", "v": "30"}, {"n": "爱情", "v": "26"}, {"n": "悬疑", "v": "27"}, {"n": "奇幻", "v": "87"}, {"n": "剧情", "v": "37"}, {"n": "恐怖", "v": "36"}, {"n": "犯罪", "v": "35"}, {"n": "动画", "v": "33"}, {"n": "惊悚", "v": "34"}, {"n": "战争", "v": "25"}, {"n": "冒险", "v": "31"}, {"n": "灾难", "v": "81"}, {"n": "伦理", "v": "83"}, {"n": "其他", "v": "43"}]}, {"key": "class", "name": "剧情", "value": [{"n": "全部", "v": ""}, {"n": "爱情", "v": "爱情"}, {"n": "动作", "v": "动作"}, {"n": "喜剧", "v": "喜剧"}, {"n": "战争", "v": "战争"}, {"n": "科幻", "v": "科幻"}, {"n": "剧情", "v": "剧情"}, {"n": "武侠", "v": "武侠"}, {"n": "冒险", "v": "冒险"}, {"n": "枪战", "v": "枪战"}, {"n": "恐怖", "v": "恐怖"}, {"n": "其他", "v": "其他"}]}, {"key": "area", "name": "地区", "value": [{"n": "全部", "v": ""}, {"n": "中国大陆", "v": "中国大陆"}, {"n": "中国香港", "v": "中国香港"}, {"n": "中国台湾", "v": "中国台湾"}, {"n": "美国", "v": "美国"}, {"n": "日本", "v": "日本"}, {"n": "韩国", "v": "韩国"}, {"n": "印度", "v": "印度"}, {"n": "泰国", "v": "泰国"}, {"n": "英国", "v": "英国"}, {"n": "法国", "v": "法国"}, {"n": "其他", "v": "其他"}]}, {"key": "year", "name": "年份", "value": [{"n": "全部", "v": ""}, {"n": "2026", "v": "2026"}, {"n": "2025", "v": "2025"}, {"n": "2024", "v": "2024"}, {"n": "2023", "v": "2023"}, {"n": "2022", "v": "2022"}, {"n": "2021", "v": "2021"}, {"n": "2020", "v": "2020"}, {"n": "2019", "v": "2019"}, {"n": "2018", "v": "2018"}, {"n": "2017", "v": "2017"}, {"n": "2016", "v": "2016"}, {"n": "2015", "v": "2015"}, {"n": "2014", "v": "2014"}, {"n": "2013", "v": "2013"}, {"n": "2012", "v": "2012"}, {"n": "2011", "v": "2011"}, {"n": "2010", "v": "2010"}, {"n": "2009~2000", "v": "2009~2000"}]}, {"key": "lang", "name": "语言", "value": [{"n": "全部", "v": ""}, {"n": "国语", "v": "国语"}, {"n": "英语", "v": "英语"}, {"n": "粤语", "v": "粤语"}, {"n": "韩语", "v": "韩语"}, {"n": "日语", "v": "日语"}, {"n": "其他", "v": "其他"}]}],
            "2": [{"key": "type", "name": "类型", "value": [{"n": "全部", "v": ""}, {"n": "国产剧", "v": "14"}, {"n": "欧美剧", "v": "15"}, {"n": "港台剧", "v": "16"}, {"n": "日韩剧", "v": "62"}, {"n": "其他剧", "v": "68"}]}, {"key": "class", "name": "剧情", "value": [{"n": "全部", "v": ""}, {"n": "古装", "v": "古装"}, {"n": "战争", "v": "战争"}, {"n": "喜剧", "v": "喜剧"}, {"n": "家庭", "v": "家庭"}, {"n": "犯罪", "v": "犯罪"}, {"n": "动作", "v": "动作"}, {"n": "奇幻", "v": "奇幻"}, {"n": "剧情", "v": "剧情"}, {"n": "历史", "v": "历史"}, {"n": "短片", "v": "短片"}, {"n": "其他", "v": "其他"}]}, {"key": "area", "name": "地区", "value": [{"n": "全部", "v": ""}, {"n": "中国大陆", "v": "中国大陆"}, {"n": "中国香港", "v": "中国香港"}, {"n": "中国台湾", "v": "中国台湾"}, {"n": "日本", "v": "日本"}, {"n": "韩国", "v": "韩国"}, {"n": "美国", "v": "美国"}, {"n": "泰国", "v": "泰国"}, {"n": "其他", "v": "其他"}]}, {"key": "year", "name": "年份", "value": [{"n": "全部", "v": ""}, {"n": "2026", "v": "2026"}, {"n": "2025", "v": "2025"}, {"n": "2024", "v": "2024"}, {"n": "2023", "v": "2023"}, {"n": "2022", "v": "2022"}, {"n": "2021", "v": "2021"}, {"n": "2020", "v": "2020"}, {"n": "2019", "v": "2019"}, {"n": "2018", "v": "2018"}, {"n": "2017", "v": "2017"}, {"n": "2016", "v": "2016"}, {"n": "2015", "v": "2015"}, {"n": "2014", "v": "2014"}, {"n": "2013", "v": "2013"}, {"n": "2012", "v": "2012"}, {"n": "2011", "v": "2011"}, {"n": "2010", "v": "2010"}]}, {"key": "lang", "name": "语言", "value": [{"n": "全部", "v": ""}, {"n": "国语", "v": "国语"}, {"n": "英语", "v": "英语"}, {"n": "粤语", "v": "粤语"}, {"n": "韩语", "v": "韩语"}, {"n": "日语", "v": "日语"}, {"n": "泰语", "v": "泰语"}, {"n": "其他", "v": "其他"}]}],
            "3": [{"key": "type", "name": "类型", "value": [{"n": "全部", "v": ""}, {"n": "国产综艺", "v": "69"}, {"n": "港台综艺", "v": "70"}, {"n": "日韩综艺", "v": "72"}, {"n": "欧美综艺", "v": "73"}]}, {"key": "class", "name": "剧情", "value": [{"n": "全部", "v": ""}, {"n": "真人秀", "v": "真人秀"}, {"n": "音乐", "v": "音乐"}, {"n": "脱口秀", "v": "脱口秀"}]}, {"key": "area", "name": "地区", "value": [{"n": "全部", "v": ""}, {"n": "中国大陆", "v": "中国大陆"}, {"n": "中国香港", "v": "中国香港"}, {"n": "中国台湾", "v": "中国台湾"}, {"n": "日本", "v": "日本"}, {"n": "韩国", "v": "韩国"}, {"n": "美国", "v": "美国"}, {"n": "其他", "v": "其他"}]}, {"key": "year", "name": "年份", "value": [{"n": "全部", "v": ""}, {"n": "2026", "v": "2026"}, {"n": "2025", "v": "2025"}, {"n": "2024", "v": "2024"}, {"n": "2023", "v": "2023"}, {"n": "2022", "v": "2022"}, {"n": "2021", "v": "2021"}, {"n": "2020", "v": "2020"}]}, {"key": "lang", "name": "语言", "value": [{"n": "全部", "v": ""}, {"n": "国语", "v": "国语"}, {"n": "英语", "v": "英语"}, {"n": "粤语", "v": "粤语"}, {"n": "韩语", "v": "韩语"}, {"n": "日语", "v": "日语"}, {"n": "其他", "v": "其他"}]}],
            "4": [{"key": "type", "name": "类型", "value": [{"n": "全部", "v": ""}, {"n": "国产动漫", "v": "75"}, {"n": "日韩动漫", "v": "76"}, {"n": "欧美动漫", "v": "77"}]}, {"key": "class", "name": "剧情", "value": [{"n": "全部", "v": ""}, {"n": "喜剧", "v": "喜剧"}, {"n": "科幻", "v": "科幻"}, {"n": "热血", "v": "热血"}, {"n": "冒险", "v": "冒险"}, {"n": "动作", "v": "动作"}, {"n": "运动", "v": "运动"}, {"n": "战争", "v": "战争"}, {"n": "动画", "v": "动画"}]}, {"key": "area", "name": "地区", "value": [{"n": "全部", "v": ""}, {"n": "中国大陆", "v": "中国大陆"}, {"n": "日本", "v": "日本"}, {"n": "美国", "v": "美国"}, {"n": "其他", "v": "其他"}]}, {"key": "year", "name": "年份", "value": [{"n": "全部", "v": ""}, {"n": "2026", "v": "2026"}, {"n": "2025", "v": "2025"}, {"n": "2024", "v": "2024"}, {"n": "2023", "v": "2023"}, {"n": "2022", "v": "2022"}, {"n": "2021", "v": "2021"}, {"n": "2020", "v": "2020"}, {"n": "2019", "v": "2019"}, {"n": "2018", "v": "2018"}, {"n": "2017", "v": "2017"}, {"n": "2016", "v": "2016"}, {"n": "2015", "v": "2015"}, {"n": "2014", "v": "2014"}, {"n": "2013", "v": "2013"}, {"n": "2012", "v": "2012"}, {"n": "2011", "v": "2011"}, {"n": "2010", "v": "2010"}]}, {"key": "lang", "name": "语言", "value": [{"n": "全部", "v": ""}, {"n": "国语", "v": "国语"}, {"n": "英语", "v": "英语"}, {"n": "日语", "v": "日语"}, {"n": "其他", "v": "其他"}]}]
        }
        return {'class': classes, 'filters': filters}

    def homeVideoContent(self):
        a = self.get_data(self.home_url)
        return {'list': a, 'parse': 0, 'jx': 0}

    def categoryContent(self, cid, page, filter, ext):
        ext_str = ''
        for key in ['lang', 'year', 'area', 'type', 'class']:
            if ext.get(key):
                ext_str += f'/{key}/{ext[key]}'
        url = self.home_url + f'/vod/show/id/{cid}{ext_str}/page/{page}'
        data = self.get_data(url)
        return {'list': data, 'parse': 0, 'jx': 0}

    def detailContent(self, did):
        ids = did[0]
        data = self.get_detail_data(ids)
        return {"list": data, 'parse': 0, 'jx': 0}

    def searchContent(self, key, quick, page='1'):
        if int(page) > 1:
            return {'list': [], 'parse': 0, 'jx': 0}
        url = self.home_url + f'/vod/search/{key}'
        data = self.get_data(url)
        return {'list': data, 'parse': 0, 'jx': 0}

    def playerContent(self, flag, pid, vipFlags):
        url = self.get_play_data(pid)
        return {"url": url, "header": self.headers, "parse": 1, "jx": 0}

    def localProxy(self, params):
        pass

    def destroy(self):
        return '正在Destroy'

    def get_data(self, url):
        data = []
        try:
            res = requests.get(url, headers=self.headers)
            if res.status_code != 200:
                return data
            vod_id_s = re.findall(r'\\"vodId\\":(.*?),', res.text)
            vod_name_s = re.findall(r'\\"vodName\\":\\"(.*?)\\"', res.text)
            vod_pic_s = re.findall(r'\\"vodPic\\":\\"(.*?)\\"', res.text)
            vod_remarks_s = re.findall(r'\\"vodRemarks\\":\\"(.*?)\\"', res.text)

            for i in range(len(vod_id_s)):
                data.append(
                    {
                        'vod_id': vod_id_s[i],
                        'vod_name': vod_name_s[i],
                        'vod_pic': vod_pic_s[i],
                        'vod_remarks': vod_remarks_s[i],
                    }
                )
        except requests.RequestException as e:
            print(e)
        return data

    def get_detail_data(self, ids):
        url = self.home_url + f'/api/mw-movie/anonymous/video/detail?id={ids}'
        t = str(int(time.time() * 1000))
        headers = self.get_headers(t, f'id={ids}&key=cb808529bae6b6be45ecfab29a4889bc&t={t}')
        try:
            res = requests.get(url, headers=headers)
            if res.status_code != 200:
                return []
            i = res.json()['data']
            urls = []
            for ii in res.json()['data']['episodeList']:
                name = ii['name']
                url = ii['nid']
                urls.append(f'{name}${ids}-{url}')
            data = {
                'type_name': i['vodClass'],
                'vod_id': i['vodId'],
                'vod_name': i['vodName'],
                'vod_remarks': i['vodRemarks'],
                'vod_year': i['vodYear'],
                'vod_area': i['vodArea'],
                'vod_actor': i['vodActor'],
                'vod_director': i['vodDirector'],
                'vod_content': i['vodContent'],
                'vod_play_from': '默认',
                'vod_play_url': '#'.join(urls),

            }
            return [data]

        except requests.RequestException as e:
            print(e)
        return []

    def get_play_data(self, play):
        info = play.split('-')
        _id = info[0]
        _pid = info[1]
        url = self.home_url + f'/api/mw-movie/anonymous/v2/video/episode/url?id={_id}&nid={_pid}'
        t = str(int(time.time() * 1000))
        headers = self.get_headers(t, f'id={_id}&nid={_pid}&key=cb808529bae6b6be45ecfab29a4889bc&t={t}')
        try:
            res = requests.get(url, headers=headers)
            if res.status_code != 200:
                return self.error_url
            return res.json()['data']['list'][0]['url']
        except requests.RequestException as e:
            print(e)
        return self.error_url

    @staticmethod
    def get_headers(t, e):
        sign = hashlib.sha1(hashlib.md5(e.encode()).hexdigest().encode()).hexdigest()
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36',
            'Accept': 'application/json, text/plain, */*',
            'sign': sign,
            'sec-ch-ua': '"Google Chrome";v="131", "Chromium";v="131", "Not_A Brand";v="24"',
            't': t,
            'referer': 'https://m.jiabaide.cn/',
        }
        return headers

if __name__ == '__main__':
    pass
