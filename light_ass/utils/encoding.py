from __future__ import annotations

_BOM_MAP = {
    b"\xef\xbb\xbf": "utf-8-sig",
    b"\xff\xfe\x00\x00": "utf-32-le",
    b"\x00\x00\xfe\xff": "utf-32-be",
    b"\xff\xfe": "utf-16-le",
    b"\xfe\xff": "utf-16-be",
}

_TEST_ENCODINGS = [
    "utf-8",
    "gb2312",
    "gb18030",
    "big5",
    "shift_jis",
    "euc-kr",
    "iso-8859-1",
    "cp1252",
]


def detect_bytes_encoding(sample: bytes) -> str | None:
    for bom, encoding in _BOM_MAP.items():
        if sample.startswith(bom):
            return encoding

    for encoding in _TEST_ENCODINGS:
        try:
            sample.decode(encoding, errors="strict")
            return encoding
        except UnicodeDecodeError:
            continue

    return None


def detect_file_encoding(file_path: str, sample_size: int = 1024) -> str | None:
    with open(file_path, "rb") as f:
        sample = f.read(sample_size)
    return detect_bytes_encoding(sample)
