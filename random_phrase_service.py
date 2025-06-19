import zipfile
import re
import random
import sys
from html.parser import HTMLParser
from http.server import BaseHTTPRequestHandler, HTTPServer


class _TextExtractor(HTMLParser):
    def __init__(self):
        super().__init__()
        self.parts = []

    def handle_data(self, data: str) -> None:
        self.parts.append(data)

    def get_text(self) -> str:
        return ' '.join(self.parts)


def _extract_text(html_bytes: bytes) -> str:
    parser = _TextExtractor()
    parser.feed(html_bytes.decode('utf-8', errors='ignore'))
    return parser.get_text()


def load_sentences(epub_path: str) -> list[str]:
    """Load sentences from an EPUB file."""
    sentences: list[str] = []
    with zipfile.ZipFile(epub_path, 'r') as zf:
        for name in zf.namelist():
            if name.lower().endswith(('.html', '.xhtml')):
                text = _extract_text(zf.read(name))
                text = text.replace('\n', ' ')
                parts = re.split(r'[.!?]+\s+', text)
                for p in parts:
                    p = p.strip()
                    if len(p) > 20:
                        sentences.append(p)
    return sentences


class RandomPhraseHandler(BaseHTTPRequestHandler):
    sentences: list[str] = []

    def do_GET(self) -> None:
        if self.path.rstrip('/') != '/random':
            self.send_error(404)
            return
        if not self.sentences:
            self.send_error(500, 'No sentences loaded')
            return
        phrase = random.choice(self.sentences)
        self.send_response(200)
        self.send_header('Content-Type', 'text/plain; charset=utf-8')
        self.end_headers()
        self.wfile.write(phrase.encode('utf-8'))


if __name__ == '__main__':
    if len(sys.argv) != 2:
        print('Usage: python random_phrase_service.py <book.epub>')
        sys.exit(1)
    epub_path = sys.argv[1]
    RandomPhraseHandler.sentences = load_sentences(epub_path)
    server = HTTPServer(('0.0.0.0', 8000), RandomPhraseHandler)
    print('Serving random phrases on http://localhost:8000/random')
    server.serve_forever()
