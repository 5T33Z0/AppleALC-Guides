# Using `alc-verb` for Audio Troubleshooting

`alc-verb` is a command-line tool that ships with the **AppleALC source code**. It lets you send HDA (High Definition Audio) verb commands directly to your audio codec at runtime, without recompiling the kext or rebooting. This makes it invaluable for testing verb sequences and pin control configurations before committing them to a layout.

> [!NOTE]
>
> `alc-verb` is not included in the AppleALC release `.zip`. It is compiled alongside the kext when you build AppleALC from source in Xcode. The binary ends up in `AppleALC/build/Release/` — refer to [Section XII of the main guide](README.md#xii-compiling-the-applealckext) for build instructions.

---

## Prerequisites

### 1. AppleALC and Lilu

`AppleALC.kext` and `Lilu.kext` must be present, enabled in `config.plist`, and actually loading. To verify, run:

```bash
kextstat | grep -v com.apple
```

This lists all currently loaded kexts that were injected via OpenCore (i.e. everything that isn't Apple's own kexts). AppleALC and Lilu should both appear in the output. If either is missing, it isn't loaded — check your `config.plist` and EFI kext folder before proceeding.

> [!IMPORTANT]
>
> Remove any conflicting kexts — **VoodooHDA** in particular will prevent AppleALC from working.

### 2. Enable verb support

`alc-verb` requires verb injection to be explicitly enabled. There are two ways to do this:

**Option A — boot argument** (simpler, good for testing):

Add `alcverbs=1` to your boot arguments in `config.plist`:

```xml
<key>boot-args</key>
<string>alcverbs=1 alcid=XX</string>
```

**Option B — DeviceProperties** (cleaner for permanent use):

Add the property to your HDEF device path (e.g. `PciRoot(0x0)/Pci(0x1f,0x3)`):

```xml
<key>PciRoot(0x0)/Pci(0x1f,0x3)</key>
<dict>
    <key>alc-verbs</key>
    <integer>1</integer>
</dict>
```

### 3. Have your codec dump ready

You need to know the Node IDs (NIDs) relevant to the audio path you are troubleshooting. These come from your `codec_dump.txt` or `codec_dump_dec.txt` — refer to [Section II of the main guide](README.md#ii-preparations) for how to obtain them. For each node you plan to target, note:

- Its NID (in hex, e.g. `0x19`)
- Its Amp-In/Amp-Out capabilities
- Its Pin Control settings (`Pin-ctls` line in the dump)

---

## How `alc-verb` works

Each command targets a single codec node and consists of three parts:

```bash
alc-verb <NID> <verb> <parameter>
```

| Field | Description | Example |
|---|---|---|
| `NID` | Node ID in hex | `0x19` |
| `verb` | The HDA verb command | `0x707` (Set Pin Control) |
| `parameter` | The value to write | `0x20` (enable output) |

### Common verbs

| Verb | Function |
|---|---|
| `0x707` | Set Pin Widget Control (enable/disable pin, set direction) |
| `0x708` | Set Unsolicited Response (jack detection) |
| `0xF07` | Get Pin Widget Control (read current state) |
| `0x500` | Set Coefficient Index (used to address processing coefficients) |
| `0x4XX` | Set Processing Coefficient (write coefficient value; `XX` = index) |

For the full verb reference, see Chapter 7.3.3 of the [Intel HDA Specification](https://www.intel.com/content/www/us/en/standards/high-definition-audio-specification.html) and [Daliansky's HDA Verb Parameter Table](https://blog-daliansky-net.translate.goog/hda-verb-parameter-detail-table.html?_x_tr_sl=auto&_x_tr_tl=en&_x_tr_hl=de&_x_tr_pto=wapp).

### Command-line options

| Option | Description |
|---|---|
| `-d <int>` | Codec index (default: 0; use if you have multiple codecs) |
| `-l` | List all known verbs |
| `-L` | List verbs one per line |
| `-q` | Quiet mode — only print errors |

---

## Typical workflow

### Step 1 — Read the current state of a node

Before sending commands, read what the codec currently has configured for a node:

```bash
alc-verb 0x19 0xF07 0x00
```

This reads the Pin Widget Control register of node `0x19`. The returned value tells you whether the pin is currently enabled and in which direction (input/output).

### Step 2 — Test a configuration

Send a verb to change the node's behavior. For example, to enable node `0x19` as an output:

```bash
alc-verb 0x19 0x707 0x40
```

Test the result immediately in macOS Sound settings or with a tone generator app — changes take effect instantly without a reboot.

### Step 3 — Iterate

Keep adjusting verb parameters and testing until the audio path behaves as expected. Document every command that produces a useful result — you'll need the exact values later.

### Step 4 — Make changes permanent

Once you have a working verb sequence, you have two options:

**Option A — Integrate into your layout** (recommended):

Add the verbs as `WakeConfigData` in the `info.plist` inside `PinConfigs.kext`. This is the proper AppleALC way and survives reboots natively.

**Option B — ALCPlugFix-Swift**:

For codecs with combo jacks (typically ALC255/256/295/298) where verbs need to be re-sent on headphone plug/unplug events, use [ALCPlugFix-Swift](https://github.com/black-dragon74/ALCPlugFix-Swift). It installs a daemon that fires verb sequences on jack sense events — something `WakeConfigData` alone cannot handle.

---

## Example: Fixing a headset microphone (ALC255, Layout-ID 66)

This is a real example of using `alc-verb` to diagnose and fix a non-working headset mic on an ALC255 codec.

The problem: plugging a headset into the combo jack produces no microphone input.

First, read the codec dump to identify the relevant nodes. On ALC255, the combo jack processing coefficients are controlled via node `0x20`, and the headset detection node is `0x57`.

Test the following sequence:

```bash
alc-verb 0x20 0x500 0x45   # Set coefficient index 0x45
alc-verb 0x20 0x4d4 0x89   # Write coefficient: enable headset mode
alc-verb 0x20 0x500 0x1b   # Set coefficient index 0x1b
alc-verb 0x20 0x40c 0x2b   # Write coefficient: configure mic bias
alc-verb 0x57 0x500 0x03   # Set coefficient index 0x03 on node 0x57
alc-verb 0x57 0x48e 0xa6   # Write coefficient: enable headset detection
```

Check the microphone in macOS Sound settings → Input. If it appears and produces signal, the sequence is correct — add it to `WakeConfigData` in your layout's `info.plist` entry inside `PinConfigs.kext`.

---

## Dumping processing coefficients for comparison

Some codec issues (particularly on laptops with combo jacks) require comparing the codec's internal processing coefficients between a working state and a broken one. AppleALC includes a `dump_coeff.sh` script in the source repo under `AppleALC/Scripts/` for this purpose.

Usage:

```bash
./dump_coeff.sh <codec_index> <node_id> <num_coefficients>
```

Example for node `0x20` on codec 0, reading 80 coefficients:

```bash
./dump_coeff.sh 0 0x20 80
```

Run this on a working system (e.g. under Linux or Windows) and again on the broken macOS setup, then diff the output to identify which coefficients differ. Those differences point to the verb commands you need to send.

---

## Troubleshooting

### Commands have no effect

- Confirm `alcverbs=1` is set and that AppleALC and Lilu are actually loading (check the log command from Prerequisites above).
- Make sure you are running the `alc-verb` binary that matches your compiled AppleALC version.
- Check that no conflicting kext (VoodooHDA, old CodecCommander) is loaded.

### Debug logging

AppleALC and Lilu support debug boot arguments (`-alcdbg`, `-liludbg`), but **these only produce output with the debug builds of the kexts** — the release binaries ignore these flags entirely. To get debug output, you need to compile AppleALC and Lilu in Debug configuration and use those builds alongside the flags.

### macOS 26 and AppleHDA

From macOS 26 Developer Preview 2 onward, Apple dropped `AppleHDA.kext`. AppleALC functioning on macOS 26 may require additional steps — check the [AppleALC GitHub releases](https://github.com/acidanthera/AppleALC/releases) page for the latest compatibility updates.

---

## Resources

- [AppleALC GitHub](https://github.com/acidanthera/AppleALC) — source, releases, wiki
- [Intel HDA Specification](https://www.intel.com/content/www/us/en/standards/high-definition-audio-specification.html) — Chapter 7.3.3 for verb reference
- [Daliansky's HDA Verb Parameter Table](https://blog-daliansky-net.translate.goog/hda-verb-parameter-detail-table.html?_x_tr_sl=auto&_x_tr_tl=en&_x_tr_hl=de&_x_tr_pto=wapp)
- [Dumping Processing Coefficients](https://github.com/acidanthera/AppleALC/wiki/Dumping-processing-coefficients) — AppleALC wiki
- [ALCPlugFix-Swift](https://github.com/black-dragon74/ALCPlugFix-Swift) — for combo jack verb automation
- [Fixing Jack Sense and EAPD](https://gist.github.com/fewtarius/f691d97513c4f7e527cb41f44c069548) — fewtarius
