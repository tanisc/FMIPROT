FMIPROT 0.15.2 (Beta)
***************************************************************
FMI Image processing tool (FMIPROT) is software designed as a toolbox for image processing for phenological and meteorological purposes, under the MONIMET Project, funded by EU Life+ Programme (2013-2017) (http://monimet.fmi.fi). The purpose of the software was to create a platform that communicates with the MONIMET project camera network in Finland, as linking the cameras from the network and downloading images according to temporal criteria automatically. At the moment FMIPROT can communicate with multiple camera networks. The software provides a graphical interface to select all relevant criteria to analyze the images and view results on plots and maps. The software is expandable by adding various processing algorithms of images taken by cameras by users. Current functions of the software are,
(1) Communication with multiple camera networks
(2) Storing scenario conditions as files
(3) Generating reports for scenario options and analyses results
(4) Multiple scenarios
(5) Multiple analyses in each scenario
(6) Mask/ROI creation by selection with GUI
(7) Filtering images according to different means of thresholds
(8) Downloading and handling images
(9) Quantitative image archive check
(10) Expandable algorithms by plugin system
(11) Customizable Plotting/Mapping of results
(12) Windows and Linux support.
The software has two processing algorithms:
(1) Color Fraction Extraction: Calculates red fraction index, green fraction index, blue fraction index, brightness, luminance, red channel mean, red channel median, red channel standard deviation, green channel mean, green channel median, green channel standard deviation, blue channel mean, blue channel median, and blue channel standard deviation.
(2) Vegetation Indices: Calculates red fraction index, green fraction index, green-red vegetation index, green excess index.
(3) Custom Color Index: Calculates an index from a mathematical formula entered by the user using average values of red, green and blue channels in ROIs. The formula supports sums, differences, multiplication, and division and operation priority by using parentheses.
***************************************************************
AUTHORS
Cemal Melih Tanis Cemal.Melih.Tanis at fmi.fi
Ali Nadir Arslan Ali.Nadir.Arslan at fmi.fi
(c) 2017 Finnish Meteorological Institute
***************************************************************
LICENSE
See license.txt
***************************************************************
VERSION ISSUES
The product is currently a beta version, thus it may crash unexpectedly. User should always save the setup file when there is a change in the setup to prevent losing the changes and wasting effort.
On unexpected crashes, please send the log file and output from the terminal/console to cemal.melih.tanis@fmi.fi.
***************************************************************
KNOWN BUGS
Frequency - importance - problem
Often - minor - the previous menu button shows 'Customize Graph' instead of showing nothing when user is in the main menu.
Rarely - minor - 'EOF Error' when connecting to FTP servers.
Always - minor - "Enable" checkboxes in the various menus displays unchecked when switching scenarios. Although the visibility is unchecked, values are actually checked, so it does not change and mess up with the scenario options. Checkboxes display checked again when mouse cursor moves over them.
***************************************************************
INSTALLATION
***************************************************************
Extract the zip archive ("fmiprot_#_setup.zip") to any directory. Run "install" to run the installation. Installation dialog is simple and straightforward. (Optionally) Choose the directory to for the software to be installed, the local image directory where images from online camera networks will be downloaded when using the software and the directory where analysis results will be saved when using the software. Choose directories that your user in your computer has the permission to write. If you do not know what that means, you can leave the default directories as chosen. Click "Install". Read the license agreement and click "Accept" if you accept it.
If the installer finds any older installation of the software, it will ask a few options. Choose them accordingly and continue installation.
In Ubuntu, installer also creates a link where the program can be started in "Dash". Simply search your applications to find the link.
In Windows, installer also creates a link in your desktop where the program can be started.
In others systems, or if somehow you have lost the links, Run "fmiprot" from the directory you have installed FMIPROT to run the software.
***************************************************************
For detailed documentation, refer to usermanual.pdf
***************************************************************
