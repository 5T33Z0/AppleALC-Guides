# How to create/modify a Layout-ID for AppleALC

## XII. Compiling the AppleALC.kext
Now that we finally prepared all the required files, we can finally compile the kext.

- Open Terminal
- Type `cd`, hit space, drag your AppleALC Folder into the Terminal window and hit enter. This is now your working directory.
- Enter `xcodebuild -configuration Release` and hit Enter. Without the `-configuration Release` flag, some Xcode versions default to a Debug build.
- Once the kext is compiled, there should be as prompt: "BUILD SUCCEEDED". 
- The kext will present in `/AppleALC/build/Release`.

## XIII. Testing and Troubleshooting
### Testing the new Layout
- Add your newly compiled AppleALC.kext to your `EFI/OC/Kexts` folder
- Open the config.plist and change the Layout-ID to the one you chose for your Layout-ID
- Save the config and reboot
- Check if sound is working (Internal, Inputs, Outputs, Headphones)
- If it's working: congrats!

> [!NOTE]
>
> For testing verbs and `WakeConfigData` you can use `alc-verb` (it's in the Build folder) and Terminal to inject verbs into the Codec during runtime. This way, you don't have to edit the PinConfig, the .xml files and recompile the kext every time you want to test something. But I have yet to figure out how it works. Requires boot-arg `alcverbs=1` or `alc-verbs` device property for the Codec to be present in the `config.plist`.

### Troubleshooting
Follow the [AppleALC Troubleshooting Guide](https://github.com/dortania/OpenCore-Install-Guide/blob/e08ee8ebe6fa030393c153b055225f721edafab2/post-install/audio.md#troubleshooting) by Dortania
- Check and adjust/correct:
	- Pin-Config (maybe calculate it manually)
	- PathMap inside of PlatformsXX.xml
	- LayoutXX.xml 
	- Info.plist &rarr; check if you added your layoutXX.xml and PlatformsXX.xml 
	- Take notes. You can use my [Template](https://github.com/5T33Z0/OC-Little-Translated/blob/main/L_ALC_Layout-ID/Testing_Notes.md) for this
- Re-compile the kext, replace it in the EFI, reboot, test, repeat.
- Ask for help on a Forum.

## XIV. Adding your Layout-ID to the AppleALC Repo
Once your custom Layout-ID is working, you can submit it to the AppleALC GitHub repo via Pull Request. Otherwise you would lose your custom made routing every time you update the AppleALC.kext since this overwrites the info.plist and the .xml support files.

In order to add your Layout-ID to AppleALC's database, you have to do the following:

- Create a fork of the AppleALC Repo
- Include the changes you made into the files 4 files mentioned in the "[Files we have to work on](https://github.com/5T33Z0/OC-Little-Translated/tree/main/L_ALC_Layout-ID#files-we-have-to-work-on)" section. Read the official [Instructions](https://github.com/acidanthera/AppleALC/wiki/Adding-codec-support) for more details. 
- Push the changes you made to your Fork
- Create a pull request on GiHub
- :warning: Make sure it has no conflicts, otherwise it will be rejected.
- Wait for approval

Once your Layout is approved it will be part of the main AppleALC repo and you can update AppleALC without having to compile your own version every time the source code is updated. 

## CREDITS and RESOURCES
- **Guides**:
	- MacPeet for [Anleitung patch AppleHDA](https://www.root86.com/blog/40/entry-51-guide-anleitung-patch-applehda-bedingt-auch-f%C3%BCr-codec-erstellung-in-applealc/) (German)
	- EMlyDinEsH for [Complete Apple HDA Patching Guide](https://osxlatitude.com/forums/topic/1946-complete-applehda-patching-guide/)
	- F0x1c for [AppleALC_Instructions](https://github.com/F0x1c/AppleALC_Instructions)
	- The King for [[How To] Patch AppleHDA - Knowledge Base, Guide for how to fix/use original AppleHDA](http://web.archive.org/web/20150105004602/http://www.projectosx.com/forum/index.php?showtopic=465&st=0)
	- Master Chief for [[How To] PinConfig for Linux users](https://www.insanelymac.com/forum/topic/149128-how-to-pinconfig-for-linux-users-%EF%BF%BD-realtek-alc883-example/)
	- Daliansky for [AppleALC Guide](https://blog-daliansky-net.translate.goog/Use-AppleALC-sound-card-to-drive-the-correct-posture-of-AppleHDA.html?_x_tr_sl=auto&_x_tr_tl=en&_x_tr_hl=de&_x_tr_pto=wapp)
	- Applelife.ru for [GetDumpXML – Auto-build Platforms.xml](https://applelife-ru.translate.goog/threads/getdumpxml-applehda-zvuk-avtomaticheskoe-postroenie-fajla-platforms-xml.2942828/?_x_tr_sl=ru&_x_tr_tl=en&_x_tr_hl=de&_x_tr_pto=wapp)
	- Daliansky for [Using VoodooHDA for finding valid Nodes](https://blog-daliansky-net.translate.goog/With-VoodooHDA-comes-getdump-find-valid-nodes-and-paths.html?_x_tr_sl=auto&_x_tr_tl=en&_x_tr_hl=de&_x_tr_pto=wapp)
	- fewtarius for [Fixing Jack Sense and EAPD](https://gist.github.com/fewtarius/f691d97513c4f7e527cb41f44c069548)
- **About Intel High Definition Audio**:
	- Intel for [HDA Specs](https://www.intel.com/content/www/us/en/standards/high-definition-audio-specification.html), esp. Chapter 7: "Codec Features and Requirements".
 	- HaC Mini Hackintosh for additional info about the [HDA Codec and Codec-Graph](https://osy.gitbook.io/hac-mini-guide/details/hda-fix#hda-codec)
 	- Daliansky for [List of HDA Verb Parameters](https://blog-daliansky-net.translate.goog/hda-verb-parameter-detail-table.html?_x_tr_sl=auto&_x_tr_tl=en&_x_tr_hl=de&_x_tr_pto=wapp)
- **Tools**:
	- Apple for [XCode](https://developer.apple.com/xcode/)
	- Acidanthera for [AppleALC](https://github.com/acidanthera/AppleALC), [Lilu](https://github.com/acidanthera/Lilu) and [MacKernelSDK](https://github.com/acidanthera/MacKernelSDK)
	- cmatsuoka for [codecgraph](https://github.com/cmatsuoka/codecgraph)
	- Core-i99 for the Python 3 Port of [Codec-Graph](https://github.com/Core-i99/Codec-Graph)
	- Headkaze for [Hackintool](https://github.com/headkaze/Hackintool) and porting [PinConfigurator](https://github.com/headkaze/PinConfigurator) to 64 bit 
	- Pixelglow for [graphviz](http://www.pixelglow.com/graphviz/)
- **Codec-specific Fixes**:
	- hackintosh-stuff for [ComboJack](https://github.com/hackintosh-stuff/ComboJack) – Fixes issues with ALC255/256
	- jief666 for [ALC298 PlugFix](https://github.com/jief666/ALC298PlugFix) – Fixes issues with ALC298
	- tctien342 for [Combojack for Dell Series](https://github.com/tctien342/ComboJack) – Fixes issues with ALC255/256, ALC295 and ALC298 on Dell Laptops
- **Other**:
	- [Mermaid](https://mermaid-js.github.io/mermaid/#/README) script for creating flowcharts and diagrams in Markdown
	- Core-i99 for PinConfigurator tips
	- Hardwaresecrets – [How on-board Audio works](https://hardwaresecrets.com/how-on-board-audio-works/)
