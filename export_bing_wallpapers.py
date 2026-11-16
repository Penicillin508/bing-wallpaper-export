#!/usr/bin/env python3
# -*- coding: utf-8 -*-
r"""
@Brief: Export Windows Bing / Spotlight lock screen wallpapers to the user's Downloads folder.
@Author: Penicillin508
@Date: 2026-09-11
@Version: 1.1.0

Default source:      %userprofile%\AppData\Local\Packages\Microsoft.Windows.ContentDeliveryManager_cw5n1h2txyewy\LocalState\Assets
Default destination: %userprofile%\Downloads
Naming:              BingWallpaper + YYMMDD (today) + 2-digit sequence + .jpg

Notes:
- No username or drive letter is hard-coded. All paths are resolved at runtime
  via %userprofile%, so the script works under any Windows user/environment
  (e.g. C:/Users/xxx, D:/Users/xxx).
- Only extension-less files are copied (Spotlight wallpaper cache, actually JPEG data).
- Numbering starts at 01. If files already exist for today in the destination,
  numbering continues after the highest existing sequence, so nothing is overwritten.

Usage:
    python export_bing_wallpapers.py                     # default source and destination
    python export_bing_wallpapers.py --src DIR           # custom source directory
    python export_bing_wallpapers.py --src DIR --dst DIR # custom source and destination
"""

import argparse
import os
import shutil
import sys
from datetime import datetime

# Resolve %userprofile% at runtime (equivalent to os.path.expanduser("~"));
# no specific username is hard-coded.
USERPROFILE = os.path.expandvars("%userprofile%")

DEFAULT_SRC = os.path.join(
    USERPROFILE,
    "AppData", "Local", "Packages",
    "Microsoft.Windows.ContentDeliveryManager_cw5n1h2txyewy",
    "LocalState", "Assets",
)
DEFAULT_DST = os.path.join(USERPROFILE, "Downloads")


def collect_no_ext_files(src):
    """Return all regular files with no extension in src, sorted by name (deterministic)."""
    items = []
    for name in os.listdir(src):
        full = os.path.join(src, name)
        if os.path.isfile(full) and os.path.splitext(name)[1] == "":
            items.append(name)
    items.sort()
    return items


def next_start_seq(dst, date_str):
    """Return max existing sequence + 1 for BingWallpaperYYMMDD*.jpg in dst."""
    prefix = "BingWallpaper" + date_str
    max_seq = 0
    if os.path.isdir(dst):
        for name in os.listdir(dst):
            if name.startswith(prefix) and name.endswith(".jpg"):
                digits = name[len(prefix):-4]
                if digits.isdigit():
                    max_seq = max(max_seq, int(digits))
    return max_seq + 1


def main(argv=None):
    parser = argparse.ArgumentParser(
        description="Export Bing lock screen wallpapers (extension-less assets) to Downloads, "
                    "renamed as BingWallpaperYYMMDD##.jpg"
    )
    parser.add_argument("--src", default=DEFAULT_SRC, help="source directory (default: %%userprofile%%\\...\\Assets)")
    parser.add_argument("--dst", default=DEFAULT_DST, help="destination directory (default: %%userprofile%%\\Downloads)")
    args = parser.parse_args(argv)

    src = os.path.expandvars(args.src)
    dst = os.path.expandvars(args.dst)

    if not os.path.isdir(src):
        print("[ERROR] Source directory not found: %s" % src)
        return 1

    os.makedirs(dst, exist_ok=True)

    files = collect_no_ext_files(src)
    if not files:
        print("[DONE] No extension-less files in source, nothing to copy.")
        return 0

    date_str = datetime.now().strftime("%y%m%d")
    seq = next_start_seq(dst, date_str)
    start_seq = seq

    copied = 0
    for name in files:
        seq_str = "%02d" % seq
        dest_name = "BingWallpaper%s%s.jpg" % (date_str, seq_str)
        dest_path = os.path.join(dst, dest_name)
        shutil.copy2(os.path.join(src, name), dest_path)
        print("%s  ->  %s" % (name, dest_name))
        copied += 1
        seq += 1

    print("\n[DONE] Copied %d file(s) to: %s" % (copied, dst))
    if start_seq > 1:
        print("(Sequence started at %02d to avoid overwriting existing files for today)" % start_seq)
    return 0


if __name__ == "__main__":
    sys.exit(main())
