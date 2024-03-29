FMIPROT 0.24.9 (Beta)
***************************************************************
FMI Image Processing Toolbox (FMIPROT) is a software designed to process digital image series from cameras and camera networks. It can acquire and process images from multiple camera networks on a single platform by adding connection information of the image repositories. It provides a graphical user interface to set up configurations and parameters to be used in the acquisition and processing of the images. The analysis can be run either using the GUI or via CLI with a single action that triggers a processing chain. The toolbox performs necessary tasks to acquire images from image repositories of the camera networks, process them and generate HTML reports with interactive plots along for visualization of the output data. The design allows using the toolbox with a job scheduler to run analysis for creating operational monitoring systems. Detailed information about the toolbox can be found in FMIPROT website (https://fmiprot.fmi.fi). The software is developed under the MONIMET Project, funded by EU Life+ Programme (2013-2017) (https://monimet.fmi.fi).
Current main functions of the software are,
(1) Image acquisition from multiple camera networks
(2) Storing scenario options as files
(3) Generating reports for scenario options and analyses results
(4) Multiple scenarios
(5) Multiple analyses in each scenario
(6) Mask/ROI creation by selection with GUI
(7) Filtering images according to different means of thresholds
(8) Downloading and handling images
(9) Quantitative image archive check
(10) Expandable algorithms by plugin system
(11) Customizable Plotting/Mapping of results
(12) HTML and JS based reports with interactive plots
(12) Cross platform (open source)
(13) Configuring settings and running analysis from command line interface (and job scheduler)
The software has following processing algorithms:
(1) Color Fraction Extraction: Calculates red fraction index, green fraction index, blue fraction index, brightness, luminance, red channel mean, red channel median, red channel standard deviation, green channel mean, green channel median, green channel standard deviation, blue channel mean, blue channel median, and blue channel standard deviation.
(2) Vegetation Indices: Calculates red fraction index, green fraction index, green-red vegetation index, green excess index.
(3) Custom Color Index: Calculates an index from a mathematical formula entered by the user using average values of red, green and blue channels in ROIs. The formula supports sums, differences, multiplication, and division and operation priority by using parentheses.
(4) Snow cover fraction: Calculates the fraction of snow covered pixels using georectification of the image and classification of pixels into snow and no-snow. Also provides the fraction without the georectification.
(5) Snow depth: Calculates snow depth from the objects in the field by finding the intersection with the snow surface.
(6) Timelapse animation: Creates a timelase video file out of available images from the cameras.
(7) Georectification: Creates orthoimages and weightmasks by orthorectifying camera images. (Not applicable for too many images, only for testing purposes.)
***************************************************************
AUTHORS
Cemal Melih Tanis Cemal.Melih.Tanis at fmi.fi
Ali Nadir Arslan Ali.Nadir.Arslan at fmi.fi
(c) 2020 Finnish Meteorological Institute
***************************************************************
LICENSE
By running this program, user agrees with the terms and conditions explained in the license file (LICENSE).
***************************************************************
VERSION ISSUES
The product is currently a beta version, thus it may crash unexpectedly. User should always save the setup file when there is a change in the setup to prevent losing the changes and wasting effort.
On unexpected crashes, please send the log file and output from the terminal/console to cemal.melih.tanis@fmi.fi.
***************************************************************
INSTALLATION
Compiled version:
Extract the archive ("fmiprot_#.#.#.zip" for Windows systems or "fmiprot_#.#.#.tar.gz" for Linux systems) to any directory. Run "fmiprot" in Linux systems and "fmiprot.exe" on Windows systems to start the program. Program can be run directly from file browser interface, i.e. using command line is not necessary, but it is advised.
Source code version:
Install Python 2.7, libraries in requirements.txt and python gdal libraries. Run fmiprot.py with python.
***************************************************************
For detailed documentation, refer to usermanual.pdf
***************************************************************
