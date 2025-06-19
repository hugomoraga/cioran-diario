# Random Phrase Service

This repository includes a small HTTP service that reads an EPUB file and
returns a random phrase extracted from its text.

## Usage

```bash
python random_phrase_service.py path/to/book.epub
```

The service listens on port `8000`. Request `http://localhost:8000/random`
for a random phrase.

The parser is simplistic: it extracts text from every HTML or XHTML file in the
EPUB and splits it into sentences. Very short sentences are skipped.
