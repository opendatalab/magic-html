# magic-html - 通用HTML数据提取器

欢迎使用magic-html，这是一个旨在简化从HTML中提取主体区域内容的Python库。



## 项目描述

magic-html提供了一套工具，能够轻松地从HTML中提取主体区域内容。无论您处理的是复杂的HTML结构还是简单的网页，这个库都旨在为您的HTML抽取需求提供一个便捷高效的接口。



## 特点

- 返回主体区域html结构，可自定义输出纯文本/markdown
- 支持多模态抽取
- 支持多种版面extractor，文章/论坛
- 支持latex公式提取转换



## 安装

```shell
pip install https://github.com/opendatalab/magic-html/releases/download/magic_html-0.1.2-released/magic_html-0.1.2-py3-none-any.whl
```



## 使用

```python
from magic_html import GeneralExtractor

# 初始化提取器
extractor = GeneralExtractor()

url = "http://example.com/"
html = """

<!doctype html>
<html>
<head>
    <title>Example Domain</title>

    <meta charset="utf-8" />
    <meta http-equiv="Content-type" content="text/html; charset=utf-8" />
    <meta name="viewport" content="width=device-width, initial-scale=1" />  
</head>

<body>
<div>
    <h1>Example Domain</h1>
    <p>This domain is for use in illustrative examples in documents. You may use this
    domain in literature without prior coordination or asking for permission.</p>
    <p><a href="https://www.iana.org/domains/example">More information...</a></p>
</div>
</body>
</html>
"""

# 文章类型HTML提取数据
data = extractor.extract(html, base_url=url)

# 论坛类型HTML提取数据
# data = extractor.extract(html, base_url=url, html_type="forum")

# 微信文章HTML提取数据
# data = extractor.extract(html, base_url=url, html_type="weixin")

print(data)
```



## benchmark report

根据html页面类型，文章/论坛，对比不同开源通用抽取框架抽取准确性

文章类型：选取头部新闻、博客站点共标注158个html页面

```Python
╒══════════════════════╤═════════════╤════════════╤═══════════╕
│ func                 │   prec_mean │   rec_mean │   f1_mean │
╞══════════════════════╪═════════════╪════════════╪═══════════╡
│ magic_html           │    0.908865 │   0.95032  │  0.92913  │
├──────────────────────┼─────────────┼────────────┼───────────┤
│ trafilatura          │    0.833434 │   0.912384 │  0.871124 │
├──────────────────────┼─────────────┼────────────┼───────────┤
│ trafilatura_fallback │    0.831229 │   0.933713 │  0.879496 │
├──────────────────────┼─────────────┼────────────┼───────────┤
│ readability-lxml     │    0.86587  │   0.861391 │  0.863625 │
├──────────────────────┼─────────────┼────────────┼───────────┤
│ newspaper3k          │    0.409585 │   0.372083 │  0.389935 │
├──────────────────────┼─────────────┼────────────┼───────────┤
│ goose3               │    0.525717 │   0.457669 │  0.489339 │
├──────────────────────┼─────────────┼────────────┼───────────┤
│ justext              │    0.224945 │   0.117092 │  0.154014 │
├──────────────────────┼─────────────┼────────────┼───────────┤
│ gne                  │    0.828849 │   0.629112 │  0.715299 │
╘══════════════════════╧═════════════╧════════════╧═══════════╛
```



论坛类型：选取头部论坛、问答站点与开源建站框架搭建站点共103个html页面

```Python
╒══════════════════════╤═════════════╤════════════╤═══════════╕
│ func                 │   prec_mean │   rec_mean │   f1_mean │
╞══════════════════════╪═════════════╪════════════╪═══════════╡
│ magic_html           │    0.796252 │  0.826819  │ 0.811248  │
├──────────────────────┼─────────────┼────────────┼───────────┤
│ trafilatura          │    0.716009 │  0.695947  │ 0.705835  │
├──────────────────────┼─────────────┼────────────┼───────────┤
│ trafilatura_fallback │    0.730304 │  0.691328  │ 0.710282  │
├──────────────────────┼─────────────┼────────────┼───────────┤
│ readability-lxml     │    0.788018 │  0.445087  │ 0.568867  │
├──────────────────────┼─────────────┼────────────┼───────────┤
│ newspaper3k          │    0.596976 │  0.298322  │ 0.397837  │
├──────────────────────┼─────────────┼────────────┼───────────┤
│ goose3               │    0.675835 │  0.312969  │ 0.427821  │
├──────────────────────┼─────────────┼────────────┼───────────┤
│ justext              │    0.175889 │  0.0517628 │ 0.0799863 │
├──────────────────────┼─────────────┼────────────┼───────────┤
│ gne                  │    0.81003  │  0.389709  │ 0.526241  │
╘══════════════════════╧═════════════╧════════════╧═══════════╛
```



## 许可

本项目代码采用[Apache 2.0 license](https://www.apache.org/licenses/LICENSE-2.0.html)授权。



## 鸣谢

- [trafilatura](https://github.com/adbar/trafilatura)
- [readability-lxml](https://github.com/buriy/python-readability)

