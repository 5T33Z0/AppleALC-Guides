# How to create/modify a Layout-ID for AppleALC

## I. Summary
### About
This is my attempt to provide an up-to-date guide for creating/modifying Layout-IDs for the AppleALC kext to make audio work on a Hackintosh in 2022 (and beyond). It covers the following topics:

- Installing and configuring the necessary tools
- Creating a Codec dump in Linux
- Converting it to visualize the Codec schematic and audio routing
- Creating a `PinConfig`, `Layout.xml` and `Platforms.xml` files
- Integrating the data into the AppleALC Source Code 
- Compiling the `AppleALC.kext`
- Successfully adding the newly created Layout-ID to the AppleALC repo

### Who this guide is for
This guide is for advanced users who want to create a new Layout-ID (based on an existing one) for their Audio Codec for different reasons. Maybe the one in use was created for a different system/mainboard and causes issues or they want to add inputs and outputs missing from the current Layout-ID in use. This is usually the case when using Laptops with an additional Docking Stations where the Audio Jacks of the dock are not included in the Layout-ID so they won't work in macOS out of the box.

<details>
<summary><strong>Why another guide?</strong> (click to reveal)</summary>

### Why another guide?
Although the AppleALC kext comes with about 600 pre-configured Layout-IDs for more than 100 Audio Codecs, the process of *creating* or *modifying* a Layout-ID and integrating the data into the source code for compiling the kext is not documented on the AppleALC repo.

The handful of guides I could find stem from an era before AppleALC even existed, when patching AppleHDA was still a thing. Most of them are either outdated (I had to use Wayback Machine for some), over-complicated or only parts of them are applicable today. And most importantly: ***none*** of them actually explain how to integrate the data into the AppleALC source code to compile the kext!

The most convincing guide I did find is written in German by MacPeet. He has created over 50 (!) Layout-IDs for AppleALC over the years. It's from 2015 so it predates AppleALC as well. Although not all of its instructions are applicable today, his guide introduced a new, partly automated workflow, using tools to visualize the Codec dump and scripts to extract required data from it which previously had to be extracted manually.

My guide is an adaptation of MacPeet's work but updates and enhances it, where possible. It introduces new tools and workflows and utilizes all the nice features markdown has to offer to present the instruction in the best way possible, such as: headings, syntax highlighting, tables and mermaid integration for flowcharts, etc.

So all in all, there is a justification for having new guide for this to enable and empower users to create their own ALC Layout-IDs if they have to.</details>

### Are you *sure*, you want to do this?
From a user's perspective, making audio work in hackintosh is a no-brainer: add AppleALC to the kext folder of your Boot Manager, enter the correct ALC Layout-ID to the config and reboot. And voilà: Sound! But once you are on the other end, trying to actually *create* your own ALC Layout-ID it becomes a completely different story. Creating Audio Layouts for AppleALC is by far the most tedious, complex and frustrating undertaking in all of Hackintoshland. It's almost a given that your Layout-ID won't work the first time around – Kernel Panics included. So, are you sure you still *want* to do this?

### 💡 Tips
- Click on the little Header icon next to `README.md` to navigate in the document quickly
- [Backup files you change](https://github.com/5T33Z0/AppleALC-Guides/tree/main/File_Management) in the Source Code and document configuration changed! Otherwise you will completely lose track of PinConfig and PathMap combinations you have tried already! I prepared a [Template for Note taking](https://github.com/5T33Z0/AppleALC-Guides/blob/main/AppleALC_Layout-ID/Testing_Notes.md) which might help. You can open it in a Markdown Editor such as Macdown or use Visual Studio Code.

## II. Preparations
Creating a Layout-ID for AppleALC is one of the more challenging tasks for "regular" hackintosh users who are not programmers (me included). It's not only challenging and time consuming, it's also confusing and requires a lot of tools and prep work. So let's get it out the way right away.

### Obtaining an Audio CODEC dump in Linux
Unfortunately, Codec dumps obtained with Clover or OpenCore can't be processed by Codec Graph, the main tool for visualizing the data inside of them to create a map of an audio codec's routing. [**Core-i99**](https://github.com/Core-i99/Codec-Graph/) is working on a solution to make dumps obtained with OpenCore processable by Codec Graph. Until then, we still rely on Codec dumps created by Linux, which can be processed without issues.[^1] Therefore, we need to use (a live version of) Linux to create the codec dump without having to actually install Linux. We can use [Ventoy](https://www.ventoy.net/en/index.html) for this. It prepares a USB flash drive which can run almost any ISO directly without having to create a USB installer.

But before you dump the audio CODEC, verify that audio is working in Linux by playing back a YouTube video or something else that produces sound. You can check [here](https://linux-hardware.org/) whether other users have been able to get audio working under Linux on their system ([create a probe]([https://linux-hardware.org/?view=howto](https://linux-hardware.org/?view=howto)) to ensure your system matches the one in the database).

#### Preparing a USB flash drive for running Linux live from an ISO
Users who already have Linux installed can skip to [Dumping the Codec](#dumping-the-codec)!

1. Use a USB 3.0 flash drive (at least 8 GB or more).
2. In Windows, download [**Ventoy**](https://www.ventoy.net/en/download.html) and follow the [Instructions](https://www.ventoy.net/en/doc_start.html) to prepare the flash drive. 
3. Next, download an ISO of a Linux distribution of your choice, e.g. [**Ubuntu**](https://ubuntu.com/download/desktop), [Zorin](https://zorin.com/os/download/) or whatever distro you prefer – they all work fine.
4. Copy the ISO to your newly created Ventoy stick
5. Reboot from the flash drive
6. In the Ventoy menu, select the Linux ISO and hit enter
7. From the GNU Grub, select "Try or Install Linux"
8. Once Ubuntu has reached the Desktop environment, select "Try Ubuntu" (or whatever the distro of your choice prompts).

#### Dumping the Codec
1. Once Linux is up and running, open Terminal and enter:</br>
	```shell
	cd ~/Desktop && mkdir CodecDump && for c in /proc/asound/card*/codec#*; do f="${c/\/*card/card}"; cat "$c" > CodecDump/${f//\//-}.txt; done && zip -r CodecDump.zip CodecDump
	```
2. Store the generated `CodecDump.zip` on a medium which you can access later from within macOS (HDD, other USB stick, E-Mail, Cloud). You cannot store it on the Ventoy drive itself, since it's formatted in ExFat and can't be accessed by Linux without installing additional utilities.
3. Reboot into macOS.
4. Extract `CodecDump.zip` to the Desktop. It contains a folder with one or more .txt files. We are only interested in `card1-codec#0.txt`, additional dumps are usually from HDMI audio devices of GPUs.
5. ⚠️ Rename `card1-codec#0.txt` to `codec_dump.txt`. Otherwise the script we will use later to convert it will fail.

#### Working with Codec dumps obtained with Clover or OpenCore 
If you can live without a schematic of the Codec, you *can* use the dumps created with Clover and OpenCore as well by following the instructions below.

- **Clover**: 
	- Hit "F8" in the boot menu. 
	- `AudioDxe.efi` has to be present in `CLOVER/drivers/UEFI`. 
	- The file(s) will be stored in `EFI/CLOVER/misc`.
- **OpenCore**: [**Follow the instructions**](https://github.com/5T33Z0/AppleALC-Guides/blob/main/AppleALC_Layout-ID/Dumping_Audio_Codec_OpenCore.md)

[^1]: When I compared the dumps obtained with Clover and Linux, I noticed that the one created in Linux contained almost twice the data (293 vs 172 lines). I guess this is because Linux dynamically discovers the paths of an audio codec through a graph traversal algorithm. And in cases where the algorithm fails, it uses a huge lookup table of patches specific to each Codec. My guess is that this additional data is captured by the Codec dump as well.

### Required Tools and Files
💡Please follow the instructions carefully and thoroughly to avoid issues.

- Follow the [**instructions**](https://github.com/5T33Z0/AppleALC-Guides/blob/main/AppleALC_Layout-ID/CodecGraph_Installation.md) to install Codec-Graph and convert your `codec-dump.txt` to `Codec-Dump.svg`.
- Download and extract [**PinConfigurator**](https://github.com/headkaze/PinConfigurator/releases)
- Download [**Hackintool**](https://github.com/headkaze/Hackintool). We may need it for Hex to Decimal conversions later.
- Download and install the correct version of [**Xcode**](https://xcodereleases.com/?scope=release) for your macOS Version. The download is about 10 GB and the installed application is about 30 GB, so make sure you have enough disk space. Move the app to the "Programs" folder – otherwise compiling fails.
- A Plist Editor like [**ProperTree**](https://github.com/corpnewt/ProperTree) or PlistEditPro (Xcode and [**VS Codium**](https://vscodium.com/) can open plists as well)

### Preparing the AppleALC Source Code
- Clone, Fork or download (click on "Code" and "Download Zip") the [**AppleALC**](https://github.com/acidanthera/AppleALC) Source Code 
- Download the Debug Version of [**Lilu Kext**](https://github.com/acidanthera/Lilu/releases) and copy it to the "AppleALC" root folder
- In Terminal, enter: `cd`, hit space and drag and drop your AppleALC folder into the window and press enter.
- Next, enter `git clone https://github.com/acidanthera/MacKernelSDK` and hit enter. This add the MacKernelSDK in the AppleALC source folder. The resulting folder structure should look like this:</br>![AALC_Dir](https://user-images.githubusercontent.com/76865553/173291777-9bc1285d-1ffa-479f-b7bf-b74cda6f23ae.png)

#### Files we have to work on

|File             |Location            |Parameter(s)
-----------------|--------------------|----------
`info.plist`      |AppleALC/Resources/PinConfigs.kext/Contents/Info.plists |PinConfig
`PlatformsXX.xml` |AppleALC/Resources/subfolder for your Codec | PathMap
`layoutXX.xml`    |AppleALC/Resources/subfolder for your Codec | Layout-ID and others
`info.plist`      |AppleALC/Resources/subfolder for your Codec | PlatformsXX.xml </br> layoutXX.xml

`XX` = Number of the chosen Layout-ID.

### 💡 Tips for editing

- To avoid conflicts with the AppleALC repo when creating a Pull Request to integrate your newly created AppleALC Layout into the esxisting codebase, it's best to clone the Repo locally to work on the files before integrating the data into the source code.
- When integrating data into the source code, make sure to use Visual Studio Code or TextEdit to edit the files – especially when editing the `info.plist` inside `PinConfig.kext`. I have noticed that PlistEditoPro and even Xcode introduce changes in places you didn't even touch just by opening and saving the file. I've seen changes in the formatting as well as changes in ConfigData. This will introduce conflicts in the code when creating the Pull Request and it will be rejected.
- Add entries to both `info.plists` at the end of the corresponding sections to append lines to the source code only and not juggles lines around. The reduces chances of conflicts and makes the reviewing and merging process easier.
- Finding "missing" platform.xml files: some Codec folders (e.g. ALC 887 and 17 others) contain less Platforms than layout xml files. If you can't find a Platforms file with the number corresponding to your layout xml, look for `PlatformsID.xml` instead. It can contain lots of pathmaps. Open the layout.xml file and check the `PathMapID`. Take a mental note of it or copy the number to the clipboard. Next, open `PlatformsID.xml` and find the PathMap with the corresponding ID.

### Configuring Xcode

> [!TIP]
>
> By default, you don't have to change anything in Xcode to compile the kext so you can skip this for now and continue with chapter III.

- Start Xcode
- Open the `AppleALC.xcodeproj` file located in the AppleALC folder
- Highlight the AppleALC project
- Under "Build Settings", scroll down to "User-Defined Settings" and check if the entries `KERNEL_EXTENSION_HEADER_SEARCH_PATHS` and `KERNEL_FRAMEWORK_HEADERS` exist
- If not, press the "+" button, click on "Add User-Defined Settings" and add them:<br>![Xcodsetings01](https://user-images.githubusercontent.com/76865553/170472634-9ead337e-0ccf-46d6-9cbe-8a988cf5d14b.png)
- Make sure that both point to "(PROJECT_DIR)/MacKernelSDK/Headers":</br>![Xcode_UDS](https://user-images.githubusercontent.com/76865553/170472740-b842f8ca-0bc7-4023-acc1-c9e30b68bbfa.png)
- Next, Link to custom `libkmod.a` library by adding it under "Link Binary with Libraries": ![Xcode_link](https://user-images.githubusercontent.com/76865553/170472832-5a077289-96a6-403d-b8c7-322459ff3156.png)
- Verify that `libkmod.a` is present in /MacKernelSDK/Library/x86_64/ inside the AppleALC Folder. Once all that is done, you are prepared to compile AppleALC.kext.

---

[**Home:** Documentation Index ↑](README.md) | [**Next:** Codec Dump Analysis →](02_Codec_Dump_Analysis.md)
