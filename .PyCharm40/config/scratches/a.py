import os
import sys
from PyQt4.QtXml import QDomDocument
from qgis.core import *
import qgis.utils


def GetScale(bbox):

    """
    Returns the best fitting scale from the list of 
    valid_scales  defined above.
    
    :prereq: map_size::list defined
    :prereq: valid_scale::list defined 
    :param bbox: List (llx , lly, ulx, uly)
    :return: int
    """
    
    # dx, dy in mm
    dx = abs(bbox[2] - bbox[0])*1000
    dy = abs(bbox[1] - bbox[3])*1000
    
    
    x_paper_res = \
        [map_size[0] * x for x in valid_scales]
    y_paper_res = \
        [map_size[1] * y for y in valid_scales]
    scales = \
        zip(valid_scales, x_paper_res, y_paper_res)

    tmp = \
        [(x, divmod(y, dx)[0], divmod(z, dy)[0]) \
        for x, y, z in scales]

    for i in tmp:
        if i[1] >= 1 and i[2] >= 1:
            return i[0]
    raise Warning("Could not find a valid scale \
    that encompass the KAEK" )
    
def normalizeBBox(scale, bbox):
    """

    :param scale: int
    :param bbox: List
    :return: List
    """
    mid_x = (bbox[2] + bbox[0]) / 2
    mid_y = (bbox[1] + bbox[3]) / 2

    return (
        mid_x - map_size[0] / 2 * scale / 1000,
        mid_y - map_size[1] / 2 * scale / 1000,
        mid_x + map_size[0] / 2 * scale / 1000,
        mid_y + map_size[1] / 2 * scale / 1000
    )


def addBBox_Margin(bbox,margin=0.8):
    llx, lly , urx, ury = bbox[0],bbox[1],bbox[2],bbox[3]
    dx = urx - llx
    dy = ury - lly
    return llx-margin*(dx/2),lly-margin*(dy/2),urx+margin*(dy/2),ury+margin*(dy/2)



path = \
     r"C:\Users\vesnikos\Desktop\tzogas\template2" 
os.chdir(path)

pixel_res = 0.1  # Resulution of basemap in meters. 
# A list of valid scales that can be used. 
# Check GetScale() bellow
valid_scales = [
    100,
    200,
    500,
    1000,
    2000,
    5000,
    20000
    ]



# list of Kaek ::str for printing. 
kaeks = ['270572610005',
               '270579701018',
               '270572604004']

bbox = None # (lrx,lry, urx,ury)

# Because initial qpj was build that way. Don't 
# change before studing qpj + for layers loop below
initial_kaek = '270572604004' 
pst_layer_id = 'pst20150512160115847'  

canvas = iface.mapCanvas()
ms = iface.mapCanvas().mapSettings() 
layers = iface.legendInterface().layers()
composition = QgsComposition(ms)

with open('kaek_template.qpt') as f:
    s = f.read()
sourceXML = QDomDocument()
sourceXML.setContent(s)
composition.loadFromTemplate(sourceXML)

# actuall map is within 5mm from the borders of 
# the Draw on both axis. 
#                        -----
#                        5mm
#                          |
#   | <- 5mm -> ### <- 5mm -> |
#                          |
#                        5mm
#                        -----
map_size = (composion.paperWidth()  - 10,
                    composion.paperHeight()  - 10)


layerStringList = []
for kaek in kaeks:
    for layer in layers:
        if type(layer) is QgsVectorLayer:
            if  layer.subsetString() != "":
                # better way to replace the subsetString() 
                # to iterate through kaek ids
                # maybe a helper class ? 
                layer.setSubsetString(
                layer.subsetString().replace(
                initial_kaek,kaek)
                )
            layerID = layer.id()
            if layerID == pst_layer_id:
                    bbox = addBBox_Margin(
                    (layer.extent().xMinimum(),
                    layer.extent().yMinimum(),
                    layer.extent().xMaximum(),
                    layer.extent().yMaximum())
                )
            layerStringList.append(layerID)
    initial_kaek = kaek
    canvas.refresh()
    
    scale = GetScale(bbox)


# papersize is 155x190 mm, mapsize is 145x180mm 
    canvas.setExtent(QgsRectangle(*bbox))
    canvas.zoomScale(scale)
    composition.getComposerMapById(0).setNewExtent(QgsRectangle(*normalizeBBox(scale,bbox)))
    composition.getComposerMapById(0).grid().setIntervalX(scale/20.)
    composition.getComposerMapById(0).grid().setIntervalY(scale/20.)
    composition.getComposerMapById(0).updateCachedImage ()
    myImage = composition.printPageAsRaster(0)
        
    myImage.save("kaek_{}_1_{}.png".format(
        kaek,scale))