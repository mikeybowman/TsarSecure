# TsarSecure v2.0
# Author: Tsardev
# Copyright (c) 2025 Tsardev - All Rights Reserved.
# This code is open-source under the MIT License.

import tkinter as tk
from tkinter import ttk
import secrets
import string
import os
import math

# --- Constants for Colors and Timing ---
NEON_GREEN = "#39FF14"
DARK_BG = "#1e1e1e"
MEDIUM_BG = "#333333"
ELECTRIC_BLUE = "#00FFFF"
WINDOW_ALPHA = 0.9

# --- Diceware Wordlist ---
# The complete Diceware wordlist used for passphrase generation, now fully alphabetized.
# In a real-world scenario, a much larger list (e.g., EFF's large wordlist)
# with thousands of words would provide higher entropy per word.
DICEWARE_WORDLIST = [
    "ability", "able", "about", "above", "absent", "absorb", "abstract", "absurd", "abuse", "access",
    "accident", "account", "accuse", "achieve", "acid", "acoustic", "acquire", "across", "act", "action",
    "active", "actor", "actual", "adapt", "add", "addict", "address", "adjust", "admire", "admit",
    "adopt", "advance", "advice", "advise", "aerobic", "affair", "affect", "afford", "afraid", "again",
    "age", "agent", "agree", "ahead", "aim", "air", "airport", "aisle", "alarm", "album",
    "alcohol", "alert", "alien", "all", "allow", "almost", "alone", "already", "also", "alter",
    "always", "amateur", "amazing", "ambition", "arbiter", "beamish", "bentley", "canihazrecon", "cortana", "dakota",
    "empty", "enable", "enact", "end", "endless", "endorse", "endure", "energy", "enforce", "engage",
    "engine", "enjoy", "enlist", "enough", "enrich", "ensure", "enter", "entire", "entry", "envelope",
    "episode", "equal", "equip", "erase", "erode", "erosion", "error", "erupt", "escape", "essay",
    "essence", "essential", "establish", "estimate", "eternal", "ether", "ethical", "euphemism", "evade",
    "evaluate", "evening", "every", "evidence", "evil", "evoke", "evolve", "exact", "example", "excel",
    "except", "exchange", "excite", "exclude", "excuse", "execute", "exercise", "exhaust", "exhibit",
    "exist", "exit", "exotic", "expand", "expect", "experience", "explain", "expose", "express", "extend",
    "extra", "eye", "eyebrow", "fabric", "face", "faculty", "fade", "fail", "faint", "fair",
    "faith", "fall", "false", "fame", "family", "famous", "fan", "fancy", "fantasy", "farm",
    "fashion", "fat", "fatal", "father", "fatigue", "fault", "favor", "fear", "feature", "federal",
    "fee", "feed", "feel", "female", "fence", "fetch", "fever", "few", "fiber", "fiction",
    "field", "figure", "file", "fill", "filter", "find", "fine", "finger", "finish", "fire",
    "firm", "first", "fiscal", "fish", "fit", "fitness", "fix", "flavor", "flee", "flight",
    "float", "flock", "floor", "flower", "fluid", "flush", "fly", "focus", "foil", "fold",
    "follow", "food", "foot", "force", "forest", "forget", "fork", "form", "formula", "fortune",
    "forum", "forward", "fossil", "foster", "found", "fox", "fragile", "frame", "frequent", "fresh",
    "friend", "fringe", "frog", "front", "fruit", "fuel", "fun", "funny", "furnace", "fury",
    "future", "gadget", "gain", "galaxy", "gallery", "game", "gap", "garage", "garden", "garlic",
    "garment", "gas", "gather", "gauge", "gaze", "general", "genius", "genre", "gentle", "genuine",
    "geography", "geometry", "gesture", "get", "ghost", "giant", "gift", "giggle", "ginger", "giraffe",
    "girl", "give", "glass", "glide", "global", "globe", "gloom", "glory", "glove", "glow",
    "glue", "goat", "goddess", "goose", "gorgeous", "gorilla", "gospel", "gossip", "govern", "grab",
    "grace", "grade", "grain", "grand", "grant", "grape", "graph", "grass", "gravity", "great",
    "green", "grid", "grief", "grow", "ground", "group", "grove", "grunt", "guard", "guess",
    "guide", "guilt", "guitar", "guiltyspark", "gun", "gym", "habit", "hair", "half", "hammer",
    "hamster", "hand", "happy", "harbor", "hard", "harsh", "harvest", "hat", "have", "hawk",
    "hazard", "head", "health", "heart", "heavy", "height", "hello", "help", "hen", "hero",
    "hidden", "high", "hold", "holiday", "home", "honey", "hope", "horn", "horror", "horse",
    "hospital", "host", "hotel", "hour", "hover", "how", "human", "humble", "humor", "hundred",
    "hungry", "hunt", "hurry", "hurt", "husband", "hybrid", "ice", "icon", "idea", "identify",
    "idle", "ignore", "ill", "illegal", "illness", "image", "imagine", "immune", "impact", "impose",
    "improve", "impulse", "in", "inch", "include", "income", "increase", "index", "indicate", "indoor",
    "infant", "inflict", "info", "inform", "inherit", "initial", "inject", "injury", "inner", "innocent",
    "input", "inquiry", "insane", "insect", "inside", "inspire", "install", "intact", "interest", "into",
    "invest", "invite", "involve", "iron", "island", "isolate", "issue", "item", "ivory", "jacket",
    "jaguar", "jail", "james", "january", "jaw", "jeans", "jelly", "jewel", "job", "join",
    "joint", "joke", "journey", "joy", "judge", "juice", "july", "jump", "june", "jungle",
    "junior", "junk", "just", "kangaroo", "keen", "keep", "kettle", "key", "kick", "kill",
    "kind", "kingdom", "kiss", "kit", "kitchen", "kite", "kitten", "kiwi", "knee", "knife",
    "knock", "know", "lab", "label", "labor", "ladder", "lady", "lake", "lamp", "language",
    "laptop", "large", "last", "late", "laugh", "lava", "law", "lawn", "leader", "leaf",
    "learn", "leave", "lecture", "left", "leg", "legal", "legend", "leisure", "lemon", "lend",
    "length", "lens", "leopard", "lesson", "let", "letter", "level", "liar", "liberty", "library",
    "license", "life", "light", "like", "limb", "limit", "link", "lion", "liquid", "list",
    "little", "live", "lizard", "load", "loan", "lobster", "local", "lock", "logic", "lonely",
    "long", "loop", "loose", "lord", "lose", "loss", "lottery", "loud", "lounge", "love",
    "loyal", "lucky", "luggage", "lumber", "lunar", "lunch", "luxury", "lyrics", "machine", "mad",
    "magic", "magnet", "magnify", "mail", "main", "major", "make", "mammal", "man", "manage",
    "mandate", "mango", "manipulate", "manual", "maple", "marble", "march", "margin", "marine", "market",
    "mask", "master", "masterchief", "match", "material", "math", "matrix", "matter", "matthias", "maximum",
    "maze", "mean", "measure", "meat", "mechanism", "medial", "mediate", "medical", "medium", "meet",
    "melody", "melt", "member", "memory", "mention", "menu", "mercy", "merge", "merit", "merry",
    "mesh", "message", "metal", "method", "mexico", "middle", "midnight", "migrate", "milk", "mill",
    "mimic", "mind", "minimum", "minor", "minute", "miracle", "mirror", "misery", "miss", "mistake",
    "mix", "moment", "monday", "money", "monitor", "monkey", "monster", "month", "moon", "moral",
    "more", "morning", "mosquito", "mother", "motion", "motor", "mountain", "mouse", "move", "movie",
    "much", "muffin", "mule", "multiply", "muscle", "museum", "mushroom", "music", "must", "mutual",
    "my", "mythic", "myself", "mystery", "myth", "naive", "name", "napkin", "narrow", "nasty",
    "nation", "nature", "near", "neat", "neck", "need", "negative", "neglect", "neither", "nephew",
    "nerve", "nest", "net", "network", "neutral", "never", "news", "next", "nice", "night",
    "note", "nothing", "notice", "novel", "now", "nuclear", "number", "nurse", "nut", "oak",
    "obey", "object", "oblige", "observe", "obtain", "obvious", "occasion", "occupy", "ocean", "october",
    "odor", "off", "offer", "office", "often", "ogre", "oil", "okay", "old", "olive",
    "on", "once", "one", "onion", "online", "only", "open", "opera", "opinion", "oppose",
    "option", "orange", "orbit", "orchard", "order", "ordinary", "organ", "orient", "original", "oscar",
    "other", "outcome", "outside", "oval", "oven", "over", "own", "owner", "oyster", "pace",
    "pack", "page", "pair", "palm", "pan", "pancake", "panda", "panel", "panic", "park",
    "parrot", "party", "pass", "patch", "path", "patient", "patrol", "pattern", "pause", "pave",
    "payment", "peace", "peanut", "pear", "peasant", "pelican", "pen", "penalty", "pencil", "people",
    "pepper", "perfect", "perform", "perfume", "perhaps", "period", "permit", "person", "pet", "phantom",
    "phase", "photo", "phrase", "physical", "piano", "pick", "picnic", "picture", "piece", "pig",
    "pigeon", "pill", "pilot", "pink", "pioneer", "pipe", "pistol", "pitch", "pizza", "place",
    "planet", "plastic", "plate", "play", "please", "pledge", "plot", "plug", "plus", "P",
    "pocket", "podium", "poem", "poet", "point", "polar", "pole", "police", "policy", "poll",
    "pond", "pony", "pool", "popular", "populate", "portion", "post", "potato", "pottery", "poverty",
    "powder", "power", "practice", "praise", "predict", "prefer", "prepare", "present", "pretty", "prevent",
    "price", "pride", "primary", "print", "priority", "prison", "private", "prize", "problem", "process",
    "produce", "profit", "program", "project", "promote", "proof", "property", "prosper", "protect", "proud",
    "provide", "public", "pudding", "pull", "pulp", "pulse", "punch", "pupil", "puppy", "purchase",
    "purity", "purpose", "purse", "push", "put", "puzzle", "pyramid", "quality", "quantify", "quantum",
    "quarter", "question", "quick", "quit", "quiz", "quote", "rabbit", "race", "rack", "radar",
    "radio", "raise", "rally", "ramp", "ranch", "random", "range", "rapid", "rare", "rate",
    "rather", "raven", "raw", "ready", "real", "reason", "rebel", "rebuild", "recall", "receive",
    "reception", "recipe", "record", "recover", "recruit", "recycle", "red", "reduce", "refuse", "regain",
    "regard", "regime", "region", "register", "regular", "reject", "relate", "release", "relief", "rely",
    "remain", "remember", "remind", "remote", "remove", "render", "renew", "rent", "reopen", "repair",
    "repeat", "replace", "report", "represent", "republic", "request", "require", "rescue", "resemble", "resist",
    "resource", "response", "result", "retire", "retreat", "return", "reveal", "reverse", "review", "reward",
    "rhythm", "ribbon", "rice", "rich", "ride", "ridge", "rift", "right", "rigid", "ring",
    "riot", "ripple", "risk", "ritual", "rival", "river", "road", "roast", "robot", "robust",
    "rocket", "rock", "rod", "roll", "roof", "rookie", "room", "rose", "rotate", "rough",
    "round", "route", "royal", "ruby", "rug", "rugby", "ruin", "rule", "run", "runway",
    "rural", "rush", "sad", "safari", "safe", "sail", "salad", "salmon", "salt", "sample",
    "sand", "satisfy", "satoshi", "sauce", "sausage", "save", "say", "scan", "scare", "scatter",
    "scene", "scheme", "school", "science", "scissors", "scorpion", "scout", "scrap", "screen", "script",
    "scrub", "sea", "search", "season", "seat", "second", "secret", "section", "security", "see",
    "seed", "seek", "seem", "segment", "select", "sell", "seminar", "senior", "sense", "sentence",
    "series", "serve", "session", "set", "settle", "setup", "seven", "shadow", "shaft", "shallow",
    "shame", "shape", "share", "shark", "sharp", "sheep", "sheet", "shelf", "shell", "sheriff",
    "shield", "shift", "shine", "ship", "short", "shoulder", "shove", "show", "shrink", "shrug",
    "shuffle", "shy", "sibling", "sick", "side", "sidewalk", "sign", "silent", "silk", "silly",
    "silver", "similar", "simple", "since", "sing", "siren", "sister", "situate", "six", "size",
    "skate", "sketch", "ski", "skill", "skin", "skirt", "skull", "slam", "sleep", "slight",
    "slim", "slogan", "slot", "slow", "slush", "small", "smart", "smile", "smoke", "smooth",
    "snack", "snake", "snap", "sniff", "snow", "soap", "soccer", "social", "sock", "soft",
    "solar", "soldier", "sole", "solid", "solution", "solve", "some", "someone", "stand", "start",
    "state", "station", "stay", "steady", "steam", "steel", "stem", "step", "stereo", "stick",
    "still", "sting", "stock", "stomach", "stone", "stool", "story", "stove", "strategy", "street",
    "strike", "strong", "struggle", "student", "stuff", "stumble", "style", "subject", "subway", "success",
    "such", "sudden", "suffer", "sugar", "suggest", "suit", "summer", "sun", "sunny", "sunset",
    "super", "supply", "support", "sure", "surface", "surge", "surprise", "surround", "survey", "suspect",
    "sustain", "swallow", "swamp", "switch", "sword", "symbol", "symptom", "syrup", "system", "table",
    "tag", "tail", "take", "talent", "talk", "tank", "target", "task", "taste", "taxi",
    "teach", "team", "tear", "tech", "telecom", "temple", "tenant", "tend", "tender", "tennis",
    "tense", "term", "test", "text", "thank", "that", "the", "then", "theory", "there",
    "they", "thing", "this", "thought", "three", "thrive", "thumb", "thunder", "ticket", "tide",
    "tie", "tilt", "timber", "time", "tiny", "tip", "tire", "tissue", "title", "toast",
    "tobacco", "today", "toddler", "toe", "together", "toilet", "token", "tomato", "tomorrow", "tone",
    "tongue", "tonight", "tool", "tooth", "top", "topic", "topple", "torch", "tornado", "tortoise",
    "total", "tour", "toward", "tower", "town", "toy", "track", "trade", "traffic", "tragic",
    "train", "transfer", "trap", "travel", "tray", "treat", "tree", "trend", "trial", "tribe",
    "trick", "trigger", "trim", "trip", "trophy", "trouble", "true", "trust", "truth", "try",
    "tube", "tuition", "tumble", "tuna", "tunnel", "turkey", "turn", "turtle", "tutor", "tv",
    "twin", "twist", "two", "type", "ugly", "umbrella", "unable", "uncover", "under", "undo",
    "unfold", "unhappy", "uniform", "unique", "unit", "universe", "unknown", "unlock", "until", "unusual",
    "unveil", "update", "upgrade", "uphold", "upon", "upper", "upset", "urban", "urge", "usage",
    "use", "used", "useful", "useless", "usual", "utility", "vacant", "vacuum", "vague", "valid",
    "valley", "valve", "van", "vanish", "vapor", "various", "vast", "vault", "vehicle", "velvet",
    "vendor", "venture", "venue", "verb", "verify", "version", "very", "vessel", "veteran"
]

# Sort the entire DICEWARE_WORDLIST alphabetically after all words are included
DICEWARE_WORDLIST.sort()

# Calculate the final size of the combined wordlist
WORDLIST_SIZE = len(DICEWARE_WORDLIST)

# --- Global variable to manage password restoration after "Copied!" message ---
_original_password_after_copy = "" 

# --- Function Definitions ---

def get_estimated_crack_time(entropy_bits):
    """
    Provides a very rough estimation of crack time based on entropy bits.
    These are highly simplified and depend heavily on attacker hardware.
    """
    if entropy_bits < 28:
        return "Instantly (or less than a second)"
    elif entropy_bits < 36:
        return "Minutes"
    elif entropy_bits < 43:
        return "Hours"
    elif entropy_bits < 50:
        return "Days"
    elif entropy_bits < 57:
        return "Months"
    elif entropy_bits < 64:
        return "Years"
    elif entropy_bits < 70:
        return "Decades"
    elif entropy_bits < 80:
        return "Centuries"
    elif entropy_bits < 90:
        return "Millennia"
    elif entropy_bits < 100:
        return "Millions of Years"
    else:
        return "Billions of Years (or longer)"

def generate_password():
    """
    Generates a secure random password or passphrase based on user-selected criteria.
    Updates the password display, checks its strength, and schedules clearing.
    """
    password_length = int(slider.get())  # Get the selected length/word count

    if passphrase_mode_var.get():
        # --- Passphrase Generation ---
        if password_length < 3: # Minimum reasonable passphrase length
            password_var.set("Error: At least 3 words for passphrase.")
            strength_label.config(text="Strength: N/A", foreground="gray")
            return

        passphrase_words = [secrets.choice(DICEWARE_WORDLIST) for _ in range(password_length)]
        password = "-".join(passphrase_words) # Join words with hyphens
        
        # Passphrase entropy: N_words * log2(WORDLIST_SIZE)
        entropy = password_length * math.log2(WORDLIST_SIZE)
        
        password_var.set(password)
        check_password_strength(password, entropy, is_passphrase=True)

    else:
        # --- Character-based Password Generation ---
        alphabet_chars = []
        if include_lower_var.get():
            alphabet_chars.extend(list(string.ascii_lowercase))
        if include_upper_var.get():
            alphabet_chars.extend(list(string.ascii_uppercase))
        if include_digits_var.get():
            alphabet_chars.extend(list(string.digits))
        if include_special_var.get():
            alphabet_chars.extend(list(string.punctuation))

        if not alphabet_chars:
            password_var.set("") # Clear any previous password
            strength_label.config(text="", foreground="gray") # Clear strength feedback
            
            error_feedback_label = ttk.Label(root, text="ERROR: SELECT CHARACTER TYPES!", foreground="red", 
                                           font=("Consolas", 11, "bold"), background=DARK_BG)
            error_feedback_label.grid(row=9, column=0, pady=5) # Place on appropriate row
            root.after(3000, lambda: error_feedback_label.destroy())
            return

        alphabet = ''.join(sorted(list(set(alphabet_chars))))
        password = ''.join(secrets.choice(alphabet) for _ in range(password_length))
        
        # Character-based entropy: Length * log2(Alphabet_size)
        entropy = password_length * math.log2(len(alphabet))

        password_var.set(password)
        check_password_strength(password, entropy, is_passphrase=False)

    root.after(30000, clear_password)

def clear_password():
    """
    Overwrites the password string in memory before clearing the variable.
    Sets the password display to blank.
    """
    global _original_password_after_copy # Ensure we can clear this if needed

    password = password_var.get()
    if password:
        random_chars = ''.join(secrets.choice(string.ascii_letters + string.digits + string.punctuation) 
                               for _ in range(len(password)))
        password_var.set(random_chars) # Overwrite for memory
        password_var.set("") # Set to blank
    strength_label.config(text="", foreground="gray") # Clear strength feedback
    _original_password_after_copy = "" # Clear stored password if timer runs

def copy_password():
    """
    Copies the generated password to the clipboard and displays 'Password Copied!'
    in the password entry, then reverts it after a short delay.
    """
    global _original_password_after_copy

    current_password = password_var.get()
    if current_password:
        root.clipboard_clear()
        root.clipboard_append(current_password)

        _original_password_after_copy = current_password # Store the actual password

        password_entry.config(state="normal") # Make editable temporarily
        password_var.set("Password Copied!")
        
        # Schedule the restoration
        root.after(2000, restore_password_entry_after_copy)
    else:
        # If password field is empty, show a temporary message below the copy button
        no_password_feedback_label = ttk.Label(root, text="No password to copy!", foreground="red", 
                                   font=("Consolas", 10, "bold"), background=DARK_BG)
        no_password_feedback_label.grid(row=12, column=0, pady=5, sticky="n") # Use same row as copy button, it's temporary
        root.after(1500, lambda: no_password_feedback_label.destroy())

def restore_password_entry_after_copy():
    """
    Restores the password entry to its original content or clears it
    if the 30-second timer ran during the 'Password Copied!' message.
    """
    global _original_password_after_copy

    # Only restore if the password_var still contains "Password Copied!"
    # This prevents overwriting a password that was cleared by clear_password()
    if password_var.get() == "Password Copied!":
        password_var.set(_original_password_after_copy)
    else: # If it's not "Password Copied!", it means clear_password() ran
        password_var.set("") # Ensure it stays blank

    password_entry.config(state="readonly") # Set back to readonly
    _original_password_after_copy = "" # Clear the stored password after use


def update_length_label(event=None):
    """Updates the label displaying the current length/word count selected by the slider."""
    current_value = int(slider.get())
    if passphrase_mode_var.get():
        length_label.config(text=f"Words: {current_value}")
    else:
        length_label.config(text=f"Length: {current_value}")

def check_password_strength(password, entropy_bits=None, is_passphrase=False):
    """
    Calculates password strength based on entropy (in bits) and updates the label.
    Includes time-to-crack estimation.
    """
    if not password:
        strength_label.config(text="Strength: N/A", foreground="gray")
        return

    if entropy_bits is None: # For "Check My Password" if not generated by us
        # Attempt to determine if it's a passphrase-like string or character-based
        # Simple heuristic: if it contains hyphens and words are in our wordlist
        if '-' in password and all(word in DICEWARE_WORDLIST for word in password.split('-')):
            word_count = len(password.split('-'))
            entropy_bits = word_count * math.log2(WORDLIST_SIZE)
        else: # Treat as complex character string
            # Estimate keyspace for arbitrary input (common printable ASCII ~94 chars)
            charset_size = 0
            if any(c.islower() for c in password): charset_size += 26
            if any(c.isupper() for c in password): charset_size += 26
            if any(c.isdigit() for c in password): charset_size += 10
            if any(c in string.punctuation for c in password): charset_size += 32
            
            if charset_size == 0: # If password contains no recognized char types
                charset_size = 1 # Prevent log2(0) error, minimal entropy
            
            entropy_bits = len(password) * math.log2(charset_size)

    
    estimated_time = get_estimated_crack_time(entropy_bits)

    # Determine strength level and update label based on entropy
    if entropy_bits >= 100:
        strength_label.config(text=f"Godlike ({int(entropy_bits)} bits)\nCracks in: {estimated_time}", foreground="#00FF7F")
    elif entropy_bits >= 80:
        # Corrected: changed estimated_BLUE to estimated_time and added foreground color
        strength_label.config(text=f"Hardened ({int(entropy_bits)} bits)\nCracks in: {estimated_time}", foreground="#FFD700")
    elif entropy_bits >= 60:
        strength_label.config(text=f"Exploitable ({int(entropy_bits)} bits)\nCracks in: {estimated_time}", foreground="#FFA500")
    else:
        strength_label.config(text=f"Breach Imminent! ({int(entropy_bits)} bits)\nCracks in: {estimated_time}", foreground="#FF4500")

def lock_computer():
    """
    Executes the Windows command to lock the computer.
    """
    try:
        os.system("rundll32.exe user32.dll,LockWorkStation")
    except Exception as e:
        print(f"Error locking computer: {e}") 

def toggle_passphrase_mode():
    """
    Toggles between character-based password generation and passphrase generation.
    Adjusts visibility/state of character type checkboxes and slider range.
    """
    if passphrase_mode_var.get():
        # Passphrase mode active
        include_lower_chk.config(state="disabled")
        include_upper_chk.config(state="disabled")
        include_digits_chk.config(state="disabled") # Corrected: added .config()
        include_special_chk.config(state="disabled")
        
        slider.config(from_=3, to=10) # 3 to 10 words for passphrase
        slider.set(6) # Default 6 words
        length_label.config(text=f"Words: {int(slider.get())}")
    else:
        # Character-based mode active
        include_lower_chk.config(state="normal")
        include_upper_chk.config(state="normal")
        include_digits_chk.config(state="normal") # Corrected: added .config()
        include_special_chk.config(state="normal")

        slider.config(from_=5, to=50) # 5 to 50 characters
        slider.set(12) # Default 12 characters
        length_label.config(text=f"Length: {int(slider.get())}")

    # Clear fields and strength info when mode changes
    password_var.set("")
    check_password_var.set("")
    strength_label.config(text="", foreground="gray")

# --- Main Window Setup ---
if __name__ == "__main__": # Ensures the GUI only runs when script is executed directly
    root = tk.Tk()
    root.title("Tsar Secure v2.0")
    root.resizable(True, True) # Window is resizable
    root.configure(bg=DARK_BG)
    root.attributes("-alpha", WINDOW_ALPHA)

    try:
        root.iconbitmap("ts.ico") 
    except Exception as e:
        print(f"Error setting icon: {e}. Make sure 'ts.ico' is in the same directory.")

    # --- Style Configuration ---
    style = ttk.Style(root)
    style.theme_use("clam") 

    style.configure("TLabel", background=DARK_BG, foreground=NEON_GREEN, font=("Consolas", 12))
    style.configure("Title.TLabel", background=DARK_BG, foreground=NEON_GREEN, font=("Consolas", 20, "bold"))
    style.configure("TButton", background=MEDIUM_BG, foreground=NEON_GREEN, font=("Consolas", 11), borderwidth=0, relief="flat", padding=8)
    style.map("TButton", background=[("active", "#444444")])
    style.configure("TCheckbutton", background=DARK_BG, foreground=NEON_GREEN, font=("Consolas", 11), padding=5)
    style.map("TCheckbutton", background=[("active", DARK_BG)])
    style.configure("TScale", background=DARK_BG, troughcolor=MEDIUM_BG, slidercolor=NEON_GREEN)
    style.configure("Futuristic.TEntry", fieldbackground=MEDIUM_BG, foreground=NEON_GREEN, 
                    font=("Consolas", 14), relief="solid", borderwidth=2, bordercolor=ELECTRIC_BLUE, padding=5) 

    # --- Grid Configuration for Responsiveness ---
    root.grid_columnconfigure(0, weight=1)
    for i in range(18): # Expanded row range for new elements
        root.grid_rowconfigure(i, weight=1)

    # --- WIDGET PLACEMENT WITH GRID ---

    # Row 0: Title
    title_label = ttk.Label(root, text="Tsar Secure v2.0", style="Title.TLabel")
    title_label.grid(row=0, column=0, pady=(20, 10), sticky="n") 

    # Row 1: Password Length/Words Label
    slider_label = ttk.Label(root, text="Password Length:")
    slider_label.grid(row=1, column=0, pady=(10, 0), sticky="s") 

    # Row 2: Slider
    slider = ttk.Scale(root, from_=5, to=50, orient="horizontal", length=300, command=update_length_label)
    slider.grid(row=2, column=0, pady=5, sticky="ew", padx=20) 

    # Row 3: Length/Words Display Label
    length_label = ttk.Label(root, text=f"Length: {int(slider.get())}")
    length_label.grid(row=3, column=0, pady=(0, 15), sticky="n")

    # Row 4: Passphrase Mode Checkbox (NEW)
    passphrase_mode_var = tk.BooleanVar(value=False)
    passphrase_mode_chk = ttk.Checkbutton(root, text="Passphrase Mode", variable=passphrase_mode_var, 
                                         command=toggle_passphrase_mode, style="TCheckbutton")
    passphrase_mode_chk.grid(row=4, column=0, pady=(5,0))

    # Rows 5-8: Character options checkboxes (now linked to a variable name for easy state change)
    include_lower_var = tk.BooleanVar(value=True)
    include_lower_chk = ttk.Checkbutton(root, text="Lowercase Letters (a-z)", variable=include_lower_var, style="TCheckbutton")
    include_lower_chk.grid(row=5, column=0, pady=2, padx=50)

    include_upper_var = tk.BooleanVar(value=True)
    include_upper_chk = ttk.Checkbutton(root, text="Uppercase Letters (A-Z)", variable=include_upper_var, style="TCheckbutton")
    include_upper_chk.grid(row=6, column=0, pady=2, padx=50)

    include_digits_var = tk.BooleanVar(value=True)
    include_digits_chk = ttk.Checkbutton(root, text="Numbers (0-9)", variable=include_digits_var, style="TCheckbutton")
    include_digits_chk.grid(row=7, column=0, pady=2, padx=50)

    include_special_var = tk.BooleanVar(value=False)
    include_special_chk = ttk.Checkbutton(root, text="Special Characters (!@#$)", variable=include_special_var, style="TCheckbutton")
    include_special_chk.grid(row=8, column=0, pady=2, padx=50)

    # Row 9: Generate Password Button (or Error Message)
    generate_button = ttk.Button(root, text="Generate Password", command=generate_password, style="TButton")
    generate_button.grid(row=9, column=0, pady=20, sticky="n") 

    # Row 10: Password display (read-only)
    password_var = tk.StringVar()
    password_entry = ttk.Entry(root, textvariable=password_var, style="Futuristic.TEntry", justify="center", state="readonly") 
    password_entry.grid(row=10, column=0, pady=5, sticky="ew", padx=30) 

    # Row 11: Password strength label (Now shows entropy bits and time-to-crack)
    strength_label = ttk.Label(root, text="", style="TLabel", justify="center") # Centered text for multi-line
    strength_label.grid(row=11, column=0, pady=(5, 10), sticky="n")

    # Row 12: Copy Password Button
    copy_button = ttk.Button(root, text="Copy Password", command=copy_password, style="TButton")
    copy_button.grid(row=12, column=0, pady=5, sticky="n")

    # --- NEW SECTION: Check My Password ---
    # Row 13: Spacer/Header for Check My Password
    ttk.Label(root, text="--- Check Your Own Password ---", style="TLabel", foreground=ELECTRIC_BLUE).grid(row=13, column=0, pady=(20,5))

    # Row 14: Check My Password Entry
    check_password_var = tk.StringVar()
    check_password_entry = ttk.Entry(root, textvariable=check_password_var, style="Futuristic.TEntry", justify="center")
    check_password_entry.grid(row=14, column=0, pady=5, sticky="ew", padx=30)

    # Row 15: Check Strength Button for input field
    check_strength_button = ttk.Button(root, text="Check Strength", 
                                       command=lambda: check_password_strength(check_password_var.get(), entropy_bits=None), 
                                       style="TButton")
    check_strength_button.grid(row=15, column=0, pady=10, sticky="n")
    # --- END Check My Password Section ---

    # Row 16: Lock Computer Button
    lock_button = ttk.Button(root, text="Lock Computer", command=lock_computer, style="TButton")
    lock_button.grid(row=16, column=0, pady=15, sticky="n")

    # Initial call to update slider label and checkbox states
    update_length_label() 

    # Start the GUI event loop
    root.mainloop()
