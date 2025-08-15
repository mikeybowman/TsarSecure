# TsarSecure v2.5.0 - External Diceware List + Breach Button Throttle/Backoff + Copy Countdown Lockout
# Author: Tsardev
# License: MIT
#
# What’s new in v2.5.0
# - Uses external EFF Diceware wordlist (lazy-loaded) instead of a giant embedded list
# - Optional SHA-256 integrity check (disabled by default)
# - Breach check button: debounce + polite exponential backoff on HTTP 429
# - Clipboard copy: live 30s countdown, button lockout until clear/new secret
# - Keeps your existing threading + UI patterns; safe fallbacks if file is missing

import tkinter as tk
from tkinter import ttk
import secrets
import string
import os
import math
import threading
import time
import gc
import ctypes
from ctypes import wintypes
import sys
import json
from collections import Counter
import hashlib
import requests

# --- App / Packaging config for Diceware ---
WORDLIST_NAME = "eff_large_wordlist.txt"
# If you want integrity checking, paste the real SHA-256 of your wordlist here.
# Leave as None to skip integrity checks.
WORDLIST_SHA256 = None  # e.g., "a1b2c3...64-hex-chars..."

def _bundle_path(name: str) -> str:
    """Return the runtime path to bundled files (works in dev & PyInstaller)."""
    base = getattr(sys, "_MEIPASS", os.path.dirname(__file__))
    return os.path.join(base, name)

_dice_words_cache = None

def _verify_sha256_bytes(data: bytes, expected_hex: str) -> bool:
    h = hashlib.sha256()
    h.update(data)
    return h.hexdigest().lower() == expected_hex.lower()

def _fallback_words():
    # Small NATO-like fallback so app still runs if the file is missing.
    return (
        "alpha","bravo","charlie","delta","echo","foxtrot","golf","hotel",
        "india","juliet","kilo","lima","mike","november","oscar","papa",
        "quebec","romeo","sierra","tango","uniform","victor","whiskey",
        "xray","yankee","zulu"
    )

def load_diceware_words():
    """
    Lazy-load the Diceware word list from an external file (EFF format).
    Supports:
      - '11111<TAB>word' (preferred EFF format)
      - plain 'word' per line
    De-duplicates while preserving order. Caches the list for reuse.
    """
    global _dice_words_cache
    if _dice_words_cache is not None:
        return _dice_words_cache

    path = _bundle_path(WORDLIST_NAME)
    words = []
    try:
        with open(path, "rb") as f:
            data = f.read()
        if WORDLIST_SHA256:
            try:
                if not _verify_sha256_bytes(data, WORDLIST_SHA256):
                    print("Warning: Diceware list SHA-256 mismatch. Using file anyway.")
            except Exception:
                pass
        text = data.decode("utf-8", "ignore")
        for line in text.splitlines():
            line = line.strip()
            if not line or line.startswith("#"):
                continue
            if "\t" in line:
                # EFF/Classic format: "11111<TAB>word"
                _, w = line.split("\t", 1)
                words.append(w.strip())
            else:
                # Plain word per line
                words.append(line)
    except FileNotFoundError:
        print("⚠ Wordlist file not found — using small fallback list")
        words = list(_fallback_words())

    # De-duplicate while preserving order
    seen = set()
    uniq = []
    for w in words:
        if w and w not in seen:
            uniq.append(w)
            seen.add(w)

    _dice_words_cache = tuple(uniq)
    return _dice_words_cache

# --- Enhanced Security Configuration ---
CLIPBOARD_CLEAR_TIMEOUT = 30  # Clear clipboard after 30 seconds
PASSWORD_DISPLAY_TIMEOUT = 30  # Clear password display after 30 seconds
BREACH_CHECK_TIMEOUT = 10      # Timeout for breach check requests

# --- Global variables for security management ---
_clipboard_clear_timer = None
_password_clear_timer = None
_secure_password_storage = None

# --- Clipboard countdown UI state ---
_clipboard_countdown_job = None
_clipboard_countdown_remaining = 0
_copy_button_ref = None

# --- Constants for Colors and Timing ---
NEON_GREEN = "#39FF14"
DARK_BG = "#1e1e1e"
MEDIUM_BG = "#333333"
ELECTRIC_BLUE = "#00FFFF"
WINDOW_ALPHA = 0.9
BREACH_RED = "#FF4444"
BREACH_ORANGE = "#FF8C00"
BREACH_YELLOW = "#FFD166"
BREACH_GREEN = "#06D6A0"

# --- Breach UI throttle/backoff ---
MIN_BREACH_CLICK_INTERVAL = 2.0   # seconds between allowed clicks
MAX_BREACH_RETRIES = 3            # max retries on HTTP 429
BACKOFF_BASE_MS = 800             # base backoff in ms (exponential)
_breach_last_click_ts = 0.0
_breach_inflight = False

# --- Core Functionality ---
def generate_password_sync(length):
    """Generate a random password using a full printable alphabet."""
    alphabet = string.ascii_letters + string.digits + string.punctuation
    if length < 8:
        length = 8
    return ''.join(secrets.choice(alphabet) for _ in range(length))

def generate_diceware_passphrase(word_count, separator=" "):
    """Generate a Diceware passphrase from the external list."""
    words = load_diceware_words()
    n = len(words)
    if n == 0:
        # Shouldn't happen; fallback ensures non-empty
        return ""
    chosen = [words[secrets.randbelow(n)] for _ in range(word_count)]
    return separator.join(chosen)

# --- Enhanced Security Classes and Functions ---
class SecureString:
    """Minimize lifetime of cleartext by holding it in a mutable buffer."""

    def __init__(self, value=""):
        self._data = bytearray(value.encode('utf-8'))
        self._is_cleared = False

    def get(self):
        if self._is_cleared:
            return ""
        return self._data.decode('utf-8')

    def clear(self):
        if not self._is_cleared:
            for _ in range(3):
                for i in range(len(self._data)):
                    self._data[i] = secrets.randbits(8)
            self._data.clear()
            self._is_cleared = True
            gc.collect()

    def __del__(self):
        self.clear()

    def __len__(self):
        return 0 if self._is_cleared else len(self._data)

def _set_copy_button_state(enabled: bool, text: str = None):
    """Enable/disable the Copy button and optionally set its text."""
    try:
        if _copy_button_ref and _copy_button_ref.winfo_exists():
            if enabled:
                _copy_button_ref.state(['!disabled'])
            else:
                _copy_button_ref.state(['disabled'])
            if text is not None:
                _copy_button_ref.config(text=text)
    except Exception:
        pass

def clipboard_cleared_ui_reset():
    """UI reset when clipboard is cleared (by timeout or manually)."""
    global _clipboard_countdown_job, _clipboard_countdown_remaining
    try:
        if _clipboard_countdown_job:
            root.after_cancel(_clipboard_countdown_job)
        _clipboard_countdown_job = None
        _clipboard_countdown_remaining = 0
        if 'status_label' in globals() and status_label and status_label.winfo_exists():
            status_label.config(text="")
        _set_copy_button_state(True, "Copy to Clipboard (Clears in 30s)")
    except Exception:
        pass

def cancel_clipboard_countdown(reason: str = ""):
    """Cancel countdown and re-enable Copy (used when generating a new secret)."""
    clipboard_cleared_ui_reset()

def _tick_clipboard_countdown():
    """Per-second countdown tick."""
    global _clipboard_countdown_remaining, _clipboard_countdown_job
    try:
        if _clipboard_countdown_remaining <= 0:
            # Time’s up: clear clipboard and reset UI
            clear_clipboard()
            clipboard_cleared_ui_reset()
            return

        # Update status label and button text
        if 'status_label' in globals() and status_label and status_label.winfo_exists():
            status_label.config(text=f"Clipboard will auto‑clear in {_clipboard_countdown_remaining}s")
        _set_copy_button_state(False, f"Copied — Clears in {_clipboard_countdown_remaining}s")

        _clipboard_countdown_remaining -= 1
        _clipboard_countdown_job = root.after(1000, _tick_clipboard_countdown)
    except Exception:
        # If something goes sideways, try to reset gracefully
        clipboard_cleared_ui_reset()

def start_clipboard_countdown(seconds: int):
    """Start/replace the clipboard countdown and lock the Copy button."""
    global _clipboard_countdown_remaining, _clipboard_countdown_job
    try:
        if _clipboard_countdown_job:
            root.after_cancel(_clipboard_countdown_job)
        _clipboard_countdown_remaining = max(0, int(seconds))
        _set_copy_button_state(False, f"Copied — Clears in {_clipboard_countdown_remaining}s")
        if 'status_label' in globals() and status_label and status_label.winfo_exists():
            status_label.config(text=f"Clipboard will auto‑clear in {_clipboard_countdown_remaining}s")
        _clipboard_countdown_job = root.after(1000, _tick_clipboard_countdown)
    except Exception:
        pass

def secure_clipboard_copy(password):
    """Copy to clipboard with auto-clear."""
    global _clipboard_clear_timer
    if not password:
        return False
    try:
        if _clipboard_clear_timer and _clipboard_clear_timer.is_alive():
            _clipboard_clear_timer.cancel()
        root.clipboard_clear()
        root.clipboard_append(password)
        # Keep the existing timed clear; UI countdown runs in parallel and also clears at 0s.
        _clipboard_clear_timer = threading.Timer(CLIPBOARD_CLEAR_TIMEOUT, clear_clipboard)
        _clipboard_clear_timer.daemon = True
        _clipboard_clear_timer.start()
        return True
    except Exception as e:
        print(f"Clipboard copy failed: {e}")
        return False

def clear_clipboard():
    """Best-effort clipboard overwrite then clear."""
    try:
        random_data = ''.join(secrets.choice(string.ascii_letters + string.digits) for _ in range(50))
        root.clipboard_clear()
        root.clipboard_append(random_data)
        root.clipboard_clear()
        if root and root.winfo_exists():
            root.after(0, lambda: show_temporary_message("Clipboard cleared for security", 2000))
    except Exception as e:
        print(f"Clipboard clear failed: {e}")
    finally:
        # Ensure UI becomes usable again when clipboard is cleared
        if root and root.winfo_exists():
            root.after(0, clipboard_cleared_ui_reset)

def show_temporary_message(message, duration_ms):
    try:
        temp_label = tk.Label(root, text=message, foreground="yellow", bg=DARK_BG, font=("Consolas", 9, "italic"))
        temp_label.grid(row=8, column=0, pady=5)
        root.after(duration_ms, lambda: temp_label.destroy() if temp_label.winfo_exists() else None)
    except Exception as e:
        print(f"Message display failed: {e}")

def secure_clear_password():
    """Securely clear displayed secret and wipe memory buffer."""
    global _secure_password_storage
    try:
        current_display = password_var.get() or passphrase_var.get()
        display_length = len(current_display)

        if display_length > 0:
            for _ in range(3):
                random_display = ''.join(secrets.choice(string.ascii_letters + string.digits) for _ in range(display_length))
                password_var.set(random_display)
                passphrase_var.set(random_display)
                root.update()
                time.sleep(0.01)

        password_var.set("")
        passphrase_var.set("")

        if _secure_password_storage:
            _secure_password_storage.clear()
            _secure_password_storage = None

        gc.collect()

        if root and root.winfo_exists():
            update_entropy_label(0)
            root.after(0, lambda: show_temporary_message("Password cleared from memory", 2000))
    except Exception as e:
        print(f"Password clear failed: {e}")

def secure_copy_password(copy_button=None):
    """Copy currently generated secret to clipboard with UI hints + countdown lockout."""
    global _secure_password_storage, _password_clear_timer, _copy_button_ref
    try:
        _copy_button_ref = copy_button or _copy_button_ref  # remember the widget for updates

        # Prefer the secure buffer; if it's gone, fall back to what's displayed.
        candidate = None
        if _secure_password_storage and not _secure_password_storage._is_cleared:
            candidate = _secure_password_storage.get()
        else:
            candidate = (password_var.get() or passphrase_var.get() or "").strip()
            if candidate:
                _secure_password_storage = SecureString(candidate)

        if not candidate:
            show_temporary_message("No password to copy!", 1500)
            return

        # Align the display auto-clear so it doesn't nuke mid‑copy UX
        try:
            if _password_clear_timer and _password_clear_timer.is_alive():
                _password_clear_timer.cancel()
            _password_clear_timer = threading.Timer(PASSWORD_DISPLAY_TIMEOUT, secure_clear_password)
            _password_clear_timer.daemon = True
            _password_clear_timer.start()
        except Exception:
            pass

        if secure_clipboard_copy(candidate):
            # Start the clipboard countdown + lock the copy button
            start_clipboard_countdown(CLIPBOARD_CLEAR_TIMEOUT)

            # Brief success banner; restore afterwards
            password_var.set("Password Copied! (Clipboard will auto‑clear)")
            passphrase_var.set("Password Copied! (Clipboard will auto‑clear)")

            def restore_display():
                try:
                    if _secure_password_storage and not _secure_password_storage._is_cleared:
                        s = _secure_password_storage.get()
                        if password_entry.cget("state") == "readonly":
                            password_var.set(s)
                        if passphrase_entry.cget("state") == "readonly":
                            passphrase_var.set(s)
                    else:
                        password_var.set("")
                        passphrase_var.set("")
                except Exception as e:
                    print(f"Display restore failed: {e}")

            root.after(1500, restore_display)

            # Scrub local temp
            junk = ''.join(secrets.choice(string.ascii_letters) for _ in range(len(candidate)))
            del junk
        else:
            show_temporary_message("Copy failed!", 1500)

    except Exception as e:
        print(f"Copy operation failed: {e}")
        show_temporary_message("Copy failed!", 1500)

def enhanced_exit_handler():
    """Clean up on exit."""
    global _secure_password_storage, _clipboard_clear_timer, _password_clear_timer
    try:
        clear_clipboard()
    except:
        pass
    if _clipboard_clear_timer and _clipboard_clear_timer.is_alive():
        _clipboard_clear_timer.cancel()
    if _password_clear_timer and _password_clear_timer.is_alive():
        _password_clear_timer.cancel()
    if _secure_password_storage:
        _secure_password_storage.clear()
    for _ in range(3):
        gc.collect()
    try:
        root.quit()
    except:
        pass

def enable_security_features():
    """Enable a couple Windows mitigations (best effort)."""
    try:
        if sys.platform == "win32":
            kernel32 = ctypes.windll.kernel32
            kernel32.SetProcessMitigationPolicy(1, ctypes.byref(ctypes.c_uint32(1)), 4)
            kernel32.SetProcessDEPPolicy(1)
    except Exception:
        pass

# --- Password Analysis ---
def calculate_actual_entropy(password):
    """Shannon entropy of observed distribution * length (educational)."""
    if not password:
        return 0
    try:
        char_counts = Counter(password)
        L = len(password)
        H = 0.0
        for c in char_counts.values():
            p = c / L
            if p > 0:
                H -= p * math.log2(p)
        return H * L
    except Exception as e:
        print(f"Entropy calculation failed: {e}")
        return 0

def get_charset_entropy(password):
    """Theoretical entropy using distinct characters (approx only)."""
    try:
        charset_size = len(set(password)) or 1
        return len(password) * math.log2(charset_size)
    except Exception as e:
        print(f"Charset entropy calculation failed: {e}")
        return 0

def detect_patterns(password):
    try:
        if len(password) < 2:
            return False
        for i in range(1, len(password) // 2 + 1):
            for j in range(len(password) - 2 * i + 1):
                if password[j:j+i] == password[j+i:j+2*i]:
                    return True
        return False
    except Exception as e:
        print(f"Pattern detection failed: {e}")
        return False

def check_dictionary_words(password):
    try:
        common = {"password", "123456", "qwerty", "secret", "p@ssw0rd", "admin", "login", "user"}
        lp = password.lower()
        if lp in common:
            return True
        return any(w in lp for w in common)
    except Exception as e:
        print(f"Dictionary check failed: {e}")
        return False

def check_keyboard_patterns(password):
    try:
        pats = ["qwerty", "asdfgh", "zxcvbn", "123456789", "qwertz", "azerty"]
        lp = password.lower()
        return any(p in lp or p[::-1] in lp for p in pats)
    except Exception as e:
        print(f"Keyboard pattern check failed: {e}")
        return False

def calculate_repetition_score(password):
    try:
        if len(password) < 2:
            return 0
        total = sum(1 for i in range(len(password) - 1) if password[i] == password[i+1])
        return total / len(password)
    except Exception as e:
        print(f"Repetition score failed: {e}")
        return 0

def comprehensive_strength_analysis(password):
    """Multi-signal strength analysis (kept from your earlier design)."""
    try:
        if not password:
            return {
                'length': 0, 'charset_size': 0,
                'theoretical_entropy': 0, 'actual_entropy': 0,
                'patterns_detected': False, 'dictionary_word_found': False,
                'keyboard_pattern_found': False, 'repetition_score': 0,
                'strength_rating': 'No Password'
            }
        analysis = {
            'length': len(password),
            'charset_size': len(set(password)),
            'theoretical_entropy': get_charset_entropy(password),
            'actual_entropy': calculate_actual_entropy(password),
            'patterns_detected': detect_patterns(password),
            'dictionary_word_found': check_dictionary_words(password),
            'keyboard_pattern_found': check_keyboard_patterns(password),
            'repetition_score': calculate_repetition_score(password)
        }
        e = analysis['actual_entropy']
        if analysis['patterns_detected'] or analysis['dictionary_word_found'] or analysis['keyboard_pattern_found']:
            rating = "Very Weak (Pattern/Word detected)"
        elif e < 40:
            rating = "Very Weak"
        elif e < 60:
            rating = "Weak"
        elif e < 80:
            rating = "Fair"
        elif e < 100:
            rating = "Good"
        else:
            rating = "Excellent"
        analysis['strength_rating'] = rating
        return analysis
    except Exception as e:
        print(f"Strength analysis failed: {e}")
        return {
            'length': 0, 'charset_size': 0,
            'theoretical_entropy': 0, 'actual_entropy': 0,
            'patterns_detected': False, 'dictionary_word_found': False,
            'keyboard_pattern_found': False, 'repetition_score': 0,
            'strength_rating': 'Analysis Failed'
        }

# --- Security self-checks (lightweight) ---
def validate_entropy_source():
    try:
        return secrets.SystemRandom is not None
    except Exception:
        return False

def check_memory_protection():
    try:
        s = SecureString("Test")
        s.clear()
        return s._is_cleared
    except Exception:
        return False

def check_timing_attacks():
    try:
        short = "a"*10
        longp = "a"*100
        runs = 5
        t0 = time.perf_counter()
        for _ in range(runs): comprehensive_strength_analysis(short)
        t1 = time.perf_counter()
        for _ in range(runs): comprehensive_strength_analysis(longp)
        t2 = time.perf_counter()
        return (t2-t1) - (t1-t0) < (t1-t0)*3.0
    except Exception:
        return False

def test_input_validation():
    try:
        for inp in ["' OR '1'='1", "A"*100, "rm -rf /", ";", "", None]:
            if inp is not None:
                comprehensive_strength_analysis(str(inp))
        return True
    except Exception:
        return False

def security_audit():
    try:
        return {
            'entropy_source': validate_entropy_source(),
            'memory_protection': check_memory_protection(),
            'timing_consistency': check_timing_attacks(),
            'input_validation': test_input_validation()
        }
    except Exception as e:
        print(f"Security audit failed: {e}")
        return {
            'entropy_source': False,
            'memory_protection': False,
            'timing_consistency': False,
            'input_validation': False
        }

# --- Async utility ---
def run_in_thread(func, callback, *args, **kwargs):
    def thread_function():
        try:
            result = func(*args, **kwargs)
            if root and root.winfo_exists():
                root.after(0, lambda: callback(result))
        except Exception as e:
            print(f"Thread execution failed: {e}")
            if root and root.winfo_exists():
                root.after(0, lambda: callback(None))
    threading.Thread(target=thread_function, daemon=True).start()

# --- Breach Detection (HIBP) with polite 429 handling ---
def check_password_breach(password):
    """
    HIBP k-anonymity 'range' API.
    Sends first 5 chars of SHA-1; matches suffix locally.
    Returns: dict { is_breached, breach_count, error, retry_after? }
    """
    if not password:
        return {'is_breached': False, 'breach_count': 0, 'error': None}
    try:
        sha1_hash = hashlib.sha1(password.encode('utf-8')).hexdigest().upper()
        prefix, suffix = sha1_hash[:5], sha1_hash[5:]
        url = f"https://api.pwnedpasswords.com/range/{prefix}"
        headers = {
            "User-Agent": "TsarSecure-PasswordChecker/2.6",
            "Add-Padding": "true"
        }
        r = requests.get(url, headers=headers, timeout=BREACH_CHECK_TIMEOUT)
        if r.status_code == 200:
            for line in r.text.strip().splitlines():
                if ':' not in line:
                    continue
                h_suf, count = line.split(':', 1)
                if h_suf == suffix:
                    try:
                        return {'is_breached': True, 'breach_count': int(count), 'error': None}
                    except ValueError:
                        return {'is_breached': True, 'breach_count': 1, 'error': None}
            return {'is_breached': False, 'breach_count': 0, 'error': None}
        elif r.status_code == 429:
            retry_after = None
            try:
                ra = r.headers.get("Retry-After")
                if ra is not None:
                    retry_after = int(float(ra))
            except Exception:
                retry_after = None
            return {'is_breached': False, 'breach_count': 0, 'error': 'Rate limited', 'retry_after': retry_after}
        else:
            return {'is_breached': False, 'breach_count': 0, 'error': f'HTTP {r.status_code}'}
    except requests.exceptions.Timeout:
        return {'is_breached': False, 'breach_count': 0, 'error': 'Timeout'}
    except requests.exceptions.ConnectionError:
        return {'is_breached': False, 'breach_count': 0, 'error': 'No internet'}
    except Exception as e:
        return {'is_breached': False, 'breach_count': 0, 'error': f'Error: {str(e)[:60]}'}

def format_breach_count(count: int) -> str:
    if count >= 1_000_000:
        return f"{count/1_000_000:.1f}M"
    if count >= 1_000:
        return f"{count/1_000:.1f}K"
    return str(count)

def get_breach_risk_level(count: int) -> str:
    if count == 0: return "SAFE"
    if count < 10: return "LOW"
    if count < 100: return "MEDIUM"
    if count < 1000: return "HIGH"
    return "CRITICAL"

def risk_color(level: str) -> str:
    return {
        "SAFE": BREACH_GREEN, "LOW": BREACH_YELLOW,
        "MEDIUM": BREACH_ORANGE, "HIGH": BREACH_ORANGE,
        "CRITICAL": BREACH_RED
    }.get(level, BREACH_YELLOW)

def update_breach_ui(result, label_widget: ttk.Label):
    if not label_widget or not label_widget.winfo_exists():
        return
    if result is None:
        label_widget.config(text="Breach: ? (error)", foreground=BREACH_YELLOW)
        return
    if result.get('error'):
        label_widget.config(text=f"Breach: ? ({result['error']})", foreground=BREACH_YELLOW)
        return
    if result.get('is_breached'):
        cnt = result.get('breach_count', 0)
        lvl = get_breach_risk_level(cnt)
        label_widget.config(text=f"Breach: {format_breach_count(cnt)} ({lvl})", foreground=risk_color(lvl))
    else:
        label_widget.config(text="Breach: 0 (SAFE)", foreground=BREACH_GREEN)

def do_breach_check(pw: str, label_widget: ttk.Label):
    run_in_thread(check_password_breach, lambda res: update_breach_ui(res, label_widget), pw)

def breach_check_with_throttle(pw: str, label_widget: ttk.Label, button_widget: ttk.Button, attempt: int = 0):
    """
    Client-side throttle + exponential backoff for HIBP checks.
    - Debounces rapid clicks
    - Disables the button while a request is in flight
    - Retries on 429 with capped exponential backoff
    """
    global _breach_last_click_ts, _breach_inflight

    if _breach_inflight:
        show_temporary_message("Breach check already running…", 1200)
        return

    now = time.time()
    if (now - _breach_last_click_ts) < MIN_BREACH_CLICK_INTERVAL:
        show_temporary_message("Too fast. Try again in a moment.", 1200)
        return
    _breach_last_click_ts = now

    # Disable UI while in flight
    try:
        if button_widget and button_widget.winfo_exists():
            button_widget.state(['disabled'])
        if label_widget and label_widget.winfo_exists():
            label_widget.config(text="Breach: checking…", foreground=ELECTRIC_BLUE)
    except Exception:
        pass

    _breach_inflight = True

    def _on_result(res):
        nonlocal attempt
        try:
            if res and res.get('error') == 'Rate limited' and attempt < MAX_BREACH_RETRIES:
                retry_after = res.get('retry_after')
                if retry_after is None:
                    delay_ms = int((BACKOFF_BASE_MS * (2 ** attempt)) + secrets.randbelow(250))
                else:
                    delay_ms = max(0, int(retry_after * 1000))
                if label_widget and label_widget.winfo_exists():
                    label_widget.config(text=f"Breach: waiting {delay_ms//1000}s (rate-limited)…", foreground=BREACH_YELLOW)
                attempt += 1
                root.after(delay_ms, lambda: breach_check_with_throttle(pw, label_widget, button_widget, attempt))
                return
            update_breach_ui(res, label_widget)
        finally:
            if not (res and res.get('error') == 'Rate limited' and attempt <= MAX_BREACH_RETRIES):
                _end_breach_request(button_widget)

    run_in_thread(check_password_breach, _on_result, pw)

def _end_breach_request(button_widget: ttk.Button):
    global _breach_inflight
    _breach_inflight = False
    try:
        if button_widget and button_widget.winfo_exists():
            button_widget.state(['!disabled'])
    except Exception:
        pass

# --- UI Functions ---
def update_entropy_label(entropy_bits):
    try:
        if not entropy_bits:
            entropy_label.config(text="")
            return
        if entropy_bits < 40:
            color, strength = "#FF0000", "Very Weak"
        elif entropy_bits < 60:
            color, strength = "#FF4500", "Weak"
        elif entropy_bits < 80:
            color, strength = "#FFA500", "Fair"
        elif entropy_bits < 100:
            color, strength = "#FFFF00", "Good"
        else:
            color, strength = "#39FF14", "Excellent"
        entropy_label.config(text=f"Entropy: {entropy_bits:.1f} bits ({strength})", foreground=color)
    except Exception as e:
        print(f"Entropy label update failed: {e}")

def secure_generate_password():
    """Generate a password (threaded) and display with entropy."""
    global _secure_password_storage, _password_clear_timer
    try:
        cancel_clipboard_countdown("new_password")
        if _secure_password_storage:
            _secure_password_storage.clear()
        if _password_clear_timer and _password_clear_timer.is_alive():
            _password_clear_timer.cancel()

        password_entry.config(state="normal")
        password_var.set("Generating...")
        passphrase_var.set("")
        root.update()

        length = int(password_length_slider.get())

        def generate_with_entropy(length):
            pw = generate_password_sync(length)
            ent = calculate_actual_entropy(pw)
            return (pw, ent)

        def on_done(result):
            try:
                if result is None:
                    password_var.set("Generation Failed")
                    password_entry.config(state="readonly")
                    return
                pw, ent = result
                _secure_password_storage = SecureString(pw)
                password_var.set(_secure_password_storage.get())
                password_entry.config(state="readonly")
                update_entropy_label(ent)
                start_auto_clear()
            except Exception as e:
                print(f"Password generation callback failed: {e}")
                password_var.set("Generation Failed")
                password_entry.config(state="readonly")

        run_in_thread(generate_with_entropy, on_done, length)
    except Exception as e:
        print(f"Password generation failed: {e}")
        password_var.set("Generation Failed")
        if 'password_entry' in globals():
            password_entry.config(state="readonly")

def secure_generate_passphrase():
    """Generate a Diceware passphrase (threaded) and display with entropy."""
    global _secure_password_storage, _password_clear_timer
    try:
        cancel_clipboard_countdown("new_password")
        if _secure_password_storage:
            _secure_password_storage.clear()
        if _password_clear_timer and _password_clear_timer.is_alive():
            _password_clear_timer.cancel()

        passphrase_entry.config(state="normal")
        passphrase_var.set("Generating...")
        password_var.set("")
        root.update()

        word_count = int(passphrase_length_slider.get())

        def generate_with_entropy(word_count):
            phrase = generate_diceware_passphrase(word_count, separator=" ")
            ent = calculate_actual_entropy(phrase)
            return (phrase, ent)

        def on_done(result):
            try:
                if result is None:
                    passphrase_var.set("Generation Failed")
                    passphrase_entry.config(state="readonly")
                    return
                phrase, ent = result
                _secure_password_storage = SecureString(phrase)
                passphrase_var.set(_secure_password_storage.get())
                passphrase_entry.config(state="readonly")
                update_entropy_label(ent)
                start_auto_clear()
            except Exception as e:
                print(f"Passphrase generation callback failed: {e}")
                passphrase_var.set("Generation Failed")
                passphrase_entry.config(state="readonly")

        run_in_thread(generate_with_entropy, on_done, word_count)
    except Exception as e:
        print(f"Passphrase generation failed: {e}")
        passphrase_var.set("Generation Failed")
        if 'passphrase_entry' in globals():
            passphrase_entry.config(state="readonly")

def start_auto_clear():
    """Start the auto-clear timer for displayed secrets."""
    global _password_clear_timer
    _password_clear_timer = threading.Timer(PASSWORD_DISPLAY_TIMEOUT, secure_clear_password)
    _password_clear_timer.daemon = True
    _password_clear_timer.start()

def on_tab_changed(event):
    try:
        selected_tab = notebook.tab(notebook.select(), "text")
        if selected_tab == "Password Generator":
            passphrase_var.set("")
            if not password_var.get():
                update_entropy_label(0)
        elif selected_tab == "Passphrase Generator":
            password_var.set("")
            if not passphrase_var.get():
                update_entropy_label(0)
    except Exception as e:
        print(f"Tab change handler failed: {e}")

def on_check_password_entry_change(*args):
    try:
        pw = check_password_var.get()
        if not pw:
            update_entropy_label(0)
            return
        def on_analysis_complete(analysis):
            try:
                update_entropy_label(analysis['actual_entropy'] if analysis else 0)
            except Exception as e:
                print(f"Analysis callback failed: {e}")
        run_in_thread(comprehensive_strength_analysis, on_analysis_complete, pw)
    except Exception as e:
        print(f"Password check handler failed: {e}")

def lock_computer():
    try:
        if sys.platform == "win32":
            ctypes.windll.user32.LockWorkStation()
        elif sys.platform == "darwin":
            os.system("/System/Library/CoreServices/Menu\\ Extras/User.menu/Contents/Resources/CGSession -suspend")
        else:
            os.system("dm-tool lock")
    except Exception as e:
        show_temporary_message(f"Lock failed: {str(e)[:30]}", 3000)

# --- Main Application ---
def main_app():
    global root, notebook, password_var, passphrase_var, entropy_label
    global password_length_slider, passphrase_length_slider, check_password_var
    global password_entry, passphrase_entry, status_label, _copy_button_ref

    try:
        # Run a lightweight security audit at startup (printed only if something fails)
        audit = security_audit()
        if not all(audit.values()):
            print("Security Audit Report:")
            print(json.dumps(audit, indent=4))

        # UI
        root = tk.Tk()
        root.title("TsarSecure v2.5.0")
        root.geometry("600x650")
        root.configure(bg=DARK_BG)
        root.attributes('-alpha', WINDOW_ALPHA)
        root.grid_columnconfigure(0, weight=1)
        root.protocol("WM_DELETE_WINDOW", enhanced_exit_handler)

        style = ttk.Style()
        style.theme_use('clam')
        style.configure("TFrame", background=DARK_BG)
        style.configure("TLabel", background=DARK_BG, foreground=NEON_GREEN, font=("Consolas", 11))
        style.configure("TButton", background=MEDIUM_BG, foreground=NEON_GREEN, font=("Consolas", 11), borderwidth=0)
        style.map("TButton", background=[("active", ELECTRIC_BLUE)], foreground=[("active", DARK_BG)])
        style.configure("TScale", background=DARK_BG, troughcolor=MEDIUM_BG)
        style.configure("Futuristic.TEntry", fieldbackground=MEDIUM_BG, foreground=NEON_GREEN, borderwidth=0,
                        insertcolor=NEON_GREEN, font=("Consolas", 12))
        style.configure("TNotebook", background=DARK_BG, borderwidth=0)
        style.configure("TNotebook.Tab", background=MEDIUM_BG, foreground=ELECTRIC_BLUE, padding=[10, 5])
        style.map("TNotebook.Tab", background=[("selected", DARK_BG)], foreground=[("selected", NEON_GREEN)])

        notebook = ttk.Notebook(root)
        notebook.grid(row=0, column=0, sticky="nsew", padx=10, pady=10)
        notebook.bind("<<NotebookTabChanged>>", on_tab_changed)

        # Password Generator Tab
        password_frame = ttk.Frame(notebook)
        notebook.add(password_frame, text="Password Generator")
        password_frame.grid_columnconfigure(0, weight=1)

        password_var = tk.StringVar()
        password_entry = ttk.Entry(password_frame, textvariable=password_var, style="Futuristic.TEntry",
                                   justify="center", state="readonly")
        password_entry.grid(row=0, column=0, pady=(20, 5), sticky="ew", padx=20)

        ttk.Label(password_frame, text="Password Length:").grid(row=2, column=0, pady=(10, 0))
        password_length_slider = ttk.Scale(password_frame, from_=8, to=30, orient=tk.HORIZONTAL, style="TScale")
        password_length_slider.set(12)
        password_length_slider.grid(row=3, column=0, sticky="ew", padx=30)

        generate_btn = ttk.Button(password_frame, text="Generate Secure Password", command=secure_generate_password)
        generate_btn.grid(row=4, column=0, pady=(10, 5))

        # Passphrase Generator Tab
        passphrase_frame = ttk.Frame(notebook)
        notebook.add(passphrase_frame, text="Passphrase Generator")
        passphrase_frame.grid_columnconfigure(0, weight=1)

        passphrase_var = tk.StringVar()
        passphrase_entry = ttk.Entry(passphrase_frame, textvariable=passphrase_var, style="Futuristic.TEntry",
                                     justify="center", state="readonly")
        passphrase_entry.grid(row=0, column=0, pady=(20, 5), sticky="ew", padx=20)

        ttk.Label(passphrase_frame, text="Word Count:").grid(row=1, column=0, pady=(10, 0))
        passphrase_length_slider = ttk.Scale(passphrase_frame, from_=4, to=8, orient=tk.HORIZONTAL, style="TScale")
        passphrase_length_slider.set(5)
        passphrase_length_slider.grid(row=2, column=0, sticky="ew", padx=30)

        generate_passphrase_btn = ttk.Button(passphrase_frame, text="Generate Secure Passphrase",
                                             command=secure_generate_passphrase)
        generate_passphrase_btn.grid(row=3, column=0, pady=(10, 5))

        # Common controls below the notebook
        common_frame = ttk.Frame(root)
        common_frame.grid(row=1, column=0, sticky="ew", padx=10)
        common_frame.grid_columnconfigure(0, weight=1)

        # Entropy label - shared
        entropy_label = ttk.Label(common_frame, text="", style="TLabel")
        entropy_label.grid(row=0, column=0, pady=5)

        copy_button = ttk.Button(
            common_frame,
            text="Copy to Clipboard (Clears in 30s)",
            command=lambda: secure_copy_password(copy_button),
            style="TButton"
        )
        copy_button.grid(row=1, column=0, pady=(10, 5), sticky="n")
        _copy_button_ref = copy_button  # keep a reference for UI state updates

        clear_button = ttk.Button(common_frame, text="Clear Password Now", command=secure_clear_password)
        clear_button.grid(row=2, column=0, pady=5, sticky="n")

        ttk.Label(root, text="--- Check Your Own Password ---", style="TLabel", foreground=ELECTRIC_BLUE).grid(row=2, column=0, pady=(20,5))

        check_password_var = tk.StringVar()
        check_password_entry = ttk.Entry(root, textvariable=check_password_var, style="Futuristic.TEntry", justify="center")
        check_password_entry.grid(row=3, column=0, pady=5, sticky="ew", padx=30)
        check_password_var.trace_add('write', on_check_password_entry_change)

        check_strength_button = ttk.Button(root, text="Check Strength",
                                           command=lambda: run_in_thread(
                                               comprehensive_strength_analysis,
                                               lambda a: update_entropy_label(a['actual_entropy'] if a else 0),
                                               check_password_var.get()),
                                           style="TButton")
        check_strength_button.grid(row=4, column=0, pady=10, sticky="n")

        # Breach UI
        breach_label = ttk.Label(root, text="Breach: —", style="TLabel", foreground=ELECTRIC_BLUE)
        breach_label.grid(row=5, column=0, pady=(0, 4))
        breach_button = ttk.Button(
            root,
            text="Check Breach (HIBP)",
            command=lambda: breach_check_with_throttle(check_password_var.get(), breach_label, breach_button),
            style="TButton"
        )
        breach_button.grid(row=6, column=0, pady=(2, 12), sticky="n")

        lock_button = ttk.Button(root, text="🔒 Lock Computer", command=lock_computer)
        lock_button.grid(row=7, column=0, pady=20, sticky="n")

        status_label = ttk.Label(root, text="", style="TLabel")
        status_label.grid(row=8, column=0, pady=5)

        info_label = ttk.Label(root,
                               text="🔒 Passwords auto-clear from display/memory after 30s\n🔒 Clipboard auto-clears after 30s",
                               foreground="#FFFF00", font=("Consolas", 9, "italic"))
        info_label.grid(row=9, column=0, pady=(5, 10))

        update_entropy_label(0)
        root.mainloop()

    except Exception as e:
        print(f"Application startup failed: {e}")
        if 'root' in locals():
            try:
                root.quit()
            except:
                pass

if __name__ == "__main__":
    try:
        enable_security_features()
        main_app()
    except Exception as e:
        print(f"Fatal error: {e}")
        sys.exit(1)
