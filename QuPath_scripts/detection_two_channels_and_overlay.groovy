//code by Dr. Olivier Burri, BIOP, EPFL, modified by Olexiy Kochubey
//Detection and classification of single-and double-labelled cells in two fluorescent channels  

// INPUT PARAMETERS
//set the maximal distance between the centroids of two cells 
//to define if these are actually the same double-positive cell detected in both channels  
def maxDistMicrons = 10

//provide the color channel names: these should be present in the image, used in detection plugin
def channelNames = ["FL FITC", "FL CY3"]

//provide the names for the detection classes, per channel
def classNames = ["FITC", "CY3"]

//modify the colors of the classes if needed (the double-label class will have a color = the sum of two)
def classColors = [0x00FF00, 0xFF0000]

//provide the intensity thresholds for cell detections, for each channel respectively
def thresholds = [1500, 150]

//other detection parameters can be adjusted in-place as needed in the lines below:
def cellDetection = [ {runPlugin('qupath.imagej.detect.cells.WatershedCellDetection', '{"detectionImage": "'+channelNames[0]+'",  "requestedPixelSizeMicrons": 0.6442,  "backgroundRadiusMicrons": 8.0,  "medianRadiusMicrons": 0.0,  "sigmaMicrons": 2.0,  "minAreaMicrons": 30.0,  "maxAreaMicrons": 250.0,  "threshold":'+thresholds[0].toString()+',  "watershedPostProcess": true,  "cellExpansionMicrons": 1.0,  "includeNuclei": true,  "smoothBoundaries": true,  "makeMeasurements": true}') }, 
                      {runPlugin('qupath.imagej.detect.cells.WatershedCellDetection', '{"detectionImage": "'+channelNames[1]+'",  "requestedPixelSizeMicrons": 0.6442,  "backgroundRadiusMicrons": 8.0,  "medianRadiusMicrons": 0.0,  "sigmaMicrons": 2.0,  "minAreaMicrons": 30.0,  "maxAreaMicrons": 250.0,  "threshold":'+thresholds[1].toString()+',  "watershedPostProcess": true,  "cellExpansionMicrons": 1.0,  "includeNuclei": true,  "smoothBoundaries": true,  "makeMeasurements": true}')}
                    ]  



//Code between the lines 25-44 draws and selects a rectangular ROI around the whole image
setImageType('FLUORESCENCE');
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

//convert distance to pixels
def maxDistPx = maxDistMicrons/server.getPixelCalibration().getAveragedPixelSizeMicrons()
        
//ROI in each detection is occurring
def parent = getSelectedObject()



//DO detections for each channel in the list of channels
def detectionsPerChannel = cellDetection.collect{ det -> 
    clearDetections()
    det.call()    
    return getDetectionObjects()
}

clearDetections()
    
ch1 = detectionsPerChannel[0]
ch2 = detectionsPerChannel[1]

def finalCells = []

//creating the new classes if they do not exist 
def ovl_class=classNames[0]+":"+" "+classNames[1]

def ch1_class=getPathClass(classNames[0])
if (ch1_class.isValid() != true )
{ch1_class=PathClass.getInstance(null, classNames[0], null )}
ch1_class.setColor(classColors[0])

def ch2_class=getPathClass(classNames[1])
if (ch2_class.isValid() != true )
{ch2_class=PathClass.getInstance(null, classNames[1], null )}
ch2_class.setColor(classColors[1])

def ch1_ch2_class=getPathClass(ovl_class)
if (ch1_ch2_class.isValid() != true )
{ch1_ch2_class=PathClass.getInstance(ch1_class, classNames[1], null )}
ch1_ch2_class.setColor(classColors[0]+classColors[1])


//sorting out double-labelled cells
ch1.each{ a ->
    a.setPathClass( ch1_class)//getPathClass(classNames[0] ) )
    // Does it have a neighbor
    nearest = ch2.find{ DelaunayTriangulation.distance( it.getROI(), a.getROI() ) < maxDistPx }
    if( nearest != null ) {
        // Found a double positive
        a.setPathClass(ch1_ch2_class)
        ch2.remove( nearest )
    }     
    finalCells.add( a )
}

ch2.each{ it.setPathClass( ch2_class )  }

finalCells.addAll( ch2 )
addObjects( finalCells )

fireHierarchyUpdate()


import qupath.lib.objects.PathObjects
import qupath.lib.roi.ROIs
import qupath.lib.regions.ImagePlane
import qupath.opencv.features.DelaunayTriangulation