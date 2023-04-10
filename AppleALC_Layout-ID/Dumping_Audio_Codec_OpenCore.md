# Dumping the Audio Codec with OpenCore

1. Download the **DEBUG** version of [OpenCore](https://github.com/acidanthera/OpenCorePkg/releases) and extract it
2. Mount your EFI
3. Replace the following files in your EFI Folder by the ones from the Debug build:
	- `EFI/OC/OpenCore.efi`
	- Drivers present in `EFI/OC/Drivers` 
	- Add`AudioDXE.efi` to `EFI/OC/Drivers` as well if it's not present
4. Open your `config.plist`
5. Under `Misc/Debug`, enable `SysReport`
6. Under `UEFI/Drivers`, add and enable `AudioDXE.efi`:</br>
7. Safe and reboot. Reboot will take a bit longer than usual 
8. Once the system is running again, Mount your EFI again
9. The root of your EFI should contain a folder "SysReport". Inside it, there will be an "Audio" folder as well, containing the codec dump labeled `Codec0.txt`: </br>![](/Users/5t33z0/Desktop/SysReport.png)
10. Copy the "SysReport" folder to your Desktop
11. Revert OpenCore files back to the Release Version
12. Open your `config.plist` again
13. Disable `SysReport` Quirk and `AudioDXE.efi` Driver
14. Save your `config.plist`
