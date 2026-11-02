"""Render the resume's HTML content to a selectable-text PDF and website PNG.

Requires: reportlab, pymupdf. Run from any directory with Python 3.
The HTML is the content source; print styles below define the PDF layout.
"""
from html import escape
from html.parser import HTMLParser
from pathlib import Path
from tempfile import TemporaryDirectory
import re

import fitz
from reportlab.lib import colors
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, KeepTogether

ROOT = Path(__file__).resolve().parent.parent
SOURCE = ROOT / "assets/resume/gary-feng-resume.html"


class Node:
    def __init__(self, tag, attrs=()):
        self.tag, self.attrs, self.children = tag, dict(attrs), []

    @property
    def classes(self):
        return self.attrs.get("class", "").split()


class DocumentParser(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.root = Node("document")
        self.stack = [self.root]

    def handle_starttag(self, tag, attrs):
        node = Node(tag, attrs)
        self.stack[-1].children.append(node)
        if tag not in {"meta", "br", "link", "img", "hr", "input"}:
            self.stack.append(node)

    def handle_endtag(self, tag):
        for i in range(len(self.stack) - 1, 0, -1):
            if self.stack[i].tag == tag:
                del self.stack[i:]
                break

    def handle_data(self, data):
        self.stack[-1].children.append(data)


def inline(node):
    if isinstance(node, str):
        return escape(re.sub(r"\s+", " ", node))
    content = "".join(inline(child) for child in node.children)
    if node.tag in {"strong", "b"} or "role" in node.classes:
        return f"<b>{content}</b>"
    if node.tag in {"em", "i"}:
        return f"<i>{content}</i>"
    if node.tag == "a":
        return f'<a href="{escape(node.attrs["href"], quote=True)}" color="#161616"><u>{content}</u></a>'
    if node.tag == "br":
        return "<br/>"
    return content


BASE = dict(fontName="Helvetica", fontSize=9.5, leading=10.9, textColor=colors.HexColor("#161616"))
styles = {
    "body": ParagraphStyle("body", **BASE, spaceAfter=2),
    "title": ParagraphStyle("title", fontName="Helvetica-Bold", fontSize=19, leading=22, spaceAfter=3),
    "contact": ParagraphStyle("contact", fontName="Helvetica", fontSize=8.6, leading=11.6, spaceAfter=6),
    "heading": ParagraphStyle("heading", fontName="Helvetica-Bold", fontSize=10, leading=12, spaceBefore=6, spaceAfter=3, keepWithNext=True),
    "row": ParagraphStyle("row", **BASE, spaceAfter=1, keepWithNext=True),
    "sub": ParagraphStyle("sub", **BASE, spaceAfter=1, keepWithNext=True),
    "bullet": ParagraphStyle("bullet", **BASE, leftIndent=10, firstLineIndent=0, bulletIndent=0, spaceAfter=1),
}


def flow(node):
    if isinstance(node, str) or node.tag in {"head", "style"}:
        return []
    if node.tag == "h1":
        return [Paragraph(inline(node), styles["title"])]
    if node.tag == "h2":
        return [Paragraph(inline(node), styles["heading"])]
    if node.tag == "li":
        return [Paragraph(inline(node), styles["bullet"], bulletText="-")]
    if "row" in node.classes:
        parts = [inline(c).strip() for c in node.children if isinstance(c, Node)]
        return [Paragraph(" | ".join(parts), styles["row"])]
    for classname in ("contact", "sub", "publication"):
        if classname in node.classes:
            return [Paragraph(inline(node), styles.get(classname, styles["body"]))]
    if node.tag == "p":
        return [Paragraph(inline(node), styles["body"])]
    children = [item for child in node.children for item in flow(child)]
    if "entry" in node.classes:
        return [KeepTogether(children), Spacer(1, 2)]
    return children


def main():
    parser = DocumentParser()
    parser.feed(SOURCE.read_text(encoding="utf-8"))
    with TemporaryDirectory() as tmp:
        output = Path(tmp) / "resume.pdf"
        doc = SimpleDocTemplate(str(output), pagesize=letter, rightMargin=36, leftMargin=36, topMargin=26, bottomMargin=26, title="Gary Feng - Resume", author="Gary Feng", pageCompression=1)
        doc.build(flow(parser.root))
        with fitz.open(output) as pdf:
            if len(pdf) != 1:
                raise ValueError(f"Resume must fit one page; got {len(pdf)}. Tighten content or spacing.")
            if "Gary Feng" not in pdf[0].get_text():
                raise ValueError("Resume PDF has no extractable name.")
            pdf[0].get_pixmap(dpi=200).save(str(SOURCE.with_suffix(".png")))
            pdf_bytes = pdf.tobytes(garbage=4, deflate=True)
        SOURCE.with_suffix(".pdf").write_bytes(pdf_bytes)
    print("Rendered one-page PDF and PNG from", SOURCE)


if __name__ == "__main__":
    main()
