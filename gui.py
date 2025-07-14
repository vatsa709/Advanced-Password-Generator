import tkinter as tk
from tkinter import ttk, messagebox
from tkinter.scrolledtext import ScrolledText
import os
import secrets # For initial random length generation in GUI
import platform # For clipboard error message

# Import modules from your project
from generator import PasswordGenerator
from utils import (
    calculate_entropy, estimate_crack_time, check_for_common_patterns,
    check_for_consecutive_repetitions, check_pwned_password,
    copy_to_clipboard, check_for_ambiguous_chars
)
from config import (
    DEFAULT_MIN_LENGTH, DEFAULT_MAX_LENGTH, DICEWARE_DEFAULT_WORD_COUNT,
    # Colors class is for terminal output, not used directly for Tkinter fg/bg
    DICEWARE_WORDLIST_PATH,
    CHARS_LOWERCASE, CHARS_UPPERCASE, CHARS_DIGITS, CHARS_SYMBOLS, AMBIGUOUS_CHARS
)

class PasswordGeneratorApp:
    def __init__(self, master):
        self.master = master
        master.title("Advanced Password Generator")
        master.geometry("800x780") # Adjusted size for better layout
        master.resizable(False, False) # Prevent resizing for now to maintain layout

        # Configure style for a modern look
        self.style = ttk.Style()
        self.style.theme_use('clam') # 'clam', 'alt', 'default', 'classic'
        self.style.configure('TFrame', background='#f0f0f0')
        self.style.configure('TLabel', background='#f0f0f0', font=('Inter', 10))
        self.style.configure('TCheckbutton', background='#f0f0f0', font=('Inter', 10))
        self.style.configure('TRadiobutton', background='#f0f0f0', font=('Inter', 10))
        self.style.configure('TButton', font=('Inter', 10, 'bold'), padding=8)
        self.style.configure('TEntry', font=('Inter', 10), padding=5)
        self.style.configure('TSpinbox', font=('Inter', 10), padding=5)

        # Define custom styles for status labels (foreground colors)
        self.style.configure('Success.TLabel', foreground='forestgreen') # Darker green for success
        self.style.configure('Warning.TLabel', foreground='darkorange') # Orange for warnings
        self.style.configure('Fail.TLabel', foreground='firebrick')     # Red for failures
        self.style.configure('Info.TLabel', foreground='navy')         # Blue for general info/checking
        self.style.configure('Normal.TLabel', foreground='black')      # Default black

        self.pw_gen = PasswordGenerator()

        # --- Main Frame ---
        self.main_frame = ttk.Frame(master, padding="15 15 15 15")
        self.main_frame.pack(fill=tk.BOTH, expand=True)

        # --- Generation Type Selection ---
        self.type_frame = ttk.LabelFrame(self.main_frame, text="Generation Type", padding="10")
        self.type_frame.grid(row=0, column=0, columnspan=2, pady=10, padx=5, sticky="ew")

        self.generation_type = tk.StringVar(value="random")
        self.random_radio = ttk.Radiobutton(self.type_frame, text="Random Password", variable=self.generation_type, value="random", command=self._toggle_options)
        self.random_radio.grid(row=0, column=0, padx=10, pady=5, sticky="w")
        self.passphrase_radio = ttk.Radiobutton(self.type_frame, text="Passphrase (Diceware)", variable=self.generation_type, value="passphrase", command=self._toggle_options)
        self.passphrase_radio.grid(row=0, column=1, padx=10, pady=5, sticky="w")

        # --- Options Frame (Grid for better alignment) ---
        self.options_container_frame = ttk.Frame(self.main_frame, padding="0")
        self.options_container_frame.grid(row=1, column=0, sticky="nsew", padx=5, pady=5)
        self.main_frame.grid_columnconfigure(0, weight=1) # Make options column expandable

        # --- Random Password Options ---
        self.random_options_frame = ttk.LabelFrame(self.options_container_frame, text="Random Password Options", padding="10")
        self.random_options_frame.grid(row=0, column=0, sticky="ew", pady=5)
        self.options_container_frame.grid_columnconfigure(0, weight=1)

        ttk.Label(self.random_options_frame, text="Password Length:").grid(row=0, column=0, padx=5, pady=5, sticky="w")
        self.length_var = tk.IntVar(value=DEFAULT_MIN_LENGTH)
        self.length_spinbox = ttk.Spinbox(self.random_options_frame, from_=8, to=64, textvariable=self.length_var, width=5, command=self._update_min_length_check)
        self.length_spinbox.grid(row=0, column=1, padx=5, pady=5, sticky="ew")
        self.random_options_frame.grid_columnconfigure(1, weight=1)

        self.use_lower = tk.BooleanVar(value=True)
        self.use_upper = tk.BooleanVar(value=True)
        self.use_digits = tk.BooleanVar(value=True)
        self.use_symbols = tk.BooleanVar(value=True)
        self.exclude_ambiguous = tk.BooleanVar(value=False)

        ttk.Checkbutton(self.random_options_frame, text="Lowercase (a-z)", variable=self.use_lower).grid(row=1, column=0, columnspan=2, padx=5, sticky="w")
        ttk.Checkbutton(self.random_options_frame, text="Uppercase (A-Z)", variable=self.use_upper).grid(row=2, column=0, columnspan=2, padx=5, sticky="w")
        ttk.Checkbutton(self.random_options_frame, text="Digits (0-9)", variable=self.use_digits).grid(row=3, column=0, columnspan=2, padx=5, sticky="w")
        ttk.Checkbutton(self.random_options_frame, text="Symbols (!@#$)", variable=self.use_symbols).grid(row=4, column=0, columnspan=2, padx=5, sticky="w")
        ttk.Checkbutton(self.random_options_frame, text="Exclude Ambiguous (l,I,O,0,1)", variable=self.exclude_ambiguous).grid(row=5, column=0, columnspan=2, padx=5, sticky="w")

        # Minimum character counts
        self.min_chars_frame = ttk.LabelFrame(self.random_options_frame, text="Minimum Character Counts", padding="5")
        self.min_chars_frame.grid(row=6, column=0, columnspan=2, sticky="ew", pady=5)

        self.min_lower_var = tk.IntVar(value=0)
        self.min_upper_var = tk.IntVar(value=0)
        self.min_digits_var = tk.IntVar(value=0)
        self.min_symbols_var = tk.IntVar(value=0)

        ttk.Label(self.min_chars_frame, text="Lowercase:").grid(row=0, column=0, padx=5, pady=2, sticky="w")
        ttk.Spinbox(self.min_chars_frame, from_=0, to=10, textvariable=self.min_lower_var, width=3, command=self._update_min_length_check).grid(row=0, column=1, padx=5, pady=2, sticky="ew")
        ttk.Label(self.min_chars_frame, text="Uppercase:").grid(row=1, column=0, padx=5, pady=2, sticky="w")
        ttk.Spinbox(self.min_chars_frame, from_=0, to=10, textvariable=self.min_upper_var, width=3, command=self._update_min_length_check).grid(row=1, column=1, padx=5, pady=2, sticky="ew")
        ttk.Label(self.min_chars_frame, text="Digits:").grid(row=0, column=2, padx=5, pady=2, sticky="w")
        ttk.Spinbox(self.min_chars_frame, from_=0, to=10, textvariable=self.min_digits_var, width=3, command=self._update_min_length_check).grid(row=0, column=3, padx=5, pady=2, sticky="ew")
        ttk.Label(self.min_chars_frame, text="Symbols:").grid(row=1, column=2, padx=5, pady=2, sticky="w")
        ttk.Spinbox(self.min_chars_frame, from_=0, to=10, textvariable=self.min_symbols_var, width=3, command=self._update_min_length_check).grid(row=1, column=3, padx=5, pady=2, sticky="ew")
        self.min_chars_frame.grid_columnconfigure((1,3), weight=1)


        # --- Passphrase Options ---
        self.passphrase_options_frame = ttk.LabelFrame(self.options_container_frame, text="Passphrase Options", padding="10")
        self.passphrase_options_frame.grid(row=1, column=0, sticky="ew", pady=5)

        ttk.Label(self.passphrase_options_frame, text="Word Count:").grid(row=0, column=0, padx=5, pady=5, sticky="w")
        self.word_count_var = tk.IntVar(value=DICEWARE_DEFAULT_WORD_COUNT)
        self.word_count_spinbox = ttk.Spinbox(self.passphrase_options_frame, from_=3, to=10, textvariable=self.word_count_var, width=5)
        self.word_count_spinbox.grid(row=0, column=1, padx=5, pady=5, sticky="ew")
        self.passphrase_options_frame.grid_columnconfigure(1, weight=1)

        ttk.Label(self.passphrase_options_frame, text="Delimiter:").grid(row=1, column=0, padx=5, pady=5, sticky="w")
        self.delimiter_var = tk.StringVar(value="-")
        self.delimiter_entry = ttk.Entry(self.passphrase_options_frame, textvariable=self.delimiter_var, width=5)
        self.delimiter_entry.grid(row=1, column=1, padx=5, pady=5, sticky="ew")

        self.capitalize_words = tk.BooleanVar(value=False)
        self.add_number = tk.BooleanVar(value=False)
        self.add_symbol = tk.BooleanVar(value=False)

        ttk.Checkbutton(self.passphrase_options_frame, text="Capitalize Words", variable=self.capitalize_words).grid(row=2, column=0, columnspan=2, padx=5, sticky="w")
        ttk.Checkbutton(self.passphrase_options_frame, text="Add Number", variable=self.add_number).grid(row=3, column=0, columnspan=2, padx=5, sticky="w")
        ttk.Checkbutton(self.passphrase_options_frame, text="Add Symbol", variable=self.add_symbol).grid(row=4, column=0, columnspan=2, padx=5, sticky="w")

        # --- Security Checks Options ---
        self.security_frame = ttk.LabelFrame(self.main_frame, text="Security Checks", padding="10")
        self.security_frame.grid(row=1, column=1, sticky="nsew", padx=5, pady=5)
        self.main_frame.grid_columnconfigure(1, weight=1) # Make security column expandable

        self.no_pattern_check = tk.BooleanVar(value=False)
        self.no_repetition_check = tk.BooleanVar(value=False)
        self.no_hibp_check = tk.BooleanVar(value=False)

        ttk.Checkbutton(self.security_frame, text="Disable Common Pattern Check", variable=self.no_pattern_check).grid(row=0, column=0, padx=5, pady=5, sticky="w")
        ttk.Checkbutton(self.security_frame, text="Disable Repetition Check", variable=self.no_repetition_check).grid(row=1, column=0, padx=5, pady=5, sticky="w")
        ttk.Checkbutton(self.security_frame, text="Disable HIBP Breach Check (Online)", variable=self.no_hibp_check).grid(row=2, column=0, padx=5, pady=5, sticky="w")

        # --- Output Frame ---
        self.output_frame = ttk.LabelFrame(self.main_frame, text="Generated Password", padding="10")
        self.output_frame.grid(row=2, column=0, columnspan=2, pady=10, padx=5, sticky="ew")
        self.main_frame.grid_rowconfigure(2, weight=1) # Make output row expandable

        self.password_display = ScrolledText(self.output_frame, height=3, wrap=tk.WORD, font=('Inter', 12, 'bold'), state='disabled', bg='#e0e0e0', fg='navy', relief=tk.FLAT)
        self.password_display.pack(fill=tk.BOTH, expand=True, pady=5)

        self.entropy_label = ttk.Label(self.output_frame, text="Entropy: N/A", font=('Inter', 10, 'bold'), style='Normal.TLabel')
        self.entropy_label.pack(pady=2, anchor="w")
        self.crack_time_label = ttk.Label(self.output_frame, text="Estimated Crack Time: N/A", font=('Inter', 10, 'bold'), style='Normal.TLabel')
        self.crack_time_label.pack(pady=2, anchor="w")
        
        # Feedback messages for security checks - now with dynamic styles
        self.hibp_status_label = ttk.Label(self.output_frame, text="HIBP Status: Not checked", font=('Inter', 10), style='Normal.TLabel')
        self.hibp_status_label.pack(pady=2, anchor="w")
        self.pattern_status_label = ttk.Label(self.output_frame, text="Pattern Check: Not checked", font=('Inter', 10), style='Normal.TLabel')
        self.pattern_status_label.pack(pady=2, anchor="w")
        self.repetition_status_label = ttk.Label(self.output_frame, text="Repetition Check: Not checked", font=('Inter', 10), style='Normal.TLabel')
        self.repetition_status_label.pack(pady=2, anchor="w")
        self.ambiguous_status_label = ttk.Label(self.output_frame, text="Ambiguous Chars: Not checked", font=('Inter', 10), style='Normal.TLabel')
        self.ambiguous_status_label.pack(pady=2, anchor="w")


        # --- Action Buttons ---
        self.button_frame = ttk.Frame(self.main_frame, padding="10")
        self.button_frame.grid(row=3, column=0, columnspan=2, pady=10)

        self.generate_button = ttk.Button(self.button_frame, text="Generate Password", command=self.generate_password)
        self.generate_button.pack(side=tk.LEFT, padx=10)

        self.copy_button = ttk.Button(self.button_frame, text="Copy to Clipboard", command=self.copy_password)
        self.copy_button.pack(side=tk.LEFT, padx=10)

        # Initialize UI state
        self._toggle_options()
        self._update_min_length_check() # Initial check for default values

    def _toggle_options(self):
        """Toggles visibility of random vs. passphrase options based on selection."""
        if self.generation_type.get() == "random":
            self.random_options_frame.grid()
            self.passphrase_options_frame.grid_remove()
            # Set default length for random password
            if self.length_var.get() < DEFAULT_MIN_LENGTH or self.length_var.get() > DEFAULT_MAX_LENGTH:
                self.length_var.set(DEFAULT_MIN_LENGTH)
            self.length_spinbox.config(from_=8, to=64)
            self.length_spinbox.config(textvariable=self.length_var) # Re-bind to ensure it updates
        else:
            self.random_options_frame.grid_remove()
            self.passphrase_options_frame.grid()
            # Set default word count for passphrase
            if self.word_count_var.get() < 3 or self.word_count_var.get() > 10:
                self.word_count_var.set(DICEWARE_DEFAULT_WORD_COUNT)
            self.word_count_spinbox.config(from_=3, to=10)
            self.word_count_spinbox.config(textvariable=self.word_count_var) # Re-bind to ensure it updates

    def _update_min_length_check(self):
        """
        Adjusts password length spinbox 'from_' value based on minimum character requirements.
        This helps prevent generating impossible passwords.
        """
        if self.generation_type.get() == "random":
            min_required = (self.min_lower_var.get() + self.min_upper_var.get() +
                            self.min_digits_var.get() + self.min_symbols_var.get())
            
            # Ensure the spinbox minimum is at least the sum of required characters, plus a buffer
            # or the default min length, whichever is higher.
            new_min_length = max(DEFAULT_MIN_LENGTH, min_required + 4) # Add buffer for flexibility

            current_length = self.length_var.get()
            if current_length < new_min_length:
                self.length_var.set(new_min_length)
            
            self.length_spinbox.config(from_=new_min_length)
            self.length_spinbox.config(to=max(64, new_min_length)) # Ensure 'to' is always greater than 'from'

    def generate_password(self):
        """Generates a password or passphrase based on current UI settings."""
        self._clear_status_labels()
        generated_pw = None

        try:
            if self.generation_type.get() == "random":
                length = self.length_var.get()
                use_lower = self.use_lower.get()
                use_upper = self.use_upper.get()
                use_digits = self.use_digits.get()
                use_symbols = self.use_symbols.get()
                exclude_ambiguous = self.exclude_ambiguous.get()
                min_lower = self.min_lower_var.get()
                min_upper = self.min_upper_var.get()
                min_digits = self.min_digits_var.get()
                min_symbols = self.min_symbols_var.get()

                # Basic validation for random password
                if not (use_lower or use_upper or use_digits or use_symbols):
                    messagebox.showerror("Input Error", "At least one character type (lowercase, uppercase, digits, symbols) must be selected for random password generation.")
                    return
                
                total_min_required = min_lower + min_upper + min_digits + min_symbols
                if total_min_required > length:
                    messagebox.showerror("Input Error", f"Minimum required characters ({total_min_required}) exceed total password length ({length}). Please adjust length or minimum counts.")
                    return

                generated_pw = self.pw_gen.generate_random_password(
                    length=length,
                    use_lower=use_lower,
                    use_upper=use_upper,
                    use_digits=use_digits,
                    use_symbols=use_symbols,
                    exclude_ambiguous=exclude_ambiguous,
                    min_lower=min_lower,
                    min_upper=min_upper,
                    min_digits=min_digits,
                    min_symbols=min_symbols,
                    avoid_patterns_func=None if self.no_pattern_check.get() else check_for_common_patterns,
                    avoid_repetitions_func=None if self.no_repetition_check.get() else check_for_consecutive_repetitions
                )

            elif self.generation_type.get() == "passphrase":
                word_count = self.word_count_var.get()
                delimiter = self.delimiter_var.get()
                capitalize_words = self.capitalize_words.get()
                add_number = self.add_number.get()
                add_symbol = self.add_symbol.get()

                if not self.pw_gen.wordlist:
                    messagebox.showerror("Wordlist Error", f"Diceware wordlist not loaded. Please ensure '{DICEWARE_WORDLIST_PATH}' exists and is accessible.")
                    return
                if word_count <= 0:
                    messagebox.showerror("Input Error", "Word count must be positive for passphrase generation.")
                    return

                generated_pw = self.pw_gen.generate_passphrase(
                    word_count=word_count,
                    delimiter=delimiter,
                    capitalize_words=capitalize_words,
                    add_number=add_number,
                    add_symbol=add_symbol,
                    avoid_patterns_func=None if self.no_pattern_check.get() else check_for_common_patterns,
                    avoid_repetitions_func=None if self.no_repetition_check.get() else check_for_consecutive_repetitions
                )

            if generated_pw:
                self._display_results(generated_pw)
            else:
                self._clear_results()
                messagebox.showerror("Generation Failed", "Could not generate a password/passphrase with the given criteria. Please adjust settings.")

        except Exception as e:
            messagebox.showerror("An Error Occurred", f"An unexpected error occurred during generation: {e}")
            self._clear_results()

    def _display_results(self, password: str):
        """Displays the generated password and its security metrics in the UI."""
        self.password_display.config(state='normal')
        self.password_display.delete(1.0, tk.END)
        self.password_display.insert(tk.END, password)
        self.password_display.config(state='disabled')

        entropy = calculate_entropy(password)
        crack_time = estimate_crack_time(entropy)

        self.entropy_label.config(text=f"Entropy: {entropy:.2f} bits", style='Normal.TLabel') # No fg, use style
        self.crack_time_label.config(text=f"Estimated Crack Time (GPU): {crack_time}", style='Normal.TLabel') # No fg, use style

        # Update security check statuses
        if not self.no_hibp_check.get():
            self.hibp_status_label.config(text="HIBP Status: Checking...", style='Info.TLabel')
            self.master.update_idletasks() # Force update UI to show "Checking..."
            if check_pwned_password(password):
                self.hibp_status_label.config(text="HIBP Status: Found in breach! (DO NOT USE)", style='Fail.TLabel')
            else:
                self.hibp_status_label.config(text="HIBP Status: Not found in public breaches (Good!)", style='Success.TLabel')
        else:
            self.hibp_status_label.config(text="HIBP Status: Skipped", style='Warning.TLabel')

        if not self.no_pattern_check.get():
            if check_for_common_patterns(password):
                self.pattern_status_label.config(text="Pattern Check: Contains common patterns!", style='Fail.TLabel')
            else:
                self.pattern_status_label.config(text="Pattern Check: No common patterns detected.", style='Success.TLabel')
        else:
            self.pattern_status_label.config(text="Pattern Check: Skipped", style='Warning.TLabel')

        if not self.no_repetition_check.get():
            if check_for_consecutive_repetitions(password):
                self.repetition_status_label.config(text="Repetition Check: Contains consecutive repetitions!", style='Fail.TLabel')
            else:
                self.repetition_status_label.config(text="Repetition Check: No consecutive repetitions detected.", style='Success.TLabel')
        else:
            self.repetition_status_label.config(text="Repetition Check: Skipped", style='Warning.TLabel')

        if self.exclude_ambiguous.get():
            self.ambiguous_status_label.config(text="Ambiguous Chars: Excluded", style='Success.TLabel')
        else:
            if check_for_ambiguous_chars(password):
                self.ambiguous_status_label.config(text="Ambiguous Chars: Present (Note: May cause typos)", style='Warning.TLabel')
            else:
                self.ambiguous_status_label.config(text="Ambiguous Chars: None detected", style='Success.TLabel')


    def _clear_results(self):
        """Clears the password display and status labels."""
        self.password_display.config(state='normal')
        self.password_display.delete(1.0, tk.END)
        self.password_display.config(state='disabled')
        self.entropy_label.config(text="Entropy: N/A", style='Normal.TLabel')
        self.crack_time_label.config(text="Estimated Crack Time: N/A", style='Normal.TLabel')
        self._clear_status_labels()

    def _clear_status_labels(self):
        """Resets the status labels to their default 'Not checked' state."""
        self.hibp_status_label.config(text="HIBP Status: Not checked", style='Normal.TLabel')
        self.pattern_status_label.config(text="Pattern Check: Not checked", style='Normal.TLabel')
        self.repetition_status_label.config(text="Repetition Check: Not checked", style='Normal.TLabel')
        self.ambiguous_status_label.config(text="Ambiguous Chars: Not checked", style='Normal.TLabel')


    def copy_password(self):
        """Copies the currently displayed password to the clipboard."""
        password_to_copy = self.password_display.get(1.0, tk.END).strip()
        if password_to_copy:
            copy_to_clipboard(password_to_copy)
        else:
            messagebox.showinfo("Copy Error", "No password generated to copy.")

def launch_gui():
    root = tk.Tk()
    app = PasswordGeneratorApp(root)
    root.mainloop()

if __name__ == "__main__":
    # Ensure wordlists directory exists when running gui.py directly for testing
    if not os.path.exists("wordlists"):
        os.makedirs("wordlists")
    launch_gui()