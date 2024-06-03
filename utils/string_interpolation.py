import re
from sys import exit

from utils.status import warn


def get_correct_ordinal(pattern) -> str:
    try:
        n = int(pattern.group(1))
    except TypeError as e:
        warn(e)
        warn(f"Could not convert '{pattern.group(1)}' to int.")
        exit(1)

    if 10 <= n % 100 <= 20:
        suffix = 'th'
    else:
        suffix = {1: 'st', 2: 'nd', 3: 'rd'}.get(n, 'th')

    return f"{str(n)}{suffix}"


def split_page_into_paragraphs(page: str) -> list[str]:
    return page.split('\n\n')


def fix_newlines(paragraph: str) -> str:
    return paragraph.replace('\n', ' ')


def fix_ambiguous_symbol(paragraph: str) -> str:
    """
    this needs a bit of work, just run the program in debug mode with errors and check the output to see
    """
    if '°' in paragraph:
        paragraph = re.sub(r' °(\d{2})', r' ’\1', paragraph)
    if '*' in paragraph:
        paragraph = re.sub(r'(\d+)\*', get_correct_ordinal, paragraph)
    return paragraph


def fix_tabs(paragraph: str) -> str:
    return paragraph.replace('\t', '')


def fix_hyphenation(paragraph: str) -> str:
    return re.sub(r' -|- | - ', r'-', paragraph)


def fix_em_dash(paragraph: str) -> str:
    return re.sub(r' —|— | — |-—|--', '—', paragraph)


def fix_quotations(paragraph: str) -> str:
    paragraph = re.sub(r'“', r"‘", paragraph)
    paragraph = re.sub(r'”', r"’", paragraph)
    paragraph = re.sub(r"([oO])[‘’]\b", r"\1'", paragraph)
    return re.sub(r"\b[‘’]([sS])", r"'\1", paragraph)


def fix_duplicated_punctuation(paragraph: str) -> str:
    return re.sub(r"([.,;:‘’“”'\"-])\1+", r'\1', paragraph)


def fix_number_concatenation(paragraph: str) -> str:
    return re.sub(r'(\d+)([a-zA-Z]+)', r'\1 \2', paragraph)


def fix_space_before_punctuation(paragraph: str) -> str:
    return re.sub(r" ([,.;:])", r'\1', paragraph)


def fix_no_space_for_punctuation(paragraph: str) -> str:
    return re.sub(r'([,.;:])([a-zA-Z])', r'\1 \2', paragraph)


def fix_quotation_bad_ending(paragraph: str) -> str:
    return re.sub(r"([,.])(['\"])\b(?!s)", r"\1\2 ", paragraph)


def fix_quotation_spaces(paragraph: str) -> str:
    return re.sub(r"\b(['\"]) s", r"\1s", paragraph)


def fix_clause_bad_ending(paragraph: str) -> str:
    return re.sub(r"([.,])([a-zA-z])", r"\1 \2", paragraph)


def fix_bad_hyphenation(paragraph: str) -> str:
    return re.sub(r"- | -| - ", r"-", paragraph)


def fix_bad_em_dash(paragraph: str) -> str:
    return re.sub(r"-—|—-", r"—", paragraph)


def fix_abbreviated_year(paragraph: str) -> str:
    return re.sub(r"' (\d{2} )", r" '\1", paragraph)


def sanitise_paragraph(paragraph: str, reverse: bool = False) -> str:
    if reverse is False:
        paragraph = fix_newlines(paragraph)
        paragraph = fix_tabs(paragraph)
        paragraph = fix_ambiguous_symbol(paragraph)
        paragraph = fix_hyphenation(paragraph)
        paragraph = fix_quotations(paragraph)
        paragraph = fix_em_dash(paragraph)
        paragraph = fix_number_concatenation(paragraph)

    if reverse is True:
        paragraph = fix_duplicated_punctuation(paragraph)
        paragraph = fix_no_space_for_punctuation(paragraph)
        """
        paragraph = fix_space_before_punctuation(paragraph)
        paragraph = fix_quotation_bad_ending(paragraph)
        paragraph = fix_clause_bad_ending(paragraph)
        paragraph = fix_bad_em_dash(paragraph)
        paragraph = fix_bad_hyphenation(paragraph)
        paragraph = fix_quotation_spaces(paragraph)
        """
        paragraph = fix_abbreviated_year(paragraph)
    return paragraph
