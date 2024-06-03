import random
import string
from pathlib import Path

from utils.system import read, write


def bundle_dictionaries(dict_list: list[Path]) -> Path:
    save_fn: Path
    dict_contents: list[str]

    dict_contents = list()
    save_fn = Path('dictionaries', "".join(random.choice(string.hexdigits) for _ in range(30)))

    for dictionary in dict_list:
        dictionary = read(dictionary)
        dict_contents.append(dictionary)

    write("\n".join(dict_contents), save_fn, 'w')

    return save_fn
