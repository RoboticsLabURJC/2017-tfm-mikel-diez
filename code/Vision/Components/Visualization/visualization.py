import jderobot

class VisionViewer(jderobot.Visualization):
    def __init__(self):
        self.cont = 0
        self.refresh = True
        self.bufferpoints = None
        self.bufferline = None

    def getPoints(self, current=None):
        rgbpointlist = jderobot.bufferPoints()
        rgbpointlist.buffer = []
        rgbpointlist.refresh = self.refresh
        for i in self.bufferpoints[:]:
            rgbpointlist.buffer.append(i)
            index = self.bufferpoints.index(i)
            del self.bufferpoints[index]
        return rgbpointlist

    def set_points(self, points):
        self.bufferpoints = points

    def getSegment(self, current=None):
        rgblinelist = jderobot.bufferSegments()
        rgblinelist.buffer = []
        rgblinelist.refresh = self.refresh
        for i in self.bufferline[:]:
            rgblinelist.buffer.append(i)
            index = self.bufferline.index(i)
            del self.bufferline[index]
        return rgblinelist

    def set_segments(self, segments):
        self.bufferline = segments
