import os
import re
import time
from pathlib import Path

import SymSpellCppPy

from utils.error import error_dispatcher
from utils.status import info, good, progress, warn
from utils.system import delete, DirectoryContents

from .utils import fix_encoding_errors, prepare_text_for_analysis, restitch_text
from .bundle import bundle_dictionaries

SCRIPT_DIR = Path(__file__).resolve().parent
PROJECT_DIR = SCRIPT_DIR.parent
DICTIONARY_DIR = Path(PROJECT_DIR, 'dictionaries')


# TODO: merge spellcheck and spellcheck_batch into one function
#   like segment object, have it run the spellcheck in the init
#   then have one function for retrieving the result
class Spellchecker(SymSpellCppPy.SymSpell):
    def __init__(self) -> None:
        super().__init__()
        self.clause_separator = re.compile(r"[.?!,:']+")  # this is unused
        self.verbosity = SymSpellCppPy.Verbosity.CLOSEST  # i don't think this is used either

        self.loaded = False
        self.dictionaries = DICTIONARY_DIR
        self.temp_std_dict_path = None  # TODO: shift these over to the /tmp path
        self.temp_bigram_dict_path = None

        self.load_dictionaries()

        return

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        if self.temp_std_dict_path:
            delete(self.temp_std_dict_path)
        if self.temp_bigram_dict_path:
            delete(self.temp_bigram_dict_path)

    def load_dictionaries(self) -> None:
        dictionaries: DirectoryContents
        std_dict: list[str]
        bigram_dict: list[str]

        dictionaries = DirectoryContents([Path(self.dictionaries, item) for item in os.listdir(self.dictionaries)])

        if not dictionaries:
            error_dispatcher.raise_error('Dictionary not found', "Use 'Dictionary' tab to load dictionaries.")
            return

        dictionaries.clear_except('.txt')
        dictionaries = DirectoryContents([str(item) for item in dictionaries])
        std_dict = list(filter(lambda x: "bigram" not in x, dictionaries))
        bigram_dict = list(filter(lambda x: "bigram" in x, dictionaries))
        del dictionaries

        # bundle dictionaries into one dictionary
        if std_dict:
            self.temp_std_dict_path = bundle_dictionaries([Path(item) for item in std_dict])
            self.load_dictionary(
                corpus=str(self.temp_std_dict_path), term_index=0, count_index=1, separator=' '
            )
            self.loaded = True

        if bigram_dict:
            self.temp_bigram_dict_path = bundle_dictionaries([Path(item) for item in std_dict])
            self.load_bigram_dictionary(
                corpus=str(self.temp_bigram_dict_path), term_index=0, count_index=2, separator=' '
            )
            self.loaded = True

        return

    def spellcheck(self, paragraph: str, log: bool = True) -> str:

        """ lookup compound with bigram dictionary seems to be much better at getting the correct word
            but it simply doesn't get it right all the time. it would probably be good to build an irish
            nationalist bigram dictionary by getting pairs of words and adding them to the standard bigram
            dictionary with an artificially elevated frequency """

        if log:
            info("Spellchecking.")

        start = time.time()
        clauses, indices = prepare_text_for_analysis(paragraph)

        for i, clause in enumerate(clauses):

            if len(clause.strip()) < 2:
                continue

            suggestion = self.lookup_compound(
                input=clause, max_edit_distance=2, transfer_casing=True
            )

            try:
                clauses[i] = suggestion[0].term
            except UnicodeDecodeError as e:
                clauses[i] = fix_encoding_errors(clause, e)

        paragraph = restitch_text(clauses, indices, paragraph)
        end = time.time()

        if log:
            good(f"Spellchecked in {(end - start):.2f} seconds.")

        return paragraph

    def spellcheck_batch(self, paragraphs: list[str]) -> list[str]:

        """ lookup compound with bigram dictionary seems to be much better at getting the correct word
            but it simply doesn't get it right all the time. it would probably be good to build an irish
            nationalist bigram dictionary by getting pairs of words and adding them to the standard bigram
            dictionary with an artificially elevated frequency """

        checked_paragraphs: list[str]

        info("Spellchecking.")

        checked_paragraphs = list()
        paragraph_count = len(paragraphs)
        start = time.time()

        for i, paragraph in enumerate(paragraphs):
            if "Digitized by mel Archive" in paragraph:
                pass

            clauses, indices = prepare_text_for_analysis(paragraph)

            for j, clause in enumerate(clauses):

                if len(clause.strip()) < 2:
                    continue

                suggestion = self.lookup_compound(
                    input=clause, max_edit_distance=2, transfer_casing=True
                )

                try:
                    clauses[j] = suggestion[0].term
                except UnicodeEncodeError as e:
                    warn(e)
                    continue
                except UnicodeDecodeError as exc:
                    clauses[j] = fix_encoding_errors(exc)

            checked_paragraphs.append(restitch_text(clauses, indices, paragraph))

            progress(
                f"Spellchecked paragraphs: {i + 1} out of {paragraph_count}.",
                end='' if i + 1 < paragraph_count else '\r'
            )

        end = time.time()

        good(f"Spellchecked in {(end - start):.2f} seconds.\n")

        return checked_paragraphs
