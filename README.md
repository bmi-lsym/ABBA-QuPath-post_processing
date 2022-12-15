# ABBA-QuPath-post_processing
Scripts for quantification of the data resulting from the ABBA-QuPath pipeline for atlas registration of the serial brain images


Manual for the post-ABBA/QuPath quantification script by Olexiy Kochubey.

QuPath is an open source bioimage analysis software developed at the University of Edinburgh by Dr. Peter Bankhead and colleagues (https://doi.org/10.1038/s41598-017-17204-5), and can be
  found at https://qupath.github.io/ 

ABBA is a tool developed at Bioimaging and Optics Platform (BIOP) at EPFL, Lausanne, by Dr. Nicolas Chiaruttini (@NicoKiaru), and can be found at https://github.com/BIOP/ijp-imagetoatlas

The purpose of the current script is to process the data following the ABBA-QuPath pipeline for brain-to-atlas registration and detection of objects throughout the brain.
The description of the ABBA-QuPath piplene can be found here: https://biop.github.io/ijp-imagetoatlas/

Functionality:   
 - reading the transformed Allen Brain Atlas ROIs and object detection data from a QuPath project(s) 
 - correction for accidental side swaps of detached slice pieces during mounting   
 - quantification of the number/density of detected objects per brain area
 - summarizing these quantifications across the atlas hierarchy for the structures of interest and versus the coordinates of slicing axis
 - visualization of the data at the level of Jupyter notebook
 - averaging of the quantifications across multiple brains and plotting of the individual and average results is currently realized in IgorPro  
 
Prerequisites:

 - installed QuPath (tested with v. 0.3.2)
 - installed Python environment including dependency packages (tested using Anaconda3 under Windows, Python 3.7)
 - the brain images was registered to the Allen Brain Atlas using ABBA-QuPath pipeline (see above)
 - transformed atlas ROIs were imported back to QuPath using an "ABBA extension" from BIOP (https://github.com/BIOP/qupath-extension-abba). Multiple QuPath projects per brain can be handled. 
 - detections of cells or other objects (currently, only one color channel is supported), were done in QuPath (see QuPath_scripts/ for example detection codes)
 - a groovy code QuPath_scripts/pixel_to_Atlas_transform.groovy should be executed on the QuPath project to extract the transformed atlas coodrinates of detections and annotations


Installation:
 -  unzip the package into a temporary folder 
 -  create a new conda environment called "abba" by running the following command in the terminal, while under the (base) environment and in the temporary folder containing the Setup/abba_env.yml file:
        conda env create -f abba_env.yml 
             -> Note that it is possible to give the environment another name by using the following command: 
             -> conda env create --name another_name -f abba_env.yml
 -  to complete the installation of paquo package (https://github.com/bayer-science-for-a-better-life/paquo), move the file Setup/.paquo.toml into the folder c:\Anaconda3\envs\abba\ or similar as appropriate; do not leave this file in the same sub-folder as the Jupyter notebook.
         Edit the line inside the file which points to the QuPath installation folder, it should read similar to the following:  
         qupath_dir = "C:/QuPath/QuPath_0_3_2/"
 - move the files "LSYM_ABBA_QuPath.py", "ABBA_QuPath_post_processing.ipynb" and the sub-folder "atlas_ontology" together into some working folder, for example "d:\MyFolder\ABBA_QuPath_scripts"


Starting up:
 - activate the environment in conda with a command: 
        conda activate abba
 - change the working folder to the one containing Jupyter notebook file ABBA_QuPath_post_processing.ipynb, or any of its parents, for example:
        chdir d:\MyFolder\ABBA_QuPath_scripts
 - start jupyter notebook:
        jupyter notebook 
 - navigate to the notebook file and run it


Usage:
 - follow the instructions given as comment lines
 - edits are necessary to specify the input file (i.e. ABBA saved state), and the output path for storing the processing results  
 - automatically generated index file in MS Excel format needs manual cross-checking and changes if necessary
 - type of the output data (e.g. list of atlas acronyms, selection of terminal vs non-terminal leaves of the atlas tree hierarchy, etc.) is configurable 
 - results are stored at the specified path with the specified filename prefixes (output format can be chosen between .csv and .xlsx)
 - further processing and plotting options for the output data (in .csv format) are available as scripts with GUI in IgorPro (see "IgorPor_tools" sub-folder)  
