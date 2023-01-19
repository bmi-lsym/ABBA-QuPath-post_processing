//The following script can be run in a batch for the whole project (Run -> Run for project)

//Code between the lines 5-23 removes all the previous detections, then draws and selects a rectangular ROI around the whole image

import qupath.lib.objects.PathObjects
import qupath.lib.roi.ROIs
import qupath.lib.regions.ImagePlane

setImageType('FLUORESCENCE');
clearDetections();

def imageData = getCurrentImageData()
def server = imageData.getServer()
xw=server.getWidth()
yw=server.getHeight()

int z = 0
int t = 0
def plane = ImagePlane.getPlane(z, t)
def roi = ROIs.createRectangleROI(0, 0, xw, yw, plane)
def annotation = PathObjects.createAnnotationObject(roi)
addObject(annotation)
setSelectedObject(annotation)


//In the line 35, adjust parameters for the appropriate detection outcome.
//It should be best tested in test ROIs in different regions of different images in the project
// by drawing/selecting small ROIs and running the line 35 alone, trying to modify different parameters.
//The most important parameters are:
//   threshold - minimal average intensity of the detected spot
//   detectionImage - provide the name of the color channel to be used
//   minAreaMicrons, minAreaMicrons - range for the detected spot size 
//   requestedPixelSizeMicrons - pixel size in microns

runPlugin('qupath.imagej.detect.cells.WatershedCellDetection', '{"detectionImage": "FL CY3",  "requestedPixelSizeMicrons": 0.6442,  "backgroundRadiusMicrons": 5.0,  "medianRadiusMicrons": 0.0,  "sigmaMicrons": 2,  "minAreaMicrons": 30,  "maxAreaMicrons": 250.0,  "threshold": 100.0,  "watershedPostProcess": false,  "cellExpansionMicrons": 1.0,  "includeNuclei": true,  "smoothBoundaries": true,  "makeMeasurements": true}');
