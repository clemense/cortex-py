import time
from cortex import *


class MyDataHandler:
    def __init__(self):
        self.alldata = []
    
    def MyErrorHandler(self, iLevel, msg):
        print("ERROR: ")
        print(iLevel, msg.contents)
        return 0
            
    def MyDataHandler(self, Frame):
        print("got called")
        try:
            print("Received multi-cast frame no %d\n"%(Frame.contents.iFrame))
            print "Bodies: ", Frame.contents.nBodies
            print "BodyData: ", Frame.contents.BodyData[0].szName
            print "Number of Markers of Body[0]: ", Frame.contents.BodyData[0].nMarkers
            for i in range(Frame.contents.BodyData[0].nMarkers):
                print "MarkerX ", Frame.contents.BodyData[0].Markers[i][0]
                print "MarkerY ", Frame.contents.BodyData[0].Markers[i][1]
                print "MarkerZ ", Frame.contents.BodyData[0].Markers[i][2]
            print "BodyMarker[2].x: ", Frame.contents.BodyData[0].Markers[3][0]
            print "Unidentified markers: ", Frame.contents.nUnidentifiedMarkers
            print "Delay: ", Frame.contents.fDelay
            print "", Frame.contents.UnidentifiedMarkers[0][0]
            self.alldata.append(Frame.contents.UnidentifiedMarkers[0][0])
        except:
            print("Frame empty")
        return 0

if __name__ == "__main__":
    my_obj = MyDataHandler()
    
    Cortex_SetErrorMsgHandlerFunc(my_obj.MyErrorHandler)
    Cortex_SetDataHandlerFunc(my_obj.MyDataHandler)

    if Cortex_Initialize() != 0:
        print("ERROR: unable to initialize")
        Cortex_Exit()
        exit(0)

    pBodyDefs = Cortex_GetBodyDefs()
    if pBodyDefs == None:
        print("Failed to get body defs")
    else:
        print("Got body defs")
        print("bodydefs: ", pBodyDefs.contents.nBodyDefs)
        print "Marker names: "
        print "", pBodyDefs.contents.BodyDefs[0].szName
        for i in range(pBodyDefs.contents.BodyDefs[0].nMarkers):
            print "Marker: ", pBodyDefs.contents.BodyDefs[0].szMarkerNames[i]
        Cortex_FreeBodyDefs(pBodyDefs)
        pBodyDefs = None
  
    pResponse = c_void_p
    nBytes = c_int
    retval = Cortex_Request("GetContextFrameRate", pResponse, nBytes)
    if retval != 0:
        print("ERROR, GetContextFrameRate")

    #contextFrameRate = cast(pResponse, POINTER(c_float))

    #print("ContextFrameRate = %3.1f Hz", contextFrameRate)

    print("*** Starting live mode ***")
    retval = Cortex_Request("LiveMode", pResponse, nBytes)
    time.sleep(1.0)
    retval = Cortex_Request("Pause", pResponse, nBytes)
    print("*** Paused live mode ***")

    print("****** Cortex_Exit ******")
    retval = Cortex_Exit();
    
    print my_obj.alldata
