from __future__ import annotations


def detect_file_encoding(file_path: str, sample_size: int = 1024) -> str | None:
    bom_map = {
        b"\xef\xbb\xbf": "utf-8-sig",
        b"\xff\xfe": "utf-16-le",
        b"\xfe\xff": "utf-16-be",
        b"\xff\xfe\x00\x00": "utf-32-le",
        b"\x00\x00\xfe\xff": "utf-32-be",
    }

    with open(file_path, "rb") as f:
        sample = f.read(sample_size)

    for bom, encoding in bom_map.items():
        if sample.startswith(bom):
            return encoding

    test_encodings = [
        "utf-8",
        "gb2312",
        "gb18030",
        "big5",
        "shift_jis",
        "euc-kr",
        "iso-8859-1",
        "cp1252",
    ]

    for encoding in test_encodings:
        try:
            sample.decode(encoding, errors="strict")
            return encoding
        except UnicodeDecodeError:
            continue

    return None
