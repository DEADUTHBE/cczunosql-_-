import json
import time
from urllib.parse import quote

import requests

from .SpiderRootClass import Spider

"""

:Author:    iWorld
:Create:    2021/11/19 15:30
:GitHub:    https://github.com/DEADUTHBE/cczunosqltwo
:Abstract:  微博爬虫, 通过request库以get方式获取微博热搜的JSON
"""


class WeiboSpider(Spider):
    '''
    返回的数据结构:
    {
        "ok": 1,
        "http_code": 200,
        "data": {
            "band_list": [
                {
                    "is_new": 1,                                    # 话题右侧是否加上 "新" 标识
                    "star_word": 0,
                    "word": "西安发现加拿大一枝黄花",                   # 热搜词
                    "category": "社会新闻",                          # 热搜分类
                    "num": 1778139,                                # 热度指数
                    "subject_querys": "",
                    "flag": 1,
                    "icon_desc": "新",                             # 话题右侧的标识
                    "raw_hot": 1778139,
                    "note": "西安发现加拿大一枝黄花",                  # 热度指数
                    "emoticon": "",
                    "ad_info": "",
                    "icon_desc_color": "#ff3852",
                    "realpos": 1,
                    "topic_flag": 1,
                    "mid": "4705195504962404",
                    "fun_word": 0,
                    "onboard_time": 1637305343,
                    "rank": 0,
                    "mblog": {
                        "text": "",                                # 预览文案
                        "pic_ids": [
                            "722ed599ly1gwk9aymbxej20m80go41s",
                            "722ed599ly1gwk9ayexzij20m80cu75k"
                        ],
                        "pic_num": 2,
                        "topic_struct": [
                            {
                                "title": "",
                                "topic_url": "",
                                "topic_title": "西安发现加拿大一枝黄花",
                                "is_invalid": 0
                            }
                        ]
                    }
                }
            ]
        }
    }
    '''

    def __init__(self):
        super().__init__("WeiBo")
        self.url = "https://weibo.com/ajax/statuses/hot_band"
        self.detail = "https://s.weibo.com/weibo?q=%23{}%23"
        self.picUrl = "https://wx4.sinaimg.cn/orj360/{}.jpg"

    def constructPicUrl(self, picUrl):
        picUrl = "https://wx4.sinaimg.cn/orj360/['6ab9a2f6ly1gxdhue1mbbj20zl0u0q8i', '6ab9a2f6ly1gxdhue8umaj20xa0u00ye', '6ab9a2f6ly1gxdhueig4qj21530u0te6', '6ab9a2f6ly1gxdhuepv8ij20oa10bwhg', '6ab9a2f6ly1gxdhudduocj20t707h0t6', '6ab9a2f6ly1gxdhuew6eaj20tz05uwf3', '6ab9a2f6ly1gxdhuf4budj20ti0483yu', '6ab9a2f6ly1gxdhufbiv8j20tl04fgm0', '6ab9a2f6ly1gxdhufhk9gj20tl044t92'].jpg"
        if "[" in picUrl:
            print("true")
        picUrl = picUrl.split('[')
        tempStr = picUrl[1].split(',')
        url = picUrl[0] + tempStr[0].replace("'", "")

        while "[" in url:
            url = url.replace("[", "")
        while "]" in url:
            url = url.replace("]", "")
        while "'" in url:
            url = url.replace("'", "")
        while "\\" in url:
            url = url.replace("\\", "")
        return url

    def getWeiboHot(self):
        self.req = requests.get(self.url, self.headers)
        if (self.req.status_code != 200):
            print(f"{self.req.status_code}")
            exit(-1)
        self.hotSearch = self.req.text
        self.hotSearch = json.loads(self.hotSearch)
        self.hotSearch = self.hotSearch["data"]["band_list"]

        hotDict = dict()
        rank = 0
        for hot in self.hotSearch:
            self.hot = hot
            hotDict.clear()
            # 热搜词
            hotDict["word"] = hot["word"]
            # 热度指数
            hotDict["num"] = hot["num"]
            try:
                # 预览文案
                hotDict["text"] = hot["mblog"]["text"]
                # 预览图url
                hotDict["picUrl"] = hot["mblog"]["page_info"]["page_pic"]

                if "[" in hotDict["picUrl"]:
                    print(f"处理前: {hotDict['picUrl']}")
                    hotDict["picUrl"] = self.constructPicUrl(hotDict["picUrl"])
                    print(f"处理后: {hotDict['picUrl']}")
            except:
                # 出现问题的情况只会有缺失key的情况, 这种都是插在热搜里的广告
                continue
            # 问题详情页url
            hotDict["detailUrl"] = self.detail.format(quote(hot["word"]))
            # 问题排名
            hotDict["rank"] = rank
            # 时间戳
            hotDict["timestamp"] = time.time()
            # 存入MongoDB
            self.myCol.insert_one(hotDict)
            rank += 1
        print(f"微博\t热搜已导入MongoDB - {time.asctime(time.localtime(time.time()))}")
