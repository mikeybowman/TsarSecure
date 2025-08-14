# TsarSecure
TsarSecure is a powerful, user-friendly desktop application for Windows, crafted to help you generate and analyze truly secure passwords and passphrases. With its intuitive, minimalist interface and a focus on cryptographic integrity, TsarSecure empowers you to strengthen your online security with confidence.

##Features:
```
∙ Entropy-Based Strength Analysis: Beyond simple rules, TsarSecure calculates the cryptographic entropy (in bits) of generated and input passwords, providing a mathematically accurate measure of their unpredictability and brute-force resistance.

∙ Time-to-Crack Estimation: Get a clear, human-readable estimate of how long it would take a malicious party to brute-force your password, ranging from "Instantly" to "Billions of Years."

∙ Versatile Generation Modes:

∙ Character-Based Passwords: Generate strong, random passwords using customizable combinations of lowercase, uppercase, digits, and special characters.

∙ Passphrase Mode: Create memorable, high-entropy passphrases by selecting multiple random words from a secure wordlist.

∙ "Check My Password" Functionality: Input any existing password to instantly analyze its strength, entropy, and estimated time-to-crack.

∙ Enhanced Security Measures:

∙ Utilizes Python's secrets module for cryptographically secure randomness.

∙ Attempts to overwrite password data in memory after use for enhanced privacy.

∙ Password display automatically clears after 30 seconds for added security.

∙ "Password Copied!" confirmation appears directly in the password field and fades away.

∙ "Lock Computer" Button: Quickly secure your workstation directly from the application with a single click (Windows only).

∙ Sleek & Responsive Design: Enjoy a modern, dark-themed interface with Consolas font and neon accents that automatically adapts to your window size and keeps elements centered.

∙ Translucent Window: Provides a subtle, see-through effect for a modern desktop integration.
```

## How to Use
# Get Started:
```
Download the latest TsarSecure.exe from the Releases page.

Run the executable. No installation or Python required!
```
# Generating Passwords:
```
Adjust Length/Words: Use the slider to choose your desired password length (for character-based passwords) or word count (for passphrases).

Select Character Types: Check or uncheck the boxes for lowercase, uppercase, numbers, and special characters. These options will be automatically disabled when "Passphrase Mode" is active.

"Passphrase Mode": Toggle this checkbox to switch between generating random character strings and multi-word passphrases.

"Generate Password": Click this button to create your new secure password or passphrase.
```
# Checking Passwords:
```
Type or paste any password into the "Check Your Own Password" input field.

Click "Check Strength" to instantly see its calculated entropy, strength rating, and estimated crack time.
```
Security Actions:
```
"Copy Password": Copies the generated password to your system clipboard. A "Password Copied!" message will briefly appear in the password display box.

"Lock Computer": Immediately locks your Windows session, requiring your PIN or password to unlock.
```
# Building from Source (for Developers)
If you want to build the .exe yourself, contribute to the project, or inspect the code:

# Clone the repository:

git clone https://github.com/mikeybowman/TsarSecure.git
cd TsarSecure

Install Python: Ensure you have Python 3.7+ installed.

Install dependencies:

pip install pyinstaller

Place ts.ico: Make sure your ts.ico icon file is in the TsarSecure project directory (same level as TsarSecure.py).

Build the executable:

pyinstaller --onefile --windowed --icon=ts.ico TsarSecure.py

The TsarSecure.exe file will be created in the dist/ subdirectory.

License
This project is open-source under the MIT License. See the LICENSE file for more details.

Contributing
Contributions are welcome! If you find bugs, have feature suggestions, or want to contribute code:

Fork the repository.

Create a new branch (git checkout -b feature/YourFeature).

Make your changes.

Commit your changes (git commit -m 'Add new feature').

Push to the branch (git push origin feature/YourFeature).

Open a Pull Request.

Author: Tsardev
