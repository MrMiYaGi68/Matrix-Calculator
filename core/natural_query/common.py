from __future__ import annotations

import re

from core.formatting import format_number


UNIT_FACTORS = {
    "mm": 0.001,
    "millimeter": 0.001,
    "cm": 0.01,
    "zentimeter": 0.01,
    "m": 1.0,
    "meter": 1.0,
    "km": 1000.0,
    "kilometer": 1000.0,
    "mg": 0.001,
    "g": 1.0,
    "gramm": 1.0,
    "kg": 1000.0,
    "kilogramm": 1000.0,
    "ml": 0.001,
    "milliliter": 0.001,
    "l": 1.0,
    "liter": 1.0,
    "min": 60.0,
    "minute": 60.0,
    "minuten": 60.0,
    "h": 3600.0,
    "std": 3600.0,
    "stunde": 3600.0,
    "stunden": 3600.0,
    "tag": 86400.0,
    "tage": 86400.0,
    "woche": 604800.0,
    "wochen": 604800.0,
    "monat": 2629800.0,
    "monate": 2629800.0,
    "jahr": 31557600.0,
    "jahre": 31557600.0,
    "w": 1.0,
    "watt": 1.0,
    "kw": 1000.0,
    "kilowatt": 1000.0,
    "ps": 735.49875,
    "pferdestaerke": 735.49875,
    "pferdestärke": 735.49875,
    "hp": 745.699872,
    "horsepower": 745.699872,
}


WORD_REPLACEMENTS = {
    "wievil": "wie viel",
    "wiviel": "wie viel",
    "wieviel": "wie viel",
    "wifiel": "wie viel",
    "wi": "wie",
    "wii": "wie",
    "sint": "sind",
    "sindd": "sind",
    "is": "ist",
    "istt": "ist",
    "wass": "was",
    "waas": "was",
    "fon": "von",
    "vohn": "von",
    "vonn": "von",
    "fuer": "für",
    "fur": "für",
    "fr": "für",
    "mitt": "mit",
    "mti": "mit",
    "bie": "bei",
    "beim": "bei",
    "brauhe": "brauche",
    "brache": "brauche",
    "brauch": "brauche",
    "brauchhe": "brauche",
    "rechne": "berechne",
    "rechnen": "berechne",
    "berechnen": "berechne",
    "prozent": "%",
    "prozente": "%",
    "proz": "%",
    "rabatt": "rabatt",
    "rabbat": "rabatt",
    "rabt": "rabatt",
    "mehrwehrtsteuer": "mehrwertsteuer",
    "mehrwertsteur": "mehrwertsteuer",
    "mwst": "mehrwertsteuer",
    "wurzel": "wurzel",
    "wurtzel": "wurzel",
    "würzel": "wurzel",
    "quadratwurzel": "quadratwurzel",
    "quatratwurzel": "quadratwurzel",
    "quadradwurzel": "quadratwurzel",
    "quadratwurtzel": "quadratwurzel",
    "pluss": "plus",
    "pls": "plus",
    "minuus": "minus",
    "mall": "mal",
    "malll": "mal",
    "mahll": "mal",
    "geteilt": "geteilt",
    "geteillt": "geteilt",
    "geteil": "geteilt",
    "duch": "durch",
    "druch": "durch",
    "kilomter": "kilometer",
    "kilomterh": "kmh",
    "stundn": "stunden",
    "stunde": "stunde",
    "std": "stunden",
}

PHRASE_REPLACEMENTS = {
    "wie fiel": "wie viel",
    "wi viel": "wie viel",
    "wie vil": "wie viel",
    "was sint": "was sind",
    "geteilt duch": "geteilt durch",
    "geteilt druch": "geteilt durch",
    "km h": "kmh",
    "km / h": "km/h",
    "kilometer pro stunde": "kmh",
    "ps kw": "ps-kw",
    "kw ps": "kw-ps",
}

ENGLISH_CHAT_ABBREVIATIONS = {
    "u": "you",
    "r": "are",
    "ur": "your",
    "ure": "you are",
    "ya": "you",
    "wut": "what",
    "wat": "what",
    "wats": "what is",
    "whats": "what is",
    "cn": "can",
    "pls": "please",
    "plz": "please",
    "thx": "thanks",
    "thnx": "thanks",
    "ty": "thanks",
    "tysm": "thanks",
    "np": "no problem",
    "yw": "you are welcome",
    "bc": "because",
    "bcz": "because",
    "cuz": "because",
    "coz": "because",
    "rn": "right now",
    "btw": "by the way",
    "fyi": "for your information",
    "idk": "i do not know",
    "imo": "in my opinion",
    "imho": "in my humble opinion",
    "asap": "as soon as possible",
    "brb": "be right back",
    "ttyl": "talk to you later",
    "lol": "laugh out loud",
    "omg": "oh my god",
    "ok": "okay",
    "sup": "what is up",
    "zup": "what is up",
}


GERMAN_SMALL_NUMBER_WORDS = {
    "null": 0,
    "eins": 1,
    "einer": 1,
    "zwei": 2,
    "drei": 3,
    "vier": 4,
    "fünf": 5,
    "fuenf": 5,
    "sechs": 6,
    "sieben": 7,
    "acht": 8,
    "neun": 9,
    "zehn": 10,
    "elf": 11,
    "zwölf": 12,
    "zwoelf": 12,
    "dreizehn": 13,
    "vierzehn": 14,
    "fünfzehn": 15,
    "fuenfzehn": 15,
    "sechzehn": 16,
    "siebzehn": 17,
    "achtzehn": 18,
    "neunzehn": 19,
}

GERMAN_TENS_NUMBER_WORDS = {
    "zwanzig": 20,
    "dreißig": 30,
    "dreissig": 30,
    "vierzig": 40,
    "fünfzig": 50,
    "fuenfzig": 50,
    "sechzig": 60,
    "siebzig": 70,
    "achtzig": 80,
    "neunzig": 90,
}

ENGLISH_SMALL_NUMBER_WORDS = {
    "zero": 0,
    "one": 1,
    "two": 2,
    "three": 3,
    "four": 4,
    "five": 5,
    "six": 6,
    "seven": 7,
    "eight": 8,
    "nine": 9,
    "ten": 10,
    "eleven": 11,
    "twelve": 12,
    "thirteen": 13,
    "fourteen": 14,
    "fifteen": 15,
    "sixteen": 16,
    "seventeen": 17,
    "eighteen": 18,
    "nineteen": 19,
}

ENGLISH_TENS_NUMBER_WORDS = {
    "twenty": 20,
    "thirty": 30,
    "forty": 40,
    "fifty": 50,
    "sixty": 60,
    "seventy": 70,
    "eighty": 80,
    "ninety": 90,
}


def normalize_natural_query(text: str) -> str:
    normalized = text.lower().strip().replace(",", ".")
    normalized = normalized.replace("–", "-").replace("—", "-")
    normalized = re.sub(r"\s+", " ", normalized)
    normalized = replace_english_chat_abbreviations(normalized)
    normalized = replace_number_abbreviations(normalized)
    for source, target in sorted(PHRASE_REPLACEMENTS.items(), key=lambda item: len(item[0]), reverse=True):
        normalized = normalized.replace(source, target)
    normalized = replace_number_words(normalized)
    for source, target in sorted(WORD_REPLACEMENTS.items(), key=lambda item: len(item[0]), reverse=True):
        normalized = re.sub(rf"(?<![a-zäöüß]){re.escape(source)}(?![a-zäöüß])", target, normalized)
    normalized = re.sub(r"\s+", " ", normalized)
    return normalized.strip()


def replace_english_chat_abbreviations(text: str) -> str:
    text = re.sub(r"(?<!\S)w/o(?!\S)", "without", text)
    text = re.sub(r"(?<!\S)w/(?!\S)", "with", text)
    text = re.sub(r"(?<!\S)u2(?!\S)", "you too", text)

    def replace_match(match: re.Match[str]) -> str:
        token = match.group(0)
        if token == "pls" and _looks_like_plus_typo(text, match.start(), match.end()):
            return "plus"
        if token == "r" and _looks_like_radius_symbol(text, match.start(), match.end()):
            return "r"
        return ENGLISH_CHAT_ABBREVIATIONS.get(token, token)

    pattern = "|".join(sorted((re.escape(key) for key in ENGLISH_CHAT_ABBREVIATIONS), key=len, reverse=True))
    return re.sub(rf"(?<![a-zäöüß])(?:{pattern})(?![a-zäöüß])", replace_match, text)


def _looks_like_plus_typo(text: str, start: int, end: int) -> bool:
    before = text[:start].rstrip()
    after = text[end:].lstrip()
    return bool(re.search(r"\d(?:\.\d+)?$", before) and re.match(r"\d", after))


def _looks_like_radius_symbol(text: str, start: int, end: int) -> bool:
    before = text[:start].rstrip()
    after = text[end:].lstrip()
    return bool(
        re.search(r"(?:circle|sphere|cylinder|cone|radius|area|volume|circumference|surface)\s*$", before)
        and re.match(r"\d", after)
    )


def replace_number_abbreviations(text: str) -> str:
    multipliers = {
        "k": 1_000,
        "tsd": 1_000,
        "tausend": 1_000,
        "mio": 1_000_000,
        "million": 1_000_000,
        "millionen": 1_000_000,
        "mn": 1_000_000,
        "mrd": 1_000_000_000,
        "milliarde": 1_000_000_000,
        "milliarden": 1_000_000_000,
        "bn": 1_000_000_000,
    }
    suffix_pattern = "|".join(sorted((re.escape(key) for key in multipliers), key=len, reverse=True))

    def replace_match(match: re.Match[str]) -> str:
        value = float(match.group("value"))
        suffix = match.group("suffix").rstrip(".")
        expanded = value * multipliers[suffix]
        return format_number(expanded)

    return re.sub(
        rf"(?<![\wäöüß])(?P<value>\d+(?:\.\d+)?)\s*(?P<suffix>{suffix_pattern})\.?(?![a-zäöüß])",
        replace_match,
        text,
    )


def replace_number_words(text: str) -> str:
    def replace_match(match: re.Match[str]) -> str:
        token = match.group(0)
        value = number_word_value(token)
        return str(value) if value is not None else token

    return re.sub(r"(?<![a-zäöüß])[\wäöüß]+(?:-[\wäöüß]+)*(?![a-zäöüß])", replace_match, text)


def number_word_value(token: str) -> int | None:
    normalized = token.lower().replace("-", "")
    if not re.fullmatch(r"[a-zäöüß]+", normalized):
        return None
    german = _german_number_word_value(normalized)
    if german is not None:
        return german
    return _english_number_word_value(normalized)


def _german_number_word_value(word: str) -> int | None:
    if word in GERMAN_SMALL_NUMBER_WORDS:
        return GERMAN_SMALL_NUMBER_WORDS[word]
    if word in GERMAN_TENS_NUMBER_WORDS:
        return GERMAN_TENS_NUMBER_WORDS[word]
    if word == "hundert":
        return 100
    if word == "tausend":
        return 1000
    if "tausend" in word:
        left, right = word.split("tausend", 1)
        left_value = 1 if left in {"", "ein"} else _german_number_word_value(left)
        right_value = _german_number_word_value(right) if right else 0
        if left_value is not None and right_value is not None:
            return left_value * 1000 + right_value
    if "hundert" in word:
        left, right = word.split("hundert", 1)
        left_value = 1 if left in {"", "ein"} else _german_number_word_value(left)
        right_value = _german_number_word_value(right) if right else 0
        if left_value is not None and right_value is not None:
            return left_value * 100 + right_value
    if "und" in word:
        left, right = word.split("und", 1)
        left_value = 1 if left == "ein" else GERMAN_SMALL_NUMBER_WORDS.get(left)
        right_value = GERMAN_TENS_NUMBER_WORDS.get(right)
        if left_value is not None and 1 <= left_value <= 9 and right_value is not None:
            return right_value + left_value
    return None


def _english_number_word_value(word: str) -> int | None:
    if word in ENGLISH_SMALL_NUMBER_WORDS:
        return ENGLISH_SMALL_NUMBER_WORDS[word]
    if word in ENGLISH_TENS_NUMBER_WORDS:
        return ENGLISH_TENS_NUMBER_WORDS[word]
    if word == "hundred":
        return 100
    if word == "thousand":
        return 1000
    if word.endswith("hundred"):
        left = word[: -len("hundred")]
        left_value = ENGLISH_SMALL_NUMBER_WORDS.get(left)
        if left_value is not None:
            return left_value * 100
    if word.endswith("thousand"):
        left = word[: -len("thousand")]
        left_value = _english_number_word_value(left)
        if left_value is not None:
            return left_value * 1000
    for tens_word, tens_value in ENGLISH_TENS_NUMBER_WORDS.items():
        if word.startswith(tens_word):
            suffix = word[len(tens_word) :]
            suffix_value = ENGLISH_SMALL_NUMBER_WORDS.get(suffix)
            if suffix_value is not None and 1 <= suffix_value <= 9:
                return tens_value + suffix_value
    return None


def extract_numbers(text: str) -> list[float]:
    return [float(value) for value in re.findall(r"\d+(?:\.\d+)?", text)]


def format_local_result(expression: str, value: float, explanation: str) -> tuple[str, str, str]:
    return expression, format_number(value), explanation


def unit_factor(unit: str) -> float | None:
    return UNIT_FACTORS.get(unit.lower())


def local_smalltalk_response(query: str) -> tuple[str, str, str] | None:
    lowered = query.lower().strip()
    compact = re.sub(r"[^\wäöüß]+", " ", lowered).strip()
    expanded_compact = re.sub(r"[^\wäöüß]+", " ", replace_english_chat_abbreviations(lowered)).strip()
    if compact in {"hallo", "hi", "hey", "moin", "guten tag", "servus"}:
        return (
            "",
            "Hallo! Ich kann einfache Rechnungen, Mathefragen und Alltagsformeln direkt lokal lösen.",
            "Du kannst zum Beispiel schreiben: Was ist 5 plus 5?, 20% von 450 oder Wurzel von 100.",
        )
    if compact in {"hello", "hi", "hey", "good morning", "good afternoon", "good evening"} or expanded_compact in {
        "what is up",
        "how are you",
    }:
        return (
            "",
            "Hello! I can solve simple calculations, math questions, and everyday formulas locally.",
            "For example, try: What is 5 plus 5?, 20% of 450, or square root of 100.",
        )
    if compact in {"danke", "dankeschön", "thanks", "thank you"} or expanded_compact in {"thanks", "you are welcome"}:
        if compact in {"thanks", "thank you"} or expanded_compact in {"thanks", "you are welcome"}:
            return ("", "You're welcome.", "You can enter the next calculation directly.")
        return ("", "Gern.", "Wenn du willst, kannst du direkt die nächste Rechnung eingeben.")
    if compact in {"what can you do", "what can you calculate", "help", "can you help me"} or expanded_compact in {
        "what can you do",
        "what can you calculate",
        "can you help me",
    }:
        return (
            "",
            "I can solve local math and calculator questions in German and English.",
            "Examples: What is 20% of 450?, How long for 600 km with 50 km/h?, or circle area with radius 5.",
        )
    if compact in {"who are you", "what are you"} or expanded_compact in {"who are you", "what are you"}:
        return (
            "",
            "I am the local Matrix AI calculator assistant.",
            "I solve supported math questions on this device; for broader topics you can use the online ChatGPT option.",
        )
    return None
