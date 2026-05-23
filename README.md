# FMIPROT 0.31.1 (Beta)

**FMI Image Processing Toolbox (FMIPROT)** is a software designed to process digital image series from cameras and camera networks. It can acquire and process images from multiple camera networks on a single platform by adding connection information of the image repositories. It provides a graphical user interface to set up configurations and parameters to be used in the acquisition and processing of the images. 

The analysis can be run either using the GUI or via CLI with a single action that triggers a processing chain. The toolbox performs necessary tasks to acquire images from image repositories of the camera networks, process them and generate HTML reports with interactive plots along for visualization of the output data. The design allows using the toolbox with a job scheduler to run analysis for creating operational monitoring systems. 

Detailed information about the toolbox can be found on the [FMIPROT website](https://fmiprot.fmi.fi). 

*The software is developed under the MONIMET Project, funded by EU Life+ Programme (2013-2017) and further developed under the IDEAS-QA4EO and QA4EO-2 projects (2020-), funded by the European Space Agency.*

## Key Features

1. **Image acquisition** from multiple camera networks
2. **Storing scenario options** as files
3. **Generating reports** for scenario options and analyses results
4. **Multiple scenarios** and **multiple analyses** in each scenario
5. **Mask/ROI creation** by selection with GUI
6. **Filtering images** according to different means of thresholds
7. **Downloading and handling** images
8. **Quantitative image archive check**
9. **Expandable algorithms** by plugin system
10. **Customizable Plotting/Mapping** of results
11. **HTML and JS based reports** with interactive plots
12. **Cross platform** (open source)
13. **Configuring settings and running analysis** from command-line interface (and job scheduler)

## Processing Algorithms

The software has the following processing algorithms:

* **Color Fraction Extraction:** Calculates red fraction index, green fraction index, blue fraction index, brightness, luminance, red channel mean, red channel median, red channel standard deviation, green channel mean, green channel median, green channel standard deviation, blue channel mean, blue channel median, and blue channel standard deviation.
* **Vegetation Indices:** Calculates red fraction index, green fraction index, green-red vegetation index, green excess index.
* **Custom Color Index:** Calculates an index from a mathematical formula entered by the user using average values of red, green and blue channels in ROIs. The formula supports sums, differences, multiplication, and division and operation priority by using parentheses.
* **Snow Cover Fraction:** Calculates the fraction of snow covered pixels using georectification of the image and classification of pixels into snow and no-snow. Also provides the fraction without the georectification.
* **Snow Depth:** Calculates snow depth from the objects in the field by finding the intersection with the snow surface.
* **Timelapse Animation:** Creates a timelapse video file out of available images from the cameras.
* **Georectification:** Creates orthoimages and weightmasks by orthorectifying camera images. *(Not applicable for too many images, mainly intended to be included as a part of snow cover fraction algorithms and other testing purposes.)*

## Installation

Install Python 2.7, the required libraries listed in `requirements.txt`, and Python GDAL libraries. 

Run `fmiprot.py` with Python:
```bash
python fmiprot.py
```

## Documentation

For detailed documentation and tutorials, refer to `usermanual.pdf` and [fmiprot.fmi.fi](https://fmiprot.fmi.fi).

## Version Issues & Bug Reporting

The product is currently a beta version, thus it may crash unexpectedly. **Users should always save the setup file when there is a change** in the setup to prevent losing the changes and wasting effort.

On unexpected crashes, please send the log file and output from the terminal/console to `cemal.melih.tanis@fmi.fi`.

## Authors & License

**Authors:**
* Cemal Melih Tanis (`Cemal.Melih.Tanis at fmi.fi`)
* Ali Nadir Arslan (`Ali.Nadir.Arslan at uwasa.fi`)

*(c) 2026 Finnish Meteorological Institute*

**License:**
By running this program, the user agrees with the terms and conditions explained in the license file (`LICENSE`).
