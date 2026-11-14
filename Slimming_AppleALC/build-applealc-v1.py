
#!/usr/bin/env python3

import os
import re
import sys
import plistlib
import shutil
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parent
OUTPUT = ROOT.parent / "AppleALC-Slimmed"
RESOURCES = ROOT / "Resources"

def abort(message):
    print(f"\n[ERROR] {message}")
    sys.exit(1)


def load_plist(path):
    with open(path, "rb") as f:
        return plistlib.load(f)


def save_plist(path, data):
    with open(path, "wb") as f:
        plistlib.dump(data, f, fmt=plistlib.FMT_XML, sort_keys=False)


def find_codec_folders():
    folders = []

    for folder in RESOURCES.iterdir():
        if not folder.is_dir():
            continue

        layouts = list(folder.glob("layout*.xml"))

        if layouts and (folder / "info.plist").exists():
            folders.append(folder)

    return sorted(folders, key=lambda p: p.name.lower())


def select_codec():
    codecs = find_codec_folders()

    if not codecs:
        abort("No codec folders found.")

    print("\nAvailable codecs:\n")

    for index, codec in enumerate(codecs, 1):
        print(f"  {index:2}. {codec.name}")

    while True:
        value = input("\nEnter CODEC: ").strip()

        matches = [c for c in codecs if c.name.lower() == value.lower()]

        if matches:
            return matches[0]

        print("Invalid codec. Enter one of the listed names.")


def select_layout(codec):
    layouts = sorted(
        codec.glob("layout*.xml"),
        key=lambda p: int(re.search(r"\d+", p.stem).group())
    )

    if not layouts:
        abort(f"No layouts found for {codec.name}.")

    print(f"\nAvailable layouts for {codec.name}:\n")

    for layout in layouts:
        print(f"  {layout.stem.replace('layout', '')}")

    while True:
        value = input("\nEnter Layout ID: ").strip()

        if not value.isdigit():
            print("Please enter a numeric Layout ID.")
            continue

        layout = codec / f"layout{value}.xml"

        if layout.exists():
            return int(value), layout

        print("Layout not found.")

def read_layout_info(layout):
    raw = layout.read_bytes()

    # AppleALC layout files contain a bare plist dictionary.
    wrapped = (
        b'<?xml version="1.0" encoding="UTF-8"?>'
        b'<plist version="1.0">'
        + raw +
        b'</plist>'
    )

    data = plistlib.loads(wrapped)

    path_refs = data.get("PathMapRef", [])

    if not path_refs:
        abort("PathMapRef is missing or empty.")

    codec_ids = path_refs[0].get("CodecID", [])
    platform_id = path_refs[0].get("PathMapID")

    if not codec_ids or platform_id is None:
        abort("Could not resolve CodecID or PathMapID.")

    return codec_ids[0], platform_id


def find_files_dictionary(data):
    files = data.get("Files")

    if not isinstance(files, dict):
        abort("Unexpected codec info.plist structure: Files dictionary missing.")

    if not isinstance(files.get("Layouts"), list):
        abort("Layouts array missing from codec info.plist.")

    if not isinstance(files.get("Platforms"), list):
        abort("Platforms array missing from codec info.plist.")

    return files


def slim_codec(codec, layout_id, layout):
    codec_id, platform_id = read_layout_info(layout)

    print(f"\nCodecID:   {codec_id}")
    print(f"LayoutID:  {layout_id}")
    print(f"PathMapID: {platform_id}")

    info_path = codec / "info.plist"
    info = load_plist(info_path)
    files = find_files_dictionary(info)

    def find_entry(entries, identifier):
        for entry in entries:
            if str(entry.get("Id")) == str(identifier):
                return entry
        return None

    layout_entry = find_entry(files["Layouts"], layout_id)

    if not layout_entry:
        abort("Selected layout is not registered in codec info.plist.")

    platform_entry = find_entry(files["Platforms"], platform_id)

    if not platform_entry:
        abort(f"Platform resource {platform_id} not registered.")

    layout_path = layout_entry.get("Path")
    platform_path = platform_entry.get("Path")

    if not layout_path or not platform_path:
        abort("Missing resource paths in codec info.plist.")

    required_files = {
        layout_path.removesuffix(".zlib"),
        platform_path.removesuffix(".zlib")
    }

    print("\nRequired resources:")
    for name in sorted(required_files):
        print(f"  {name}")

    # Remove unused layout and platform XML files.
    for pattern in ("layout*.xml", "Platforms*.xml"):
        for file in codec.glob(pattern):
            if file.name not in required_files:
                file.unlink()

    # Keep only the selected layout and platform references.
    files["Layouts"] = [layout_entry]
    files["Platforms"] = [platform_entry]

    save_plist(info_path, info)

    return codec_id


def slim_other_codecs(selected):
    for folder in find_codec_folders():
        if folder.name != selected.name:
            shutil.rmtree(folder)
            print(f"Removed codec: {folder.name}")


def find_pinconfig():
    candidates = [
        OUTPUT / "PinConfigs.kext" / "Contents" / "Info.plist",
        OUTPUT / "Resources" / "PinConfigs.kext" / "Contents" / "Info.plist",
        OUTPUT / "PinConfig.kext" / "Contents" / "Info.plist",
        OUTPUT / "Resources" / "PinConfig.kext" / "Contents" / "Info.plist"
    ]

    for path in candidates:
        if path.exists():
            return path

    abort("Could not locate PinConfig.kext Info.plist.")


def slim_pinconfig(layout_id, codec_id):
    path = find_pinconfig()
    data = load_plist(path)

    try:
        personalities = data["IOKitPersonalities"]
        personality = personalities["as.vit9696.AppleALC"]
        entries = personality["HDAConfigDefault"]
    except (KeyError, TypeError):
        abort("Unexpected PinConfig plist structure.")

    original_count = len(entries)

    kept = [
        entry for entry in entries
        if str(entry.get("LayoutID")) == str(layout_id)
        and str(entry.get("CodecID")) == str(codec_id)
    ]

    if not kept:
        abort(
            "No PinConfig entry found matching "
            f"CodecID {codec_id} and LayoutID {layout_id}."
        )

    personality["HDAConfigDefault"] = kept
    save_plist(path, data)

    print(f"\nPinConfig entries: {original_count} -> {len(kept)}")


def prepare():
    if not (ROOT / "AppleALC.xcodeproj").exists():
        abort("Run this script from the AppleALC repository root.")

    if not (ROOT / "MacKernelSDK").exists():
        abort("MacKernelSDK missing. Clone it into the AppleALC root.")

    if not (ROOT / "Lilu.kext").exists():
        abort("Debug Lilu.kext missing from the AppleALC root.")

    if OUTPUT.exists():
        answer = input(
            f"\n{OUTPUT} already exists. Replace it? [y/N]: "
        ).strip().lower()

        if answer != "y":
            abort("Cancelled.")

        shutil.rmtree(OUTPUT)

    print("\nCreating isolated working copy...")

    shutil.copytree(
        ROOT,
        OUTPUT,
        ignore=shutil.ignore_patterns(
            ".git", "build", "DerivedData", "__pycache__"
        )
    )


def build():
    print("\nStarting AppleALC compilation...\n")

    result = subprocess.run(
        [
            "xcodebuild",
            "-project", "AppleALC.xcodeproj",
            "-configuration", "Release",
            "clean", "build"
        ],
        cwd=OUTPUT
    )

    if result.returncode != 0:
        abort("xcodebuild failed.")

    candidates = [
        OUTPUT / "build" / "Release" / "AppleALC.kext",
        OUTPUT / "build" / "Release" / "AppleALC.kext"
    ]

    kext = next((p for p in candidates if p.exists()), None)

    if not kext:
        abort("Build succeeded but AppleALC.kext was not found.")

    size = sum(
        f.stat().st_size
        for f in kext.rglob("*")
        if f.is_file()
    )

    print("\n======================================")
    print("       APPLEALC BUILD SUCCEEDED")
    print("======================================")
    print(f"Codec:     {SELECTED.name}")
    print(f"Layout:    {LAYOUT_ID}")
    print(f"Kext:      {kext}")
    print(f"Size:      {size / 1024:.1f} KB")
    print("======================================")


if __name__ == "__main__":
    print("\n======================================")
    print("          APPLEALC SLIM BUILDER")
    print("======================================")

    SELECTED = select_codec()
    LAYOUT_ID, LAYOUT = select_layout(SELECTED)

    print("\nSelected configuration:")
    print(f"  Codec:  {SELECTED.name}")
    print(f"  Layout: {LAYOUT_ID}")

    confirm = input("\nProceed with slimming and compiling? [Y/n]: ")
    if confirm.strip().lower() in ("n", "no"):
        abort("Cancelled.")

    prepare()

    RESOURCES = OUTPUT / "Resources"

    working_codec = RESOURCES / SELECTED.name

    codec_id = slim_codec(
        working_codec,
        LAYOUT_ID,
        working_codec / LAYOUT.name
    )

    slim_other_codecs(working_codec)
    slim_pinconfig(LAYOUT_ID, codec_id)
    build()
