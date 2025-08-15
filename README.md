# TsarSecure v2.5.0

TsarSecure is a powerful, privacy-focused desktop application for Windows, built to help you generate and assess truly secure passwords and passphrases.  
With a modern, dark UI and a focus on **real-world security**, TsarSecure 2.5.0 combines **mathematical strength analysis** with **breach detection** to give you the most complete password risk assessment possible.

---

## 🆕 What’s New in 2.5.0

### New Features
- **Breach Detection** – Checks passwords against the HaveIBeenPwned database (800M+ compromised passwords) using a privacy-preserving k-anonymity API.
- **Full Diceware Support** – References all 7,776 words for stronger, more varied passphrase generation.
- **Passphrase Generation Tab** – Dedicated UI for multi-word passphrases.
- **Clipboard Countdown** – Live countdown from 30 seconds before clipboard auto-clear.
- **Copy Button Lockout** – Copy button is disabled until clipboard is cleared or a new password is generated.

### Logic & Security Improvements
- Stronger subprocess handling for locking the computer.
- Safer clipboard operations with verification.
- Better exception handling and thread safety.
- Improved secure memory clearing to minimize sensitive data exposure.
- Granular strength ratings (Very Weak → Excellent).
- More accurate entropy calculation and crack time estimates.

### UI Refinements
- Larger main window to fit new features.
- Clearer button labels and tooltips.
- Dual display for entropy and breach results.
- Modernized layout for faster navigation.

---

## 🔐 Core Features
- **Entropy-Based Strength Analysis** – Calculates true cryptographic entropy in bits.
- **Time-to-Crack Estimates** – From “Instantly” to “Billions of Years.”
- **Character-Based Passwords** – Customizable lowercase, uppercase, digits, and symbols.
- **Passphrase Mode** – Random multi-word passphrases from a secure Diceware list.
- **Breach Risk Classification** – SAFE → LOW → MEDIUM → HIGH → CRITICAL.
- **Privacy Protection** – Never sends full passwords to external services.
- **Clipboard Auto-Clear** – Wipes copied passwords after 30 seconds.
- **Lock Computer** – Secure your session instantly from the app.

---

## 📥 How to Use
1. **Download** the latest TsarSecure.exe from the [Releases](../../releases) page.
2. Run the executable — no install or Python needed.

---

## ⚙️ Developer & Build Instructions
```bash
# Clone repo
git clone https://github.com/mikeybowman/TsarSecure.git
cd TsarSecure

# Install dependencies
pip install -r requirements.txt

# Build Consumer Edition
pyinstaller TsarSecure.spec --clean

# Build Developer Edition (console on)
pyinstaller TsarSecure_Dev.spec --clean
```
Binaries will be in the `dist/` folder.

---

## 📜 License
Open-source under the MIT License. See the LICENSE file for details.

---

## 🤝 Contributing
1. Fork the repository.
2. Create a feature branch:  
   ```bash
   git checkout -b feature/MyFeature
   ```
3. Commit changes and push:  
   ```bash
   git commit -m "feat: Add my new feature"
   git push origin feature/MyFeature
   ```
4. Open a Pull Request into `dev`.
