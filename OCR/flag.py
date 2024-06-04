from enum import IntFlag


class ScanFlags(IntFlag):
    NoFlags = 0
    SplitPage = 1 << 0
    FixHyphenation = 1 << 1
    FixNewlines = 1 << 2
