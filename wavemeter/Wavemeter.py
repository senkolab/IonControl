# *****************************************************************
# IonControl:  Copyright 2016 Sandia Corporation
# This Software is released under the GPL license detailed
# in the file "license.txt" in the top-level IonControl directory
# *****************************************************************

import logging
from functools import partial
from PyQt5 import QtCore, QtNetwork
from time import time
from collections import defaultdict
import http.client

from modules.quantity import Q

class WavemeterReadException(Exception):
    pass

class Wavemeter(QtCore.QObject):
    resultReceived = QtCore.pyqtSignal( object, object )
    
    def __init__(self, address):
        super(Wavemeter, self).__init__()
        self.address = address if address else "http://134.253.204.71:8082"
        self.nAttempts = 0
        self.nMaxAttempts = 10
        #self.connection.set_debuglevel(5)
        self.lastResult = dict()
        self.queryRunning = defaultdict( lambda: False )
        self.am = QtNetwork.QNetworkAccessManager()
        self.callbackFuncs = dict()
        self.callbackFailureCount = dict()
        
    def onWavemeterError(self, channel, reply, error):
        """Print out received error"""
        self.queryRunning[channel] = False
        logging.getLogger(__name__).warning( "Error {0} accessing wavemeter query '{1}'".format(error, self.query) )
        reply.finished.disconnect()  # necessary to make reply garbage collectable
        reply.error.disconnect()

    def getWavemeterData(self, channel, course=None):
        """Get the data from the wavemeter at the specified channel."""
        if not self.queryRunning[channel]:
            self.query = self.address + "?channel={0}".format(int(channel))
            if course is not None:
                self.query += "&course={0}".format(course.m_as('THz'))
            #reply = self.am.get( QtNetwork.QNetworkRequest(QtCore.QUrl(self.query)))
            #reply.error.connect( partial(self.onWavemeterError, int(channel), reply ) )
            #reply.finished.connect(partial(self.onWavemeterData, int(channel), reply))
            #print(self.query)            
            self.connection = http.client.HTTPConnection(self.address, timeout = 5)
            self.connection.request("GET", self.query)
            reply = self.connection.getresponse()
            self.onWavemeterData(int(channel), reply)
            #print(reply)
            data = reply.read()
            #print(data)
            print("Status is: ", reply.status, " Reason is: ", reply.reason)
            self.connection.close()
            self.queryRunning[channel] = False
            

    def onWavemeterData(self, channel, reply):
        """Execute when reply is received from the wavemeter."""
        logger = logging.getLogger(__name__)
        self.queryRunning[channel] = False
        print(reply)
        if reply.status==200 and reply.reason == "OK":
            data = reply.read()
            #print(data)
            logger.debug( str( self.query ) )
            logger.debug( "reply: '{0}'".format(data))
            result = Q( round(float(data), 5), 'THz' )
            #print(result.m_as('THz'))
            if result.m_as('THz')<0 and self.callbackFailureCount[channel]<self.nMaxAttempts:
                print("result: ", result.m_as('THz'))
                self.getWavemeterData(channel)
                self.callbackFailureCount[channel] += 1                
            else:    
                self.resultReceived.emit( channel, result ) 
                self.lastResult[channel] = (result, time())
                if channel in self.callbackFuncs:
                    self.callbackFuncs.pop(channel)(result)
        elif channel in self.callbackFuncs:
            self.callbackFuncs.pop(channel)(None)
        #reply.finished.disconnect()  # necessary to make reply garbage collectable
        self.connection.close()
        #reply.error.disconnect()
        
    def get_frequency(self, channel, max_age = None):
        return self.set_frequency(None, channel, max_age if max_age else Q(3, 's'))
    
    def asyncGetFrequency(self, channel, callback):
        self.getWavemeterData(channel)
        self.callbackFuncs[channel] = callback
        self.callbackFailureCount[channel] = 0
                   
    def set_frequency(self, freq, channel, max_age=None):
        max_age = max_age if max_age is not None else Q(3, 's')
        self.getWavemeterData(channel, freq)
        if channel in self.lastResult:
            result, measure_time = self.lastResult[channel]
            if time()-measure_time < max_age.m_as('s'):
                return result
        return None                    


if __name__ == '__main__':
    import timeit
    fg = Wavemeter()
    def speed():
        print(fg.get_frequency(4))
    t = timeit.Timer("speed()", "from __main__ import speed")
    print(t.timeit(number = 10))
    del fg    
