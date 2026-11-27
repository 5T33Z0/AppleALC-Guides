# Alternative Kexts

Kext | CODEC | Additional Info
--- |--- |---
| [**SimpleHDA**](https://github.com/laobamac/SimpleHDA) | - | Restores the native AppleHDA stack in macOS Tahoe without root patching, allowing AppleALC to use existing audio configurations. |
[**Cirrus Audio Fixup**](https://github.com/hoaug-tran/CirrusAudioFixup) | [Cirrus Logic CS35L41](https://www.alldatasheet.com/datasheet-pdf/view/1245321/CIRRUS/CS35L41.html) | Experimental support for laptops with CS35L41 smart amplifiers. Initializes the amplifier, loads DSP firmware, and enables internal speakers with volume control and sleep/wake support.
| [**AMDMicrophone**](https://github.com/qhuyduong/AMDMicrophone) | AMD Audio Co-Processor (ACP) | Enables digital microphone input on compatible AMD laptops using the Audio Co-Processor (ACP). Primarily targets Renoir-based systems. Requires installation in `/Library/Extensions` and reduced SIP security; AppleALC is still needed for audio output. |
| [**TGLDmic**](https://github.com/labrouss/TGLDmic) | DMIC | Enables Internal digital microphones (DMIC) of Intel Tiger Lake and Comet Lake / Cannon Lake laptops via the Intel Smart Sound DSP (SOF). AppleALC is still needed for audio output.