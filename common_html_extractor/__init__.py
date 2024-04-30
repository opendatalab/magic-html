# -*- coding: utf-8 -*-

from urllib.parse import urlparse

from common_html_extractor.extractors import *


class GeneralExtractor:
    def extract(self, html="", **kwargs) -> dict:
        base_url = kwargs.get("base_url", "")
        html_type = kwargs.pop("html_type", None)
        if html_type:
            if html_type == "forum":
                return ForumExtractor().extract(html=html, **kwargs)
            elif html_type == "weixin":
                return WeixinExtractor().extract(html=html, **kwargs)
        if base_url:
            if urlparse(base_url).netloc == "mp.weixin.qq.com":
                return WeixinExtractor().extract(html=html, **kwargs)
        return ArticleExtractor().extract(html=html, **kwargs)
