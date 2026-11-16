# How to create/modify a Layout-ID for AppleALC

## VIII. Adding/Modifying `layoutXX.xml`
The `layoutXX.xml` file defines which Codec the Layout is for (`CodecID` = `Vendor Id` in codec_dump_dec.txt) and describes the types of Inputs and Outputs that are available. It also contains the reference to the PathMap which should be applied to the Codec (`PathMapID`) for the chosen `LayoutID` (ID 39 in this example).

### Modifying an existing `layoutXX.xml`
- Navigate to `AppleALC/Resources/YOUR_CODEC` (in my case ALC269)
- Duplicate the `LayoutXX.xml` you want to modify (in my case layout18.xml)
- Change the number of the filename an unused one (between 11 to 99). In my case: layout39.xml
- Open it with a Plist Editor 
- Change the `LayoutID` &rarr; must be identical with # used in the filename
- Expand `PathMapRef`
- Adjust the following settings:
	- `Inputs`: Add Type of Inputs (if missing)
	- `Output`: Add Type of Output (if missing). I have to add `LineOut` for my Docking Station.
	- `PathMapID` (# must match that of the filename):</br>![layoutxml](https://user-images.githubusercontent.com/76865553/172024303-0485b52c-1f2f-4615-bcac-bdd056ea745b.png)
- Save the file.

### Calculating `MuteGPIO`
`MuteGPIO` sets the voltage reference (VREF) applied to an input pin node via a pin control verb. It controls whether the pin is in input mode with the correct bias voltage, which effectively enables or disables the mic/line-in signal path. Not all codecs require this — check your codec dump for `Pin-ctls: IN VREF_xx` entries to determine if and which nodes need it. It has to be entered in the `layout.xml` in decimal:

![](https://user-images.githubusercontent.com/76865553/172787254-f5fe21fb-5466-49a6-afcc-87c16391aa71.png)

`MuteGPIO` is calculated based on the following formula:  

`Vref hex + 0100 + Node ID hex` &rarr; Converted to Dec. 💡 Use the Calculator  inside of Hackinool to convert the value.

Let's have a look at the "Vref caps" of Node 24 ("Mic Boost Volume") inside of the Codec dump: 

"Vref caps: HIZ 50 GRD 80 100" &rarr; GRD 80 is the value which pulls the connection to the ground (disables it). 

A bit further down we find this line: 

"Pin-ctls: 36: **IN VREF_80**" &rarr; this is the confirmation that this Node uses a VREF of 80 %, as most Codecs do.

If we use 80% as a reference for Node 24 and apply the formula from the beginning, we get:

0x50 (80 in hex) + 0100 + 0x18 (Node 24 in hex) = 0x50010018 (Hex) &rarr; **1342242840** (Dec). This is the value which has to be added for this Node.

#### MuteGPIO Table
With the table below, you only have to copy the **decimal** value for your Node(s) based on the "IN VREF_" method your Codec uses (50 or 80) and add the `MuteGPIO` value to the layout.xml file.

NodeID | GPIO VREF = 50%</br>Dec | GPIO VREF = 50% </br>Hex| GPIO VREF = 80%</br>Dec |GPIO VREF = 80% </br>Hex|GPIO VREF = ?%</br>Dec |GPIO VREF = ?% </br>Hex|
:-:|:-------------:|:----------:|:--------------:|:----------:|:--------------:|:----------:
20 | **838926356** | 0x32010014 | **1342242836** | 0x50010014 | **1677787156** | 0x64010014
21 | **838926357** | 0x32010015 | **1342242837** | 0x50010015 | **1677787157** | 0x64010015
22 | **838926358** | 0x32010016 | **1342242838** | 0x50010016 | **1677787158** | 0x64010016
23 | **838926359** | 0x32010017 | **1342242839** | 0x50010017 | **1677787159** | 0x64010017
24 | **838926360** | 0x32010018 | **1342242840** | 0x50010018 | **1677787160** | 0x64010018
25 | **838926361** | 0x32010019 | **1342242841** | 0x50010019 | **1677787161** | 0x64010019
26 | **838926362** | 0x3201001A | **1342242842** | 0x5001001A | **1677787162** | 0x6401001A
27 | **838926363** | 0x3201001B | **1342242843** | 0x5001001B | **1677787163** | 0x6401001B
28 | **838926364** | 0x3201001C | **1342242844** | 0x5001001C | **1677787164** | 0x6401001C
29 | **838926365** | 0x3201001D | **1342242845** | 0x5001001D | **1677787165** | 0x6401001D
30 | **838926366** | 0x3201001E | **1342242846** | 0x5001001E | **1677787166** | 0x6401001E
31 | **838926367** | 0x3201001F | **1342242847** | 0x5001001F | **1677787167** | 0x6401001F
…  |

### Creating a new `LayoutXX.xml` from scratch
TODO…
