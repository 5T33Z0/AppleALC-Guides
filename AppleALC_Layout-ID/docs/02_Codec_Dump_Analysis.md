# How to create/modify a Layout-ID for AppleALC

## III. Extracting data from the Codec dump
In order to route audio inputs and outputs for macOS, we need to analyze and work with data inside the Codec dump. To make the data easier to work with, we will use codec-graph to generate a schematic of the audio codec which makes routing audio much easier than working solely with the text file.

### Converting the Codec Dump
- Follow the [**instructions**](https://github.com/5T33Z0/AppleALC-Guides/blob/main/AppleALC_Layout-ID/CodecGraph_Installation.md) to install Codec-Graph and convert your `codec-dump.txt` to `Codec-Dump.svg`.
- Next, run [**PinConfigurator**](https://github.com/benbaker76/PinConfigurator)
- Select "File > Open…" (⌘+O) and open "codec_dump.txt"
- This will extract the available audio sources from the Codec dump
- Select File > Export > **`verbs.txt`**. It will will be stored on the Desktop automatically. We may need it later.

### Relevant Codec data
Amongst other things, the Codec dump text contains the following details:

- The Codec model
- Its Address (usually `0`)
- Its Vendor Id (in AppleALC it's used as `CodecID`)
- Pin Complex Nodes with Control Names (these are eligible for the `PinConfig`)
- The actual routing capabilities of the Codec:
	- Pin Complex Nodes
	- Mixer/Selector Nodes
	- Audio Output Nodes
	- Audio Input Nodes
	- Number of connections from/to a Node/Mixer/Selector/Switch

## IV. Understanding the Codec schematic and signal flow
Shown below is `codecdumpdec.svg`, a visual representation of the data inside the codec dump for the **Realtek ALC269VC** used in my Laptop. It shows the routing capabilities of the Audio Codec. Depending on the Codec used in your system, the schematic will look different![^3]

![codec_dump_dec](https://user-images.githubusercontent.com/76865553/170470041-6a872399-d75a-4145-b305-b66e242a1b47.svg)

[^3]: This repo contains some more Codec dumps with schematics you can check out.

Form/Color        | Function
------------------|-----------------------------------------------
**Triangle**      | Amplifier
**Blue Ellipse**  | Audio Output
**Red Ellipse**   | Audio Input
**Parallelogram** | Audio selector (this codec doesn't have any)
**Hexagon**       | Audio mixer (with various connections 0, 1, 2,…)
**Rectangle**     | Pin Complex Nodes representing audio sources we can select in system settings (Mic, Line-out, Headphone etc.)
**Black Lines**   | Default connection (indicated by an asterisk in the Codec_Dump.txt)
**Dotted Lines**  | Optional connection(s) a Node offers 
**Blue Lines**    | Connections to the Outputs

### How to read the schematic
⚠️ The schematic is a bit hard to comprehend and interpret because of its structure. It's also misleading: the arrows represent _connection capability_ — which nodes a given node can connect to — not signal flow direction. For outputs, they happen to point against the signal flow; for inputs, they coincidentally align with it. So don't rely on them. Instead, follow the actual signal flow.

#### Routing Input Devices
For **Input Devices**, start at the Input Node (red) and trace the route to the Pin Complex Node. 

- **Option 1**: Input &rarr; Mixer/Audio Selector &rarr; PinComplex Node:

	```mermaid
	flowchart LR
		id1(((Input))) -->|Signal flow|id2{Mixer A} -->|Signal flow|id3(Pin Complex XY)
		id4(((Input))) -->id5[/Audio Selector/]-->id6(Pin Complex XY)
	```
- **Option 2**: Input &rarr; PinComplex Node:

	```mermaid
		flowchart LR
		id1(((Input))) ------>|Direct Connection|id3(Pin Complex XY)
	```
#### Routing Output Devices
For **Output Devices**, start at the Pin Complex Node and follow the signal through Audio Mixer(s)/Selectors to the physical output.Here are some examples of possible routings.

- **Option 1**: Pin Complex Node &rarr; Mixer/Audio Selector &rarr; Output (common):

	```mermaid
	flowchart LR
       id1(Pin Complex XY) -->|Signal flow|Aid2{Mixer A} -->|Signal flow|id5(((Output X)))
       id3(Pin Complex XY)-->id2[/Audio Selector/]-->id6(((Output X)))
	 ```
- **Option 2**: Direct connection from Pin Complex Node to Output:

	```mermaid
	flowchart LR
       id1(Pin Complex XY) ---->|Direct Connection|id5(((Output X)))
	```

> [!NOTE]
>
> Whether or not a signal traverses more than one Mixer Node depends on the Codec's design. What's important is to list all the "stations" a signal passes from the Pin Complex Node to the desired Output!

#### Routing Examples from ALC269

- **Internal Speakers** (Fixed):

	```mermaid
	flowchart LR
    	id1(Node 20: Speaker out) --> |Fixed path| id3{Mixer 12} --> id5(((Output 2)))
	```

- **Headphone Output**:

	```mermaid
	flowchart LR
    	id1(Node21: HP out) --> |possible path A| id3{Mixer 12} --> id5(((Output 2)))
    	id1(Node21: HP out) --> |possible path B| id4{Mixer 13} --> id6(((Output 3)))
	```
 	> [!NOTE]
  	> The number of possible paths depends on the number of connections a PinComplex Node provides. 
- **Internal Mic Input** (fixed/hardwired connection):

	```mermaid
	flowchart LR
    	   id1(((Input 9))) -->Aid2{Mixer 34} -->id2(Node 18: Mic Int. fixed)-.-> id3(Aux Return to Mixer 11)-.->id4(Etc.)
	```
- **Line Input**:
	
	```mermaid
		flowchart LR
   		   id1(((Input 8))) -->Aid2{Mixer 35} -->id2(Node 24: Mic Jack)-.-> id3(Aux Return to Mixer 11)-.->id4(Etc.)
	```

**💡 About Signal Flow**

The ALC 269 Codec includes an Aux Return to send (or return) the incoming signal back into the Output path for monitoring via Mixer 11 through either Mixer Nodes 12/13 or 15 (Mono). 

If you'd trust the arrows in the schematic, the existence of Mixer 11 wouldn't make any sense. That's why ***you need to follow the signal flow instead of the arrows!*** For the `PathMap`, you only need to enter the path following this formula: Input &rarr; Mixer &rarr; PinComplex Node.

#### Tracing possible paths
Since I want the Line-Out of my docking station dock to work, I need to assign some other Pin Complex Node to Mixer 13. 

We can use the .svg schematic to trace all available paths the codec provides and create a chart with it, which helps when transferring the data to a Platforms.xml fle later:

Node ID (Pin Complex)| Device Name/Type            | Path(s)               | EAPD
--------------------:|-----------------------------|-----------------------|:--------:
18 (In)              |Internal Mic                 | 9 - 34 - 18 (**FIXED**)|
20 (Out)             |Internal Speakers (S)        | 20 - 12 - 2 (**FIXED**)| YES
21 (Out)             |Headphone Output (S)         | 21 - 12 - 2 or </br>21 - 13 - 3|YES
23 (Out)             |Speaker at Ext Rear (M)      | 23 - 15 - 2 (Mono) |
24 (as Output)       |Mic/Line-In (Jack) (S)       | 24 - 12 - 2 or </br>24 - 13 - 3|
24 (as Input)        |(Jack) Mic at Ext Left       | 8 - 35 - 24 or </br> 9 - 34 - 24
25 (as Output)       |Speaker Ext. Rear (S) OUT Detect| 25 - 12 - 2 or </br>25 - 13 - 3
25 (as Input)        |Speaker Ext. Rear (S) IN Detect| 8 - 35 - 25 or </br>9 - 34 - 25
26 (as Output)       |Speaker at Ext Rear OUT HP Detect| 26 - 12 - 2 or</br>26 - 13 - 3
26 (as Input)        |Speaker at Ext Rear IN HP Detect| 8 - 35 - 26 or </br> 9 - 34 - 26 
27 (as Output)       |Speaker at Ext Rear OUT Detect| 27 - 13 - 3 or </br>27 - 12 - 2
27 (as Input)        |Speaker at Ext Rear IN Detect| 8 - 35 - 27 or </br> 9 - 34 - 27 or
29 Mono (as Input)   |Mono In                      | 8 - 35 - 29 or </br> 9 - 34 -29
30 (Digital Out)     |Speaker Ext. Rear Digital (S/PDIF)| 6 - 30|

After a many, many trials, I settled with the following routing:

Node ID (Pin Complex)| Device Name/Type            | Path(s)                | EAPD
--------------------:|-----------------------------|------------------------|:-----:
18 (In)              |Internal Mic                 | 9 - 34 - 18 (**FIXED**)|
20 (Out)             |Internal Speakers (S)        | 20 - 12 - 2 (**FIXED**)| YES
21 (Out)             |Headphone Output (S)         | 21 - 13 - 3            | YES
24 (as Input)        |(Jack) Mic at Ext Left       | 8 - 35 - 24            |
25 (as Input)        |Speaker Ext. (S) IN Detect   | 8 - 35 - 25            |
27 (as Output)       |Speaker Ext. Rear OUT Detect | 27 - 13 - 3            |

<details>
<summary><strong>Double-Checking</strong> (click to reveal)</summary>

##### Double-Checking against codec-dump_dec.txt
We can also use the codec dump to verify the routing. Here's an example for Node 21 which is the main output of the T530:

![Node21](https://user-images.githubusercontent.com/76865553/170473509-a3e96ded-c9db-4de5-9774-40b6ef094629.png)

As you can see, Node 21 has 2 possible connections (Node 12 and 13) and is currently connected to Node 13, which is one of the Audio mixers:

![Node13](https://user-images.githubusercontent.com/76865553/170470502-7c4952c7-b865-4b63-9d58-d74ec38fe278.png)

 And Node 13's final destination is Node 3, which is the HP out:

![Node3](https://user-images.githubusercontent.com/76865553/170470592-22c22176-f1f9-4aec-91b0-6b829c6bdbb1.png)
</details>

We will come back to the schematic later… 

---

[← **Previous:** Preparations](01_Preparations.md) | [**Next:** Create PathMap & Platforms.xml →](03_Create_Pathmap_Platforms-XML.md)
