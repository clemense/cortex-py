from ctypes import *

lib = cdll.LoadLibrary('libcortex_sdk.so')

# --------------------------------- constants ------------------------------------

MAX_N_BODIES = 100

# Data for one segment
tSegmentData = c_double * 7 # !<  X,Y,Z, aX,aY,aZ, Length
# Data for one marker
tMarkerData  = c_float * 3  # !<  X,Y,Z
# Data for one forceplate
tForceData   = c_float * 7  # !<  X,Y,Z, fX,fY,fZ, mZ
# Data for one degree of freedom
tDofData     = c_double     # !<  Usually an angle value in degrees

# ---------------------------------- structs -------------------------------------

class sHostInfo(Structure):
    '''
    ! The description of the connection to Cortex.
    ! This contains information about the host machine, the host program, and the connection status.
    '''
    _fields_ = [("bFoundHost", c_int),               # !< True = have talked to Cortex
                ("LatestConfirmationTime", c_int),   # !< Time of last receipt from Cortex
                ("szHostMachineName",c_char * 128),  # !< Name of machine Cortex is running on
                ("HostMachineAddress", c_ubyte * 4), # !< IP Address of that machine 
                ("szHostProgramName", c_char * 128), # !< Name of module communicating with
                ("HostProgramVersion", c_ubyte * 4)] # !< Version number of that module


class sHierarchy(Structure):
    '''
    ! The rudimentary description of a skeleton's bones and hierarchy.
    ! This description is defined by szSegmentNames[iSegment], and iParent[iSegment]
    '''
    _fields_ = [("nSegments", c_int),                       # !< Number of segments
                ("szSegmentNames", POINTER(c_char_p)),# !< Array of segment names
                ("iParents", POINTER(c_int) )]         # !< Array of segment parents (defines the hierarchy)

class sBodyDef(Structure):
    '''
    ! The description of a single tracking object that will have streaming data.
    ! This description includes the object's name, the marker names, the skeleton hierarchy, and the DOF names.
    '''
    _fields_ = [("szName", c_char_p),                      # !< Name of the object
                ("nMarkers", c_int),                       # !< Number of markers
                ("szMarkerNames", POINTER(c_char_p)), # !< Array of marker names
                ("Hierarchy", sHierarchy),                 # !< The Skeleton description for HTR data
                ("nDofs", c_int),                          # !< Number of degrees of freedom
                ("szDofNames", POINTER(c_char_p))]       # !< Array of degrees of freedom names

class sBodyDefs (Structure):
    '''
    ! The description of all the data that will stream from Cortex.
    ! This description includes all the body descriptions, the analog channels,
    ! and the number of forceplates.
    '''
    _fields_ = [("nBodyDefs", c_int),                             # !< Number of bodies being tracked
                ("BodyDefs", sBodyDef * MAX_N_BODIES),            # !< The definition of each body
                ("nAnalogChannels", c_int),                       # !< The number of active analog channels
                                                                  # !< The names given to each channel
                ("szAnalogChannelNames", POINTER(c_char_p)),
                ("nForcePlates", c_int),                          # !< The number of active forceplates
                ("AllocatedSpace", c_void_p)]                     # !< Private space (DON'T TOUCH)

class sBodyData (Structure):
    '''
    ! A structure containing ALL the data to drive one markerset.
    ! This contains the markerset's name, the marker positions, the segment 
    ! positions relative to each segment's parent, and the DOFs.
    '''
    _fields_ = [("szName", c_char * 128),        # !< For dynamic matching of objects.
                ("nMarkers", c_int),             # !< Number of markers defined
                # ! [nMarkers][3] array.  Markers[iMarker][0] == XEMPTY means no data.
                ("Markers", POINTER(tMarkerData)),
                ("fAvgMarkerResidual", c_float), # !< Average residual of the marker triangulations
                ("nSegments", c_int),            # !< Number of segments
                ("Segments", POINTER(tSegmentData)),             # !< [nSegments][7] array
                ("nDofs", c_int),                # !< Number of degrees-of-freedom
                ("Dofs", POINTER(tDofData)),   # !< Array of degree-of-freedom angles
                ("fAvgDofResidual", c_float),    # !< Average residual from the solve
                ("nIterations", c_int),          # !< Number of iterations to solve
                ("ZoomEncoderValue", c_int),     # !< Zoom value from the Camera Tracker Encoder
                ("FocusEncoderValue", c_int)]    # !< Focus value from the Camera Tracker Encoder

class sAnalogData (Structure):
    '''
    ! All the analog data for one frame's worth of time.
    ! This includes the raw analog samples, processed forces, and also angle encoder values (if available).
    '''
    _fields_ = [("nAnalogChannels", c_int),                  # !< Total number of active channels
                ("nAnalogSamples", c_int),                   # !< The number of samples in the current frame
                ("AnalogSamples", POINTER(c_short)),    # !< The data: nChannels * nSamples of these
                ("nForcePlates", c_int),                     # !< Total number of active forceplates
                ("nForceSamples", c_int),                    # !< The number of samples in the current frame
                ("Forces", POINTER(tForceData)),     # !< The forces: nForcePlates * nForceSamples of these
                ("nAngleEncoders", c_int),                   # !< Number of encoders
                ("nAngleEncoderSamples", c_int),             # !< Number of samples per encoder
                ("AngleEncoderSamples", POINTER(c_double))]  # !< The angles: nEncoders*nEncoderSamples of these

class sRecordingStatus (Structure):
    '''
    ! The recording status tells us the frame numbers and capture filename.
    '''
    _fields_ = [("bRecording", c_int), # !< 0=Not Recording, anything else=Recording
                # ! The frame number of the first data frame to be recorded from Cortex Live Mode
                ("iFirstFrame", c_int),
                # ! The frame number of the last data frame to be recorded from Cortex Live Mode
                ("iLastFrame", c_int), 
                ("szFilename", c_char * 256)] # !< The full capture filename 

class sFrameOfData (Structure):
    '''
    ! ALL the data for one frame streamed from Cortex.
    ! This include the two items that describe the frame. The first is the frame number.
    ! The second is the time delay measuring the delay between the real world action 
    ! and the host sending this frame. The actual data for the frame includes the data 
    ! for each body, the unidentified markers, and data that is associated with the analog captures.
    '''
    _fields_ = [("iFrame", c_int),                     # !< Cortex's frame number
                # ! Total time (seconds) from Camera to the Host sending the data
                ("fDelay", c_float),                  
                ("nBodies", c_int),                    # !< The bodies should match the descriptions
                ("BodyData", sBodyData * MAX_N_BODIES),# !< The data for each body
                ("nUnidentifiedMarkers", c_int),       # !< Number of unrecognized markers
                ("UnidentifiedMarkers", POINTER(tMarkerData)),# !< The unrecognized markers
                ("AnalogData", sAnalogData),           # !< The analog data packaged
                ("RecordingStatus", sRecordingStatus)] # !< Info about name and frames being recorded

# ---------------------------------- methods -------------------------------------


def Cortex_GetSdkVersion(version = [4, 1, 3, 1]):
    '''
    This function returns a 4-byte version number.
    Version - An array of four bytes: ModuleID, Major, Minor, Bugfix
    RC_Okay
    '''
    _Cortex_GetSdkVersion = lib.Cortex_GetSdkVersion
    _Cortex_GetSdkVersion.argtypes = [c_ubyte * 4]
    return _Cortex_GetSdkVersion((c_ubyte*4)(*version))

def Cortex_SetVerbosityLevel(iLevel):
    '''    
    This function sets the filter level of the LogMessages.
    The default verbosity level is VL_Warning.
    iLevel - one of the maVerbosityLevel enum values.
    RC_Okay
    '''
    _Cortex_SetVerbosityLevel = lib.Cortex_SetVerbosityLevel
    _Cortex_SetVerbosityLevel = [c_int]
    return _Cortex_SetVerbosityLevel(iLevel)

callback_pointer = [None, None]

def Cortex_SetErrorMsgHandlerFunc(callback):
    '''
    The user supplied function handles text messages posted from within the SDK.
    Logging messages is done as a utility to help code and/or run using the SDK.
    Various messages get posted for help with error conditions or events that happen.
    Each message has a Log-Level assigned to it so the user can.
    Cortex_SetVerbosityLevel
    MyFunction - This user defined function handles messages from the SDK.
    maReturnCode - RC_Okay
    '''
    _Cortex_SetErrorMsgHandlerFunc = lib.Cortex_SetErrorMsgHandlerFunc
    func_pointer = CFUNCTYPE(c_void_p, c_int, POINTER(c_char))
    _Cortex_SetErrorMsgHandlerFunc.argtypes = [func_pointer]
    _Cortex_SetErrorMsgHandlerFunc.restype = None
    #callback_pointer[0] = func_pointer(MyErrorHandler)
    callback_pointer[0] = func_pointer(callback)
    return _Cortex_SetErrorMsgHandlerFunc(callback_pointer[0])

def Cortex_SetDataHandlerFunc(callback):
    '''
    The user supplied function will be called whenever a frame of data arrives.
    
    The ethernet servicing is done via a thread created
    when the connection to Cortex is made.  This function is
    called from that thread.  Some tasks are not sharable
    directly across threads.  Window redrawing, for example,
    should be done via events or messages.
    MyFunction - This user supply callback function handles the streaming data
    maReturnCode - RC_Okay
  
    Notes: The data parameter points to "hot" data. That frame of data
           will be overwritten with the next call to the callback function.
    '''
    _Cortex_SetDataHandlerFunc = lib.Cortex_SetDataHandlerFunc
    func_pointer = CFUNCTYPE(c_void_p, POINTER(sFrameOfData))
    _Cortex_SetDataHandlerFunc.argtypes = [func_pointer]
    _Cortex_SetDataHandlerFunc.restype = None
    callback_pointer[1] = func_pointer(callback)
    return _Cortex_SetDataHandlerFunc(callback_pointer[1])

def Cortex_Initialize(szMyNicCardAddress = "", szCortexNicCardAddress = ""):
    '''
    This function defines the connection routes to talk to Cortex.

    Machines can have more than one ethernet interface.  This function
    is used to either set the ethernet interface to use, or to let
    the SDK auto-select the local interface, and/or the Cortex host.
    This function should only be called once at startup.
 
    szMyNicCardAddress - "a.b.c.d" or HostName.  "" and NULL mean AutoSelect
    szCortexNicCardAddress - "a.b.c.d" or HostName.  "" and NULL mean AutoSelect
    maReturnCode - RC_Okay, RC_ApiError, RC_NetworkError, RC_GeneralError

    MY ADVICE: USE WITHOUT PARAMETERS!!!
    '''
    _Cortex_Initialize = lib.Cortex_Initialize
    _Cortex_Initialize.argtypes = [c_char_p, c_char_p]
    return _Cortex_Initialize(szMyNicCardAddress, szCortexNicCardAddress)

def Cortex_GetHostInfo(pHostInfo):
    '''
    This function gets information about the connection to Cortex
  
    This function returns IP-Address information and Cortex version information.
    The version info can be used to handle incompatible changes in either our code
    or your code.
    pHostInfo - Structure containing connection information
    RC_Okay, RC_NetworkError
    '''
    if type(pHostInfo) != sHostInfo:
        print("ERROR: Argument must be of type sHostInfo")
        exit(0)
    _Cortex_GetHostInfo = lib.Cortex_GetSdkVersion
    return _Cortex_GetHostInfo(byref(pHostInfo))

def Cortex_Exit():
    '''
    This function stops all activity of the SDK.
 
    This function should be called once before exiting.
    '''
    _Cortex_Exit = lib.Cortex_Exit
    return _Cortex_Exit()

def Cortex_Request(szCommand, ppResponse, pnBytes):
    '''
    This function sends commands to Cortex and returns a response.
 
    This function is an extendable interface between the Client programs
    and the Host (Cortex) program.  The commands are sent as readable text strings.
    The response is returned unaltered.
 
    szCommand - The request to send the Cortex
    ppResponse - The reply
    pnBytes - The number of bytes in the response
 
    \verbatim
    Example:
    void *pResponse=NULL;
    Cortex_Request("GetContextFrameRate", &pResponse, sizeof(void*));
    fFrameRate = *(float*)pResponse;
    \endverbatim 
    
    return RC_Okay, RC_TimeOut, RC_NotRecognized, RC_GeneralError
    '''
    # cast python objects
    _szCommand = c_char_p(szCommand) 
    _ppResponse = c_void_p()
    _pnBytes = c_int()
    # call cortex method
    _Cortex_Request = lib.Cortex_Request
    ret = _Cortex_Request(_szCommand, byref(_ppResponse), byref(_pnBytes))
    # get pointer values
    ppResponse = _ppResponse
    pnBytes = _pnBytes
    return ret

def Cortex_GetBodyDefs():
    '''
    This function queries Cortex for its set of tracking objects.
 
    sBodyDefs* - This is a pointer to the internal storage of
                 the results of the latest call to this function.
    sa Cortex_FreeBodyDefs
    '''
    _Cortex_GetBodyDefs = lib.Cortex_GetBodyDefs
    _Cortex_GetBodyDefs.restype = POINTER(sBodyDefs)
    return _Cortex_GetBodyDefs()

def Cortex_FreeBodyDefs(pBodyDefs):
    '''
    This function frees the memory allocated by Cortex_GetBodyDefs
 
    The data within the structure is freed and also the structure itself.

    pBodyDefs - The item to free.
    RC_Okay
    '''
    if type(pBodyDefs) != POINTER(sBodyDefs):
        print("ERROR: Argument must be a pointer of sBodyDefs")
        print("Argumentis type: ", type(pBodyDefs))
        exit(0)
    _Cortex_FreeBodyDefs = lib.Cortex_FreeBodyDefs
    return _Cortex_FreeBodyDefs(pBodyDefs)

def Cortex_GetCurrentFrame():
    '''
    This function polls Cortex for the current frame
 
    The SDK user has the streaming data available via the callback function.
    In addition, this function is available to get a frame directly.
    Note: Cortex considers the current frame to be the latest LiveMode frame completed or,
          if not in LiveMode, the current frame is the one that is displayed on the screen.

    return sFrameOfData
    '''
    _Cortex_GetCurrentFrame = lib.Cortex_GetCurrentFrame
    _Cortex_GetCurrentFrame.restype = POINTER(sFrameOfData)
    return _Cortex_GetCurrentFrame()# Can POLL for the current frame.

def Cortex_CopyFrame(pSrc, pDst):
    '''
    This function copies a frame of data.
 
    The Destination frame should start initialized to all zeros.  The CopyFrame
    and FreeFrame functions will handle the memory allocations necessary to fill
    out the data.
    
    param pSrc - The frame to copy FROM.
    param pDst - The frame to copy TO
    
    return RC_Okay, RC_MemoryError
    '''
    if type(pSrc) != POINTER(sFrameOfData) or type(pDst) != POINTER(sFrameOfData):
        print("ERROR: Arguments must be sFrameOfData pointers")
        exit(0)
    _Cortex_CopyFrame = lib.Cortex_CopyFrame
    return _Cortex_CopyFrame(pSrc, pDst) # Allocates or reallocates pointers
    
def Cortex_FreeFrame(pFrame):
    '''
    This function frees memory within the structure.
 
    The sFrameOfData structure includes pointers to various pieces of data.
    That data is dynamically allocated or reallocated to be consistent with
    the data that has arrived from Cortex.  To properly use the sFrameOfData
    structure, you should use the utility functions supplied.  It is possible
    to reuse sFrameOfData variables without ever freeing them.  The SDK will
    reallocate the components for you.
    
    param pFrame - The frame of data to free.
 
    return RC_Okay
    '''
    if type(pFrame) != POINTER(sFrameOfData):
        print("ERROR: Argument must be a sFrameOfData pointer")
        exit(0)
    _Cortex_FreeFrame = lib.Cortex_FreeFrame
    return _Cortex_FreeFrame(pFrame)

# there are more functions which are not implemented mainly skeleton related





    
