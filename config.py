import string

# Default character sets
CHARS_LOWERCASE = string.ascii_lowercase
CHARS_UPPERCASE = string.ascii_uppercase
CHARS_DIGITS = string.digits
CHARS_SYMBOLS = string.punctuation

# Characters that are commonly confused (e.g., 1, l, I, O, 0)
AMBIGUOUS_CHARS = "lIO01"

# Common keyboard sequences and dictionary words to avoid
COMMON_PATTERNS = [
    "password", "123456", "qwerty", "asdfgh", "zxcvbn", "qazwsx",
    "password123", "admin", "abcdef", "111111", "222222", "333333",
    "john", "mary",
]

# Path to the EFF Long Wordlist for Diceware
DICEWARE_WORDLIST_PATH = "wordlists/eff_large_wordlist.txt"

# HIBP local database path (Still exists in config but not used for checks by utils.py anymore)
HIBP_LOCAL_DB_PATH = "pwned-passwords-sha1-v7.txt"

# HIBP API URL for online checks
HIBP_API_URL = "https://api.pwnedpasswords.com/range/"

# Minimum and Maximum lengths for generated passwords
DEFAULT_MIN_LENGTH = 12
DEFAULT_MAX_LENGTH = 24
DICEWARE_DEFAULT_WORD_COUNT = 6 # Recommended for strong passphrases

# ANSI escape codes for coloring CLI output
class Colors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKCYAN = '\033[96m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'