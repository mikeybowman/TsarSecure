# TsarSecure Requirements Specification (v2.5.0)

## 1. Introduction
TsarSecure is a password and passphrase generation and analysis tool designed to provide users with mathematically sound strength evaluations and real-world breach detection data.  
Version 2.5.0 significantly expands functionality with breach detection, full Diceware support, improved clipboard security, and refined UI/UX.

---

## 2. Functional Requirements

### FR1: Password Generation
- **FR1.1**: Support random password generation with configurable length and character sets (lowercase, uppercase, digits, symbols).
- **FR1.2**: Provide entropy calculation in bits for each generated password.
- **FR1.3**: Display estimated crack times based on entropy.

### FR2: Passphrase Generation
- **FR2.1**: Support generation of multi-word passphrases using the full EFF Diceware list (7,776 words).
- **FR2.2**: Allow users to select the number of words.
- **FR2.3**: Display entropy and crack times for passphrases.

### FR3: Breach Detection
- **FR3.1**: Check generated or user-entered passwords against the HaveIBeenPwned database using the k-anonymity API.
- **FR3.2**: Classify breach risk as SAFE, LOW, MEDIUM, HIGH, CRITICAL.
- **FR3.3**: Display breach count if applicable.
- **FR3.4**: Operate with privacy preservation (only send first 5 chars of SHA-1 hash).

### FR4: Clipboard Management
- **FR4.1**: Allow copying passwords/passphrases to the clipboard.
- **FR4.2**: Display a live 30-second countdown until clipboard auto-clear.
- **FR4.3**: Overwrite clipboard contents before clearing.
- **FR4.4**: Disable the copy button until clipboard is cleared or a new password is generated.

### FR5: UI Features
- **FR5.1**: Provide separate tabs for password and passphrase generation.
- **FR5.2**: Display both entropy and breach check results in real-time.
- **FR5.3**: Offer a responsive and accessible interface.

### FR6: Security Actions
- **FR6.1**: Include an option to lock the user’s computer immediately via system call.

---

## 3. Non-Functional Requirements

### NFR1: Security
- **NFR1.1**: All sensitive data cleared from memory after use.
- **NFR1.2**: Clipboard cleared automatically after timeout.
- **NFR1.3**: No full password ever sent over the network.
- **NFR1.4**: Resistant to timing attacks in entropy/breach calculations.

### NFR2: Performance
- **NFR2.1**: UI must remain responsive during all operations (threaded tasks).
- **NFR2.2**: Breach checks complete within 3 seconds on a standard broadband connection.

### NFR3: Compatibility
- **NFR3.1**: Windows 10+ support.
- **NFR3.2**: Python 3.11+ build environment.

---

## 4. Constraints
- **C4.1**: Application must operate fully offline for password generation and entropy analysis.
- **C4.2**: Breach detection requires internet access.
- **C4.3**: Full EFF Diceware list required for passphrase mode.
- **C4.4**: Must run as a standalone executable (via PyInstaller) for end users.

---

## 5. Future Enhancements
- Multi-language wordlist support.
- Configurable breach API endpoint.

---
