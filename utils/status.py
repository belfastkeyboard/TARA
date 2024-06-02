def good(text: object) -> None:
    print(f"[+] {text}")


def info(text: object) -> None:
    print(f"[i] {text}")


def warn(text: object) -> None:
    print(f"[!] {text}")


def progress(text: object, end: str = '') -> None:
    print(f"\r[i] {text} ", end=end, flush=True)
