# magic-html - 通用HTML数据提取器

欢迎使用magic-html，这是一个旨在简化从HTML中提取主体区域内容的Python库。



## 项目描述

magic-html提供了一套工具，能够轻松地从HTML中提取主体区域内容。无论您处理的是复杂的HTML结构还是简单的网页，这个库都旨在为您的HTML抽取需求提供一个便捷高效的接口。



## 特点

- 返回主体区域html结构，可自定义输出纯文本/markdown
- 支持多模态抽取
- 支持多种版面extractor，文章/论坛
- 支持latex公式提取转换



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



## 许可

本项目代码采用[Apache 2.0 license](https://www.apache.org/licenses/LICENSE-2.0.html)授权。



## 鸣谢

- [trafilatura](https://github.com/adbar/trafilatura)
- [readability-lxml](https://github.com/buriy/python-readability)

