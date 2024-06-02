from interface import interface_init

MAJOR: int = 0
MINOR: int = 1
PATCH: int = 0
VERSION: str = f"{MAJOR}.{MINOR}.{PATCH}"
NAME: str = "TARA"


def main() -> None:

    # TODO:
    # 1. correctly load dictionaries from /dictionaries
    # 2. gracefully handle cases where dictionaries not found
    # 3. when processing files, change screen

    interface_init(NAME, VERSION)

    return


if __name__ == '__main__':
    main()
