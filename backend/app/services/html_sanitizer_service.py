from html.parser import HTMLParser
from html import escape
from urllib.parse import urlparse


class HTMLSanitizer(HTMLParser):
    allowed_tags = {
        "p",
        "br",
        "h2",
        "h3",
        "h4",
        "ul",
        "ol",
        "li",
        "strong",
        "b",
        "em",
        "i",
        "blockquote",
        "table",
        "thead",
        "tbody",
        "tr",
        "th",
        "td",
        "a",
    }
    allowed_anchor_attrs = {"href", "target", "rel"}

    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self.parts: list[str] = []

    def handle_starttag(self, tag: str, attrs) -> None:
        tag = tag.lower()
        if tag not in self.allowed_tags:
            return
        if tag == "a":
            clean_attrs = self._clean_anchor_attrs(attrs)
            attr_text = "".join(f' {key}="{escape(value, quote=True)}"' for key, value in clean_attrs)
            self.parts.append(f"<a{attr_text}>")
            return
        self.parts.append(f"<{tag}>")

    def handle_endtag(self, tag: str) -> None:
        tag = tag.lower()
        if tag in self.allowed_tags and tag != "br":
            self.parts.append(f"</{tag}>")

    def handle_data(self, data: str) -> None:
        self.parts.append(escape(data))

    def handle_entityref(self, name: str) -> None:
        self.parts.append(f"&{name};")

    def handle_charref(self, name: str) -> None:
        self.parts.append(f"&#{name};")

    def _clean_anchor_attrs(self, attrs) -> list[tuple[str, str]]:
        clean = []
        for raw_key, raw_value in attrs:
            key = raw_key.lower()
            value = raw_value or ""
            if key not in self.allowed_anchor_attrs:
                continue
            if key == "href" and not self._is_safe_url(value):
                continue
            clean.append((key, value))
        return clean

    def _is_safe_url(self, value: str) -> bool:
        parsed = urlparse(value)
        return parsed.scheme in {"http", "https", ""}

    def get_html(self) -> str:
        return "".join(self.parts).strip()


def sanitize_html(html: str) -> str:
    parser = HTMLSanitizer()
    parser.feed(html or "")
    parser.close()
    return parser.get_html()
