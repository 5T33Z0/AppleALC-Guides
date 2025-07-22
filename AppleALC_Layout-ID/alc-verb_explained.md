# Using `alc-verb` for Audio Troubleshooting in Hackintosh Systems

This guide explains how to use `alc-verb`, a command-line tool included with **AppleALC**, to test and configure audio routings on Hackintosh systems by sending HDA (High Definition Audio) verb commands to audio codecs. It is designed for advanced users troubleshooting issues like non-working microphones, headphone jacks, or speakers.

## Prerequisites

1. **AppleALC and Lilu Installed**:
   - Ensure **AppleALC.kext** and **Lilu.kext** are installed in your EFI/OC/Kexts partition’s kexts folder and are present and enabled in `config.plist`
   - Verify they are loaded by checking OpenCore logs:
     ```bash
     log show --predicate 'process == "kernel" AND (eventMessage CONTAINS "AppleALC" OR eventMessage CONTAINS "Lilu")' --style syslog --source
     ```

2. **Enable `alc-verb`**:
   - Add the boot argument `alcverbs=1` in your bootloader’s `config.plist`:
     ```xml
     <key>boot-args</key>
     <string>alcverbs=1</string>
     ```
   - Alternatively, set the `alc-verbs` property to a non-zero value in `DeviceProperties` for your HDEF device.

3. **Install `alc-verb`**:
   - Download the latest AppleALC release from [GitHub](https://github.com/acidanthera/AppleALC/releases).
   - Extract the `alc-verb` binary and place it in a directory like `/usr/local/bin/` or make it accessible via:
     ```bash
     export PATH=$(pwd):$PATH
     ```

4. **Identify Your Audio Codec**:
   - Determine your codec (e.g., ALC255, ALC887) using **Hackintool** or by booting into Linux and running:
     ```bash
     cat /proc/asound/card0/codec#0
     ```
   - Note the node IDs (NIDs) for components like microphones, speakers, or headphone jacks.

## Understanding `alc-verb`

`alc-verb` sends HDA verb commands to configure audio codec nodes. Each command consists of:

- **NID**: Node ID (e.g., `0x19` for a headphone jack).
- **Verb**: The command (e.g., `0x707` to set pin control).
- **Parameter**: The configuration value (e.g., `0x20` to enable a pin).

### Syntax

```bash
alc-verb [options] nid verb param
```

- **Options**:
  - `-d <int>`: Specify codec index (usually 0).
  - `-l`: List known verbs and parameters.
  - `-q`: Quiet mode (only print errors).
  - `-L`: List verbs and parameters (one per line).
- **nid**: Node ID (e.g., `0x19`).
- **verb**: HDA verb (e.g., `0x707`).
- **param**: Parameter value (e.g., `0x20`).

## Testing Audio Routings

Use `alc-verb` to test audio routing configurations, such as enabling a microphone or headphone jack.

### Step-by-Step Process

1. **Prepare Your System**:
   - Confirm `alcverbs=1` is set and AppleALC/Lilu are loaded.
   - Remove conflicting kexts like **VoodooHDA** or **CodecCommander**.

2. **Identify Nodes and Verbs**:
   - Boot into Linux (e.g., Ubuntu Live USB) and dump codec info:
     ```bash
     cat /proc/asound/card0/codec#0
     ```
   - Use tools like **PinConfigurator** or **codecverb** to analyze the dump and find node IDs and verbs for your codec.
   - Check the [AppleALC wiki](https://github.com/acidanthera/AppleALC/wiki) for codec-specific verbs.

3. **Test Audio Routings**:
   - Run `alc-verb` commands to configure nodes. For example, to enable a headphone jack (node `0x19`):
     ```bash
     alc-verb 0x19 0x707 0x20
     ```
   - To configure a microphone (e.g., node `0x20` for ALC255):
     ```bash
     alc-verb 0x20 0x500 0x45
     alc-verb 0x20 0x4d4 0x89
     ```
   - Test audio output/input after each command using macOS’s Sound settings or an audio app.

4. **Dump Coefficients for Debugging**:
   - Use the `dump_coeff.sh` script from AppleALC’s GitHub to compare coefficients:
     ```bash
     ./dump_coeff.sh 0 0x20 142
     ```
   - Compare macOS coefficients with a working Linux/Windows setup to identify routing issues.

5. **Make Changes Permanent**:
   - If a routing works, add the verbs to a custom AppleALC layout by editing the codec’s `Info.plist` as explained in the [main guide](https://github.com/5T33Z0/AppleALC-Guides/tree/main/AppleALC_Layout-ID).
   - Alternatively, use **ALCPlugFix-Swift** to automate verb execution on boot or headphone plug-in events.

## Example: Fixing a Headset Microphone (ALC255, Layout-ID 66)

To enable a headset microphone:
```bash
alc-verb 0x20 0x500 0x45
alc-verb 0x20 0x4d4 0x89
alc-verb 0x20 0x500 0x1b
alc-verb 0x20 0x40c 0x2b
alc-verb 0x57 0x500 0x03
alc-verb 0x57 0x48e 0xa6
```
Test the microphone in macOS’s Sound settings. If successful, add these verbs to your AppleALC configuration.

## Troubleshooting

- **No Effect from Commands**:
  - Verify `alcverbs=1` is set and AppleALC/Lilu are loaded.
  - Check for kext conflicts.
  - Use `-alcdbg` and `-liludbg` boot arguments for debug logs.

- **Incorrect Verbs**:
  - Ensure verbs match your codec. Refer to Linux codec dumps or AppleALC’s wiki.
  - Test multiple layout IDs in `alcid=<id>` boot argument.

- **macOS Version Issues**:
  - As of macOS 26 Developer Preview 2, `AppleHDA.kext` is deprecated. Check AppleALC’s GitHub for compatibility updates.

## Additional Resources

- **AppleALC GitHub**: [github.com/acidanthera/AppleALC](https://github.com/acidanthera/AppleALC)
- **AppleALC Wiki**: [github.com/acidanthera/AppleALC/wiki](https://github.com/acidanthera/AppleALC/wiki)
- **Dumping Coefficients**: [Dumping Processing Coefficients](https://github.com/acidanthera/AppleALC/wiki/Dumping-processing-coefficients)
- **Hackintosh Communities**: **tonymacx86**, **InsanelyMac**, **r/hackintosh** on Reddit.

## Notes

- **Codec-Specific**: Verbs are unique to each codec (e.g., ALC255 vs. ALC887). Always verify your codec.
- **Backup**: Save your EFI configuration before testing.
- **Advanced Use**: Creating custom layouts requires XML editing and codec knowledge.

This guide should help you use `alc-verb` to test and fix audio routings. For specific issues or codecs, consult the AppleALC community or provide more details for tailored assistance.

