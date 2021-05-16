# EbootCK
The Eboot Customization Kit

EbootCK is a multiplatform utility that aims to be a central hub to dealing with PSX eboot customizations.

Installation:
EbootCK depends on leaked proprietary programs for AT3 (at3tool.exe) and PMF (UMD Stream Composer) conversions which are not distributed with EbootCK as well as Python and PyQt. The script expects to have everything in the EbootCK folder, but the folder itself can be placed anywhere.

Functions:
- Preview eboot images
- Preview audio
- Preview video
- Save to a folder and .zip for distribution
- Convert media files to at3 (audio or video)
- Convert media files to avi for use in UMD Stream Composer
- Add a valid pmf icon header to mps
- Adds a simple metadata text file
- Automatically makes a preview copy after loading an icon1/snd0 or converting audio/video

Previewer Controls:
- Right click icon: Toggle video/audio preview
- Left click icon: Toggle fancy overlay
- Right click bg: Refresh preview screen
- Left click bg: Toggle boot image preview

Future Features:
- Sanity check on pmf/at3 file sizes for over the 500KB limit
- Suggest removing X amount of seconds from audio/video if over limit