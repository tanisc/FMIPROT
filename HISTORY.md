Version 0.21.1 (Beta)
Requirement file names fixed in conda scripts.
libglu added to linux requirements.
Bug fix (Minor): Latest one month temporal selection code.
Setup report jquery link changed to Http to Https.
Bug fix (Minor): Preview filename fix for temporarily added cameras.
Exception on failures in "downloadas" enabled.
Improvements and bug fixes in image fetching.

Version 0.21.1 (Beta)
Bug fix (Minor): Opening user manual and license from GUI in source-code mode fixed.
Documentation updates for 0.21.0 updates are done.
Library versions fixed.
netCDF library version requirement added.
Requirement file names changed to be compliant with conda cloud prefixes.
Importing moviepy fixed.
Clean flag added for build scripts.


Version 0.21.0 (Beta)
Snow cover detection algorithm is added.
Snow cover fraction algorithm is added.
Snow depth algorithm is added.
Georectification algorithm is added.
Animation creation is added.
Auto GUI scaling is added for 4K screens. (Doesn't work with multiple screens)
Memory usage limit option is added. (Only for some processes.)

Version 0.20.5 (Beta)
Bug fix (Major): Removing old values in the merging mode fixed. The problem was that the dates were removed correctly but values were not, resulting a shift in the new results instead of adding new results.

Version 0.20.4 (Beta)
Bug fix: Filtering images for "Latest 1 hour" temporal selection is fixed.

Version 0.20.3 (Beta)
Bug fix: Reading integers, nan and inf in old results in merge results mode fixed.
Bug fix: Setup file and result directory from CLI is converted to realpath, which was causing crash in results viewer.
Bug fix/postpone: Number of connection for FTP downloads disabled until it is fixed.

Version 0.20.2 (Beta)
Millisecond support is added for filename conventions. ('%3' for 3 digits and '%L' for 6 digits milliseconds)

Version 0.20.1 (Beta)
A bug in checking image file if valid when creating masks for separate ROIs fixed.

Version 0.20.0 (Beta)
Major and minor bugs are fixed.
Command line interface options are introduced.
Images downloaded for cameras that are not added to the toolbox but stored in setup files are now stored under "tmp" directory. (i.e. setup files created in any instance/platform can be run in another instance/platform directly)
Camera network proxies are introduced.
File extentions are added. Most of old extentions are still supported, but not tested. CNIF extention, output .ini file extention are now ".tsvx". output .dat file extention is now .tsv.
Preview image times are now stored in setup files, used in later runs for preview in GUI and reports.
Documentation is moved from "doc" directory to the main directory.
"Update preview images" option for all cameras is added to the menu.
"Generate setup report with analysis results" is moved to "Processing settings" menu from "Results" menu and the option is now stored as a setting.

Version 0.15.3 (Beta)
A major bug in the functions for listing images is fixed.

Version 0.15.2 (Beta)
Minor bugs are fixed:
- Installer error on copying preview images.
- Listing preview pictures for cameras which has images in local directories.
- Old polygons on the preview image were still visible after "Duplicate without masking".
Content and format of the preview images in setup reports are modified. Image showing polygon numbers are provided without the background to increase visibility.

Version 0.15.1 (Beta)
Number of FTP connections are not available for Windows anymore. Due to a bug, it is disabled until it is solved.
Instead of one file (only 'fmiprot' or 'fmiprot.exe'), the program is distributed also with library files. (Does not affect the usage, altough it is faster to initialize now.) The structure is changed for the program to be able to run in the computers with strict restrictions in user control.

Version 0.15.0 (Beta)
Versions are named as "V#.#" anymore, "#.#.#" are used from now on.
License agreement is added.
Installation program is added and it detects an older installation if the directory with older installation is selected so that use can choose different options about the updating the program and the settings.
Minor/major bugs are fixed.
GUI is updated, effects and colors are added.
New algorithm: "Custom color index" is added.
"Tools" menu is added.
Plugin system is changed (simplified) and "Add Plugin" and "Remove Plugin" options are added under "Tools" menu.
"Help" menu is added and relevant menus are moved under it.
"Log" window is added.
Progress of many steps can be followed from "Log", including progress bars for scenarios, analyses and ROIs.
"Log pane" content is changed. Now it shows the last event happened.
"Log menu" is added under "Help" menu.
"License agreement" window option is added under "Help" menu.
User manual now can be opened from "Help" menu.
"Add camera network from an online CNIF", a camera network wizard is added.
"Create directories for each result" option is removed.
"Download images" options under preview image menus now have temporal selection dialog.
New temporal selection modes are added. Now the analyses can be also done only images from yesterday, today, for images not 1 hour older than the last image taken and for the last image taken.
"Image thresholds", "ROI thresholds" and "Pixel threshold" menu contents are moved altogether under "Thresholds" menu.
"Masking" enu is now "Masking/ROIs" menu.
Polygons are now also considered as different ROIs and analyses are done separately for each polygon if the relevant option is enabled. (Union of all polygons is also analyzed.)
Can not add more polygons now if there is only one polygon and no point is selected.
Setup and post-processing reports now have 4 types of preview images for each scenario to be used for different purposes.
Polygon colors for setup reports and masking preview are updated. Selection of polygon colors now shows the color instead of hex values.
"Copy polygons from other scenarios..." option is added to copy ROIs easier. Polygon coordinates are not editable by entry anymore.
"Results" menu is now "Result Viewer".
A new "Results" menu is added.
Modes for the storage of results are added. For the same exact setup, old and new results can be merged (automatically) during analyses.
"Generate setup report with analysis results" option is added. (Enabled by default)
Custom directories now can selected to view results without changing the results directory.

V0.14 Beta
Major/minor bugs are fixed.
"Connection Settings" menu is added.
Passive/active mode for FTP connections option is added.
Multiple FTP connections option (1-10) is added.
Download online images from servers option is moved to "Connection Settings" menu.
MONIMET camera network is removed and MONIMET Demo camera network is added.
Polygons in setup reports are now drawn as vertices with the color selected in "Masking menu", instead of shading the area out of polygons.
Post processing reports, which are setup reports including results with interactive charts are added. Post-processing reports are produced automatically at the end of analysis runs ("Run all scenarios" and "Run scenario").
"Open local image directory" button is added to camera selection menu.
Passwords are now asked once per run for camera network connections.  Incorrect password exception for FTP connections added.  "Processing settings" menu is added. Camera time zone support is added.
Time zone conversion is available if CNIF or filename formats have time zone information. (Time zone information cannot be added to CNIFs automatically at this point)
"Color fraction extraction" analysis now also calculates statistical information for image channels.

V0.134 Beta
Major bugs are fixed.
Scenarios now can be named.
Certain cameras now can be selected before "Download all images" and "Quantity Report" options.
Scrollbars are added where necessary.
Format of the results files are changed and metadata files are added.
Format of the setup reports is edited slightly.
In masking preview menu, polygons are now also visible when switching between preview images.

V0.133 Beta
Major bugs are fixed.
Image folders now will be created in the first run and after adding a new network/camera.
Now polygons are also visible when selecting preview image in the masking menu.
Message texts in multiple message windows are edited.

V0.132 Beta
Major bugs are fixed.

V0.131 Beta
Major bug (Improper display help popups in the camera network manager) is fixed.

V0.13 Beta
Multiple camera network support is added.
"Camera network manager" is added.
Structure of setup files is changed. (Old structure is still supported.)
Menu bar order is changed.
"Run" menu is removed.
"Run current scenario…" option is moved under "Scenario" menu.
"Run all scenarios…" option is moved under "Setup" menu.
"Camera network" menu is renamed as "Camera networks".
"Camera network manager" and "Single directory wizard" are added under "Camera networks" menu.
"Camera information" in the camera menu is removed.
"Camera metadata…" option is added under camera menu.
"Enable" option in "Masking" menu is replaced with "Display previews with polygons" option.
Setup reports now also have masked preview images.

V0.126 Beta
"Settings" menu is added.
"Proxy settings" are added.
"Storage settings" are added.
"Export Settings" and "Import Settings" options are added.
Results and image directories and download new images from FTP server option are now set up in "storage settings" menu.
"Image options" menu is deleted from main menu.
"Quantity check" and "Download all images" options are moved under new "Camera network menu" and "Online images" menu is deleted.
Setup report design is improved.
User Manual is updated.

V0.125 Beta
Visual details of the Interface is updated.
"Configuration" is now named as "Setup".
"Analysis" is now named as "Scenario".
"Calculation" is now named as "Analysis".
Analysis "Vegetation indices" is added.
Exclusion of burned pixels for "Color Fractions" analysis is added.
Luminance calculation for "Color Fractions" is added.
Threshold selection is divided into three groups and new values to be used as thresholds are added.
 "Duplicate without masking" options is added under "Scenario" menu in menu bar.
Color and line width options for masking interface are added and dashed lines are converted to continuous lines.
"Download all images" options is added under "Image Options".
"Images" menu is now named as "Image Options".
"Local Images" menu is now named as "Local Storage".
Order of the main menu is changed.
"Run all" option is added to the main menu.
"Size" option is added for the plots in "Results" menu.
"Axes" menu is added under "Customize Graph" menu.
"Histogram" analysis is removed from the software since it causes software to crash when applied on many images. It will be added after the extensive memory management is implemented.
Major bugs are fixed.
Minor bugs are fixed.
User Manual is updated.

V0.122 Beta
Major bug is fixed.
User Manual is updated.
Correction in Usage/Menu/Thresholds

V0.121 Beta
Major bug is fixed.

V0.12 Beta
Major bug is fixed.

V0.11 Beta
Readme introduction is updated.
Release notes are added to Readme.
User Manual introduction is updated.
Release notes are added to User Manual.
