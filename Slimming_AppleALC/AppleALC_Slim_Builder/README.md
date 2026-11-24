# AppleALC Slim Builder

<img width="650" height="379" alt="Bildschirmfoto 2026-11-14 um 19 45 02" src="https://github.com/user-attachments/assets/d7be802c-7e44-4e21-97d5-f1e289f055c3" />

Build a codec- and layout-specific `AppleALC.kext` from an AppleALC source checkout.

## About

The stock AppleALC kext ships resources for every supported codec and layout, which makes it much larger than most systems need. A typical machine uses exactly one codec with one layout ID.

**AppleALC Slim Builder** is an interactive Python script that:

1. Lets you pick a codec, either by **searching** (codec name **or** layout/platform comment) or by listing all codecs.
2. Shows the available layouts for that codec, each with its description taken from the codec's `info.plist` (`Layouts` comment, falling back to the `Platforms` comment, otherwise `Description unavailable`).
3. Copies the source tree to an isolated working directory, so your original checkout stays untouched.
4. Removes everything that is not needed:
   - all other codec folders
   - all other layouts and platforms of the selected codec (including their entries in the codec's `info.plist`)
   - all PinConfig entries that do not match the selected CodecID and LayoutID
5. Builds the slimmed kext with `xcodebuild` (Release) and saves it as `Builds/AppleALC-<codec>-layout<id>.kext`.

> [!NOTE]
>
> Not every Layout-ID has a corresponding `LayoutXX.xml`. Some configurations reference a PathMap defined in a platform file using a different ID.
>
> **Example:** ALC892 Layout-ID 98 uses `Platforms98.xml`, which defines PathMap 5. `Layout5.xml` contains the corresponding `PathMapRef` entry. Both resources must be retained when slimming AppleALC for this configuration.
>
> In such cases, you must slim the kext manually. If you are using a Layout-ID that is missing from the script output but is known to work, this limitation may apply.

## Requirements

- **macOS**
- **Python 3.9 or newer** (no third-party packages needed)
- **Xcode** (including the command line tools, so `xcodebuild` works)
- **MacKernelSDK**, cloned into the AppleALC root
- **AppleALC source**, from the [acidanthera/AppleALC](https://github.com/acidanthera/AppleALC) repository (git clone or source ZIP)
- **Lilu.kext (Debug version)**, placed in the AppleALC root

## Setup

Your AppleALC root should look like this:

```
AppleALC/
├── AppleALC.xcodeproj
├── MacKernelSDK/          <- required
├── Lilu.kext              <- required (Debug version)
├── Resources/
├── build-applealc.py      <- this script
└── ...
```

1. **Get the AppleALC source**

   ```sh
   git clone https://github.com/acidanthera/AppleALC.git
   cd AppleALC
   ```

   Alternatively, download the source ZIP and extract it. Version info is then read from the Xcode project instead of Git.

2. **Add MacKernelSDK**

   ```sh
   git clone https://github.com/acidanthera/MacKernelSDK.git
   ```

3. **Add Lilu.kext (Debug)**

   Download the **DEBUG** build from the [Lilu releases](https://github.com/acidanthera/Lilu/releases), extract it, and copy `Lilu.kext` into the AppleALC root.

4. **Copy the script** `build-applealc.py` into the AppleALC root.

## Usage

Run the script from the AppleALC root:

```sh
python3 build-applealc.py
```

Then follow the prompts:

1. **Select a codec**
   - `[1] Search codecs`: enter part of a codec name or any word from a layout/platform comment, for example `ALC887` or `thinkpad`. Several words are allowed and all of them must match. Matches found via a comment show that comment next to the codec.
   - `[2] List all codecs`
   - Typing an exact codec name selects it directly.
2. **Enter the Layout ID** from the list shown (or `b` to go back and choose another codec).
3. **Choose whether to keep the slimmed working directory** after the build.
4. **Confirm** to start slimming and compiling.

When finished, the script prints a summary including the kext size.

## Output

| Item | Location |
| --- | --- |
| Finished kext | `Builds/AppleALC-<codec>-layout<id>.kext` (inside the AppleALC root) |
| Working copy | `../AppleALC-Slimmed` (next to the AppleALC folder; removed afterwards unless you chose to keep it) |

If either location already exists, the script asks before replacing it.

## Using the result

Use the built kext in place of the regular `AppleALC.kext`. Keep Lilu loading before it, and make sure your `layout-id` (or `alcid` boot argument) matches the layout you built. The slimmed kext contains only that one layout.

## Notes

- The script must be run from the AppleALC root. It aborts if `AppleALC.xcodeproj`, `MacKernelSDK`, or `Lilu.kext` is missing.
- Your source checkout is never modified; all slimming happens in the copy.
- Only the slimmed version is compiled.
