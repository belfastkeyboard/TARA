from interface import interface_init

MAJOR: int = 0
MINOR: int = 2
PATCH: int = 0
VERSION: str = f"{MAJOR}.{MINOR}.{PATCH}"
NAME: str = "TARA"


def main() -> None:

    # TODO:
    #   1. when processing files, change screen

    interface_init(NAME, VERSION)

    return


if __name__ == '__main__':
    main()
