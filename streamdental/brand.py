#!/usr/bin/env python3
"""Apply Stream Dental Support branding to the RustDesk source tree.

Run from the repository root after `git submodule update --init` (the
server address, key and app name live in the libs/hbb_common submodule,
so they are patched here instead of in a separate fork).
"""
import pathlib
import re
import shutil
import sys

ROOT = pathlib.Path(__file__).resolve().parent.parent
BRAND = ROOT / "streamdental"

APP_NAME = "StreamDentalSupport"          # internal name: no spaces (used unquoted in `sc create`)
DISPLAY_NAME = "Stream Dental Support"    # shown in file properties / installer
DESCRIPTION = "Stream Dental Support - fjärrsupport"
SERVER = "streamdental.webredirect.org"
PUB_KEY = "lpNDghUXel1CbGmMt34vZH36ZZmpO75adBezXgR6ygk="
COPYRIGHT = "Stream Dental (Dental Overdrive AB). Based on RustDesk (AGPL-3.0)."


def sub(path, pattern, repl, count=1, flags=0):
    p = ROOT / path
    text = p.read_text(encoding="utf-8")
    new, n = re.subn(pattern, repl, text, count=count, flags=flags)
    if n == 0:
        sys.exit(f"brand.py: pattern not found in {path}: {pattern}")
    p.write_text(new, encoding="utf-8")
    print(f"patched {path} ({n})")


# 1. App name, server and key (hbb_common submodule)
cfg = "libs/hbb_common/src/config.rs"
sub(cfg, r'RwLock::new\("RustDesk"\.to_owned\(\)\)', f'RwLock::new("{APP_NAME}".to_owned())')
sub(cfg, r'pub const RENDEZVOUS_SERVERS: &\[&str\] = &\[[^\]]*\];',
    f'pub const RENDEZVOUS_SERVERS: &[&str] = &["{SERVER}"];')
sub(cfg, r'pub const RS_PUB_KEY: &str = "[^"]*";', f'pub const RS_PUB_KEY: &str = "{PUB_KEY}";')

# 2. Windows runner fallback name and version resources
sub("flutter/windows/runner/main.cpp", r'std::wstring app_name = L"RustDesk";',
    f'std::wstring app_name = L"{APP_NAME}";')
sub("flutter/windows/runner/Runner.rc", r'VALUE "FileDescription", "[^"]*"',
    f'VALUE "FileDescription", "{DESCRIPTION}"')
sub("flutter/windows/runner/Runner.rc", r'VALUE "ProductName", "[^"]*"',
    f'VALUE "ProductName", "{DISPLAY_NAME}"')
sub("flutter/windows/runner/Runner.rc", r'VALUE "CompanyName", "[^"]*"',
    'VALUE "CompanyName", "Stream Dental"')
sub("flutter/windows/runner/Runner.rc", r'VALUE "LegalCopyright", "[^"]*"',
    f'VALUE "LegalCopyright", "{COPYRIGHT}"')

# 3. Rust binary metadata
sub("Cargo.toml", r'description = "RustDesk Remote Desktop"', f'description = "{DESCRIPTION}"')
sub("Cargo.toml", r'LegalCopyright = "[^"]*"', f'LegalCopyright = "{COPYRIGHT}"')
sub("Cargo.toml", r'ProductName = "RustDesk"', f'ProductName = "{DISPLAY_NAME}"')
sub("Cargo.toml", r'FileDescription = "RustDesk Remote Desktop"', f'FileDescription = "{DESCRIPTION}"')

# 4. Icons
copies = {
    "icon.ico": ["res/icon.ico", "res/tray-icon.ico", "flutter/windows/runner/resources/app_icon.ico"],
    "icon.png": ["res/icon.png"],
    "32x32.png": ["res/32x32.png"],
    "64x64.png": ["res/64x64.png"],
    "128x128.png": ["res/128x128.png"],
    "128x128@2x.png": ["res/128x128@2x.png"],
    "mac-icon.png": ["res/mac-icon.png"],
    "icon.svg": ["flutter/assets/icon.svg", "res/logo.svg", "res/scalable.svg"],
}
for src, dests in copies.items():
    for d in dests:
        dest = ROOT / d
        if dest.exists():
            shutil.copyfile(BRAND / src, dest)
            print(f"icon {d}")

print("Stream Dental branding applied.")
