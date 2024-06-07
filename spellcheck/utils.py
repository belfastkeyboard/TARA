from sys import exit

from utils.status import info, warn


def fix_byte(bad_string: str, bad_byte: str, replacement: str) -> str:
    return bad_string.replace(bad_byte, replacement)


def fix_encoding_errors(exc: UnicodeDecodeError) -> str:
    byte_repr = exc.object
    inv_byte = byte_repr[exc.start:exc.end]

    byte_repr = byte_repr.replace(inv_byte, b'')

    try:
        return byte_repr.decode('utf-8')
    except UnicodeDecodeError as e:
        byte_repr = fix_encoding_errors(e)
    finally:
        return byte_repr.decode('utf-8') if isinstance(byte_repr, bytes) else byte_repr


def prepare_text_for_analysis(text: str) -> tuple[list[str], list[int]]:

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


def restitch_text(text: list[str], indices: list[int], original_text: str) -> str:
    length = len(original_text)
    modified_text = original_text
    i = 0

    while text:

        try:
            if i > len(original_text) + 1000:
                raise IndexError(f"Index i: {i} out of bounds.")
        except IndexError as e:
            warn(e)
            info(f"Original bounds: {len(original_text)}.")
            warn("Aborting spellchecking, returning original text.")
            return original_text

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
            except MemoryError as e:  # TODO: figure out why this exception is here
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
