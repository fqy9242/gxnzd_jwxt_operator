from pathlib import Path


CONFIG_PATH = Path(".env")
CONFIG_KEYS = ("JWXT_USERNAME", "JWXT_PASSWORD", "JWXT_COOKIES")


def load_config(path=CONFIG_PATH):
    if not path.exists():
        return {}

    config = {}
    for line in path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        if line.startswith("export "):
            line = line[7:].strip()
        if "=" not in line:
            continue

        key, value = line.split("=", 1)
        key = key.strip()
        if key not in CONFIG_KEYS:
            continue
        config[key] = _decode_value(value.strip())

    return config


def save_config(user_name, password, cookies, path=CONFIG_PATH):
    lines = [
        f"JWXT_USERNAME={_encode_value(user_name)}",
        f"JWXT_PASSWORD={_encode_value(password)}",
        f"JWXT_COOKIES={_encode_value(cookies)}",
    ]
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def _decode_value(value):
    if len(value) >= 2 and value[0] == value[-1] and value[0] in ("'", '"'):
        quote = value[0]
        value = value[1:-1]
        if quote == '"':
            value = value.replace(r"\\", "\\").replace(r"\"", '"')
    return value


def _encode_value(value):
    value = str(value).replace("\\", r"\\").replace('"', r"\"")
    return f'"{value}"'
