# How to create/modify a Layout-ID for AppleALC

## V. Creating a PathMap
The PathMap defines the routings of the Nodes within the Codec which are injected into macOS. Some routings are fixed (internal Speakers/Mics) while others can be routed freely. some Nodes can even be both, input and output.

### Structure of `PlatformsXX.xml`
1. The PathMap has to be entered in `PlatformXX.xml` (`XX` = chosen number of the Layout-ID). 
2. The way inputs and outputs are organized within the hierarchy of the PathMap defines whether or not the system switches between sources automatically if a device is plugged in or if the inputs/outputs have to be changed manually in System Preferences (as VoodooHDA.kext requires). For auto-switching between sources to work, they have to be in the same group/array. Usually you create a group for inputs and a group. for outputs.

#### Auto-Switching Mode
In Auto-Switching Mode, the Input/Output signal is re-routed from the current Input/Output to another one automatically, once a jack is plugged into the system. On Laptops for example, Internal Speakers are muted and the signal is automatically re-routed to the Headphone or Line Output. Once the plug is pulled from the audio jack, the output switches  back to the internal speakers. Same for Inputs: the Internal Mic is muted when an external Mic or Headset is plugged into the 1/8" audio jack.

For Auto Switching-Mode to work, certain conditions have to be met:
- The Pin Complex Node(s) must support the "Detect" feature
- The Pin Complex Node(s) must have at least 2 possible connections to 2 different Mixer Nodes or Audio Switches. Note that having multiple connections alone is not sufficient — the codec and board hardware must also have jack detection (presence detect) circuitry wired to the pin. Maybe switching between 2 Nodes connected to the same Mixer Node works as well but I haven't tested this.

Let's have a look at the output side of the schematic:</br>![SwitchMode01](https://user-images.githubusercontent.com/76865553/171393009-65312baf-77c3-41d6-96d6-18359933aad5.png)

- Nodes 20, 21, 24, 25, 26 and 27 support the Detect feature
- These Nodes can all connect to Mixers 12 (red) and 13 (green)
- Therefore, they can be operated in Auto Switching Mode

Nodes that make up the audio "circuitry" as well as the switching behavior have to be represented in the file structure of the `PathMap`. Nodes you want to switch between have to be part of that same Array (one for Inputs, one for Outputs). Here's how the structure inside the Platforms.xml file looks:

- PathMaps (Array)
	- 0 (Dict) (Codec Address)
		- PathMap (Array)
			- **0 (Array) [INPUTS]** (Sources you want to switch between)
				- 0 (Array) [Input Source 1]
					- 0 (Array) [Container for Nodes of Input Source 1]
						-  0 (Dict) Input Node 
						-  1 (Dict) Mixer Node
						-  2 (Dict) Pin Complex Node
				- 1 (Array) (Input Source 2)
					- 0 (Array) [Container for Nodes of Input Source 2]
						-  0 (Dict) Input Node 
						-  1 (Dict) Mixer Node
						-  2 (Dict) Pin Complex Node
					- etc.
			- **1 (Array) [OUTPUTS]**
				- 0 (Array) [Output Source 1]
					- 0 (Array) [Container for Nodes of Output Source 1]
						-  0 (Dict) Pin Complex Node
						-  1 (Dict) Mixer Node
						-  2 (Dict) Output Node
				- 1 (Array) (Output Source 2)
					- 0 (Array) [Container for Nodes of Output Source 2]
						-  0 (Dict) Pin Complex Node
						-  1 (Dict) Mixer Node
						-  2 (Dict) Output Node
				- etc. 

#### Manual Switching Mode
In manual switching mode, you have to switch/select Inputs/Outputs manually in the Audio Settings. In this configuration, each Array only contains the nodes for the path of one device. The structure looks as follows:

- PathMaps (Array)
	- 0 (Dict) (Codec Address)
		- PathMap (Array)
			- 0 (Array)
				- 0 (Array) (Device 1) (Input 1)
					- 0 (Dict) (Nodes of Input 1)
						- 0 (Dict) (Input Node)
						- 1 (Dict) (Mixer Node)
						- 2 (Dict) (Pin Complex Node)
			- 1 (Array)
				- 0 (Array) (Device 2) (Input 2)
					- 0 (Dict) (Nodes of Input 2)
						- 0 (Dict) (Input Node)
						- 1 (Dict) (Mixer Node)
						- 2 (Dict) (Pin Complex Node)
			- 2 (Array)
				- 0 (Array) (Device 3) (Output 1)
					- 0 (Dict) (Nodes of Device 1)
						- 0 (Dict) (Pin Complex Node)
						- 1 (Dict) (Mixer Node)
						- 2 (Dict) (Output Node)
			- etc.

Now that we know to enter the routing data into the PlatformsXX.xml file, we can begin entering the data in a new file.

> [!NOTE]
>
> - Make sure to get the hierarchy of the Platforms.xml right. Otherwise there won't be any Input/Output Sources available!
> - Nodes used in the `PathMap` must exist in the `PinConfig`! You might have to go back and forth between generating a `PinConfig`, adding/updating it in the info.plist inside of `PinConfigs.kext` and adjusting the `PlatformsXX.xml` to make it all work!
> - You can combine both, auto switching and manual switching. For example, you could use auto mode to switch back and forth between internal Speakers and the Headphone Out but add an extra Line-Out in manual mode if your Codec can't be configured to switch between all three sources automatically (if it lacks an Audio Switch).

## VI. Creating a `PlatformsXX.xml`
There are 2 methods for creating a `PlatformsXX.xml` file: one utilizes VoodooHDA.kext and a forgotten script called `GetDumpXML`. It generates a `Platforms.xml` file, which contains all the required Nodes for switching Inputs/Outputs manually. It works out of the box and allows you to skip Chapter IX completely which is a big time saver. Unfortunately, this method doesn't work beyond macOS Catalina, so users of Big Sur and newer need to follow the manual method instead.

### Automated method using VoodooHDA and GetDumpXML (macOS ≤ 10.15.7 only)
- Download [**GetDumpXML.zip**](https://github.com/5T33Z0/AppleALC-Guides/blob/main/AppleALC_Layout-ID/Tools/GetDumpXML.zip?raw=true) and unpack it
- Add VoodooHDA.kext to your EFI's kext folder and config.plist.
- Disable/delete AppleALC.kext
- Reboot
- Double-click `GetDumpXML` (in GetDumpXML folder)
- This will create a "GetDumpXML_YOURCODEC" folder on the desktop, containing a `Platforms.xml` file.
- Add the # of your chosen Layout-ID to the filename (`Platforms39.xml` in my case)
- Open the File with a Plist Editor
- Expand `PathMaps` branch. As you can see, the entries are organized for manual switching:</br>![VoodooHDAXML01](https://user-images.githubusercontent.com/76865553/172041677-93a86db8-af31-4172-a68f-dffcc0888646.png)
- Compare the Nodes used in the PathMap with the Nodes present your PinConfig and adjust the PinConfig accordingly, so that it contains the same nodes as the PathMap!
- Change `PathMapID` to the number of your Layout-ID!
- Save the file
- Move PlatformsXX.xml to: "AppleALC/Resources/YOURCODEC" folder
- Disable/remove VoodooHDA.kext and re-enable AppleALC.kext again
- Reboot
- Continue in Chapter X.

> [!NOTE]
>
> You can also rearrange the structure of the .xml file to introduce auto-switching, but I would do that after you've verified that everything is working.

### Manual Method
Obviously, we need to avoid changing data of existing Platforms.xml files created by other users. Because it would destroy the Layout for other users, if the Source Code would get synced with the AppleALC repo. Instead, we need to create a new one for our Layout-ID with our own routing, so do the following:

- In Finder, navigate to the "Resources" folder for your Codec. For me, it's `AppleALC/Resources/ALC269`.
- Select the `Platforms.xml` of the Layout-ID you are currently using (the number is identical). Since I am using ALC Layout-ID 18, I use Platforms18.xml.
- Duplicate the file (⌘+D)
- Change the name to the Layout-ID you chose (For me Platforms39.xml)
- Change the `PathMapID` at the bottom of list so it's identical to the number of your Layout-ID (in my case it's `39`):</br>![platforms02](https://user-images.githubusercontent.com/76865553/171393131-44cd8562-104b-4008-9a4d-43707b880327.png)

## VII. Transferring the PathMap to `PlatformsXX.xml`
Now that we traced all the possible paths to connect Pin Complex Nodes with Inputs and Outputs, we need to transfer the ones we need to a `PlatformsXX.xml` file. "XY" corresponds to the previously chosen Layout-ID. In my case it will be `Platforms39.xml`.

### Transferring PinComplex Nodes to PlatformsXX.xml
1. Take the chart with the possible connections you traced in Chapter IV.
2. Decide which Input/Output Device(s) you want to add to the PathMap
3. Decide if you want to add the device(s) in a switch mode configuration or if you want switch the device manually.
4. Add the Nodes to the PlatformsXX.xml accordingly

For reference, Let's have a look how Switch-Mode for Outputs is realized in ALC Layout-ID 18 inside of `Platforms18.xml`:</br>![PlatformsStructure01](https://user-images.githubusercontent.com/76865553/171393277-13b2ec45-ec83-452c-ba5d-06aaab795d74.png)

On the Input side, the structure is the same. The only difference is that the order of the nodes is reversed: instead of tracing the path from the Pin Complex Nodes to the Outputs, you start at the output and trace the path back to the Pin Complex Node:</br>![PlatformsStructure02](https://user-images.githubusercontent.com/76865553/171393394-0244592c-a961-4ab7-ae1f-1942dbd6a5d4.png)

- Enter the required Node IDs you found in chapter IV for the Inputs and Outputs you need (as explained). 
- To add more devices to the PathMap, duplicate one of the "Source" Array and change the data.
- Once, you're done, save the file.

> [!NOTE]
>
> `LayoutID` and `PathMapID` **must be identical** and must use the same number you chose for your Layout-ID previously.

#### Example: Finished PathMap for Layout39
Here's how the finished `Platforms39.xml` with added Node 27 in Auto Switch Mode looks like:

![Outputs_final01](https://user-images.githubusercontent.com/76865553/173155479-1d16c43c-ffc1-47f6-9998-3e4ad3e4a9fa.png)

On the Input side, the PathMap looks like this:

![Inputs_final01](https://user-images.githubusercontent.com/76865553/173155511-e9f260fd-5c80-4f0a-a12b-8388b15960ba.png)

Array 2 (Line-In, manual mode) is an extra Line-In connection with path 8 – 35 – 24. It can be used to override the Line-In of the Headphone jack in order to attach a different mic or audio input to it. 

Since the T530 uses a Combojack which integrates the input and output into the Headphone jack, simply plugging a headset into it reserves the Line-In as long as it is physically connected because headsets have a plug with 4 poles (Mic, Ground, L and R Audio). So automatic switching to a Line-In of the dock is not possible. Therefore, you have to switch between Line-In of the dock and the Line-In of the HP jack manually in System Settings:

![Lineinswitch](https://user-images.githubusercontent.com/76865553/173165968-e4a607c7-a32b-4610-a7c3-1f44e4c40b55.png)

### Amp Capabilities
Besides entries for the Nodes that the incoming/outgoing signal traverses, the Codec dump also includes entries for Amp stage(s) which have to be reflected in the **Platforms.xml** as well.

#### Amp Node (Input side)
For Inputs, the Amp is usually part of the first entry in the chain, the Input Node: 

![Amp01](https://user-images.githubusercontent.com/76865553/171593290-792700c2-f82d-4d8e-93bd-0ce5bc22a0c6.png)

Let's have a look inside the Input Amp Array:

![Amp02](https://user-images.githubusercontent.com/76865553/171593343-ea59ec99-c65d-4a2a-be82-317734595db5.png)

The available options/features of the Amp Array are part of the PinComplex Node it belongs to (Input Node 9 in this example) as defined in the codec_dump_dec.txt. So let's see, what it says:

![Amp03](https://user-images.githubusercontent.com/76865553/171593456-b85e243a-8f65-4abc-a824-986f5c46dbc3.png)

For Node 9 (and others), there's an entry called "Amp-In Caps", which among other things contains different parameters.

#### Amp Node (Output side)
Next, let's look at Array 1 of the PathMap, which contains the Output Devices:

![Amp04](https://user-images.githubusercontent.com/76865553/171671059-bc3a8b93-fa9a-45d6-99fa-ba05ea5fc50c.png)

As you can see, for the ALC269, each Node of the Output Path has an Amp stage and the "Channels" array is part of the last Node in the chain rather than the first Node.

### Transferring Amp Capabilities to PlatformsXX.xml

Here's how "Amp Caps" translate to entries in the .xml file:

codec_dump.txt         | PlatformsXX.xml
-----------------------|----------------------------
**Mono/Stereo Amp-In/Out** | **Channels** Array with 1 or 2 Dictionaries: 2=Stereo, 1=Mono. ⚠️ The "Channels" Array is only present **once** in a path: <ul><li>In **Input** Devices it's included in the ***first*** node <li> In **Output** Devices side it's included in the ***last*** Node!|
**Amp-In Caps**</br>**nsteps**= 0 or ≥1 |</br>**VolumeInputAmp** (NO/YES)
**mute**=0 or 1        | **MuteInputAmp** (NO/YES)
**nsteps**=3           | **Boost** Level (=3) on the input. Applied to the destination Node (last Node in the chain). In this example to Node 18 "Internal Mic Boost Volume". For ALC269 is also applies to Nodes 11, 24, 25, 26, and 27.||
**Amp-Out Caps**</br>**nsteps** 0 or ≥1   |</br>**PublishVolume** (NO/YES)
**mute**=0 or 1        | **PublishMute** (YES/NO)

**Explanations**: 

- `Mute` in Amp-In an Amp-Out Nodes are different functions in Platforms.xml:
	- `mute` in ***Amp-In Nodes*** = `MuteInputAmp`
	- `mute` in ***Amp-Out Nodes*** = `PublishMute`
- `Nsteps` also has different functions whether it's used in Amp-In or Amp-Out Nodes:
	- `nsteps` in ***Amp-In Nodes*** = `VolumeInputAmp`
	- `nsteps` in ***Amp-Outs Nodes*** = `PublishVolume`
	- `nsteps=3` in **Amp-In Node** = `Boost` factor 3 last Node of the Chain on the Input Device (as shown in the first screenshot)

#### Usual Amp Settings used in PlatformsXX.xml

- For **Inputs**:
	- MuteInputAmp: NO
	- PublishMute: YES
	- PublishVolume: YES
	- VolumeInputAmp: YES

- For **Outputs**:
	- MuteInputAmp: YES
	- PublishMute: YES
	- PublishVolume: YES
	- VolumeInputAmp: NO

### Example: Adding an Output device to the `PlatformsXX.xml`

As we figured out in Chapter IV and VII, possible paths for adding Node 27 as an Output device can be: 27 &rarr; 13 &rarr; 3 or 27 &rarr; 12  &rarr; 2. I may have to try both. 
Since I want the Output to switch from the speakers (connected via 21 &rarr; 12 &rarr; 2) to the dock when I pluck my speakers in, I first try to connect Node 27 to Mixer 12 and Output 2 as well and see if it switches between Node 21 and 27.

So, I add the path 27 - 12 - 2 to `Platforms39.xml`:

- Open PlatformsXX.xml (`XX` = number you chose for your Layout-ID)
- Navigate to the branch containing the Output Devices (expand PathMaps > 0 > PathMap > 1):</br> ![Outdevs01](https://user-images.githubusercontent.com/76865553/171813688-09bc6040-cbe8-4262-ad62-0321297df4cb.png)
- Duplicate Array 1 (Output Device 2). The Output device branch should contain 3 arrays now:</br>![Outdevs02](https://user-images.githubusercontent.com/76865553/171813707-703f1526-54da-454d-b1d3-879d34efc61e.png)
- Next, we need to correct the Nodes inside of Array 2 (Output device 3) to 27, 12, 2: </br>![Outdevs03](https://user-images.githubusercontent.com/76865553/171813717-e691b1fc-7d26-45cd-8a97-3896b1621bcf.png)
- Next, we need to take care of the Amp section of Node 27. Since we are configuring as an output, we can use the default settings for testing:
	- **MuteInputAmp**: YES
	- **PublishMute**: YES
	- **PublishVolume**: YES
	- **VolumeInputAmp**: NO 
- For Inputs, you also have to check the `nsteps` value of the Amp-In Caps for the destination node. If `nsteps=3`, add a `Boost` entry with value `3` to the last node in the input path.
- Repeat for other devices you want to add to the PathMap.
- Save the file.

### Example: Adding an Input device to the `PlatformsXX.xml`
- Open PlatformsXX.xml (`XX` = number you chose for your Layout-ID)
- Navigate to the branch containing the Input Devices (expand PathMaps > 0 > PathMap > 0):</br>![InputsArray0](https://user-images.githubusercontent.com/76865553/173223277-d471a722-bf75-47ba-bea5-a84c6c313689.png)
- Duplicate an existing Device Array
- Adjust the following:
	- Node IDs (according the the path of the source you want to add), 
	- Amp Settings
	- Boost Settings (If `Amp-In Caps` of destination Node contain `nsteps=3`, add `Boost` entry to the last Node in the path (here NID 25)
- Let's look inside Device 2. It contains the following Nodes and settings:</br>![Input01Nodes](https://user-images.githubusercontent.com/76865553/173223291-53c78f9e-976e-4044-9eb8-812b709dee86.png)
- Repeat for other devices you want to add to the PathMap
- Save the file.
