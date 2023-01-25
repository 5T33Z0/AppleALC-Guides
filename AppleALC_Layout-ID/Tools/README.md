# Instructions

This is the old workflow for converting Codec Dumps. The new one can be found here

## Install graphviz

- Install [**Python 3**](https://www.python.org/downloads/) if you haven't already
- Install either [**MacPorts**](https://www.macports.org/install.php) or [**Homebrew**](https://brew.sh/) (may require reboot afterwards)
- Next, install [**graphviz**](https://graphviz.org/) via Terminal:
	- If you are using **Homebrew**, enter `brew install graphviz` 
	- If you are using **MacPorts**, enter `sudo port install graphviz`
- Move the `codec_dump.txt` into the "Codec-Graph" folder

## Converting the Codec Dump

1. Download and unzip [**Codec-Graph.zip**](https://github.com/5T33Z0/AppleALC-Guides/blob/main/AppleALC_Layout-ID/Tools/Codec-Graph.zip?raw=true)
2. Copy the `Codec-Graph` folder to the Desktop and enter it
3. Double-click `Convert_Dump`. 
4. Follow the on-screen instructions to convert the Codec dump
5. This creates 3 new files inside the "output" folder:
	- **`codec_dump_dec.txt`** &rarr; Codec dump converted from Hex to Decimal. We need it since the data has to be entered in decimals in AppleAlC's .xml files.
	- **`codecdump.svg`** – Schematic of the Codec.
	- **`codecdumpdec.svg`** &rarr; Schematic of the Codec converted from hex to decimal. We will work with this primarily. You can open it in the web browser to view it in full size.
6. Next, run PinConfigurator
7. Select "File > Open…" (⌘+O) and open "codec_dump.txt"
8. This will extract the available audio sources from the Codec dump
9. Select File > Export > **`verbs.txt`**. It will will be stored on the Desktop automatically. We may need it later.
