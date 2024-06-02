import re

from SymSpellCppPy import SymSpell, Info

from spellcheck.spellcheck import _load_spellchecker


def regex_interpolation(text: str) -> str:
    text = text.lower().strip()
    text = re.sub(r'\n', r'', text)
    text = re.sub("[‘’]", "'", text)  # standardise '
    text = re.sub(r'\d', '', text)  # remove all digits
    text = re.sub(r"(?<!^o)(')(?![ts])", r'', text)  # keep o' 't 's
    text = re.sub(r"(?<!^o)'s", r"", text)  # remove all 's not in irish name
    text = re.sub(r"(?!(^'t|^o't))'t", r"", text)  # remove all 't not wanted
    text = re.sub(r'[,.—;!*:()“”"&%\[\]?°\\/¢]', r'', text)  # remove symbols
    text = re.sub(r'([,.—;!*:()“”"&%\[\]?\'°\\/¢])\1+', r'\1', text)  # remove consecutive instances that remain
    text = re.sub(r'[^\'\w]$', r'', text)  # remove any non ' symbols at end. why?
    text = re.sub(r"'$", r'', text)  # catch weird ' at end
    return text


def generate_freq_dictionary(frequency: list[str]) -> dict:
    dictionary: dict
    pattern: str

    dictionary = dict()

    for line in frequency:
        split: list[str]
        word: str
        freq: int

        line = re.sub(r'[\n\ufeff]', r'', line)
        split = line.split(' ')
        word = split[0].strip()
        freq = int(split[1])
        dictionary.update({word: freq})

    return dictionary


def generate_freq_list(frequency: dict) -> list[str]:
    to_sort: list[tuple]
    to_return: list[str]

    to_sort = list(x for x in frequency.items())
    to_sort = sorted(to_sort, key=lambda x: x[1], reverse=True)
    to_return = list()

    for item in to_sort:
        entry: str = f"{item[0]} {item[1]}\n"
        to_return.append(entry)

    return to_return


def add_to_dictionary(src_path: str, dict_path: str, dest_path: str) -> None:
    spellchecker: SymSpell
    text: list[str]
    frequency: list[str]
    dictionary: dict
    added_words: dict

    spellchecker = _load_spellchecker()
    added_words = dict()

    with open(src_path, 'r') as f:
        text = f.readlines()

    with open(dict_path, 'r') as f:
        frequency = f.readlines()

    dictionary = generate_freq_dictionary(frequency)

    for line in text:

        words = line.split(' ')

        for word in words:
            word = regex_interpolation(word)

            """ Let's try to find two big words and discard them """
            if len(word) > 9:
                split: Info = spellchecker.word_segmentation(word, max_edit_distance=1)
                if split.distance_sum > 0:
                    to_check = split.corrected_string.split(' ')
                    if all(term in dictionary for term in to_check):
                        continue

            if not word or (len(word) < 2 and word != 'a'):
                continue

            if word not in dictionary:

                if word in added_words:
                    freq = added_words.get(word)
                    freq += 1
                    added_words.update({word: freq})
                    print(added_words)
                    continue

                char = input(f"'{word}' is not in dictionary. Add? ")
                if char == 'y':
                    added_words.update({word: 1})
                    print(added_words)
                elif char == 'n':
                    continue
                else:
                    if char in added_words:
                        freq = added_words.get(char)
                        freq += 1
                        added_words.update({char: freq})
                        print(added_words)
                        continue
                    else:
                        added_words.update({char: 1})
                        print(added_words)
                        continue

    with open(dest_path, 'a') as f:
        entry: str

        for key in added_words.keys():
            entry = f"{key} {added_words[key]}\n"
            f.write(entry)

    return


def merge_dictionaries(src_path: str, merge_path: str, dest_path: str) -> None:
    source: list[str]
    merge_to: list[str]
    combined: list[str]
    from_dict: dict
    to_dict: dict

    with open(src_path, 'r') as f:
        source = f.readlines()

    with open(merge_path, 'r') as f:
        merge_to = f.readlines()

    from_dict = generate_freq_dictionary(source)
    to_dict = generate_freq_dictionary(merge_to)

    for key in from_dict:
        if key in to_dict:
            value: int = to_dict[key]
            value += from_dict[key]
            to_dict.update({key: value})
        else:
            value: int = from_dict[key]
            to_dict.update({key: value})

    combined = generate_freq_list(to_dict)

    with open(dest_path, 'a') as f:
        f.writelines(combined)

    return


""" trying to guess if we should separate a word or not,
    difficult since we have no nationalist vocab yet
if word:
    x: Info = spellchecker.word_segmentation(word)
    if x.log_prob_sum < -10 or x.log_prob_sum > -2:
        confidence.add((word, x.log_prob_sum, x.segmented_string))
        # print(f"Probability: {x.log_prob_sum}.\nWord: {word}.")
"""

"""
for word in words_unique:
    print(word)
print(f"Unique words: {len(words_unique)}")
"""

"""
y = list(x for x in confidence)
y = sorted(y, key=lambda z: z[1])
for w in y:
    print(f"Word: {w[0]}. Probability: {w[1]}. Correction: {w[2]}.")
"""