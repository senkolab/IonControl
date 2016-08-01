# *****************************************************************
# IonControl:  Copyright 2016 Sandia Corporation
# This Software is released under the GPL license detailed
# in the file "license.txt" in the top-level IonControl directory
# *****************************************************************
## This is a class to handle errors generated by the niSync python module.
class niSyncError(Exception):
    ## This is the constructor of the niSyncError class.
    def __init__(self, code, msg):
        ## This is the status code returned by the NI-Sync drivers.
        #
        #  The code value is useful, because error codes can be searched
        #  on the National Instruments website (www.ni.com).
        self.code = code 

        ## This is the message returned by the NI-Sync drivers.
        #
        #  The message give a more detailed explanation as to why an
        #  error occurred.
        self.msg = msg

    ## This function returns a string containing the code and message
    #  describing the error that occurred.
    #  This strig will be displayed to the stderr output when a NI-Sync
    #  error occurs.
    def __str__(self):
        ret = '\n\tCode: {0} \n\tMessage: {1}'.format(self.code, self.msg)
        return ret
