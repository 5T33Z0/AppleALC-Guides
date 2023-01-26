# Getting Codec-Graph to work
Core-i99 has released an updated and improved version of Codec-Graph for Python 3 which includes a GUI to simplify the file conversion. Codec-Graph is a tool for visualizing the data contained within the `codec_dump.txt` obtained from Linux. It utilizes graphviz to generate a schematic of an audio CODEC's routing. The generated .svg now includes both hexadecimal as well as decimal values:

![Codec-Dump](https://user-images.githubusercontent.com/76865553/213944003-89744984-4df5-473c-8ae5-1b4d948a7d38.svg)

## Instructions (macOS)

### 1. Install MacPorts or Homebrew
Install either 

- [**MacPorts**](https://www.macports.org/install.php) (macOS Package Installer) or 
- [**Homebrew**](https://brew.sh/)

For me, MacPorts worked much better than Homebrew, which gave me a lot of errors.

### 2. Install graphviz
Next, install [**graphviz**](https://graphviz.org/).

- Open Terminal and enter one of the following commands:
	- If you are using **MacPorts**, enter `sudo port install graphviz`
	- If you are using **Homebrew**, enter `brew install graphviz` 

### 3. Install Python 3 (optional)
MacPorts/Homebrew should have installed Python 3 already since it's a dependency for graphviz. But just to make sure, sift through the installation log to verify. If it's installed already, skip to step 4, if it isnt, download and Install [**Python 3**](https://www.python.org/downloads/) yourself.

### 4. Download Codec-Graph
- Dowload the latest release of [**Codec-Graph**](https://github.com/Core-i99/Codec-Graph/releases) and unzip it
- Open Terminal 
- Enter: `python3 ~/Downloads/Codec-Graph-Release/Codec-Graph.py`
- This will open the GUI:</br> ![CGGUI](https://user-images.githubusercontent.com/76865553/213944025-ee8a9f97-e560-47fa-87c4-871324a6d40b.png)
- Click on "Select Codec Dump"
- Navigate to the `codec_dump.txt` and open it
- Codec Graph will generate a svg file and ask the user where to save it.
- Continue with the [guide](https://github.com/5T33Z0/AppleALC-Guides/blob/main/AppleALC_Layout-ID/README.md#converting-the-codec-dump)
