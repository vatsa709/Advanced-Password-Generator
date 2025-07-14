import argparse
import sys
import os
import secrets # Used for random length generation

from generator import PasswordGenerator
from utils import (
    calculate_entropy, estimate_crack_time, check_for_common_patterns,
    check_for_consecutive_repetitions, check_pwned_password,
    copy_to_clipboard, check_for_ambiguous_chars
)
from config import (
    DEFAULT_MIN_LENGTH, DEFAULT_MAX_LENGTH, DICEWARE_DEFAULT_WORD_COUNT,
    Colors, DICEWARE_WORDLIST_PATH,
)

# New import for the GUI
from gui import launch_gui

def main():
    parser = argparse.ArgumentParser(
        description=f"{Colors.BOLD}{Colors.OKBLUE}Advanced Password Generator{Colors.ENDC}",
        formatter_class=argparse.RawTextHelpFormatter
    )

    # General options
    parser.add_argument('-l', '--length', type=int,
                        help=f"Length of the password (default: random between {DEFAULT_MIN_LENGTH}-{DEFAULT_MAX_LENGTH} for random, or {DICEWARE_DEFAULT_WORD_COUNT} for passphrase). If minimum character types are specified, default is {DEFAULT_MIN_LENGTH}.")
    parser.add_argument('-n', '--count', type=int, default=1,
                        help="Number of passwords to generate (default: 1)")
    parser.add_argument('-c', '--copy', action='store_true',
                        help="Copy the generated password(s) to clipboard (requires 'pyperclip').")
    
    # New argument to launch the GUI
    parser.add_argument('--gui', action='store_true',
                        help="Launch the graphical user interface.")

    # Random password generation options
    random_group = parser.add_argument_group(f'{Colors.OKCYAN}Random Password Options{Colors.ENDC}')
    random_group.add_argument('--no-lower', action='store_true',
                               help="Exclude lowercase characters (a-z)")
    random_group.add_argument('--no-upper', action='store_true',
                               help="Exclude uppercase characters (A-Z)")
    random_group.add_argument('--no-digits', action='store_true',
                               help="Exclude digits (0-9)")
    random_group.add_argument('--no-symbols', action='store_true',
                               help="Exclude symbols (!@#$...)")
    random_group.add_argument('--exclude-ambiguous', action='store_true',
                               help="Exclude ambiguous characters (l, I, O, 0, 1) to improve readability/typing.")
    random_group.add_argument('--min-lower', type=int, default=0,
                               help="Minimum number of lowercase characters required.")
    random_group.add_argument('--min-upper', type=int, default=0,
                               help="Minimum number of uppercase characters required.")
    random_group.add_argument('--min-digits', type=int, default=0,
                               help="Minimum number of digits required.")
    random_group.add_argument('--min-symbols', type=int, default=0,
                               help="Minimum number of symbols required.")

    # Passphrase generation options
    passphrase_group = parser.add_argument_group(f'{Colors.OKCYAN}Passphrase Options{Colors.ENDC}')
    passphrase_group.add_argument('--passphrase', action='store_true',
                                   help="Generate a Diceware-style passphrase instead of a random password.")
    passphrase_group.add_argument('--delimiter', type=str, default='-',
                                  help="Delimiter for passphrase words (default: '-')")
    passphrase_group.add_argument('--capitalize-words', action='store_true',
                                  help="Capitalize the first letter of each word in the passphrase.")
    passphrase_group.add_argument('--add-number', action='store_true',
                                  help="Add a random digit to the passphrase.")
    passphrase_group.add_argument('--add-symbol', action='store_true',
                                  help="Add a random symbol to the passphrase.")

    # Security checks options
    security_group = parser.add_argument_group(f'{Colors.OKCYAN}Security Checks{Colors.ENDC}')
    security_group.add_argument('--no-pattern-check', action='store_true',
                                 help="Disable checking for common patterns (e.g., 'password', '123456').")
    security_group.add_argument('--no-repetition-check', action='store_true',
                                 help="Disable checking for consecutive character repetitions (e.g., 'aaa', '111').")
    security_group.add_argument('--no-hibp-check', action='store_true',
                                 help="Disable checking generated passwords against the HaveIBeenPwned database (online API).")

    args = parser.parse_args()

    # Check if GUI is requested
    if args.gui:
        launch_gui()
        sys.exit(0) # Exit after GUI is closed

    # Initialize generator (only if not launching GUI)
    pw_gen = PasswordGenerator()

    # Validate length arguments
    if args.length is not None and args.length <= 0:
        print(f"{Colors.FAIL}Error: Password/passphrase length must be a positive integer.{Colors.ENDC}")
        sys.exit(1)

    if args.count <= 0:
        print(f"{Colors.FAIL}Error: Number of passwords to generate must be a positive integer.{Colors.ENDC}")
        sys.exit(1)

    generated_passwords = []

    for i in range(args.count):
        password = None
        if args.passphrase:
            # Passphrase mode
            word_count = args.length if args.length is not None else DICEWARE_DEFAULT_WORD_COUNT
            if not os.path.exists(DICEWARE_WORDLIST_PATH):
                print(f"{Colors.FAIL}Error: Diceware wordlist not found. Cannot generate passphrase.{Colors.ENDC}")
                print(f"Please download it from https://www.eff.org/files/2016/07/18/eff_large_wordlist.txt and place it in the 'wordlists' directory.{Colors.ENDC}")
                sys.exit(1)

            password = pw_gen.generate_passphrase(
                word_count=word_count,
                delimiter=args.delimiter,
                capitalize_words=args.capitalize_words,
                add_number=args.add_number,
                add_symbol=args.add_symbol,
                avoid_patterns_func=None if args.no_pattern_check else check_for_common_patterns,
                avoid_repetitions_func=None if args.no_repetition_check else check_for_consecutive_repetitions
            )
        else:
            # Random password mode
            use_lower = not args.no_lower
            use_upper = not args.no_upper
            use_digits = not args.no_digits
            use_symbols = not args.no_symbols

            if not (use_lower or use_upper or use_digits or use_symbols):
                print(f"{Colors.FAIL}Error: For random password generation, at least one character type (lower, upper, digits, symbols) must be enabled.{Colors.ENDC}")
                sys.exit(1)

            # Determine actual length
            actual_length = args.length
            if actual_length is None:
                # If no specific min/max types requested, default to a random length within range
                if args.min_lower == 0 and args.min_upper == 0 and args.min_digits == 0 and args.min_symbols == 0:
                    actual_length = secrets.randbelow(DEFAULT_MAX_LENGTH - DEFAULT_MIN_LENGTH + 1) + DEFAULT_MIN_LENGTH
                else:
                    # If specific types are requested, use default min length to avoid conflicts
                    actual_length = DEFAULT_MIN_LENGTH
                    # Ensure actual_length is at least the sum of min_required
                    total_min_required = args.min_lower + args.min_upper + args.min_digits + args.min_symbols
                    if total_min_required > actual_length:
                        actual_length = total_min_required + 4 # Add some buffer to ensure length is reasonable

            if actual_length < (args.min_lower + args.min_upper + args.min_digits + args.min_symbols):
                 print(f"{Colors.FAIL}Error: Total minimum required characters ({args.min_lower + args.min_upper + args.min_digits + args.min_symbols}) exceeds the specified or default password length ({actual_length}).{Colors.ENDC}")
                 sys.exit(1)


            password = pw_gen.generate_random_password(
                length=actual_length,
                use_lower=use_lower,
                use_upper=use_upper,
                use_digits=use_digits,
                use_symbols=use_symbols,
                exclude_ambiguous=args.exclude_ambiguous,
                min_lower=args.min_lower,
                min_upper=args.min_upper,
                min_digits=args.min_digits,
                min_symbols=args.min_symbols,
                avoid_patterns_func=None if args.no_pattern_check else check_for_common_patterns,
                avoid_repetitions_func=None if args.no_repetition_check else check_for_consecutive_repetitions
            )

        if password:
            generated_passwords.append(password)
            print(f"\n{Colors.OKBLUE}Generated Password {i+1}:{Colors.ENDC} {Colors.BOLD}{password}{Colors.ENDC}")

            entropy = calculate_entropy(password)
            crack_time = estimate_crack_time(entropy)
            print(f"  {Colors.OKGREEN}Entropy:{Colors.ENDC} {entropy:.2f} bits")
            print(f"  {Colors.OKGREEN}Estimated Crack Time (GPU):{Colors.ENDC} {crack_time}")

            if not args.no_hibp_check:
                print(f"  {Colors.OKBLUE}HIBP Check:{Colors.ENDC} Using online API...")
                if check_pwned_password(password): # Uses the online API check exclusively
                    print(f"  {Colors.FAIL}{Colors.BOLD}WARNING: This password has been found in a data breach (HIBP). Do NOT use!{Colors.ENDC}")
                else:
                    print(f"  {Colors.OKGREEN}HIBP Check:{Colors.ENDC} Not found in public breaches (good!).")
            else:
                print(f"  {Colors.WARNING}HIBP Check: Skipped (--no-hibp-check){Colors.ENDC}")

            if check_for_common_patterns(password) and not args.no_pattern_check:
                print(f"  {Colors.FAIL}WARNING: Password contains common patterns. Consider regenerating.{Colors.ENDC}")
            if check_for_consecutive_repetitions(password) and not args.no_repetition_check:
                print(f"  {Colors.FAIL}WARNING: Password contains consecutive repetitions. Consider regenerating.{Colors.ENDC}")
            if check_for_ambiguous_chars(password) and not args.exclude_ambiguous:
                 print(f"  {Colors.WARNING}Note: Password contains ambiguous characters (e.g., 'l', '1', 'I', 'O', '0').{Colors.ENDC}")
                 print(f"  {Colors.WARNING}Use --exclude-ambiguous to avoid them if typing manually.{Colors.ENDC}")


    if args.copy and generated_passwords:
        copy_to_clipboard(generated_passwords[-1]) # Copies the last generated password
    elif args.copy and not generated_passwords:
        print(f"{Colors.WARNING}No passwords generated to copy to clipboard.{Colors.ENDC}")

if __name__ == "__main__":
    # Create wordlists directory if it doesn't exist
    if not os.path.exists("wordlists"):
        os.makedirs("wordlists")
    main()

