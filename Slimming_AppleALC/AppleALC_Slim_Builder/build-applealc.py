#!/usr/bin/env python3
"""
AppleALC Slim Builder
Builds a codec/layout-specific AppleALC.kext from an isolated copy
of an AppleALC source checkout.
"""

import hashlib
import json
import plistlib
import re
import shutil
import subprocess
import sys
import tempfile
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent
OUTPUT = ROOT.parent / "AppleALC-Slimmed"
RESOURCES = ROOT / "Resources"
BUILDS = ROOT / "Builds"

SDK_URL = "https://github.com/acidanthera/MacKernelSDK.git"
# Build list of the Dortania build repo (the data behind dortania.github.io/builds)
LILU_BUILDS_URL = "https://raw.githubusercontent.com/dortania/build-repo/builds/config.json"


def abort(message):
    print(f"\n[ERROR] {message}")
    raise SystemExit(1)


def confirm(prompt, default=True):
    suffix = "[Y/n]" if default else "[y/N]"
    answer = input(f"{prompt} {suffix}: ").strip().lower()
    if not answer:
        return default
    return answer in ("y", "yes")


def load_plist(path):
    with open(path, "rb") as f:
        return plistlib.load(f)


def save_plist(path, data):
    with open(path, "wb") as f:
        plistlib.dump(data, f, fmt=plistlib.FMT_XML, sort_keys=False)


def find_codec_folders():
    if not RESOURCES.is_dir():
        abort(f"Resources directory not found: {RESOURCES}")

    folders = []
    for folder in RESOURCES.iterdir():
        if not folder.is_dir():
            continue
        layouts = list(folder.glob("layout*.xml"))
        if layouts and (folder / "info.plist").is_file():
            folders.append(folder)

    return sorted(folders, key=lambda p: p.name.lower())


_files_cache = {}


def codec_files(codec):
    """The Files dictionary of the codec's info.plist (cached, {} if unreadable)."""
    key = str(codec)
    if key not in _files_cache:
        try:
            files = load_plist(codec / "info.plist").get("Files", {})
            _files_cache[key] = files if isinstance(files, dict) else {}
        except Exception:
            _files_cache[key] = {}
    return _files_cache[key]


def layout_ids(codec):
    """Layout IDs as registered in info.plist.

    Not every ID has its own layoutN.xml: some IDs reuse another layout's file
    (e.g. ALC892 layout 98 uses layout5.xml together with Platforms98.xml).
    """
    ids = set()
    for entry in codec_files(codec).get("Layouts", []) or []:
        try:
            ids.add(int(entry["Id"]))
        except (KeyError, TypeError, ValueError):
            continue
    return sorted(ids)


def layout_resource(codec, layout_id):
    """The layout XML file a Layout ID is registered with, or None."""
    for entry in codec_files(codec).get("Layouts", []) or []:
        if isinstance(entry, dict) and str(entry.get("Id")) == str(layout_id):
            path = entry.get("Path")
            if path:
                return codec / path.removesuffix(".zlib")
    return None


_comment_cache = {}


def codec_comments(codec):
    """All Layout and Platform comments of a codec (cached)."""
    if codec.name in _comment_cache:
        return _comment_cache[codec.name]

    comments = []
    files = codec_files(codec)
    for key in ("Layouts", "Platforms"):
        for entry in files.get(key, []) or []:
            comment = entry.get("Comment") if isinstance(entry, dict) else None
            if isinstance(comment, str) and comment.strip():
                comments.append(comment.strip())

    _comment_cache[codec.name] = comments
    return comments


def search_codecs(codecs, term):
    """Match codec names and layout/platform comments.

    Every word of the search term must appear. Returns (codec, hint) pairs,
    where hint is the first matching comment (None for a name match).
    """
    words = term.lower().split()
    results = []
    for codec in codecs:
        name = codec.name.lower()
        if all(w in name for w in words):
            results.append((codec, None))
            continue
        for comment in codec_comments(codec):
            haystack = f"{name} {comment.lower()}"
            if all(w in haystack for w in words):
                results.append((codec, comment))
                break
    return results


def show_codec_matches(matches, hints=None):
    hints = hints or {}
    print(f"\nMatching codecs ({len(matches)}):\n")
    for index, codec in enumerate(matches, 1):
        count = len(layout_ids(codec))
        line = f"  [{index:3}] {codec.name:<12} ({count} layouts)"
        hint = hints.get(codec.name)
        if hint:
            if len(hint) > 70:
                hint = hint[:67] + "..."
            line += f"  <- {hint}"
        print(line)


def select_from_matches(matches, hints=None):
    if not matches:
        print("No matching codecs found.")
        return None

    show_codec_matches(matches, hints)

    while True:
        value = input("\nSelect codec number (or 'b' to go back): ").strip().lower()
        if value in ("b", "back"):
            return None
        if value.isdigit() and 1 <= int(value) <= len(matches):
            return matches[int(value) - 1]
        print("Invalid selection.")


def select_codec():
    codecs = find_codec_folders()
    if not codecs:
        abort("No codec folders found in Resources.")

    while True:
        print("\nCodec selection")
        print("  [1] Search codecs")
        print("  [2] List all codecs")
        print("  [3] Exit")

        choice = input("\nSelect option: ").strip()

        if choice == "1":
            term = input(
                "\nEnter codec name or search term (name or comment): "
            ).strip().lower()
            if not term:
                print("Please enter a search term.")
                continue

            exact = [c for c in codecs if c.name.lower() == term]
            if exact:
                return exact[0]

            results = search_codecs(codecs, term)
            matches = [codec for codec, _ in results]
            hints = {codec.name: hint for codec, hint in results if hint}

            selected = select_from_matches(matches, hints)
            if selected:
                return selected

        elif choice == "2":
            selected = select_from_matches(codecs)
            if selected:
                return selected

        elif choice == "3":
            raise SystemExit(0)

        else:
            print("Invalid option.")


def entry_comment(entries, identifier):
    """Return the Comment of the entry whose Id matches, or None."""
    if not isinstance(entries, list) or identifier is None:
        return None
    for entry in entries:
        if isinstance(entry, dict) and str(entry.get("Id")) == str(identifier):
            comment = entry.get("Comment")
            if isinstance(comment, str) and comment.strip():
                return comment.strip()
    return None


def layout_description(codec, layout_id, files):
    # Primary: Files > Layouts > <entry with this Id> > Comment
    comment = entry_comment(files.get("Layouts"), layout_id)
    if comment:
        return comment

    # Fallback: Files > Platforms > <entry with this layout's Id> > Comment
    comment = entry_comment(files.get("Platforms"), layout_id)
    if comment:
        return comment

    return "Description unavailable"


def select_layout(codec):
    ids = layout_ids(codec)
    if not ids:
        abort(f"No layouts found for {codec.name}.")

    files = codec_files(codec)

    print(f"\nAvailable layouts for {codec.name}:\n")
    for layout_id in ids:
        description = layout_description(codec, layout_id, files)
        print(f"  [{layout_id}] Layout {layout_id} - {description}")

    while True:
        value = input("\nEnter Layout ID ('b' to choose another codec): ").strip().lower()

        if value in ("b", "back"):
            return None, None

        if not value.isdigit():
            print("Enter a numeric Layout ID or 'b' to go back.")
            continue

        layout_id = int(value)
        layout = layout_resource(codec, layout_id)

        if layout is not None and layout.is_file():
            if layout.name.lower() != f"layout{layout_id}.xml":
                print(f"Layout {layout_id} uses the shared resource {layout.name}.")
            return layout_id, layout

        print("Layout not found for this codec.")


def read_layout_info(layout):
    raw = layout.read_bytes()

    # AppleALC layout files contain a bare plist dictionary, not a plist wrapper.
    wrapped = (
        b'<?xml version="1.0" encoding="UTF-8"?>'
        b'<plist version="1.0">'
        + raw
        + b'</plist>'
    )

    try:
        data = plistlib.loads(wrapped)
    except plistlib.InvalidFileException:
        abort(f"Could not parse layout resource: {layout.name}")

    path_refs = data.get("PathMapRef", [])
    if not path_refs:
        abort("PathMapRef is missing or empty in the selected layout.")

    codec_ids = path_refs[0].get("CodecID", [])
    platform_id = path_refs[0].get("PathMapID")

    if not codec_ids or platform_id is None:
        abort("Could not resolve CodecID or PathMapID from the selected layout.")

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
    print(f"PathMapID: {platform_id} (internal)")

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

    # Platforms entries share the Id of their layout. PathMapID inside the
    # layout file is an internal PathMap identifier, not a Platforms entry Id.
    platform_entry = find_entry(files["Platforms"], layout_id)
    if not platform_entry:
        abort(f"Platform resource for layout {layout_id} not registered.")

    layout_path = layout_entry.get("Path")
    platform_path = platform_entry.get("Path")
    if not layout_path or not platform_path:
        abort("Missing resource paths in codec info.plist.")

    required_files = {
        layout_path.removesuffix(".zlib"),
        platform_path.removesuffix(".zlib"),
    }

    print("\nRequired resources:")
    for name in sorted(required_files):
        print(f"  {name}")

    for pattern in ("layout*.xml", "Platforms*.xml"):
        for file in codec.glob(pattern):
            if file.name not in required_files:
                file.unlink()

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
        OUTPUT / "Resources" / "PinConfig.kext" / "Contents" / "Info.plist",
    ]

    for path in candidates:
        if path.is_file():
            return path

    abort("Could not locate PinConfig(s).kext Info.plist.")


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


def source_version():
    version = "Unknown"
    commit = "Not available"

    if (ROOT / ".git").exists():
        try:
            result = subprocess.run(
                ["git", "describe", "--tags", "--always"],
                cwd=ROOT, capture_output=True, text=True, check=True
            )
            version = result.stdout.strip()
            result = subprocess.run(
                ["git", "rev-parse", "--short", "HEAD"],
                cwd=ROOT, capture_output=True, text=True, check=True
            )
            commit = result.stdout.strip()
            return version, commit
        except (subprocess.CalledProcessError, FileNotFoundError):
            pass

    # ZIP/source-archive fallback: read project build settings if present.
    project_file = ROOT / "AppleALC.xcodeproj" / "project.pbxproj"
    if project_file.is_file():
        project_text = project_file.read_text(errors="replace")
        match = re.search(r"MARKETING_VERSION\s*=\s*([^;]+);", project_text)
        if match:
            version = match.group(1).strip().strip('"')
        commit = "Source archive (no Git metadata)"

    return version, commit


def download(url, destination, quiet=False):
    """Download with curl, which uses the macOS system certificate store."""
    if shutil.which("curl") is None:
        abort("curl not found.")
    command = ["curl", "-fL", "--retry", "2", "-sS" if quiet else "-#",
               "-o", str(destination), url]
    if subprocess.run(command).returncode != 0:
        abort(f"Download failed: {url}")


def sha256_of(path):
    digest = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def extract_zip(archive, destination):
    # ditto keeps permissions and metadata exactly as macOS expects them.
    if shutil.which("ditto"):
        result = subprocess.run(["ditto", "-x", "-k", str(archive), str(destination)])
        if result.returncode != 0:
            abort("Could not extract the downloaded archive.")
        return

    with zipfile.ZipFile(archive) as z:
        z.extractall(destination)
        for info in z.infolist():
            mode = info.external_attr >> 16
            if mode:
                (Path(destination) / info.filename).chmod(mode & 0o777)


def sdk_complete(sdk):
    return (sdk / "Headers").is_dir() and (sdk / "Library" / "universal").is_dir()


def ensure_sdk():
    """Clone MacKernelSDK into the AppleALC root if it is missing."""
    sdk = ROOT / "MacKernelSDK"
    if sdk_complete(sdk):
        return

    if sdk.exists() and any(sdk.iterdir()):
        abort(f"{sdk} exists but looks incomplete. "
              "Delete it and run the script again.")

    print(f"\nMacKernelSDK not found. Cloning {SDK_URL} ...")
    try:
        result = subprocess.run(["git", "clone", "--depth", "1", SDK_URL, str(sdk)])
    except FileNotFoundError:
        abort("git not found. Install the Xcode command line tools "
              "(xcode-select --install).")
    if result.returncode != 0:
        abort("Cloning MacKernelSDK failed.")
    if not sdk_complete(sdk):
        abort("MacKernelSDK was cloned but looks incomplete.")


def latest_lilu_debug(config):
    builds = [
        v for v in config.get("Lilu", {}).get("versions", [])
        if v.get("links", {}).get("debug")
    ]
    if not builds:
        abort("No Lilu Debug build found in the Dortania build list.")
    return max(builds, key=lambda v: v.get("date_built", ""))


def ensure_lilu():
    """Download the newest Lilu Debug build from Dortania if Lilu.kext is missing."""
    kext = ROOT / "Lilu.kext"
    if kext.is_dir():
        return
    if kext.exists():
        abort(f"{kext} exists but is not a folder.")

    print("\nLilu.kext not found. Downloading the latest Debug build "
          "from Dortania ...")

    with tempfile.TemporaryDirectory() as tmp:
        tmp = Path(tmp)

        config_file = tmp / "config.json"
        download(LILU_BUILDS_URL, config_file, quiet=True)
        try:
            config = json.loads(config_file.read_text(encoding="utf-8"))
        except ValueError:
            abort("Could not read the Dortania build list.")

        build = latest_lilu_debug(config)
        link = build["links"]["debug"]
        expected = build.get("hashes", {}).get("debug", {}).get("sha256")
        sha = build.get("commit", {}).get("sha", "")[:7]
        print(f"Lilu {build.get('version', '?')} "
              f"(commit {sha}, built {build.get('date_built', '')[:10]})")

        archive = tmp / Path(link).name
        download(link, archive)

        if expected:
            if sha256_of(archive) != expected:
                abort("Checksum mismatch for the downloaded Lilu archive.")
        else:
            print("Warning: no checksum available for this build.")

        extracted = tmp / "extracted"
        extracted.mkdir()
        extract_zip(archive, extracted)

        found = extracted / "Lilu.kext"
        if not found.is_dir():
            abort("The downloaded archive does not contain Lilu.kext.")
        shutil.copytree(found, kext, symlinks=True)

    print(f"Installed {kext}")


def setup_dependencies():
    if not (ROOT / "AppleALC.xcodeproj").exists():
        abort("Run this script from the AppleALC repository root.")
    ensure_sdk()
    ensure_lilu()


def prepare():
    if OUTPUT.exists():
        if not confirm(f"\n{OUTPUT} already exists. Replace it?", default=False):
            abort("Cancelled.")
        shutil.rmtree(OUTPUT)

    print("\nCreating isolated working copy...")
    shutil.copytree(
        ROOT,
        OUTPUT,
        ignore=shutil.ignore_patterns(
            ".git", "build", "Builds", "DerivedData", "__pycache__", ".DS_Store"
        ),
    )


def run_build(label):
    print(f"\n{label}\n")
    result = subprocess.run(
        [
            "xcodebuild",
            "-project", "AppleALC.xcodeproj",
            "-configuration", "Release",
            "clean", "build",
        ],
        cwd=OUTPUT,
    )

    if result.returncode != 0:
        abort(f"{label} failed (xcodebuild exit code {result.returncode}).")

    kext = OUTPUT / "build" / "Release" / "AppleALC.kext"
    if not kext.is_dir():
        abort(f"Build completed but expected kext was not found: {kext}")

    return kext


def directory_size(path):
    return sum(
        file.stat().st_size
        for file in path.rglob("*")
        if file.is_file()
    )


def format_size(size):
    return f"{size / (1024 * 1024):.2f} MB"


def main():
    global RESOURCES

    setup_dependencies()
    version, commit = source_version()

    print("\n==========================================")
    print("           APPLEALC SLIM BUILDER")
    print("==========================================")
    print(f"AppleALC: {version}")
    print(f"Git:      {commit}")

    while True:
        selected = select_codec()
        layout_id, layout = select_layout(selected)
        if layout is not None:
            break

    print("\n==========================================")
    print("             BUILD CONFIGURATION")
    print("==========================================")
    print(f"Codec:       {selected.name}")
    print(f"Layout ID:   {layout_id}")
    print(f"AppleALC:    {version}")
    print(f"Git:         {commit}")

    keep_working = confirm(
        "\nKeep the slimmed working directory after building?", default=True
    )
    if not confirm("\nProceed with slimming and compiling?", default=True):
        abort("Cancelled.")

    final_name = f"AppleALC-{selected.name}-layout{layout_id}.kext"
    final_path = BUILDS / final_name

    if final_path.exists():
        if not confirm(f"\n{final_path} already exists. Replace it?", default=False):
            abort("Cancelled.")

    prepare()
    RESOURCES = OUTPUT / "Resources"

    working_codec = RESOURCES / selected.name
    copied_layout = working_codec / layout.name
    if not copied_layout.is_file():
        abort(f"Selected layout was not copied into the working tree: {copied_layout}")

    codec_id = slim_codec(working_codec, layout_id, copied_layout)
    slim_other_codecs(working_codec)
    slim_pinconfig(layout_id, codec_id)

    slimmed_kext = run_build("Building slimmed AppleALC...")
    slimmed_size = directory_size(slimmed_kext)

    BUILDS.mkdir(parents=True, exist_ok=True)
    if final_path.exists():
        shutil.rmtree(final_path)
    shutil.copytree(slimmed_kext, final_path)

    print("\n==========================================")
    print("          APPLEALC BUILD SUCCESSFUL")
    print("==========================================")
    print(f"Codec:             {selected.name}")
    print(f"Layout:            {layout_id}")
    print(f"AppleALC:          {version}")
    print(f"Kext size:         {format_size(slimmed_size)}")
    print(f"\nOutput:            {final_path}")

    if keep_working:
        print(f"Working directory: {OUTPUT}")
    else:
        shutil.rmtree(OUTPUT)
        print("Working directory: removed")

    print("==========================================")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\nCancelled by user.")
        raise SystemExit(130)
