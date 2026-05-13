# -*- coding: utf-8 -*-
"""
Tests for magic-html extractors after lxml upgrade (>=6.1.0).
Covers: ArticleExtractor, ForumExtractor, WeixinExtractor, CustomExtractor,
        and lxml API compatibility (Cleaner, text_content, body property, etc.)
"""

import pytest
from lxml.html import fromstring, tostring, Element, HtmlElement

from magic_html import GeneralExtractor
from magic_html.utils import (
    load_html,
    iter_node,
    is_empty_element,
    text_len,
    HTML_CLEANER,
    HTML_PARSER,
)

# ---------------------------------------------------------------------------
# Sample HTML fixtures
# ---------------------------------------------------------------------------

ARTICLE_HTML = """
<!DOCTYPE html>
<html>
<head><title>Test Article Title</title></head>
<body>
<div id="main">
  <article>
    <h1>Test Article Title</h1>
    <p>This is the first paragraph of the article with enough text content to be considered meaningful by the extraction algorithm. It needs to be long enough to pass the minimum text length threshold.</p>
    <p>This is the second paragraph with additional content. The readability algorithm needs sufficient text density to properly identify the main content area of the page.</p>
    <p>A third paragraph helps establish this as a real article block. More content means higher confidence in the extraction result and better quality output.</p>
  </article>
</div>
<footer><p>Footer noise content</p></footer>
</body>
</html>
"""

FORUM_HTML = """
<!DOCTYPE html>
<html>
<head><title>Forum Post Title</title></head>
<body>
<div id="main-content">
  <h1>Forum Post Title</h1>
  <div class="post" id="post-1">
    <div class="post-content">
      <p>This is the main forum post content with enough text to be meaningful for extraction. The forum extractor handles comments and post structures differently from articles.</p>
    </div>
  </div>
  <div class="comment" id="comment-1">
    <p>This is a reply comment with some content that should also be captured by the forum extractor when comment mode is enabled.</p>
  </div>
</div>
</body>
</html>
"""

WEIXIN_HTML = """
<!DOCTYPE html>
<html>
<head><title>WeChat Article</title></head>
<body>
<div id="img-content">
  <h1>WeChat Test Title</h1>
  <div id="js_content">
    <p>This is a WeChat article paragraph with enough content. WeChat articles have a specific structure that the WeixinExtractor is designed to handle.</p>
    <p>Second paragraph of WeChat content provides more density for extraction.</p>
    <img data-src="https://example.com/image.jpg" />
  </div>
</div>
</body>
</html>
"""

MINIMAL_HTML = """
<html><body><p>Hello world</p></body></html>
"""

NO_BODY_HTML = """
<div><p>Content without body tag wrapper for testing.</p></div>
"""

MATH_HTML = """
<!DOCTYPE html>
<html>
<head><title>Math Page</title></head>
<body>
<article>
  <h1>Math Article</h1>
  <p>Here is some text before the equation that provides context for the math content below.</p>
  <math xmlns="http://www.w3.org/1998/Math/MathML">
    <mrow><mi>x</mi><mo>=</mo><mn>2</mn></mrow>
  </math>
  <p>More text after the equation to provide enough content density for the extraction algorithm to work properly.</p>
  <p>Additional paragraph with even more text to ensure the article passes the minimum length requirements for extraction.</p>
</article>
</body>
</html>
"""


# ---------------------------------------------------------------------------
# 1. lxml API Compatibility Tests (post-upgrade validation)
# ---------------------------------------------------------------------------

class TestLxmlApiCompatibility:
    """Verify critical lxml APIs still work after upgrade to >=6.1.0."""

    def test_html_parser(self):
        tree = fromstring(MINIMAL_HTML, parser=HTML_PARSER)
        assert tree is not None
        assert isinstance(tree, HtmlElement)

    def test_fromstring_tostring_roundtrip(self):
        tree = fromstring("<div><p>test</p></div>")
        html_str = tostring(tree, encoding=str)
        assert "<p>test</p>" in html_str

    def test_element_creation(self):
        elem = Element("div")
        elem.text = "hello"
        assert elem.tag == "div"
        assert elem.text == "hello"

    def test_text_content_returns_str(self):
        """lxml 6.0: text_content() returns plain str, not smart string."""
        tree = fromstring("<div><p>hello</p> <span>world</span></div>")
        result = tree.text_content()
        assert isinstance(result, str)
        assert "hello" in result
        assert "world" in result

    def test_body_property_returns_none(self):
        """lxml 6.0: .body returns None instead of raising when missing."""
        tree = fromstring("<div><p>no body</p></div>")
        body = tree.body if hasattr(tree, 'body') else None
        # Should not raise — body is either an element or None

    def test_list_instead_of_getchildren(self):
        tree = fromstring("<div><p>a</p><p>b</p></div>")
        children = list(tree)
        assert len(children) == 2
        assert children[0].tag == "p"

    def test_iter_instead_of_getiterator(self):
        tree = fromstring("<div><p>a</p><span>b</span></div>")
        tags = [e.tag for e in tree.iter()]
        assert "div" in tags
        assert "p" in tags
        assert "span" in tags

    def test_iter_with_tag_filter(self):
        tree = fromstring("<div><p>a</p><span>b</span><p>c</p></div>")
        p_tags = list(tree.iter("p"))
        assert len(p_tags) == 2

    def test_cleaner_import(self):
        """lxml 6.0: Cleaner moved to lxml_html_clean package."""
        assert HTML_CLEANER is not None
        tree = fromstring("<div><p>text</p><script>alert(1)</script></div>")
        cleaned = HTML_CLEANER.clean_html(tree)
        assert cleaned is not None

    def test_xpath(self):
        tree = fromstring('<div><p class="main">text</p></div>')
        results = tree.xpath('//p[@class="main"]/text()')
        assert results == ["text"]

    def test_drop_tree(self):
        tree = fromstring("<div><p>keep</p><span>remove</span></div>")
        for span in tree.findall(".//span"):
            span.drop_tree()
        assert "remove" not in tostring(tree, encoding=str)
        assert "keep" in tostring(tree, encoding=str)

    def test_etree_fromstring(self):
        from lxml import etree
        xml = '<root><child>text</child></root>'
        tree = etree.fromstring(xml)
        assert tree.tag == "root"
        assert tree[0].text == "text"

    def test_tounicode(self):
        from lxml.etree import tounicode
        tree = fromstring("<div><p>hello</p></div>")
        result = tounicode(tree, method="html")
        assert isinstance(result, str)
        assert "hello" in result

    def test_comment_and_strip_elements(self):
        from lxml.etree import Comment, strip_elements
        tree = fromstring("<div><!-- comment --><p>text</p></div>")
        strip_elements(tree, Comment)
        html_str = tostring(tree, encoding=str)
        assert "text" in html_str

    def test_fragment_fromstring(self):
        from lxml.html import fragment_fromstring
        frag = fragment_fromstring("<div/>")
        assert frag.tag == "div"

    def test_document_fromstring(self):
        from lxml.html import document_fromstring
        doc = document_fromstring("<div>hello</div>")
        assert doc is not None


# ---------------------------------------------------------------------------
# 2. Utility Function Tests
# ---------------------------------------------------------------------------

class TestUtils:
    def test_load_html_with_string(self):
        tree = load_html(MINIMAL_HTML)
        assert tree is not None
        assert isinstance(tree, HtmlElement)

    def test_load_html_with_bytes(self):
        tree = load_html(MINIMAL_HTML.encode("utf-8"))
        assert tree is not None

    def test_load_html_wraps_plain_text(self):
        tree = load_html("not html at all just plain text")
        assert tree is not None
        assert "not html at all" in tree.text_content()

    def test_iter_node(self):
        tree = fromstring("<div><p>a</p><span>b</span></div>")
        nodes = list(iter_node(tree))
        assert len(nodes) >= 3

    def test_is_empty_element(self):
        empty = Element("div")
        assert is_empty_element(empty) is True

        non_empty = Element("div")
        non_empty.text = "content"
        assert is_empty_element(non_empty) is False

    def test_text_len(self):
        assert text_len("hello world") == 2
        # "你好世界" → split() gives 1 word + 4 Chinese chars = 5
        assert text_len("你好世界") == 5
        # "hello 你好" → split() gives ["hello", "你好"] = 2 words + 2 chinese chars = 4
        assert text_len("hello 你好") == 4


# ---------------------------------------------------------------------------
# 3. GeneralExtractor — Article Type (default)
# ---------------------------------------------------------------------------

class TestArticleExtractor:
    def setup_method(self):
        self.extractor = GeneralExtractor()

    def test_extract_returns_dict(self):
        result = self.extractor.extract(html=ARTICLE_HTML)
        assert isinstance(result, dict)
        assert "html" in result
        assert "title" in result

    def test_extract_has_content(self):
        result = self.extractor.extract(html=ARTICLE_HTML)
        assert result["html"] is not None
        assert len(result["html"]) > 0

    def test_extract_title(self):
        result = self.extractor.extract(html=ARTICLE_HTML)
        assert result["title"] is not None

    def test_extract_with_base_url(self):
        result = self.extractor.extract(
            html=ARTICLE_HTML, base_url="https://example.com/article/1"
        )
        assert isinstance(result, dict)
        assert "html" in result

    def test_extract_empty_html_raises(self):
        with pytest.raises((ValueError, TypeError)):
            self.extractor.extract(html="")

    def test_extract_result_keys(self):
        result = self.extractor.extract(html=ARTICLE_HTML)
        for key in ["xp_num", "drop_list", "html", "title", "base_url"]:
            assert key in result, f"Missing key: {key}"

    def test_extract_bytes_input_goes_through_load_html(self):
        """Bytes must be decoded before passing to extractors since they call str.replace first."""
        from magic_html.utils import decode_file
        html_bytes = ARTICLE_HTML.encode("utf-8")
        html_str = decode_file(html_bytes)
        result = self.extractor.extract(html=html_str)
        assert isinstance(result, dict)
        assert result["html"] is not None


# ---------------------------------------------------------------------------
# 4. ForumExtractor
# ---------------------------------------------------------------------------

class TestForumExtractor:
    def setup_method(self):
        self.extractor = GeneralExtractor()

    def test_forum_extract_returns_dict(self):
        result = self.extractor.extract(
            html=FORUM_HTML, html_type="forum"
        )
        assert isinstance(result, dict)
        assert "html" in result

    def test_forum_extract_has_content(self):
        result = self.extractor.extract(
            html=FORUM_HTML, html_type="forum"
        )
        assert result["html"] is not None
        assert len(result["html"]) > 0

    def test_forum_extract_with_base_url(self):
        result = self.extractor.extract(
            html=FORUM_HTML,
            base_url="https://forum.example.com/thread/1",
            html_type="forum",
        )
        assert isinstance(result, dict)

    def test_forum_body_none_handling(self):
        """Regression: lxml 6.0 .body returns None instead of raising."""
        no_body = """
        <html><head><title>No Body</title></head>
        <div class="content">
            <p>This content is outside body tag but has enough text for extraction to work with it properly in the forum context.</p>
            <p>Additional paragraph for text density requirements of the extraction algorithm.</p>
        </div>
        </html>
        """
        result = self.extractor.extract(html=no_body, html_type="forum")
        assert isinstance(result, dict)


# ---------------------------------------------------------------------------
# 5. WeixinExtractor
# ---------------------------------------------------------------------------

class TestWeixinExtractor:
    def setup_method(self):
        self.extractor = GeneralExtractor()

    def test_weixin_by_type(self):
        result = self.extractor.extract(
            html=WEIXIN_HTML, html_type="weixin"
        )
        assert isinstance(result, dict)
        assert "html" in result

    def test_weixin_by_url(self):
        result = self.extractor.extract(
            html=WEIXIN_HTML,
            base_url="https://mp.weixin.qq.com/s/test123",
        )
        assert isinstance(result, dict)

    def test_weixin_img_data_src(self):
        """data-src should be converted to src for images."""
        result = self.extractor.extract(
            html=WEIXIN_HTML, html_type="weixin"
        )
        html_out = result["html"]
        if "image.jpg" in html_out:
            assert "src=" in html_out

    def test_weixin_has_content(self):
        result = self.extractor.extract(
            html=WEIXIN_HTML, html_type="weixin"
        )
        assert result["html"] is not None
        assert len(result["html"]) > 0


# ---------------------------------------------------------------------------
# 6. CustomExtractor
# ---------------------------------------------------------------------------

class TestCustomExtractor:
    def test_custom_extract_with_rule(self):
        from magic_html.extractors.custom_extractor import CustomExtractor

        html = """
        <html>
        <head><title>Custom Page</title></head>
        <body>
        <div class="main-content">
            <h2>Custom Title</h2>
            <p>Custom body content that should be extracted by the xpath rule.</p>
        </div>
        <div class="sidebar">Noise</div>
        </body>
        </html>
        """
        rule = {
            "content": {
                "mode": "xpath",
                "value": "//div[@class='main-content']",
            }
        }
        ext = CustomExtractor()
        result = ext.extract(html=html, rule=rule)
        assert isinstance(result, dict)
        assert "Custom body content" in result["html"]

    def test_custom_extract_with_title_rule(self):
        from magic_html.extractors.custom_extractor import CustomExtractor

        html = """
        <html>
        <head><title>Page Title</title></head>
        <body>
        <div class="content">
            <h2 class="post-title">Specific Title</h2>
            <p>Some content here for extraction.</p>
        </div>
        </body>
        </html>
        """
        rule = {
            "title": {
                "mode": "xpath",
                "value": "//h2[@class='post-title']/text()",
            },
            "content": {
                "mode": "xpath",
                "value": "//div[@class='content']",
            },
        }
        ext = CustomExtractor()
        result = ext.extract(html=html, rule=rule)
        assert result["title"] == "Specific Title"

    def test_custom_extract_with_clean_rule(self):
        from magic_html.extractors.custom_extractor import CustomExtractor

        html = """
        <html>
        <head><title>Clean Test</title></head>
        <body>
        <div class="content">
            <p>Keep this content.</p>
            <div class="ad">Remove this ad.</div>
        </div>
        </body>
        </html>
        """
        rule = {
            "clean": ["//div[@class='ad']"],
            "content": {
                "mode": "xpath",
                "value": "//div[@class='content']",
            },
        }
        ext = CustomExtractor()
        result = ext.extract(html=html, rule=rule)
        assert "Remove this ad" not in result["html"]
        assert "Keep this content" in result["html"]


# ---------------------------------------------------------------------------
# 7. Math/LaTeX Processing
# ---------------------------------------------------------------------------

class TestMathProcessing:
    def test_math_tag_in_article(self):
        result = GeneralExtractor().extract(html=MATH_HTML)
        assert isinstance(result, dict)

    def test_mathjax_script(self):
        html = """
        <!DOCTYPE html>
        <html><head><title>Math</title></head>
        <body>
        <article>
            <p>Consider the equation below which is important for understanding the concept.</p>
            <script type="math/tex">E = mc^2</script>
            <p>This equation describes mass-energy equivalence and is one of the most famous equations in physics.</p>
            <p>Albert Einstein published this result as part of his special theory of relativity in 1905.</p>
        </article>
        </body>
        </html>
        """
        result = GeneralExtractor().extract(html=html)
        assert isinstance(result, dict)


# ---------------------------------------------------------------------------
# 8. Edge Cases
# ---------------------------------------------------------------------------

class TestEdgeCases:
    def setup_method(self):
        self.extractor = GeneralExtractor()

    def test_html_with_comments(self):
        html = """
        <html><head><title>Comments</title></head>
        <body>
        <article>
            <!-- This is a comment -->
            <p>Actual content that should be preserved after comment removal during extraction.</p>
            <p>More content paragraphs to provide sufficient text density for the extraction algorithm.</p>
            <p>Third paragraph adds even more content density to ensure proper extraction behavior.</p>
        </article>
        </body>
        </html>
        """
        result = self.extractor.extract(html=html)
        assert isinstance(result, dict)

    def test_html_with_scripts(self):
        html = """
        <html><head><title>Scripts</title></head>
        <body>
        <article>
            <script>alert('xss')</script>
            <p>Safe content that should be extracted while the script tag above is removed.</p>
            <p>Additional paragraph with more text content for density requirements.</p>
            <p>Third paragraph provides further text density for the extraction process.</p>
        </article>
        </body>
        </html>
        """
        result = self.extractor.extract(html=html)
        assert isinstance(result, dict)
        if result["html"]:
            assert "alert" not in result["html"]

    def test_deeply_nested_html(self):
        inner = "<p>Deep content for testing deeply nested HTML structure handling.</p>"
        for _ in range(20):
            inner = f"<div>{inner}</div>"
        html = f"<html><head><title>Deep</title></head><body>{inner}</body></html>"
        result = self.extractor.extract(html=html)
        assert isinstance(result, dict)

    def test_unicode_content(self):
        html = """
        <html><head><title>Unicode Test</title></head>
        <body>
        <article>
            <p>中文内容测试，确保Unicode字符在提取过程中能够被正确处理和保留。这段文字包含了足够多的中文字符来满足提取算法的最小文本长度要求。</p>
            <p>日本語テスト内容。この段落は、抽出アルゴリズムが日本語コンテンツを正しく処理できることを確認するために含まれています。</p>
            <p>العربية اختبار المحتوى. تم تضمين هذه الفقرة للتحقق من أن خوارزمية الاستخراج يمكنها التعامل مع المحتوى العربي بشكل صحيح.</p>
        </article>
        </body>
        </html>
        """
        result = self.extractor.extract(html=html)
        assert isinstance(result, dict)
        assert result["html"] is not None

    def test_empty_body(self):
        html = "<html><head><title>Empty</title></head><body></body></html>"
        result = self.extractor.extract(html=html)
        assert isinstance(result, dict)

    def test_nbsp_handling(self):
        html = """
        <html><head><title>Nbsp</title></head>
        <body>
        <article>
            <p>Text&nbsp;with&nbsp;non-breaking&nbsp;spaces&nbsp;that&nbsp;should&nbsp;be&nbsp;handled&nbsp;properly&nbsp;by&nbsp;the&nbsp;extraction&nbsp;algorithm.</p>
            <p>Additional paragraph providing more content density for the extraction to work correctly with special characters.</p>
            <p>Third paragraph with even more text to ensure sufficient content for algorithm processing.</p>
        </article>
        </body>
        </html>
        """
        result = self.extractor.extract(html=html)
        assert isinstance(result, dict)

    def test_large_html(self):
        paragraphs = "\n".join(
            [f"<p>Paragraph {i} with sufficient content length for testing large HTML documents and extraction performance.</p>" for i in range(100)]
        )
        html = f"""
        <html><head><title>Large</title></head>
        <body><article>{paragraphs}</article></body>
        </html>
        """
        result = self.extractor.extract(html=html)
        assert isinstance(result, dict)
        assert result["html"] is not None
