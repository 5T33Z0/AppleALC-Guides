# How to create/modify a Layout-ID for AppleALC

## IX. Creating a PinConfig
Audio Codecs support various Inputs and Outputs: Internal speakers and a mic (usually on Laptops) as well as Line-Ins and Outs (both analog and digital). These audio sources are injected into macOS by AppleALC as a long sequence of code (or "verbs") which form the so-called `PinConfig`. It's the single most important parameter to get Audio Inputs and Outputs working properly.

"Verbs" consist of a combination of 4 components: the Codec's address, Pin Complex Nodes with Control Names, Verb Commands and Verb Data which has to be extracted from the Codec dump, corrected and injected into macOS via AppleALC kext. Here's a color-coded example showing all the paramaters (and their positions in the bitmask) that form the PinDefault value of a Pin Complex Node:

![PinComplexNodeStructure](https://user-images.githubusercontent.com/76865553/174908462-07db8885-9337-4e34-b620-54619c38db06.png)

If you're interested in the tedious process of extracting verbs from a Codec dump *manually*, please refer to Parts 2 and 3 of [EMlyDinEsH's guide](https://osxlatitude.com/forums/topic/1946-complete-applehda-patching-guide/).

Luckily for us, we can use **PinConfigurator** to extract Verbs from the Codec dump automatically and also apply corrections to them easily.

⚠️ Ensure that your `PinConfig` contains ***all*** the Input and Output Nodes (Mixers/Switches are irrelevant) you are referring to in the `PathMap` so the routing is coherent. If you are referencing a node in a path which doesn't exist (in the PinConfig) then there will be no sound for this path. On the other hand, you can have more Nodes in the PinConfig than you are actually assigning in the PathMap – they just won't be available/visible in System Preferences as Input/Output sources.

### Using PinConfigurator to create a PinConfig

#### Default Method (keeps connected Nodes only)
Preferred method if you just want to inject the default Input/Output sources into macOS (Double-check against Nodes used in the Platforms.xml and if necessary, adjust them accordingly).

1. Open **PinConfigurator**
2. Click on "File > Open…" (⌘+O) and select "codec_dump.txt"
3. This will extract and import all the available audio sources from the Codec dump:</br>![PCnu01](https://user-images.githubusercontent.com/76865553/171392638-7a72f44b-8e13-4ff4-ae9e-9e24d11accda.png)
4. Next, click on "Patch > Remove Disabled". This will remove all Nodes which are not connected except ATAPI Internal (= Optical Drive):</br>![PCnu02](https://user-images.githubusercontent.com/76865553/171389936-1931ef51-b2ae-4f5b-889e-d02acc057710.png)
5. Click on "Options > Verb Sanitize" and enable all the options:</br>![Verbfixes](https://user-images.githubusercontent.com/76865553/171390150-65fb7777-666d-4385-8798-ed2288bfd6e5.png)
6. Select "Patch > Verb Sanitize". This will apply [various fixes](https://github.com/headkaze/PinConfigurator#what-patch-apply-verbit-fix-does-now) to the PinDefault values and Verb Data so that the `PinConfig` will work in macOS.
7. Next, click on "Get ConfigData":</br>![PCnu04](https://user-images.githubusercontent.com/76865553/171390411-5335a259-2aae-4e27-82fa-cb00f3799ecf.png)
8. Copy the `ConfigData` into the clipboard
9. Select "File > Export > verbs.txt". It will be stored on the Desktop.
10. Open verbs.txt.
11. Paste the `ConfigData` in an empty line and save the file. We'll need it later.
12. Continue in **Chapter X.**

> [!NOTE]
>
> If you want to know how decode `ConfigData` to fix issues, have a look at [this](https://gist.github.com/fewtarius/f691d97513c4f7e527cb41f44c069548#a-simple-pincomplex-primer). 

#### Modifying an existing PinConfig (adding Outputs/Inputs)
In case you already have a somewhat working Layout-ID that you want/need to modify, you can import its PinConfig into PinConfigurator for editing. There are 2 methods to do it:

##### Method 1: Importing PinConfig from IO Registry
If `AppleALC.kext` is loaded, you can import the `PinConfig` directly from the I/O Registry:

1. Open PinConfigurator
2. From the menubar, select "File > Import > IO Registry"
3. Select the Audio Codec (not the HDMI port)
4. Check `codecdumpdec.svg` to find the Pin Complex Nodes you want to add to the current PinConfig and modify it as explained in the next section

##### Method 2 Importing PinConfig from PinConfigs.kext
If AppleALC is not loaded or you want to import a different PinConfig for your Codec, do the following:

1. Open the `info.plist` inside the `PinConfig.kext` (in AppleALC/Resources)
2. Use the search function to to find the Layout-ID you want to modify:
	- Search by `CodecID` (look it up in `codec_dump_dec.txt`) and skip through the results until you find it, or
	- Search by the description the author added to the `Codec` string – like the Codec name, Laptop or Mainboard model for example.
3. Select the data inside the `ConfigData` field (⌘+A) and copy it (⌘+C):</br>![Modpinconf](https://user-images.githubusercontent.com/76865553/171391426-5b518d5d-f0f4-464c-89e5-9eb65b7437fe.png)
4. Start the PinConfigurator App
5. From the menubar, select "File > Import > Clipboard"
6. This is how it looks:</br>![pincfgimprtd](https://user-images.githubusercontent.com/76865553/171391513-9cf5d5a7-b83f-4641-a11f-87603092306b.png)
7. Check `codecdumpdec.svg` to find the Pin Complex Nodes you want to add to the current PinConfig.[^2]

[^2]: In my case, the PinConfig lacks a second Output to get sound out of the docking station's jack when I plug in external speakers. The Layout-ID I am currently using (ID 18 for ALC269) was created for the Lenovo X230 which is very similar to the T530 in terms of features. It uses the same Codec revision and works fine besides the missing Line-Out for the dock. Since Node 27 has a Headphone Playback switch as well, I will add it to the current PinConfig. For your configuring your Codec, you will have to refer to the Codec schematic and the codec dump text file to find appropriate nodes. In some cases you might even have to inspect the block diagram which is part of the documentation provided by the Codec manufacturer. 

There are 2 methods to do add a Node to the PinConfig: you can either add one in PinConfigurator and configure it manually or combine verb data inside the `verbs.txt` to "craft" one, copy it into memory and import it.

#### Adding Nodes, Method 1: Using `verbs.txt`

1. Open `verbs.txt`
2. Place the cursor at the end of the document 
3. Paste (⌘+V) the ConfigDate (green). It should still be stored in the Clipboard.
4. Next, add the Verb Data of the Node(s) you want to add (cyan) to the existing PinConfig:</br>![Modpfcg18](https://user-images.githubusercontent.com/76865553/171391880-12628a54-8cde-4a66-bf3b-7bd810f09bd7.png)
5. Copy the resulting PinConfig (pink) into the clipboard
6. Switch back to PinConfigurator
7. From the menubar, select File > Import > Clipboard. In this example, Node 27 has been added:</br>![modpinpc](https://user-images.githubusercontent.com/76865553/171392147-c6b4df49-8f51-46a5-a707-c2e0fc40a557.png)
8. Select "Patch > Verb Sanitize" to correct the Verb data.
9. Export the data. There are 2 ways to do so: 
	- Either copy/paste the ConfigData to a text file and save it for later, or 
	- Select "File > Export > "PinConfigs.kext" (it's located under /AppleALC/Resources/) to write the data to the info.plist of the kext directly.

#### Adding Nodes, Method 2: Using PinConfigurator's `Add` feature

1. In PinConfigurator, click "Add"
2. This opens a dialog with a bunch of options to configure the new Node:</br>![AddNode01](https://user-images.githubusercontent.com/76865553/172112636-1f207237-bb45-48a7-9b21-b20a72927e0a.png)
3. Use `verbs.txt` or `codec_dump.txt` to configure the Node (see "Config Notes")
4. Press "Save" when you're done. In my case, Node 27 will be added.
5. Select "Patch > Verb Sanitize". This will apply [fixes](https://github.com/headkaze/PinConfigurator#what-patch-apply-verbit-fix-does-now) to the PinDefault values and Verb Data so that the `PinConfig` will work in macOS.
6. Back in the main Window, click on "Get ConfigData"
7. The new/modified PinConfig will be listed in the text field below it:</br>![GetConfig02](https://user-images.githubusercontent.com/76865553/171392396-5dea072e-f57b-492f-b44e-d2819e2a74d7.png)
8. Export the data. There are 2 ways to do so: 
	- Either copy/paste the ConfigData to a text file and save it for later, or 
	- Select "File > Export > "PinConfigs.kext" (it's located under /AppleALC/Resources/) to write the data to the info.plist of the kext directly.

#### PinConfigurator's "Edit Node" window explained
PinConfigurator's "Edit Node" dialog window lets you configure the `PinDefault` value of a Node. Since the App is mostly undocumented, some of the settings are obvious while others are not (like "Misc", "Group" or "Position"). Luckily, chapter `7.3.3.31 Configuration Default` of the [Intel HDA specs](https://www.intel.com/content/www/us/en/standards/high-definition-audio-specification.html) provides the necessary explanations:

Parameter        | Description
-----------------|------------
**NodeID** (NID) | Add the Node number in decimal (get it from `codec_dump_dec.txt`). Only PinComplex Nodes with a Control Name are eligible! **Example**:</br>![PCNID](https://user-images.githubusercontent.com/76865553/173185594-cf4757df-47c0-4ae7-aaec-003e72ecaf73.png)
**PinDefault** | = **Configuration Default**. A 32-bit register required in each Pin Widget. It is used by software as an aid in determining the configuration of jacks and devices attached to the codec. At the time the codec is first powered on, this register is internally loaded with default values indicating the typical system use of this particular pin/jack. Get the `PinDefault` value (in Hex) from `codec_dump.txt`
**Device** | = **Default Device.** Indicates the intended use of the jack or device. This can indicate either the label on the jack or the device that is hardwired to the port, as with integrated speakers and the like.
**Connector** | = **Connection Type.** Indicates the type of physical connection, such as a 1/8-inch stereo jack or an optical digital connector, etc. Software can use this information to provide helpful user interface descriptions to the user or to modify reported codec capabilities based on the capabilities of the physical transport external to the codec.
**Port** | = **Port Connectivity**. Indicates the external connectivity of the Pin Complex. Software can use this value to know what Pin Complexes are connected to jacks, internal devices, or not connected at all. If a Node contains "fixed" in the Codec Schematic (usually for Laptop Speakers and Internal Mics) it should be set to fixed here as well.
**Gross Location** | Upper bits of the Location field describing the gross location, such as “External” (on the primary system chassis, accessible to the user), “Internal” (on the motherboard, not accessible without opening the box), on a separate chassis (such as a mobile box), or other. For Internal Speakers/Mics, set it to "Internal" (mostly Laptops), for things you connect to it by a plug, select "External".
**Geo Location** | Lower bits of the Location field. Provide a geometric location, such as “Front,” “Left,” etc., or provide special encodings to indicate locations such as mobile lid mounted microphones.
**Color** | Indicates the color of the physical jack for use by software.</br>- For internal devices: select "[0] Unknown" </br> - For external devices like Headphones etc.: select "[1] Black".
**Misc.** |Bit field used to indicate other information about the jack. Currently, only bit `0` is defined. If bit `0` is set, it indicates that the jack has no presence detect capability, so even if a Pin Complex indicates that the codec hardware supports the presence detect functionality on the jack, the external circuitry is not capable of supporting the functionality.
**Group** | = **Default Association**. Default Association and Sequence are used together by software to **group** Pin Complexes (and therefore jacks) together into functional blocks to support multichannel operation. Software may assume that all jacks with the same association number are intended to be grouped together, for instance to provide six channel analog output. The Default Association can also be used by software to prioritize resource allocation in constrained situations. Lower Default Association values would be higher in priority for resources such as processing nodes or Input and Output Converters.
**Position** | = **Sequence**. Indicates the **order** of the jacks in the association group. The lowest numbered jack in the association group should be assigned the lowest numbered channels in the stream, etc. The numbers need not be sequential within the group, only the order matters. Sequence numbers within a set of Default Associations must be unique.
**EAPD** | = **EAPD/BTL Enable, L/R Swap**. Controls the EAPD pin and configures Pin Widgets into balanced output mode, when these features are supported. It also configures any widget to swap L and R channels when this feature is supported. Check if the Node supports EAPD and adjust the setting accordingly. Read chapter 7.3.3.16 of the HDA Specs for more details.

#### Example: PinConfig for using the Audio Jacks of Docking Station 4337/4338 with a Lenovo T530 Laptop (ALC 269)

![PCfgFnl01](https://user-images.githubusercontent.com/76865553/173185501-f06f390b-819b-4859-9796-6cbac3487618.png)

> [!NOTE]
>
> Ignore NID 24, it's unused.

---

[← **Previous:** Create Layout.xml](04_Create_Layout-XML.md) | [**Next:** Integrate Files →](06_Integrate_Files.md)

