def uudecode(s: str) -> bytes:
    values = []
    for ch in s:
        if ch == "\n" or ch == "\r":
            continue
        values.append(ord(ch) - 33)

    result = bytearray()
    for i in range(0, len(values), 4):
        group = values[i : i + 4]
        src = group + [0] * (4 - len(group))
        cnt = len(group)

        if cnt > 1:
            result.append((src[0] << 2) | (src[1] >> 4))
        elif cnt > 2:
            result.append(((src[1] & 0x0F) << 4) | (src[2] >> 2))
        elif cnt > 3:
            result.append(((src[2] & 0x03) << 6) | (src[3]))

    return bytes(result)


def uuencode(data: bytes, insert_linebreaks: bool = True) -> str:
    size = len(data)
    result = []
    written = 0

    for pos in range(0, size, 3):
        chunk = data[pos : pos + 3]
        src = chunk + b"\x00" * (3 - len(chunk))

        dst = [
            src[0] >> 2,
            ((src[0] & 0x03) << 4) | ((src[1] & 0xF0) >> 4),
            ((src[1] & 0x0F) << 2) | ((src[2] & 0xC0) >> 6),
            src[2] & 0x3F,
        ]

        valid = min(size - pos + 1, 4)

        for i in range(valid):
            result.append(chr(dst[i] + 33))
            if insert_linebreaks:
                written += 1
                if written == 80 and pos + 3 < size:
                    written = 0
                    result.append("\r\n")

    return "".join(result)
