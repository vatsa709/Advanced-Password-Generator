# 🔐 KeyWise - Advanced Password Generator

A robust, secure, and user-friendly password and passphrase generator designed to address common vulnerabilities and usability issues found in typical password tools. Generate strong, unique, and memorable credentials with confidence.

## 📋 Table of Contents
- [✨ Features](#-features)  
- [🚀 Why This Generator Stands Out](#-why-this-generator-stands-out)  
- [⚙️ Installation](#️-installation)  
- [🚀 Usage](#-usage)  
  - [Command-Line Interface (CLI)](#command-line-interface-cli)  
  - [Graphical User Interface (GUI)](#graphical-user-interface-gui)  
- [📂 Project Structure](#-project-structure)  
- [🔒 Security & Privacy](#-security--privacy)  
- [🤝 Contributing](#-contributing)  
- [📄 License](#-license)  
- [🙏 Acknowledgements](#-acknowledgements)

---

## ✨ Features

This project incorporates advanced features to ensure high security and excellent user experience:

- **Cryptographically Secure Randomness**: Utilizes Python's `secrets` module for generating unpredictable passwords.

- **Comprehensive Character Options**: Full control over inclusion/exclusion of lowercase, uppercase, digits, and symbols.

- **Minimum Character Type Guarantees**: Ensures generated passwords meet specific complexity requirements (e.g., at least 1 uppercase, 1 digit).

- **Passphrase Generation (Diceware)**: Create memorable yet strong passphrases using the EFF Diceware wordlist.

- **Ambiguous Character Exclusion**: Option to remove characters like `l`, `I`, `O`, `0`, `1` to prevent typing errors.

- **Pattern & Repetition Avoidance**: Built-in checks to prevent common, easily guessable patterns (e.g., "password", "123") and consecutive character repetitions (e.g., "aaa").

- **Real-time Strength & Crack Time Estimation**: Provides immediate feedback on password entropy and estimated crack time by a powerful attacker.

- **HaveIBeenPwned (HIBP) Integration**: Checks generated passwords against the HIBP database via its secure online API to ensure they haven't been compromised in public data breaches.

- **Copy to Clipboard**: Convenient one-click (or command) functionality to copy the generated password.

- **Interactive GUI**: A clean and intuitive graphical interface built with Tkinter for an enhanced user experience.

- **Flexible CLI**: Robust command-line interface for scripting and advanced users.

---

## 🚀 Why This Generator Stands Out

Traditional password generators often fall short in critical areas. This project directly addresses common problems identified through extensive research:

- **Problem: Predictable Patterns & Weak Entropy**  
  Many generators use insecure random number generators or produce easily guessable patterns.  
  **Solution**: We use `secrets` for true randomness and implement post-generation checks for common patterns and repetitions, regenerating if necessary. Entropy calculation provides transparent strength feedback.

- **Problem: Lack of Customization & Inflexibility**  
  Users often can't tailor passwords to specific website requirements (e.g., "must contain a symbol, no @").  
  **Solution**: Granular control over character sets, minimum type counts, and ambiguous character exclusion.

- **Problem: Poor Usability & Memorability**  
  Random strings are hard to remember, and CLI-only tools can be daunting.  
  **Solution**: Offers Diceware-style passphrases for memorability and provides a user-friendly GUI, alongside CLI options. Copy-to-clipboard enhances convenience.

- **Problem: No Breach Checking**  
  A strong-looking password might already be compromised in a data breach.  
  **Solution**: Seamless integration with the HaveIBeenPwned API ensures generated passwords are not publicly known.

---

## ⚙️ Installation

Follow these steps to get the Advanced Password Generator running on your system.

### Clone the Repository:

First, clone this GitHub repository to your local machine:

```bash
git clone https://github.com/vatsa709/Advanced-Password-Generator.git
cd Advanced-Password-Generator
````


### Install Dependencies:

Install the required Python libraries:

```bash
pip install requests pyperclip
```

### Download Diceware Wordlist:

The passphrase generator uses the EFF Diceware wordlist.

Create a wordlists directory if it doesn't exist:

```bash
mkdir -p wordlists
```

Download the `eff_large_wordlist.txt` file from [EFF Diceware Wordlist](https://www.eff.org/files/2016/07/18/eff_large_wordlist.txt) and place it inside the `wordlists/` directory.

---

## 🚀 Usage

You can use the password generator via its **Command-Line Interface (CLI)** or its **Graphical User Interface (GUI)**.

### Command-Line Interface (CLI)

Navigate to the project's root directory in your terminal (where `main.py` is located) and run `python main.py` followed by desired arguments.

#### Basic Usage:

```bash
python main.py
# Generates a default random password (12-24 chars, mixed types)
```

#### Common Examples:

* Generate a random password 16 characters long, excluding symbols:

  ```bash
  python main.py --length 16 --no-symbols
  ```

* Generate a random password with at least 2 uppercase and 2 digits, no ambiguous characters:

  ```bash
  python main.py --length 20 --min-upper 2 --min-digits 2 --exclude-ambiguous
  ```

* Generate a 7-word passphrase with spaces and capitalized words:

  ```bash
  python main.py --passphrase --length 7 --delimiter " " --capitalize-words
  ```

* Generate 3 random passwords and copy the last one to clipboard:

  ```bash
  python main.py --count 3 --copy
  ```

* Generate a password without pattern or repetition checks (less secure, not recommended):

  ```bash
  python main.py --no-pattern-check --no-repetition-check
  ```

* View all CLI options:

  ```bash
  python main.py --help
  ```

---

### Graphical User Interface (GUI)

To launch the interactive GUI, run the following command from the project's root directory:

```bash
python main.py --gui
```

The GUI provides an intuitive interface with checkboxes, spinboxes, and radio buttons to configure your password generation options, along with real-time feedback on strength and security checks.

---

## 📂 Project Structure

The project is organized into modular files for clarity and maintainability:

```
Advanced-Password-Generator/
├── __init__.py         # Marks the directory as a Python package (empty)
├── main.py             # Main entry point for CLI and GUI launch
├── generator.py        # Core logic for generating random passwords and passphrases
├── utils.py            # Utility functions (entropy calculation, security checks, clipboard)
├── config.py           # Configuration constants (character sets, lengths, API URLs)
├── gui.py              # Graphical User Interface (Tkinter) implementation
└── wordlists/          # Directory for external wordlists (e.g., Diceware)
    └── eff_large_wordlist.txt # Diceware wordlist file
```

---

## 🔒 Security & Privacy

* **No Storage**: This password generator does not store any generated passwords or user input. All generation and checks happen in memory during runtime.

* **Cryptographically Secure**: Utilizes Python's `secrets` module, which is designed for generating cryptographic-strength random numbers suitable for passwords.

* **HIBP API**: The HaveIBeenPwned (HIBP) check uses a k-anonymity model. This means only the first 5 characters of your password's SHA-1 hash are sent to the HIBP API. Your full password or its complete hash is never transmitted, ensuring your privacy while checking against known breaches.

---

## 🤝 Contributing

Contributions are welcome! If you have suggestions for improvements, new features, or bug fixes, please feel free to:

1. Fork the repository.
2. Create a new branch (`git checkout -b feature/YourFeatureName`).
3. Make your changes and commit them (`git commit -m 'Add new feature'`).
4. Push to the branch (`git push origin feature/YourFeatureName`).
5. Open a Pull Request.

---

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

## 🙏 Acknowledgements

* **Have I Been Pwned (HIBP)**: For providing the invaluable service and API for checking compromised passwords.
* **Electronic Frontier Foundation (EFF)**: For their work on the Diceware wordlists, promoting strong and memorable passphrases.

