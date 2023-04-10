# Dumping the Audio Codec with OpenCore

1. Download the **DEBUG** version of [OpenCore](https://github.com/acidanthera/OpenCorePkg/releases) and extract it.
2. Mount your EFI.
3. Replace the following files in your EFI Folder by the ones from the Debug build:
	- `EFI/OC/OpenCore.efi`
	- Drivers present in `EFI/OC/Drivers` 
	- Add`AudioDXE.efi` to `EFI/OC/Drivers` as well if it's not present
4. Open your `config.plist`.
5. Under `Misc/Debug`, enable `SysReport`.
6. Under `UEFI`, enable `Connect Drivers`.
7. Under `UEFI/Drivers`, add and enable `AudioDXE.efi`.
8. Safe and reboot. Reboot will take a bit longer than usual. 
9. Once you're back in macOS, Mount your EFI again.
10. Navigate to the EFI partition. It should contain the folder "SysReport". The codec dump will be located in the "Audio" folder as `Codec0.txt`: </br>![SysReport](https://user-images.githubusercontent.com/76865553/230842080-4d8741f6-aefc-4546-95be-3c6fb922f3ad.png)
11. Copy it to your Desktop
12. Revert OpenCore files back to the Release version
13. Open your `config.plist` again
14. Disable the following:
	- `SysReport` Quirk
	- `AudioDXE.efi` Driver
17. Save your `config.plist`.

Continue with step [III of the guide](https://github.com/5T33Z0/AppleALC-Guides/tree/main/AppleALC_Layout-ID#iii-extracting-data-from-the-codec-dump)
