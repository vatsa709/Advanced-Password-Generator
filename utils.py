import math
import hashlib
import os
import requests # Used for HIBP online check
import sys
import platform # To check OS for clipboard functionality
import string # Added for string.punctuation

# Corrected import: HIBP_LOCAL_DB_PATH is no longer imported
from config import COMMON_PATTERNS, AMBIGUOUS_CHARS, HIBP_API_URL, Colors

def calculate_entropy(password: str) -> float:
    """
    Calculates the Shannon entropy of a password.
    More accurately, it considers the unique characters present in the password.
    """
    if not password:
        return 0.0

    charset = set()
    for char in password:
        if 'a' <= char <= 'z':
            charset.add('lowercase')
        elif 'A' <= char <= 'Z':
            charset.add('uppercase')
        elif '0' <= char <= '9':
            charset.add('digit')
        elif char in string.punctuation:
            charset.add('symbol')
        else:
            charset.add('other') # For any other characters (e.g., extended ASCII, Unicode)

    estimated_charset_size = 0
    if 'lowercase' in charset:
        estimated_charset_size += 26
    if 'uppercase' in charset:
        estimated_charset_size += 26
    if 'digit' in charset:
        estimated_charset_size += 10
    if 'symbol' in charset:
        estimated_charset_size += 32 # Common ASCII symbols in string.punctuation
    if 'other' in charset:
        estimated_charset_size += 50 # Example: for extended ASCII or specific Unicode blocks

    if estimated_charset_size == 0:
        return 0.0

    return len(password) * math.log2(estimated_charset_size)

def estimate_crack_time(entropy: float) -> str:
    """
    Estimates crack time based on entropy, assuming 1 trillion (10^12) guesses per second.
    """
    if entropy <= 0:
        return "Instantly"

    guesses_per_second = 10**12 # Assuming a powerful attacker (e.g., modern GPUs)
    total_guesses = 2**entropy

    seconds = total_guesses / guesses_per_second

    minutes = seconds / 60
    hours = minutes / 60
    days = hours / 24
    years = days / 365.25

    if years >= 1:
        return f"{years:.2f} years"
    elif days >= 1:
        return f"{days:.2f} days"
    elif hours >= 1:
        return f"{hours:.2f} hours"
    elif minutes >= 1:
        return f"{minutes:.2f} minutes"
    else:
        return f"{seconds:.2f} seconds"

def check_for_common_patterns(password: str) -> bool:
    """
    Checks if the password contains any common, easily guessable patterns.
    """
    password_lower = password.lower()
    for pattern in COMMON_PATTERNS:
        if pattern in password_lower:
            return True
    return False

def check_for_consecutive_repetitions(password: str, max_consecutive: int = 2) -> bool:
    """
    Checks for characters repeating `max_consecutive + 1` or more times consecutively.
    e.g., if max_consecutive is 2, it checks for 'aaa', '111'.
    """
    if max_consecutive < 1:
        return False # Invalid setting

    for i in range(len(password) - max_consecutive):
        if all(password[j] == password[i] for j in range(i, i + max_consecutive + 1)):
            return True
    return False

def check_for_ambiguous_chars(password: str) -> bool:
    """
    Checks if the password contains any ambiguous characters.
    """
    return any(char in AMBIGUOUS_CHARS for char in password)

def check_pwned_password(password: str) -> bool:
    """
    Checks if a password has been compromised using the HIBP online API.
    """
    password_hash = hashlib.sha1(password.encode('utf-8')).hexdigest().upper()
    prefix = password_hash[:5]
    suffix = password_hash[5:]

    try:
        # User-Agent header is recommended by HIBP API guidelines
        response = requests.get(HIBP_API_URL + prefix, headers={'User-Agent': 'PythonPasswordGenerator'})
        response.raise_for_status() # Raise an HTTPError for bad responses (4xx or 5xx)

        for line in response.text.splitlines():
            s, count = line.split(':')
            if s == suffix:
                return True # Password found in breach
        return False
    except requests.exceptions.RequestException as e:
        print(f"{Colors.WARNING}Warning: Could not connect to HIBP API for check. (Error: {e}){Colors.ENDC}")
        print(f"{Colors.WARNING}This might be due to network issues or API rate limits. Check skipped.{Colors.ENDC}")
        return False
    except Exception as e:
        print(f"{Colors.FAIL}An unexpected error occurred during HIBP online check: {e}{Colors.ENDC}")
        return False

def copy_to_clipboard(text: str):
    """
    Copies the given text to the system clipboard.
    Requires 'pyperclip' to be installed (`pip install pyperclip`).
    Falls back to a message if pyperclip is not available or if on unsupported OS.
    """
    try:
        import pyperclip
        pyperclip.copy(text)
        print(f"{Colors.OKGREEN}Password copied to clipboard!{Colors.ENDC}")
    except ImportError:
        print(f"{Colors.WARNING}Warning: pyperclip not installed. Cannot copy to clipboard automatically.{Colors.ENDC}")
        print(f"{Colors.OKCYAN}Please install it: pip install pyperclip{Colors.ENDC}")
    except pyperclip.PyperclipException as e:
        # Catch specific pyperclip errors, e.g., on Linux without xclip/xsel
        print(f"{Colors.WARNING}Warning: Could not copy to clipboard. Pyperclip error: {e}{Colors.ENDC}")
        if platform.system() == "Linux":
            print(f"{Colors.WARNING}On Linux, you might need 'xclip' or 'xsel'. Try: sudo apt-get install xclip{Colors.ENDC}")
    except Exception as e:
        print(f"{Colors.WARNING}Could not copy to clipboard due to an unexpected error: {e}{Colors.ENDC}")