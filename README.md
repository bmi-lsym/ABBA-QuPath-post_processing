# ABBA-QuPath post-processing tools

Here one can find scripts for quantification of the data which result from the ABBA-QuPath pipeline for atlas registration of the serial brain images. The scripts deposited here were written by Dr. Olexiy Kochubey in the Laboratory of Synaptic Mechanisms (Prof. Ralf Schneggenburger), Brain Mind Institute, EPFL, Lausanne, Switzerland.

QuPath is an open source bioimage analysis software developed at the University of Edinburgh by Dr. Peter Bankhead and colleagues (https://doi.org/10.1038/s41598-017-17204-5), and can be found at https://qupath.github.io/ 

ABBA is a tool developed at Bioimaging and Optics Platform (BIOP) at EPFL, Lausanne, by Dr. Nicolas Chiaruttini (@NicoKiaru), and can be found at https://github.com/BIOP/ijp-imagetoatlas

The description of the ABBA-QuPath atlas registration piplene can be found here: https://biop.github.io/ijp-imagetoatlas/


Below is the description of the tools serving two different purposes: 1) to quantify the number/density of detected objects (like fluorescent cells, etc.) in the atlas-registered image stack throughout the regions of the Allen Brain Atlas; 2) to identify and quantify the areas that were expressing optgenetic constructs and were illuminated by light emanating from the tips of optic fiber implants 


------------------------------------ 


1) The package for quantification of detected objects across the registered brain (i.e. across the atlas regions). Package content: all files and sub-folders except the "Fibers_and_cones" sub-folder. Language: Python for the main processing script, and IgorPro macro language for GUI-assisted averaging across brains and customizable visualization.

Functionality:   
 - reading the transformed Allen Brain Atlas ROIs and object detection data from a QuPath project(s) 
 - correction for accidental side swaps of detached slice pieces during mounting   
 - quantification of the number/density of detected objects per brain area (multiple color channels, i.e. QuPath classifications supported)
 - summarizing these quantifications across the atlas hierarchy for the structures of interest and versus the coordinates of slicing axis
 - visualization of the data at the level of Jupyter notebook
 - averaging of the quantifications across multiple brains and plotting of the individual and average results is currently realized in IgorPro  
 
Prerequisites:

 - installed QuPath (tested with v. 0.3.2)
 - installed Python environment including dependency packages (tested using Anaconda3 under Windows, Python 3.7)
 - the brain images was registered to the Allen Brain Atlas using ABBA-QuPath pipeline (see above)
 - transformed atlas ROIs were imported back to QuPath using an "ABBA extension" from BIOP (https://github.com/BIOP/qupath-extension-abba). Multiple QuPath projects per brain can be handled. 
 - detections of cells or other objects were done in QuPath (see QuPath_scripts/ for example detection codes)
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
 - activate environment in conda with the command: 
        conda activate abba
 - change the working folder to the one containing Jupyter notebook file ABBA_QuPath_post_processing.ipynb, or any of its parents, for example:
        chdir d:\MyFolder\ABBA_QuPath_scripts
 - start jupyter notebook:
        jupyter notebook 
 - navigate to the notebook file and run it


Usage:
 - follow the instructions given as comment lines in Jupyter notebook
 - edits are necessary to specify the input file (i.e. ABBA saved state) and the output path for storing the results  
 - automatically generated index file in MS Excel format needs manual cross-checking and changes if necessary
 - type of the output data (e.g. list of atlas acronyms) is configurable 
 - results are stored at the specified path with the specified filename prefixes (output format can be chosen between .csv and MS Excel for the end results)
 - further processing/plotting options for the output data in .csv format are available as GUI enabled scripts in IgorPro (see "IgorPor_tools" sub-folder)
 
------------------------------------ 
 
2) The GUI-assisted package for quantification of brain areas expressing optogenetic construct AND illuminated by light during experiments. Package content: sub-folder "Fibers_and_cones". Language: Jython for ImageJ as the main processing script, and optional Python scripts to post-process the .csv output files. Such analysis was previously described (see Baleisyte et al., 2022, Cell Reports; doi: 10.1016/j.celrep.2022.110850) and was performed in IgorPro in that study. This tool is a functionally improved and more user-friendly version of that algorithm which now runs under ImageJ / FIJI. 

Functionality:
 - reading the TIFF RGB stack or multi-channel hyperstack files containing atlas-registered images of the post-hoc brain sections with the optic fiber tracks
 - fitting the cylindrical model(s) of >=1 optic fiber(s) into the visible fiber tracks using the GUI-specified X-Y-Z translations and rotations 
 - estimation of the illuminated brain tissue volume below the fiber tip ("light cone") based on the fiber parameters (as described in Aravanis et al., 2007 J Neural Eng; doi: 10.1088/1741-2560/4/3/S02; PubMed ID: 17873414)
 - determination of the brain areas expressing optogenetic construct using interactive intensity thresholding
 - calculation of the overlap areas between the expression area, "light cone" illuminated area, and the atlas ROIs, in all combinations
 - all generated regions of interest such as thresholding results or results of overlap are stored in ImageJ RoiManager format
 - all the parameters/configuration are stored in the .json project file
 
 Prerequisites:
 - as input, takes a stack of brain images pre-aligned using ABBA registration tool
 - atlas outlines can be contained in the TIFF stack as overlay (as directly exported in the latest ABBA versions), or loaded via ImageJ RoiManager
 - image stack scaling such as pixel dimensions, units, and pixel origins for X, Y, Z dimensions are directly considered
 
 Installation:
 - at the moment, the script can be directly opened in the ImageJ script editor and executed from there
 - in future, a compiled .jar file for the plugin will be co-supplied
 
 Usage:
 - GUI is largely self-explanatory
 - a project keeping all the details and customization can be newly created, saved, and re-loaded
 - to keep preferred settings from start, one could use a pre-existing .json file as template. One only needs to manually change the path and the name of the image stack, and to reset the thresholding flag to "False"
 - the original image stack is never over-written. To store the graphical output, the stack can be "Saved as" from the ImageJ menu, or, alternatively, overlay can be exported via the RoiManager (Image->Overlay->To ROI Manager) in ImageJ
 - Image dimsnsion, pixel size and units have to be set properly (ImageJ->Image->Properties) before using the tool. X and Y values as well as origins are usually pre-set by the export routine from ABBA; Z-step has to be manually checked. Pay attention to the textual info about the image dimensions below the GUI. 
 - X-Y-Z translational coordinates for the fibers can be easily guessed by pointing the assumed fiber tip locations with the ImageJ cursor on the images. ImageJ reports the cursor coordinates in the info line, which can be directly used to enter into the respective GUI fields
 - the surfaces of the fiber(s) and of the light cone(s) are rendered by populating them with dots at specific density ("Fiber density dpi" in dots/mm2). To save computational time, it is highly recommended to position the fibers at low settings (such as default 0.02), and when done, re-calculate high resolution output at higher settings (e.g. 0.1-0.15)
 - another parameter relevant for rendering the fiber and the "light cone" cross-sections is "Tolerance along Z", changing which may affect (improve or degrade) the quality of the outlines. Make small changes at a time, if needed.
 - after analysis is complete and all overlays are computed (see Menu "Analysis"), two provided Python scripts can be used [as templates] to further analyse the output .csv files (for the overlays of thresholded areas with atlas, or for the overlays of thresholded & illuminated areas with the atlas, respectively). The scripts produce the summed and normalized results over all the planes of the image stack and allow for batch-processing over multiple projects.  
 
 
