from sys import exit

from SymSpellCppPy import SymSpell
import SymSpellCppPy
import re
from utils.status import warn, info, good, progress
import time


class Spellchecker:
    def __init__(self):
        self.spellchecker = _load_spellchecker()
        self.clause_separator = re.compile(r"[.?!,:']+")
        self.verbosity = SymSpellCppPy.Verbosity.CLOSEST

    def spellcheck(self, paragraph: str, log: bool = True) -> str:

        """ lookup compound with bigram dictionary seems to be much better at getting the correct word
            but it simply doesn't get it right all the time. it would probably be good to build an irish
            nationalist bigram dictionary by getting pairs of words and adding them to the standard bigram
            dictionary with an artificially elevated frequency """

        if log:
            info("Spellchecking.")

        start = time.time()
        clauses, indices = _prepare_text_for_analysis(paragraph)

        for i, clause in enumerate(clauses):

            if len(clause.strip()) < 2:
                continue

            suggestion = self.spellchecker.lookup_compound(
                input=clause, max_edit_distance=2, transfer_casing=True
            )

            try:
                clauses[i] = suggestion[0].term
            except UnicodeDecodeError as e:
                clauses[i] = _fix_encoding_errors(clause, e)

        paragraph = _restitch_text(clauses, indices, paragraph)
        end = time.time()

        if log:
            good(f"Spellchecked in {(end - start):.2f} seconds.")

        return paragraph

    def spellcheck_batch(self, paragraphs: list[str], log: bool = True) -> list[str]:

        """ lookup compound with bigram dictionary seems to be much better at getting the correct word
            but it simply doesn't get it right all the time. it would probably be good to build an irish
            nationalist bigram dictionary by getting pairs of words and adding them to the standard bigram
            dictionary with an artificially elevated frequency """

        checked_paragraphs: list[str]

        if log:
            info("Spellchecking.")

        checked_paragraphs = list()
        start = time.time()
        paragraph_count = len(paragraphs)

        for i, paragraph in enumerate(paragraphs):
            clauses, indices = _prepare_text_for_analysis(paragraph)

            for j, clause in enumerate(clauses):

                if len(clause.strip()) < 2:
                    continue

                suggestion = self.spellchecker.lookup_compound(
                    input=clause, max_edit_distance=2, transfer_casing=True
                )

                try:
                    clauses[j] = suggestion[0].term
                except UnicodeDecodeError as e:
                    clauses[j] = _fix_encoding_errors(clause, e)

            checked_paragraphs.append(_restitch_text(clauses, indices, paragraph))

            if log:
                progress(
                    f"Spellchecked paragraphs: {i + 1} out of {paragraph_count}.",
                    end='' if i + 1 < paragraph_count else '\r'
                )

        end = time.time()

        if log:
            good(f"Spellchecked in {(end - start):.2f} seconds.\n")

        return checked_paragraphs


def _load_spellchecker() -> SymSpell:
    spellchecker: SymSpell

    spellchecker = SymSpellCppPy.SymSpell()
    spellchecker.load_dictionary(
        corpus='irish_dictionary.txt', term_index=0, count_index=1, separator=' '
    )
    spellchecker.load_bigram_dictionary(
        corpus='resources/frequency_bigramdictionary_en_243_342.txt', term_index=0, count_index=2, separator=' '
    )

    return spellchecker


def fix_byte(bad_string: str, bad_byte: str, replacement: str) -> str:
    return bad_string.replace(bad_byte, replacement)


def _fix_encoding_errors(clause: str, exception: UnicodeDecodeError) -> str:
    if exception.reason == 'invalid continuation byte' or exception.reason == 'invalid start byte':
        invalid_byte = clause[exception.start: exception.end - 1]
        if invalid_byte == "‘":
            clause = fix_byte(bad_string=clause, bad_byte=invalid_byte, replacement="'")
        if invalid_byte == '\x00':
            clause = fix_byte(bad_string=clause, bad_byte=invalid_byte, replacement="")
        if invalid_byte == '\xee':
            clause = fix_byte(bad_string=clause, bad_byte=invalid_byte, replacement="--")
    return clause


def _prepare_text_for_analysis(text: str) -> tuple[list[str], list[int]]:

    """
    Breaks text into clauses without punctuation for spellchecking.

    Returns a tuple: clauses, indices.
    Clauses are used for analysis, indices are needed to re-stitch text after processing.

    Call restitch_text to re-stitch text.
    """

    indices = []
    strings = []
    current_str = []

    for i, char in enumerate(text):
        if _is_punctuation(char):
            clause = "".join(current_str)
            if clause:
                strings.append(clause)
            current_str.clear()
            indices.append(i)
        else:
            current_str.append(char)

    if current_str:
        clause = "".join(current_str)
        if clause:
            strings.append(clause)

    return strings, indices


def _restitch_text(text: list[str], indices: list[int], original_text: str) -> str:
    length = len(original_text)
    modified_text = original_text
    i = 0

    if "Mr. Williams (the clerk)" in original_text:  # the slicing is incorrect on 'James F' before 'Lalor' 'in the'...
        pass

    while text:

        try:
            char = modified_text[i]
        except IndexError as e:
            print(f"\nException: {e}.")
            warn(f"Error at at index '{i}' where modified text:\n'{modified_text}'.")
            print(f"{'-' * (i + 5)}^")
            exit(1)

        if _is_punctuation(char):

            if indices and i == indices[0]:
                indices.remove(indices[0])
            i += 1

        else:

            sliced = modified_text[i: indices[0]] if indices else modified_text[i:]

            try:
                modified_text = modified_text.replace(sliced, _should_insert_space(text[0], sliced))
            except MemoryError as e:
                warn(e)
                info(f"modified_text: '{modified_text}'. sliced: '{sliced}. text[0]: '{text[0]}'.")

            diff = (length - len(modified_text)) * -1
            indices = [x + diff for x in indices]
            length += diff
            if indices:
                i = indices[0] + 1
                indices.remove(indices[0])
            text.remove(text[0])

    return modified_text


def _is_punctuation(char: str) -> bool:
    return char in ",.;:!?—*‘’()"


def _should_insert_space(text: str, comparison: str) -> str:
    try:
        if comparison[0] == ' ' and text[0] != ' ' and comparison[-1] == ' ' and text[-1] != ' ':
            text = f" {text} "
        elif comparison[0] == ' ' and text[0] != ' ':
            text = f" {text}"
        elif comparison[-1] == ' ' and text[-1] != ' ':
            text = f"{text} "
    except IndexError as e:
        warn(e)
        info(f"Text: {text or 'empty string error'}. Comparison string: {comparison or 'empty string error'}.")
        text = text if text else 'empty string error'
    finally:
        return text
