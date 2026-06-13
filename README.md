![macOS](https://img.shields.io/badge/Supported_macOS:-≤15.x_(Sequoia)-gree.svg) ![Last Update](https://img.shields.io/badge/Last_Update_(yy/mm/dd):-26.06.13-blueviolet.svg)

# AppleALC Guides

![codec_dump txt](https://user-images.githubusercontent.com/76865553/179084535-62f3634b-8e3e-4807-b0c1-bb04c035c5e0.svg)

## About

This repository contains guides for working with the AppleALC source code to get audio working on Wintel machines running macOS. The centerpiece of this repo is a guide for creating/modifying ALC Layout-IDs for the `AppleALC.kext`.

## Included Guides

- [How to create/modify a Layout-ID for AppleALC](/AppleALC_Layout-ID)
- [Using alc-verb for testing audio routes](/AppleALC_Layout-ID/alc-verb_explained.md)
- [AppleALC File Management](/File_Management)
- [Testing Notes Template](/AppleALC_Layout-ID/Testing_Notes.md)
- [Slimming and compiling the AppleALC kext](/Slimming_AppleALC)
- [CODEC Dumps with Schematics](/Codec_Dumps)

## ⚠️ macOS 26 Tahoe — Analog Audio is Broken

As of macOS 26 Tahoe beta 2, **AppleALC no longer works** for analog onboard audio (Realtek, Conexant, and similar codecs). This affects built-in speakers, headphone jacks, and line inputs.

**Why**: Apple removed `AppleHDA.kext` entirely in Tahoe beta 2. Since all Intel Macs still supported by Tahoe use a T2 chip to handle audio — and therefore never needed `AppleHDA` — Apple dropped it. Hackintosh systems don't have a T2 chip, so the driver layer that AppleALC depends on is simply gone.

**What still works**: Digital audio via HDMI or DisplayPort outputs is unaffected, as it relies on different kexts. 

**Workarounds**:

- [**VoodooHDA-Tahoe**](https://github.com/chris1111/VoodooHDA-Tahoe) — a drop-in replacement that doesn't depend on `AppleHDA`. Audio quality is generally lower than AppleALC, but it works. For additional info check Dortanias's [Notes about macOS Tahoe](https://dortania.github.io/OpenCore-Install-Guide/extras/tahoe.html).
- **OCLP root patching** — reinstates `AppleHDA.kext` and its associated dylib via root volume patches, restoring full AppleALC functionality. Requires lowered SIP and an OCLP-based patcher. See [Audio on macOS Tahoe for Hackintosh systems](https://github.com/5T33Z0/OCLP4Hackintosh/blob/main/Enable_Features/Audio_Tahoe.md) for details.

## Credits and Resources
&rarr; see respective sections for details.
