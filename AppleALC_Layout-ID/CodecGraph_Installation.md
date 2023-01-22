# Getting Codec-Graph to work
Codec-Graph is a tool which visualizes the data contained in the `codec_dump.txt` you dumped earlier from runninng Linux. It creates a map of an audio CODEC's routing:

![Codec-Dump](https://user-images.githubusercontent.com/76865553/213944003-89744984-4df5-473c-8ae5-1b4d948a7d38.svg)


Core-i99 has released an updated and improved version of Codec-Graph which includes a GUI to simplify the file conversion. The generated visualization now includes both hex and decimal values.

## Instructions

### 1. Install Homebrew
- Go to https://brew.sh/
- Copy the command listed on the homepage to the clipboard
- Run Terminal, paste the command inand hit <kbd>Enter</kbd>
- Enter your Admin password when asked to begin the installation
- Once the Homebew installation is complete, you can install Graphwiz

**NOTE**: On macOS Catalina or older, you don't have to install Homebrew to get Graphwiz. You can use the [**.pkg installer**](https://github.com/5T33Z0/AppleALC-Guides/blob/main/AppleALC_Layout-ID/Tools/graphviz-2.40.1.pkg?raw=true) instead!

### 2. Install Graphwiz
- Enter `brew install graphviz` command in Terminal and hit <kbd>Enter</kbd>
- Once that's done you can now use CodecGraph

### 3. Install Python 3
Download and Install [**Python**](https://www.python.org/downloads/) 

### 4. Download Codec-Graph
- Visit Core-99's [**Codec-Graph**](https://github.com/Core-i99/Codec-Graph) repo
- Click on "Code" > "Download zip" and unpack it
- Open Terminal 
- Enter: `python3 ~/Downloads/Codec-Graph/Codec-Graph.py`
- This will open the GUI:</br> ![CGGUI](https://user-images.githubusercontent.com/76865553/213944025-ee8a9f97-e560-47fa-87c4-871324a6d40b.png)
- Click on "Select Codec Dump"
- Navigate to the `codec_dump.txt` and open it
- Codec Graph will generate `Codec-Dump.svg` and place it on the Desktop.
