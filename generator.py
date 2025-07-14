import secrets
import math
from typing import List, Optional
from config import (
    CHARS_LOWERCASE, CHARS_UPPERCASE, CHARS_DIGITS, CHARS_SYMBOLS,
    AMBIGUOUS_CHARS, DICEWARE_WORDLIST_PATH,
)

class PasswordGenerator:
    def __init__(self):
        self.wordlist: List[str] = []
        self._load_diceware_wordlist()

    def _load_diceware_wordlist(self):
        """Loads the Diceware wordlist from the specified path."""
        try:
            with open(DICEWARE_WORDLIST_PATH, 'r', encoding='utf-8') as f:
                # Assuming wordlist format is "XXXXX\tword"
                self.wordlist = [line.strip().split('\t')[1] for line in f if line.strip()]
            if not self.wordlist:
                raise ValueError("Diceware wordlist is empty after loading.")
        except FileNotFoundError:
            print(f"Error: Diceware wordlist not found at '{DICEWARE_WORDLIST_PATH}'.")
            print("Please download it from https://www.eff.org/files/2016/07/18/eff_large_wordlist.txt and place it in the 'wordlists' directory.")
            self.wordlist = [] # Ensure wordlist is empty if file not found
        except Exception as e:
            print(f"Error loading Diceware wordlist: {e}")
            self.wordlist = []

    def generate_random_password(
        self,
        length: int,
        use_lower: bool = True,
        use_upper: bool = True,
        use_digits: bool = True,
        use_symbols: bool = True,
        exclude_ambiguous: bool = False,
        min_lower: int = 0,
        min_upper: int = 0,
        min_digits: int = 0,
        min_symbols: int = 0,
        avoid_patterns_func=None, # Callable for pattern checking (e.g., check_for_common_patterns)
        avoid_repetitions_func=None # Callable for repetition checking (e.g., check_for_consecutive_repetitions)
    ) -> Optional[str]:
        """
        Generates a random password with specified criteria.
        Uses secrets module for cryptographically secure randomness.
        Guarantees minimum inclusion of character types.
        """
        if not (use_lower or use_upper or use_digits or use_symbols):
            print("Error: At least one character type (lower, upper, digits, symbols) must be selected.")
            return None

        char_pool = ""
        if use_lower:
            char_pool += CHARS_LOWERCASE
        if use_upper:
            char_pool += CHARS_UPPERCASE
        if use_digits:
            char_pool += CHARS_DIGITS
        if use_symbols:
            char_pool += CHARS_SYMBOLS

        if exclude_ambiguous:
            char_pool = "".join(c for c in char_pool if c not in AMBIGUOUS_CHARS)

        if not char_pool:
            print("Error: Character pool is empty after exclusions. Cannot generate password.")
            return None

        # Ensure minimum length requirements are met
        total_min_required = min_lower + min_upper + min_digits + min_symbols
        if total_min_required > length:
            print(f"Error: Minimum required characters ({total_min_required}) exceed total length ({length}).")
            return None

        password_chars: List[str] = []

        # 1. Guarantee minimum required characters
        # Ensure we add chars only if their type is enabled for general use
        if use_lower:
            for _ in range(min_lower):
                password_chars.append(secrets.choice(CHARS_LOWERCASE))
        if use_upper:
            for _ in range(min_upper):
                password_chars.append(secrets.choice(CHARS_UPPERCASE))
        if use_digits:
            for _ in range(min_digits):
                password_chars.append(secrets.choice(CHARS_DIGITS))
        if use_symbols:
            for _ in range(min_symbols):
                password_chars.append(secrets.choice(CHARS_SYMBOLS))

        # 2. Fill the rest of the password length
        remaining_length = length - len(password_chars)
        for _ in range(remaining_length):
            password_chars.append(secrets.choice(char_pool))

        # 3. Shuffle the password characters to randomize positions of guaranteed chars
        secrets.SystemRandom().shuffle(password_chars)
        generated_password = "".join(password_chars)

        # 4. Apply post-generation checks and regenerate if necessary
        # We limit regeneration attempts to prevent infinite loops for impossible constraints
        max_attempts = 100
        attempts = 0
        while attempts < max_attempts:
            is_valid = True
            if avoid_patterns_func and avoid_patterns_func(generated_password):
                is_valid = False
            if is_valid and avoid_repetitions_func and avoid_repetitions_func(generated_password):
                is_valid = False

            if is_valid:
                return generated_password
            else:
                # If invalid, regenerate the entire password
                password_chars = []
                # Re-do step 1 and 2
                if use_lower:
                    for _ in range(min_lower):
                        password_chars.append(secrets.choice(CHARS_LOWERCASE))
                if use_upper:
                    for _ in range(min_upper):
                        password_chars.append(secrets.choice(CHARS_UPPERCASE))
                if use_digits:
                    for _ in range(min_digits):
                        password_chars.append(secrets.choice(CHARS_DIGITS))
                if use_symbols:
                    for _ in range(min_symbols):
                        password_chars.append(secrets.choice(CHARS_SYMBOLS))
                
                remaining_length = length - len(password_chars)
                for _ in range(remaining_length):
                    password_chars.append(secrets.choice(char_pool))
                
                # Re-do step 3
                secrets.SystemRandom().shuffle(password_chars)
                generated_password = "".join(password_chars)
                attempts += 1
        
        print(f"Warning: Could not generate a password meeting all criteria after {max_attempts} attempts. Returning last attempt.")
        return generated_password


    def generate_passphrase(
        self,
        word_count: int,
        delimiter: str = "-",
        capitalize_words: bool = False,
        add_number: bool = False,
        add_symbol: bool = False,
        avoid_patterns_func=None,
        avoid_repetitions_func=None
    ) -> Optional[str]:
        """
        Generates a Diceware-style passphrase.
        """
        if not self.wordlist:
            print("Error: Diceware wordlist not loaded. Cannot generate passphrase.")
            return None
        if word_count <= 0:
            print("Error: Word count must be positive for passphrase generation.")
            return None

        max_attempts = 100
        attempts = 0
        while attempts < max_attempts:
            phrase_words: List[str] = [secrets.choice(self.wordlist) for _ in range(word_count)]

            if capitalize_words:
                phrase_words = [word.capitalize() for word in phrase_words]

            if add_number:
                phrase_words.append(secrets.choice(CHARS_DIGITS))
            if add_symbol:
                phrase_words.append(secrets.choice(CHARS_SYMBOLS))

            # Shuffle if number/symbol added, otherwise just join
            if add_number or add_symbol:
                secrets.SystemRandom().shuffle(phrase_words)

            generated_passphrase = delimiter.join(phrase_words)

            is_valid = True
            if avoid_patterns_func and avoid_patterns_func(generated_passphrase):
                is_valid = False
            if is_valid and avoid_repetitions_func and avoid_repetitions_func(generated_passphrase):
                is_valid = False

            if is_valid:
                return generated_passphrase
            else:
                attempts += 1
        
        print(f"Warning: Could not generate a passphrase meeting all criteria after {max_attempts} attempts. Returning last attempt.")
        return generated_passphrase