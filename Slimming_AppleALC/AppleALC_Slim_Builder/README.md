# AppleALC Slim Builder

<img width="599" height="357" alt="alcslimmer" src="https://github.com/user-attachments/assets/c2c18f3f-11f7-483e-b126-30a8ef0eb9ff" />

Build a codec- and layout-specific `AppleALC.kext` from an AppleALC source checkout.

## About

The stock AppleALC kext ships resources for every supported codec and layout, which makes it much larger than most systems need. A typical machine uses exactly one codec with one layout ID.

**AppleALC Slim Builder** is an interactive Python script that:

1. Lets you pick a codec, either by **searching** (codec name **or** layout/platform comment) or by listing all codecs.
2. Shows the available layouts for that codec, each with its description taken from the codec's `info.plist` (`Layouts` comment, falling back to the `Platforms` comment, otherwise `Description unavailable`). The list comes from the layouts registered in `info.plist`, so layout IDs without their own `layoutN.xml` are included too (see Notes).
3. Copies the source tree to an isolated working directory, so your original checkout stays untouched.
4. Removes everything that is not needed:
   - all other codec folders
   - all other layouts and platforms of the selected codec (including their entries in the codec's `info.plist`)
   - all PinConfig entries that do not match the selected CodecID and LayoutID
5. Builds the slimmed kext with `xcodebuild` (Release) and saves it as `Builds/AppleALC-<codec>-layout<id>.kext`.

## Requirements

- **macOS**
- **Python 3.9 or newer** (no third-party packages needed)
- **Xcode** (including the command line tools, so `xcodebuild` works)
- **git** and **curl** (both included with macOS and the Xcode command line tools), used to download the dependencies
- **AppleALC source**, from the [acidanthera/AppleALC](https://github.com/acidanthera/AppleALC) repository (git clone or source ZIP)
- **MacKernelSDK** and **Lilu.kext (Debug version)**: both are **downloaded automatically** by the script if they are missing (see below)

## Setup

1. **Download AppleALC**

   ```sh
   git clone https://github.com/acidanthera/AppleALC.git ~/Downloads/AppleALC
   ```

   Alternatively, download the source ZIP and extract it to your Downloads folder (it unpacks to `AppleALC-master`). Version info is then read from the Xcode project instead of Git.

2. **Run the script**

   Copy `build-applealc.py` into the AppleALC folder and start it from there:

   ```sh
   cd ~/Downloads/AppleALC
   python3 build-applealc.py
   ```

> [!NOTE]
> MacKernelSDK and Lilu need no manual setup. On startup the script downloads whatever is missing:
>
> - **MacKernelSDK**: cloned from [acidanthera/MacKernelSDK](https://github.com/acidanthera/MacKernelSDK) into `MacKernelSDK/`.
> - **Lilu.kext**: the newest **Debug** build from the [Dortania build repo](https://dortania.github.io/builds/?product=Lilu&viewall=true) is downloaded, checked against its SHA-256 hash, and extracted to `Lilu.kext`.
>
> Existing folders are reused as they are. The script does not check whether an existing `Lilu.kext` is a Debug or Release build, so replace it yourself if you need the Debug build. To update either dependency, delete its folder and run the script again.
>
> Afterwards your AppleALC folder looks like this:
>
> ```
> AppleALC/
> ├── AppleALC.xcodeproj
> ├── MacKernelSDK/          <- downloaded by the script if missing
> ├── Lilu.kext              <- downloaded by the script if missing (Debug version)
> ├── Resources/
> ├── build-applealc.py      <- this script
> └── ...
> ```

## Usage

Once the script is running, follow the prompts:

1. **Select a codec**
   - `[1] Search codecs`: enter part of a codec name or any word from a layout/platform comment, for example `ALC887` or `thinkpad`. Several words are allowed and all of them must match. Matches found via a comment show that comment next to the codec.
   - `[2] List all codecs`
   - Typing an exact codec name selects it directly.
2. **Enter the Layout ID** from the list shown (or `b` to go back and choose another codec). If the layout uses a shared resource file, the script says so, e.g. `Layout 98 uses the shared resource layout5.xml.`
3. **Choose whether to keep the slimmed working directory** after the build.
4. **Confirm** to start slimming and compiling.

When finished, the script prints a summary including the kext size.

## Output

| Item | Location |
| --- | --- |
| Finished kext | `Builds/AppleALC-<codec>-layout<id>.kext` (inside the AppleALC root) |
| Working copy | `../AppleALC-Slimmed` (next to the AppleALC folder, e.g. `~/Downloads/AppleALC-Slimmed`; removed afterwards unless you chose to keep it) |

If either location already exists, the script asks before replacing it.

## Using the result

Use the built kext in place of the regular `AppleALC.kext`. Keep Lilu loading before it, and make sure your `layout-id` (or `alcid` boot argument) matches the layout you built. The slimmed kext contains only that one layout.

## Notes

- The script must be run from the AppleALC root. It aborts if `AppleALC.xcodeproj` is missing.
- If `MacKernelSDK` exists but is incomplete, the script aborts and asks you to delete it, so it never overwrites a folder it does not recognize.
- If a download fails or the Lilu checksum does not match, nothing is installed and the script aborts.
- Your source checkout is never modified; all slimming happens in the copy.
- Only the slimmed version is compiled.
- Not every Layout ID has its own `layoutN.xml`. Some IDs reuse another layout's file together with their own platform file. For example, ALC892 layout 98 uses `layout5.xml` and `Platforms98.xml`. The script follows the paths registered in `info.plist` and keeps exactly those files, so no manual slimming is needed for these layouts.
