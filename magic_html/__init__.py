# -*- coding: utf-8 -*-

from urllib.parse import urlparse
from magic_html.extractors.article_extractor import ArticleExtractor
from magic_html.extractors.weixin_extractor import WeixinExtractor
from magic_html.extractors.forum_extractor import ForumExtractor


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
