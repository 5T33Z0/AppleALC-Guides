# How to create/modify a Layout-ID for AppleALC

## X. Integrating the `PinConfig` into the AppleALC source code
Now that we (finally) have our `PinConfig`, we have to integrate it into the AppleALC source code. Depending on your use case, the workflow differs. So pick a scenario which best suits your use case.

### Finding an unused Layout-ID number
In order to find a yet unused Layout-ID for your Codec, you have to check which Layout-IDs exist already and chose a different one in the range from 11 to 255:

- In the AppleALC-master folder, browse the `Resources` folder
- Find the folder representing your Codec (in my example it's `ALC269`)
- As you can see, ALC269 has a lot of Layout-IDs already.
- Pick a Layout-ID which is not used already (make a mental note or write it down somewhere)

I am picking Layout-ID 39 because a) it's available and b) followed by by the Lenovo W530 which is the workstation version of the T530.

> [!IMPORTANT]
>
> Layout-IDs 1 to 10 are reserved. Layout-IDs 11 to 255 are user-assignable, though values above 99 are rarely used in practice. 

#### Scenario 1: Modifying data of an existing Layout-ID

1. Open "codec_dump_dec.txt"
2. Copy the "Vendor-Id" in decimal (= `CodecID` in AppleALC)
3. Locate the `PinConfigs.kext` inside AppleALC/Resources
4. Right-click it and select "Show Package Contents"
5. Inside the Contents folder, you'll find the "info.plist"
6. Open it with a Plist editor. I am using PlistEdit Pro because it automatically converts `<data>` fields to base64 which we need.
7. All PinConfigs and the Layout-ID they are associated with are stored under:
	- IOKitPersonalities
		- as.vit9696.AppleALC
			- HDAConfigDefault
8. Use the search function (⌘+F) and paste the "Vendor Id". In my case it's "283902569". This will show all existing Layout-IDs your Codec.
9. For my test, Im am using entry number 162 as a base, since it's for the same Codec and was created for the the Lenovo X230 which is very similar to the T530 and works for my system:</br>![infoplist](https://user-images.githubusercontent.com/76865553/170472084-0dc4d888-1987-4185-a5b9-153e6fb2225c.png)
10. Highlight the dictionary and press ⌘+D. This will duplicate the entry.
11. Add/change the following data to the new entry:
	- In the `Codec` String: Author name (Yours) and description
	- In `ConfigData`, enter the PinConfig data we created in PinConfigurator (and saved in "verbs.txt")
	- Add `WakeConfigData`. It's part of the "verbs.txt":</br>![verbspcfg](https://user-images.githubusercontent.com/76865553/171962726-acbb19cd-e231-43f1-9499-6025f6f1898a.png)
	- Change the `LayoutID` the PinConfig Data should be associated with. 
12. This is the resulting entry:</br>![PCfginfopl](https://user-images.githubusercontent.com/76865553/171962769-834652b6-96e3-462e-bc39-3ed7e9c258af.png)
13. Highlight the raw text of this entry, exactly as shown below (whitespace included):
![01CopyPinCfgPlist](https://user-images.githubusercontent.com/76865553/173181910-77013179-0a5c-43b1-b2b6-1040d334e20b.png)
14. Copy the raw text to the Clipboard
15. Close the Plist Editor but **DON'T SAVE THE FILE!!!**

> [!IMPORTANT]
>
> I've noticed that PlistEdit Pro and Xcode tend to mess up huge plist files and change formatting and data which shouldn't be changed and which you didn't even touch. This will result in your Pull Request being rejected. There have also been reports about Xcode changing `<integer>` to `<real>` which is a nightmare. Because if this slips into the source code unnoticed it will cause kernel panics during boot on the target system, which happened with the release of AppleALC 1.7.3.

To avoid this, use Visual Studio Code or TextEdit to paste the entry instead:

1. Open the `info.plist` again in Visual Studio Code (or TextEdit)
2. Scroll all the way to the end of the `HDAConfigDefault` array containing the entries for the PinConfigs and paste your entry right before the end of the `</array>` (you can use the vertical lines as a visual guide):</br>![PasteLayout01](https://user-images.githubusercontent.com/76865553/177260440-96c56b62-ef75-4354-a3f8-b757116e32cf.png)
3. Ensure that all keys in the dictionary consist of 1 line only: `<key>AAAAAA</key>`. Fix any line breaks that may be in raw text.
4. Save the file.
5. Open it again in Xcode or a Plist Editor and verify that the entry is in the correct location (at the end):</br>![02Verify](https://user-images.githubusercontent.com/76865553/173181933-5dff03a6-fbd0-46d1-bd99-40d9ee2e5b29.png)

Now that we got the PinConfig out of the way, we can continue integrating the rest of the files into the AppleALC Source Code…

## XI. Add `Platforms.xml` and `layout.xml` to `info.plist`

Now the we have edited all the files we need, we have to integrate them into the AppleALC Source Code. As mentioned [earlier](01_Preparations.md#files-we-have-to-work-on), there are 2 info.plists which have to be edited in the AppleALC Source Code. In this case, I am referring to the second one, located inside the ALCXXX folder. In my case the one in `AppleALC/Resources/ALC269`.

- Open the `info.plist`
- Look for the `Files` Dictionary:</br>![Info01](https://user-images.githubusercontent.com/76865553/171393791-6c8f90ab-e860-42e0-940a-1b2fa26a1fc6.png)
- Open the `Layouts` Dictionary
- Duplicate one of the Dictionaries inside it, doesn't matter which one
- Move the Dictionary to the end of the list (makes it easier when committing the file for a Pull Request).
- Expand it:</br>![Info02](https://user-images.githubusercontent.com/76865553/171393919-0797081d-3296-4588-be78-7213e819a36a.png)
- Change the following details:
	- **Comment**: Author and Codec/Device
	- **Id**: Enter the Layout-ID you are using
	- **Path**: layoutXX.xml.zlib (XX = the chosen layout-id number. During compilation, the .xml file will be compressed to .zlib so the path has to point to the compressed version)
- Do the same in the "Platforms" section but use "PlatformsXX.xml.zlib" as "Path" instead:</br>![Info03](https://user-images.githubusercontent.com/76865553/171394021-c85dbda3-e248-4445-85b1-8c5d7c15cf9c.png)

> [!IMPORTANT]
>
> If these entries don't exist, the AppleALC.kext will be compiled but your Layout-ID entry won't be included, aka no Sound!

---

[← **Previous:** Create PinConfig](05_Create_PinConfig.md) | [**Next:** Compiling AppleALC →](07_Compiling_AppleALC.md)

