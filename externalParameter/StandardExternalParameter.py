# *****************************************************************
# IonControl:  Copyright 2016 Sandia Corporation
# This Software is released under the GPL license detailed
# in the file "license.txt" in the top-level IonControl directory
# *****************************************************************
from collections import OrderedDict

import logging
import numpy
import pint
ureg = pint.UnitRegistry()

from modules.quantity import Q
from .ExternalParameterBase import ExternalParameterBase
from ProjectConfig.Project import getProject
from uiModules.ImportErrorPopup import importErrorPopup
from .qtHelper import qtHelper
import re
from collections.abc import Mapping as MappingABC
from typing import Any, Dict, Mapping, Optional, Tuple
#LKSJDFLJ
project=getProject()
HighFinesseWavemeterEnabled = project.isEnabled('hardware', 'HighFinesse Wavemeter')
wavemeterEnabled = False
visaEnabled = project.isEnabled('hardware', 'VISA')
DG4000Enabled = project.isEnabled('hardware', 'DG4000 AWG')
rigol_dp832_enabled = project.isEnabled('hardware', 'Rigol DP832')

from PyQt5 import QtCore



if visaEnabled:
    try:
        import visa
    except ImportError: #popup on failed import of enabled visa
        importErrorPopup('VISA')

if visaEnabled:
    
    class N6700BPowerSupply(ExternalParameterBase):
        """
        Adjust the current on the N6700B current supply
        """
        className = "N6700 Powersupply"
        _outputChannels = OrderedDict([("Curr1", "A"), ("Curr2", "A"), ("Curr3", "A"), ("Curr4", "A"), ("Volt1", "V"),
                                       ("Volt2", "V"), ("Volt3", "V"), ("Volt4", "V"), ("OutEnable1", ""),
                                       ("OutEnable2", ""), ("OutEnable3", ""), ("OutEnable4", "")])
        _outputLookup = { "Curr1": ("Curr", "Meas:Curr", 1, "A"), "Curr2": ("Curr", "Meas:Curr", 2, "A"),
                          "Curr3": ("Curr", "Meas:Curr", 3, "A"), "Curr4": ("Curr", "Meas:Curr", 4, "A"),
                          "Volt1": ("Volt", "Meas:Volt", 1, "V"), "Volt2": ("Volt", "Meas:Volt", 2, "V"),
                          "Volt3": ("Volt", "Meas:Volt", 3, "V"), "Volt4": ("Volt", "Meas:Volt", 4, "V"),
                          "OutEnable1": ("OUTP:STAT", "OUTP:STAT", 1, ""), "OutEnable2": ("OUTP:STAT", "OUTP:STAT", 2, ""),
                          "OutEnable3": ("OUTP:STAT", "OUTP:STAT", 3, ""), "OutEnable4": ("OUTP:STAT", "OUTP:STAT", 4, "")}
        _inputChannels = dict({"Curr1":"A", "Curr2":"A", "Curr3":"A", "Curr4":"A", "Volt1":"V", "Volt2":"V", "Volt3":"V", "Volt4":"V"})
        def __init__(self, name, config, globalDict, instrument="QGABField"):
            logger = logging.getLogger(__name__)
            ExternalParameterBase.__init__(self, name, config, globalDict)
            logger.info( "trying to open '{0}'".format(instrument) )
            self.rm = visa.ResourceManager()
            self.instrument = self.rm.open_resource( instrument)
            logger.info( "opened {0}".format(instrument) )
            self.setDefaults()
            self.initializeChannelsToExternals()
            self.qtHelper = qtHelper()
            self.newData = self.qtHelper.newData
            self.initOutput()

        def setValue(self, channel, v):
            function, _, index, unit = self._outputLookup[channel]
            command = "{0} {1},(@{2})".format(function, v.m_as(unit), index)
            self.instrument.write(command) #set voltage
            return v

        def getValue(self, channel):
            function, _, index, unit = self._outputLookup[channel]
            command = "{0}? (@{1})".format(function, index)
            return Q(float(self.instrument.query(command)), unit) #set voltage

        def getExternalValue(self, channel):
            _, function, index, unit = self._outputLookup[channel]
            command = "{0}? (@{1})".format(function, index)
            value = Q( float( self.instrument.query(command)), unit )
            return value

        def close(self):
            del self.instrument

    class AFG3102(ExternalParameterBase):
        """
        Adjust parameters on the AFG3102 tektronix arbitrary function generator
        """
        className = "AFG3102 Arbitrary Function Generator"
        _outputChannels = OrderedDict([("OutEnable1", ""),
                                       ("OutEnable2", ""),
                                       ("Freq1", "Hz"),
                                       ("Freq2", "Hz"),
                                       ("Amp1", "V"),
                                       ("Amp2", "V"),
                                       #("SweepEnabled1", ""),
                                       #("SweepEnabled2", ""),
                                       ("SweepStartFreq1", "Hz"),
                                       ("SweepStartFreq2", "Hz"),
                                       ("SweepStopFreq1", "Hz"),
                                       ("SweepStopFreq2", "Hz"),
                                       ("SweepTime1", "s"),
                                       ("SweepTime2", "s"),
                                       ("SweepReturnTime1", "s"),
                                       ("SweepReturnTime2", "s")]
                                      )

        _outputLookup = { "OutEnable1": ("OUTP1:STAT", 1, ""),
                          "OutEnable2": ("OUTP2:STAT", 2, ""),
                          "Freq1": ("SOUR1:FREQ:CENT", 1, "Hz"),
                          "Freq2": ("SOUR2:FREQ:CENT", 2, "Hz"),
                          "Amp1": ("SOUR1:VOLT:AMPL", 1, "V"),
                          "Amp2": ("SOUR2:VOLT:AMPL", 2, "V"),
                          #"SweepEnabled1": ("SOUR1:FREQ:MODE", 0, ""),
                          #"SweepEnabled2": ("SOUR2:FREQ:MODE", 0, ""),
                          "SweepStartFreq1": ("SOUR1:FREQ:STAR", 1, "Hz"),
                          "SweepStartFreq2": ("SOUR2:FREQ:STAR", 2, "Hz"),
                          "SweepStopFreq1": ("SOUR1:FREQ:STOP", 1, "Hz"),
                          "SweepStopFreq2": ("SOUR2:FREQ:STOP", 2, "Hz"),
                          "SweepTime1": ("SOUR1:SWE:TIME", 1, "s"),
                          "SweepTime2": ("SOUR2:SWE:TIME", 2, "s"),
                          "SweepReturnTime1": ("SOUR1:SWE:RTIM", 1, "s"),
                          "SweepReturnTime2": ("SOUR2:SWE:RTIM", 2, "s")}


        _inputChannels = {"OutEnable1": "",
                          "OutEnable2": "",
                          "Freq1": "Hz",
                          "Freq2": "Hz",
                          "Amp1": "V",
                          "Amp2": "V",
                          #"SweepEnabled1": "",
                          #"SweepEnabled2": "",
                          "SweepStartFreq1": "Hz",
                          "SweepStartFreq2": "Hz",
                          "SweepStopFreq1": "Hz",
                          "SweepStopFreq2": "Hz",
                          "SweepTime1": "s",
                          "SweepTime2": "s",
                          "SweepReturnTime1": "s",
                          "SweepReturnTime2": "s"}

        def __init__(self, name, config, globalDict, instrument="QGABField"):
            logger = logging.getLogger(__name__)
            ExternalParameterBase.__init__(self, name, config, globalDict)
            logger.info( "trying to open '{0}'".format(instrument) )
            self.rm = visa.ResourceManager()
            self.instrument = self.rm.open_resource( instrument)
            logger.info( "opened {0}".format(instrument) )
            self.setDefaults()
            self.initializeChannelsToExternals()
            self.qtHelper = qtHelper()
            self.newData = self.qtHelper.newData
            self.initOutput()

        def setValue(self, channel, v):
            function, index, unit = self._outputLookup[channel]
            command = "{0} {1}".format(function, v.m_as(unit))#, index)
            self.instrument.write(command) #set voltage
            return v

        def getValue(self, channel):
            function, index, unit = self._outputLookup[channel]
            command = "{0}?".format(function)#, index)
            try:
                return Q(float(self.instrument.query(command)), unit) #set voltage
            except:
                return self.instrument.query(command)

        def getExternalValue(self, channel):
            function, index, unit = self._outputLookup[channel]
            command = "{0}?".format(function)#, index)
            value = Q( float( self.instrument.query(command)), unit )
            return value

        def close(self):
            del self.instrument

    class HP8672A(ExternalParameterBase):
        """
        Scan the laser frequency by scanning a synthesizer HP8672A. (The laser is locked to a sideband)
        setValue is frequency of synthesizer
        currentValue and currentExternalValue are current frequency of synthesizer

        This class programs the 8672A using the directions in the manual, p. 3-17: cp.literature.agilent.com/litweb/pdf/08672-90086.pdf
        """
        className = "HP8672A"
        _outputChannels = {'Freq': 'MHz', 'Power_dBm': ''}
        def __init__(self, name, config, globalDict, instrument="TCPIP0::192.168.168.123::inst0::INSTR"):
            ExternalParameterBase.__init__(self, name, config, globalDict)
            self.setDefaults()
            initialAmplitudeString = self.createAmplitudeString()
            self.rm = visa.ResourceManager()
            self.synthesizer = self.rm.open_resource( instrument)
            self.synthesizer.write(initialAmplitudeString)
            self.initOutput()

        def setValue(self, channel, value ):
            """Send the command string to the HP8672A to set the frequency to 'value'."""
            if channel =='Freq':
                value = value.round('kHz')
                command = "P{0:0>8.0f}".format(value.m_as('kHz')) + 'Z0' + self.createAmplitudeString()
                #Example string: P03205000Z0K1L6O1 would set the oscillator to 3.205 GHz, -13 dBm
            elif channel=='Power_dBm':
                command = self.createAmplitudeString(value)
            self.synthesizer.write(command)
            return value

        def createAmplitudeString(self, value=None):
            """Create the string for setting the HP8672A amplitude.
            The string is of the form K_L_O_, where _ is a number or symbol indicating an amplitude."""
            KDict = {0:'0', -10:'1', -20:'2', -30:'3', -40:'4', -50:'5', -60:'6', -70:'7', -80:'8', -90:'9', -100:':', -110:';'}
            LDict = {3:'0', 2:'1', 1:'2', 0:'3', -1:'4', -2:'5', -3:'6', -4:'7', -5:'8', -6:'9', -7:':', -8:';', -9:'<', -10:'='}
            amp = int(round(value)) if value else 0 #convert the amplitude to a number, and round it to the nearest integer
            amp = max(-120, min(amp, 13)) #clamp the amplitude to be between -120 and +13
            Opart = '1' if amp <= 3 else '3' #Determine if the +10 dBm range option is necessary
            if Opart == '3':
                amp -= 10
            if amp >= 0:
                Kpart = KDict[0]
                Lpart = LDict[amp]
            else:
                Kpart = KDict[10*(divmod(amp, 10)[0]+1)]
                Lpart = LDict[divmod(amp, 10)[1]-10]
            return 'K' + Kpart + 'L' + Lpart + 'O' + Opart

        def close(self):
            del self.synthesizer


    class MicrowaveSynthesizer(ExternalParameterBase):
        """
        Scan the microwave frequency of microwave synthesizer
        """
        className = "Microwave Synthesizer"
        _outputChannels = {'Freq': 'MHz', 'Power_dBm': ''}
        def __init__(self, name, config, globalDict, instrument="GPIB0::23::INSTR"):
            ExternalParameterBase.__init__(self, name, config, globalDict)
            self.rm = visa.ResourceManager()
            self.synthesizer = self.rm.open_resource( instrument)
            self.setDefaults()
            self.initializeChannelsToExternals()
            self.initOutput()

        def setValue(self, channel, v):
            if channel =='Freq':
                command = ":FREQ:CW {0:.5f}KHZ".format(v.m_as('kHz'))
            elif channel=='Power_dBm':
                command = ":POWER {0:.3f}".format(float(v))
            self.synthesizer.write(command)
            return v

        def getValue(self, channel):
            if channel=='Frequency':
                answer = self.synthesizer.query(":FREQ:CW?")
                return Q( float(answer), "Hz" )
            elif channel=='Power':
                answer = self.synthesizer.query(":POWER?")
                return Q( float(answer), "" )

        def close(self):
            del self.synthesizer


    class E4422Synthesizer(ExternalParameterBase):
        """
        Scan the microwave frequency of microwave synthesizer
        """
        className = "E4422 Synthesizer"
        _outputChannels = {'Freq': 'MHz', 'Power_dBm': ''}
        def __init__(self, name, config, globalDict, instrument="GPIB0::23::INSTR"):
            ExternalParameterBase.__init__(self, name, config, globalDict)
            self.rm = visa.ResourceManager()
            self.synthesizer = self.rm.open_resource( instrument)
            self.setDefaults()
            self.initializeChannelsToExternals()
            self.initOutput()

        def setValue(self, channel, v):
            if channel =='Freq':
                command = ":FREQ:CW {0:.5f}KHZ".format(v.m_as('kHz'))
            elif channel=='Power_dBm':
                command = ":POWER {0:.3f}".format(float(v))
            self.synthesizer.write(command)
            return v

        def getValue(self, channel):
            if channel=='Freq':
                answer = self.synthesizer.query(":FREQ:CW?")
                return Q( float(answer), "Hz" )
            elif channel=='Power_dBm':
                answer = self.synthesizer.query(":POWER?")
                return Q( float(answer), "" )

        def close(self):
            del self.synthesizer


    class AgilentPowerSupply(ExternalParameterBase):
        """
        Scan a laser by changing the voltage on a HP power supply. The frequency is controlled via a VCO.
        setValue is voltage of vco
        currentValue and currentExternalValue are current applied voltage
        """
        className = "Agilent Powersupply"
        _outputChannels = {None: 'V'}
        def __init__(self, name, config, globalDict, instrument="power_supply_next_to_397_box"):
            ExternalParameterBase.__init__(self, name, config, globalDict)
            self.rm = visa.ResourceManager()
            self.powersupply = self.rm.open_resource( instrument)
            self.setDefaults()
            self.initializeChannelsToExternals()
            self.initOutput()

        def setDefaults(self):
            ExternalParameterBase.setDefaults(self)
            self.settings.__dict__.setdefault('AOMFreq', Q(1, 'MHz'))

        def setValue(self, channel, value):
            """
            Move one steps towards the target, return current value
            """
            self.powersupply.write("volt {0}".format(value.m_as('V')))
            return value

        def paramDef(self):
            superior = ExternalParameterBase.paramDef(self)
            superior.append({'name': 'AOMFreq', 'type': 'magnitude', 'value': self.settings.AOMFreq})
            return superior

        def close(self):
            del self.powersupply

    class HP6632B(ExternalParameterBase):
        """
        Set the HP6632B power supply
        """
        className = "HP6632B Power Supply"
        _outputChannels = {"Curr": "A", "Volt": "V", "OnOff": ""}
        def __init__(self, name, config, globalDict, instrument="GPIB0::8::INSTR"):
            logger = logging.getLogger(__name__)
            ExternalParameterBase.__init__(self, name, config, globalDict)
            logger.info( "trying to open '{0}'".format(instrument) )
            self.rm = visa.ResourceManager()
            self.instrument = self.rm.open_resource(instrument)
            logger.info( "opened {0}".format(instrument) )
            self.setDefaults()
            self.initializeChannelsToExternals()
            self.initOutput()

        def setValue(self, channel, v):
            if channel=="OnOff":
                command = "OUTP ON" if v > 0 else "OUTP OFF"
            elif channel=="Curr":
                command = "Curr {0}".format(v.m_as('A'))
            elif channel=="Volt":
                command = "Volt {0}".format(v.m_as('V'))
            self.instrument.write(command)
            return v

        def getValue(self, channel):
            if channel=="OnOff":
                command, unit = "OUTP?", ""
            elif channel=="Curr":
                command, unit = "MEAS:Curr?", "A"
            elif channel=="Volt":
                command, unit = "Meas:Volt?", "V"
            value = Q(float(self.instrument.query(command)), unit)
            return value

        def close(self):
            del self.instrument


    class PTS3500(ExternalParameterBase):
        """
        Set the PTS3500 Frequency Source
        """
        className = "PTS3500 Frequency "
        _outputChannels = {"Freq": "GHz"}
        _outputLookup = { "Freq": ("F","Hz","\\nA1\\n")}
        def __init__(self, name, config, globalDict, instrument="GPIB0::16::INSTR"):
            logger = logging.getLogger(__name__)
            ExternalParameterBase.__init__(self, name, config, globalDict)
            logger.info( "trying to open '{0}'".format(instrument) )
            self.rm = visa.ResourceManager()
            self.instrument = self.rm.open_resource(instrument)
            self.setValue('Freq', self.settings.channelSettings['Freq'].value) #deals with the fact that PTS resets to zero when open_resource is called
            logger.info( "opened {0}".format(instrument) )
            self.setDefaults()
            self.initializeChannelsToExternals()
            self.initOutput()

        def setValue(self, channel, v):
            function, unit, suffix= self._outputLookup[channel]
            command = "{0}{1}{2}".format(function, int(v.m_as(unit)), suffix)
            self.instrument.write(command)
            return v

        def close(self):
            del self.instrument


    class DS345(ExternalParameterBase):
        """
        Set the DS345 SRS Function Generator
        """
        className = "DS345 SRS Function Generator "
        _outputChannels = {"Freq": "MHz", "Ampl": "dB"}
        _outputLookup = { "Freq": ("FREQ","Hz"),
                          "Ampl": ("AMPL","dB")}

        def __init__(self, name, config, globalDict, instrument="GPIB0::19::INSTR"):
            logger = logging.getLogger(__name__)
            ExternalParameterBase.__init__(self, name, config, globalDict)
            logger.info( "trying to open '{0}'".format(instrument) )
            self.rm = visa.ResourceManager()
            self.instrument = self.rm.open_resource(instrument)
            logger.info( "opened {0}".format(instrument) )
            self.setDefaults()
            self.initializeChannelsToExternals()
            self.initOutput()

        def setValue(self, channel, v):
            function, unit = self._outputLookup[channel]
            if channel=="Ampl":
                command = "{0}{1}DB".format(function, v.m_as(unit))
            else:
                command = "{0} {1}".format(function, v.m_as(unit))
            self.instrument.write(command)
            return v

        def close(self):
            del self.instrument









                                           #Start of in-house instruments~!



    class RG4000WFGenerator(ExternalParameterBase):
        className = "RG4000 Waveform Generator"
	#Populates the Params Control 
        _outputChannels = OrderedDict([("OutEnable1", ""),
                                       ("OutEnable2", ""),
                                       ("Freq1", "Hz"),
                                       ("Freq2", "Hz"),
                                       ("Amp1", "V"),
                                       ("Amp2", "V"),
                                       #("SweepEnabled1", ""),
                                       #("SweepEnabled2", ""),
                                       ("SweepStartFreq1", "Hz"),
                                       ("SweepStartFreq2", "Hz"),
                                       ("SweepStopFreq1", "Hz"),
                                       ("SweepStopFreq2", "Hz"),
                                       ("SweepTime1", "s"),
                                       ("SweepTime2", "s"),
                                       ("SweepReturnTime1", "s"),
                                       ("SweepReturnTime2", "s")]
                                      )

        _outputLookup = { "OutEnable1": ("OUTP1:STAT", 1, ""),
                          "OutEnable2": ("OUTP2:STAT", 2, ""),
                          "Freq1": ("SOUR1:FREQ", 1, "Hz"),
                          "Freq2": ("SOUR2:FREQ", 2, "Hz"),
                          "Amp1": ("SOUR1:VOLT:AMPL", 1, "V"),
                          "Amp2": ("SOUR2:VOLT:AMPL", 2, "V"),
                          #"SweepEnabled1": ("SOUR1:FREQ:MODE", 0, ""),
                          #"SweepEnabled2": ("SOUR2:FREQ:MODE", 0, ""),
                          "SweepStartFreq1": ("SOUR1:FREQ:STAR", 1, "Hz"),
                          "SweepStartFreq2": ("SOUR2:FREQ:STAR", 2, "Hz"),
                          "SweepStopFreq1": ("SOUR1:FREQ:STOP", 1, "Hz"),
                          "SweepStopFreq2": ("SOUR2:FREQ:STOP", 2, "Hz"),
                          "SweepTime1": ("SOUR1:SWE:TIME", 1, "s"),
                          "SweepTime2": ("SOUR2:SWE:TIME", 2, "s"),
                          "SweepReturnTime1": ("SOUR1:SWE:RTIM", 1, "s"),
                          "SweepReturnTime2": ("SOUR2:SWE:RTIM", 2, "s")}


        _inputChannels = {"OutEnable1": "",
                          "OutEnable2": "",
                          "Freq1": "Hz",
                          "Freq2": "Hz",
                          "Amp1": "V",
                          "Amp2": "V",
                          #"SweepEnabled1": "",
                          #"SweepEnabled2": "",
                          "SweepStartFreq1": "Hz",
                          "SweepStartFreq2": "Hz",
                          "SweepStopFreq1": "Hz",
                          "SweepStopFreq2": "Hz",
                          "SweepTime1": "s",
                          "SweepTime2": "s",
                          "SweepReturnTime1": "s",
                          "SweepReturnTime2": "s"}
        def __init__(self, name, config, globalDict, instrument="TCPIP0::192.168.168.21::INSTR"):
            ExternalParameterBase.__init__(self, name, config, globalDict)
            self.rm = visa.ResourceManager()
            self.instrument = self.rm.open_resource( instrument)
            self.setDefaults()
            self.initializeChannelsToExternals()
            self.qtHelper = qtHelper()
            self.newData = self.qtHelper.newData
            self.initOutput()            
        def setValue(self, channel, v):
            function, index, unit = self._outputLookup[channel]
            #print(function)
            if(function == ':OUTP1' or function == ':OUTP2' or function == 'OUTP1:STAT' or function == 'OUTP2:STAT'):
                #print('YOOYoooOyo I made it in here StandardExternalParameter')
                command = "{0} {1}".format(function, v)
            else:
                command = "{0} {1}".format(function, v.m_as(unit))#, index)
            #print(command)
            self.instrument.write(command) #set voltage
            return v
        def getValue(self, channel):
            function, index, unit = self._outputLookup[channel]
            command = "{0}?".format(function)#, index)
            try:
                return Q(float(self.instrument.query(command)), unit) #set voltage
            except:
                return self.instrument.query(command)
        def close(self):
            del self.instrument

    class AWG81180B(ExternalParameterBase):
        className = "81180B Arbitrary Waveform Generator"
	#Populates the Params Control 
        _outputChannels = OrderedDict([("InstrSelect", ""),
                                       ("Mode (0:FIX, 1:USER, 2:SEQ)", ""),
                                       ("Output Port (0:DC, 1:AC, 2:DAC)", ""),
                                       ("Clock Ref. (0:INT, 1:EXT)", ""),
                                       ("OutEnable", ""),
                                       ("Freq", "Hz"),
                                       ("Power_dBm", ""),
				       ("Cont/Trig Run Mode (0:CONT, 1:TRIG)", "")]
                                      )

        _outputLookup = { "InstrSelect":("INST:SEL", ""),
                          "Mode (0:FIX, 1:USER, 2:SEQ)": ("SOUR:FUNC:MODE", ""),
                          "Output Port (0:DC, 1:AC, 2:DAC)": ("", ""),
                          "Clock Ref. (0:INT, 1:EXT)": ("", ""),
                          "OutEnable": ("OUTP:STAT", ""),
                          "Freq": ("SOUR:FREQ", "Hz"),
                          "Power_dBm": ("SOUR:VOLT:LEV:AMPL", ""),
			  "Cont/Trig Run Mode (0:CONT, 1:TRIG)": ("INIT:CONT", "")}

        _inputChannels = {"InstrSelect": "",
                          "Mode (0:FIX, 1:USER, 2:SEQ)": "",
                          "Output Port (0:DC, 1:AC, 2:DAC)": "",
                          "Clock Ref. (0:INT, 1:EXT)": "",
                          "OutEnable": "",
                          "Freq": "Hz",
                          "Power_dBm": "",
			  "Cont/Trig Run Mode (0:CONT, 1:TRIG)": ""}
        def __init__(self, name, config, globalDict, instrument="TCPIP0::192.xxx.xxx.xx::inst0::INSTR"):
            ExternalParameterBase.__init__(self, name, config, globalDict)
            self.rm = visa.ResourceManager()
            self.instrument = self.rm.open_resource( instrument)
            self.setDefaults()
            self.initializeChannelsToExternals()
            self.qtHelper = qtHelper()
            self.newData = self.qtHelper.newData
            self.initOutput()
            channel = self.settings.channel #Set channel based on what is in the external parameter currently
            command = "INST:SEL %i"%channel
            self.instrument.write(command)

        def setDefaults(self):
            ExternalParameterBase.setDefaults(self)
            self.settings.__dict__.setdefault('channel', 1)
            
        def setValue(self, channel, v):
            if channel == "Mode (0:FIX, 1:USER, 2:SEQ)":
                if v == 0:
                    command = "SOUR:FUNC:MODE FIX"
                elif v == 1:
                    command = "SOUR:FUNC:MODE USER"
                elif v == 2:
                    command = "SOUR:FUNC:MODE SEQ"
            elif channel == "Output Port (0:DC, 1:AC, 2:DAC)":
                if v == 0:
                    command = "OUTP:COUP DC"
                elif v == 1:
                    command = "OUTP:COUP AC"
                elif v == 2:
                    command = "OUTP:COUP DAC"
            elif channel == "Clock Ref. (0:INT, 1:EXT)":
                if v == 0:
                    command = "SOUR:ROSC:SOUR INT"
                elif v == 1:
                    command = "SOUR:ROSC:SOUR EXT"
            elif channel == "Cont/Trig Run Mode (0:TRIG, 1:CONT)":
                if v == 0:
                    command = "INIT:CONT 0"
                elif v == 1:
                    command = "INIT:CONT 1"
            else:
                function, unit = self._outputLookup[channel]
                command = "{0} {1}".format(function, v)
            self.instrument.write(command)
            return v
        #def getValue(self, channel):
        #    function, unit = self._outputLookup[channel]
        #    command = "{0}?".format(function)#, index)
        #    try:
        #        return Q(float(self.instrument.query(command)), unit) #set voltage
        #    except:
        #        return self.instrument.query(command)
        def close(self):
            del self.instrument

    class HP08672A(ExternalParameterBase):
        className = "HP08672A Signal Generator (Boat Anchor)"
	#Populates the Params Control 
        _outputChannels = OrderedDict([("Freq", ""),
                                       ("OutLevel", ""),]
                                      )
        _outputLookup = { "Freq": ("", ""),
                          "OutLevel": ("", "")}
        _inputChannels = {"Freq": "",
                          "OutLevel": ""}
        freq_codes = ["P", "Q", "T", "U", "V", "W"] #P:10GHz, Q:1GHz, T:1MHz, U:100kHz, V:10kHz, W:1kHz
        vernier_codes = {3:"0", 2:"1", 1:"2", 0:"3", -1:"4", -2:"5", -3:"6", -4:"7", -5:"8", -6:"9", -7:":"}
        def __init__(self, name, config, globalDict, instrument="TCPIP0::192.xxx.xxx.xx::inst0::INSTR"):
            ExternalParameterBase.__init__(self, name, config, globalDict)
            self.rm = visa.ResourceManager()
            self.instrument = self.rm.open_resource( instrument)
            self.setDefaults()
            self.initializeChannelsToExternals()
            self.qtHelper = qtHelper()
            self.newData = self.qtHelper.newData
            self.initOutput()    
            command = "RL2"
            self.instrument.write(command) #Put device in remote mode        
        def setValue(self, channel, v):
            function, index, unit = self._outputLookup[channel]
            vv = v.to_base_units
            if function == "Freq":
            	if vv >= 10e8:
            	    code = 0
            	elif vv >= 1e8:
            	    code = 1
            	elif vv >= 1e6:
            	    code = 2
            	elif vv >= 1e5:
            	    code = 3
            	elif vv >= 1e4:
            	    code = 4
            	elif vv >= 1e3:
            	    code = 5
            	else:
            	    code = None
            	    print("Frequency too low for device - must be over 1 kHz")
            	try:
            	    command = "{0} {1}".format(freq_codes[code], vv)
            	except:
            	    return v
            elif function == "OutLevel":
                range_code = "K"
                vernier_code = "L"
                range = round(vv, -1) #Rounded to 10s digit
                vernier = vv - range
                if range > -100:
                    arg_range = abs(int(range/10))
                elif range > -110:
                    arg_range = ":"
                else:
                    arg_range = ";"
                arg_vernier = vernier_codes[vernier]
                try:
                    command = "{0}{1}{2}{3}".format(range_code, arg_range, vernier_code, arg_vernier)
                except:
                    return v
            self.instrument.write(command) #set voltage
            return v
        def getValue(self, channel):
            function, index, unit = self._outputLookup[channel]
            command = "{0}?".format(function)#, index)
            try:
                return Q(float(self.instrument.query(command)), unit) #set voltage
            except:
                return self.instrument.query(command)
        def close(self):
            del self.instrument
            
    if rigol_dp832_enabled:
        from rigol_dp832_controller.controller import DP832Controller, normalize_resource_string
        from rigol_dp832_controller.errors import RigolValidationError

        class RigolDP832Parameter(ExternalParameterBase):  # type: ignore[misc]
            """Thin translation layer from IonControl channels to DP832 controller API."""

            className = "Rigol DP832"

            _outputChannels: Dict[str, str] = {
                "Volt1": "V",
                "Volt2": "V",
                "Volt3": "V",
                "Curr1": "A",
                "Curr2": "A",
                "Curr3": "A",
                "OnOff1": "",
                "OnOff2": "",
                "OnOff3": "",
            }

            _inputChannels: Dict[str, str] = {
                "MeasVolt1": "V",
                "MeasVolt2": "V",
                "MeasVolt3": "V",
                "MeasCurr1": "A",
                "MeasCurr2": "A",
                "MeasCurr3": "A",
            }

            def __init__(self, name: str, config: Any, globalDict: Any, instrument: str = ""):
                super().__init__(name, config, globalDict)

                target = instrument or str(self._settings_get(config, "instrument", "")).strip()
                if not target:
                    raise RigolValidationError("No instrument provided. Use VISA string, host, or host:port.")

                timeout_ms = int(self._settings_get(config, "timeout_ms", 3000))
                query_delay_ms = int(self._settings_get(config, "query_delay_ms", 50))
                verify_readback = bool(self._settings_get(config, "verify_readback", True))
                retries = int(self._settings_get(config, "retries", 2))
                voltage_round_decimals = self._settings_get(config, "voltage_round_decimals", None)
                if isinstance(config, MappingABC):
                    backend_is_set = "backend" in config
                    backend = config.get("backend")
                else:
                    backend_is_set = hasattr(config, "backend")
                    backend = getattr(config, "backend", None)

                self.instrument = normalize_resource_string(target)
                controller_kwargs = {
                    "timeout_ms": timeout_ms,
                    "query_delay_ms": query_delay_ms,
                    "retries": retries,
                    "verify_readback": verify_readback,
                    "voltage_round_decimals": voltage_round_decimals,
                }
                if backend_is_set:
                    controller_kwargs["backend"] = backend

                self.controller = DP832Controller(self.instrument, **controller_kwargs)
                self.controller.connect()

                self.setDefaults()
                self.initializeChannelsToExternals()
                self.qtHelper = qtHelper()
                self.newData = self.qtHelper.newData
                self.initOutput()

            def setValue(self, channel: str, value: Any) -> Any:  # noqa: N802 - IonControl API style
                op, idx = self._parse_output_channel(channel)
                if op == "volt":
                    self.controller.set_voltage(idx, self._as_unit(value, "V"))
                    return self.getValue(channel)
                if op == "curr":
                    self.controller.set_current(idx, self._as_unit(value, "A"))
                    return self.getValue(channel)
                self.controller.set_output(idx, self._as_bool(value))
                return self.getValue(channel)

            def getValue(self, channel: str) -> Any:  # noqa: N802 - IonControl API style
                op, idx = self._parse_output_channel(channel)
                if op == "volt":
                    return Q(self.controller.get_voltage_setpoint(idx), "V")
                if op == "curr":
                    return Q(self.controller.get_current_setpoint(idx), "A")
                return Q(1 if self.controller.get_output(idx) else 0, "")

            def getExternalValue(self, channel: str) -> Any:  # noqa: N802 - IonControl API style
                # IonControl's OutputChannel calls this with the *output* channel name
                # (VoltN/CurrN/OnOffN), not the MeasVoltN/MeasCurrN name -- except when
                # callers pass a MeasVoltN/MeasCurrN name directly (e.g. getInputData
                # callers), which we also accept for backward compatibility.
                if channel.startswith("Meas"):
                    return self.getInputData(channel)
                if channel.startswith("OnOff"):
                    # No separate measured telemetry for output enable state; report
                    # the current setpoint, matching other IonControl driver classes.
                    return self.getValue(channel)
                if channel.startswith("Volt") or channel.startswith("Curr"):
                    return self.getInputData("Meas" + channel)
                raise RigolValidationError(f"Unsupported channel: {channel!r}")

            def getInputData(self, channel: str) -> Any:  # noqa: N802 - IonControl API style
                op, idx = self._parse_input_channel(channel)
                if op == "meas_volt":
                    return Q(self.controller.measure_voltage(idx), "V")
                return Q(self.controller.measure_current(idx), "A")

            @classmethod
            def connectedInstruments(cls):  # noqa: N802 - IonControl API style
                return []

            def close(self) -> None:
                self.controller.close()
                super_close = getattr(super(), "close", None)
                if callable(super_close):
                    super_close()

            @staticmethod
            def _settings_get(settings: Any, key: str, default: Any) -> Any:
                """Read IonControl InstrumentSettings-style attributes with default fallback."""
                value = getattr(settings, key, default)
                return default if value is None else value

            @staticmethod
            def _parse_output_channel(channel: str) -> Tuple[str, int]:
                match = re.fullmatch(r"(Volt|Curr|OnOff)([123])", channel)
                if not match:
                    raise RigolValidationError(f"Unsupported output channel: {channel!r}")
                prefix, idx_raw = match.groups()
                prefix_map = {"Volt": "volt", "Curr": "curr", "OnOff": "onoff"}
                return prefix_map[prefix], int(idx_raw)

            @staticmethod
            def _parse_input_channel(channel: str) -> Tuple[str, int]:
                match = re.fullmatch(r"(MeasVolt|MeasCurr)([123])", channel)
                if not match:
                    raise RigolValidationError(f"Unsupported input channel: {channel!r}")
                prefix, idx_raw = match.groups()
                prefix_map = {"MeasVolt": "meas_volt", "MeasCurr": "meas_curr"}
                return prefix_map[prefix], int(idx_raw)

            @staticmethod
            def _as_unit(value: Any, unit: str) -> float:
                if hasattr(value, "m_as"):
                    return float(value.m_as(unit))
                return float(value)

            @staticmethod
            def _as_bool(value: Any) -> bool:
                if isinstance(value, bool):
                    return value
                if hasattr(value, "m_as"):
                    return float(value.m_as("")) > 0
                return float(value) > 0

if DG4000Enabled:
    class RG4000WFGeneratorNonVisa(ExternalParameterBase):
        className = "RG4000 Waveform Generator Non VISA"
	#Populates the Params Control 
        _outputChannels = OrderedDict([("OutEnable1", ""),
                                       ("OutEnable2", ""),
                                       ("Freq1", "Hz"),
                                       ("Freq2", "Hz"),
                                       ("Amp1", "V"),
                                       ("Amp2", "V")
                                       #("SweepEnabled1", ""),
                                       #("SweepEnabled2", ""),
                                       #("SweepStartFreq1", "Hz"),
                                       #("SweepStartFreq2", "Hz"),
                                       #("SweepStopFreq1", "Hz"),
                                       #("SweepStopFreq2", "Hz"),
                                       #("SweepTime1", "s"),
                                       #("SweepTime2", "s"),
                                       #("SweepReturnTime1", "s"),
                                       #("SweepReturnTime2", "s")]
                                       ]
                                      )

        _outputLookup = { "OutEnable1": ("OUTP1:STAT", 1, ""),
                          "OutEnable2": ("OUTP2:STAT", 2, ""),
                          "Freq1": ("SOUR1:FREQ", 1, "Hz"),
                          "Freq2": ("SOUR2:FREQ", 2, "Hz"),
                          "Amp1": ("SOUR1:VOLT:AMPL", 1, "V"),
                          "Amp2": ("SOUR2:VOLT:AMPL", 2, "V")
                          #"SweepEnabled1": ("SOUR1:FREQ:MODE", 0, ""),
                          #"SweepEnabled2": ("SOUR2:FREQ:MODE", 0, ""),
                          #"SweepStartFreq1": ("SOUR1:FREQ:STAR", 1, "Hz"),
                          #"SweepStartFreq2": ("SOUR2:FREQ:STAR", 2, "Hz"),
                          #"SweepStopFreq1": ("SOUR1:FREQ:STOP", 1, "Hz"),
                          #"SweepStopFreq2": ("SOUR2:FREQ:STOP", 2, "Hz"),
                          #"SweepTime1": ("SOUR1:SWE:TIME", 1, "s"),
                          #"SweepTime2": ("SOUR2:SWE:TIME", 2, "s"),
                          #"SweepReturnTime1": ("SOUR1:SWE:RTIM", 1, "s"),
                          #"SweepReturnTime2": ("SOUR2:SWE:RTIM", 2, "s")
                          }


        _inputChannels = {"OutEnable1": "",
                          "OutEnable2": "",
                          "Freq1": "Hz",
                          "Freq2": "Hz",
                          "Amp1": "V",
                          "Amp2": "V"
                          #"SweepEnabled1": "",
                          #"SweepEnabled2": "",
                          #"SweepStartFreq1": "Hz",
                          #"SweepStartFreq2": "Hz",
                          #"SweepStopFreq1": "Hz",
                          #"SweepStopFreq2": "Hz",
                          #"SweepTime1": "s",
                          #"SweepTime2": "s",
                          #"SweepReturnTime1": "s",
                          #"SweepReturnTime2": "s"
                          }
        def __init__(self, name, config, globalDict, instrument="TCPIP0::192.168.168.21::inst0::INSTR"):
            ExternalParameterBase.__init__(self, name, config, globalDict)
            self.rm = visa.ResourceManager()
            self.instrument = self.rm.open_resource( instrument)
            self.setDefaults()
            self.initializeChannelsToExternals()
            self.qtHelper = qtHelper()
            self.newData = self.qtHelper.newData
            self.initOutput()   
        def setValue(self, channel, v):
            function, index, unit = self._outputLookup[channel]
            #print(function)
            if(function == ':OUTP1' or function == ':OUTP2' or function == 'OUTP1:STAT' or function == 'OUTP2:STAT'):
                #print('YOOYoooOyo I made it in here StandardExternalParameter')
                command = "{0} {1}".format(function, v)
            else:
                command = "{0} {1}".format(function, v.m_as(unit))#, index)
            #print(command)
            self.instrument.write(command) #set voltage
            return v
        def getValue(self, channel):
            function, index, unit = self._outputLookup[channel]
            command = "{0}?".format(function)#, index)
            try:
                val = Q(float(self.instrument.query(command)), unit)
                val = str(val)
                val = val[:-2]
                #print("Q unit %s"%val)
                if val == "ON":
                    #print("Q unit IN %s"%val)
                    val = 1
                else:
                    val = 0
                return val #set voltage
            except:
                val = str(self.instrument.query(command))
                val = val[:-2]
                #print("Other unit %s"%val)
                if val == "ON":
                    #print("Other unit IN %s"%val)
                    val = 1
                else:
                    val = 0
                return val
        def close(self):
            del self.instrument

if wavemeterEnabled or HighFinesseWavemeterEnabled:
    from wavemeter.Wavemeter import Wavemeter

if HighFinesseWavemeterEnabled:
    class WavemeterChannel(ExternalParameterBase):
        className = "HighFinesseChannel"
        _outputChannels = {None: "THz"}
        #_outputLookup = {None:("", "THz")}
        #_inputChannels = {None: "THz"}
        def __init__(self, name, config, globalDict, instrument="192.168.168.203:8080"):
            logger = logging.getLogger(__name__)
            ExternalParameterBase.__init__(self, name, config, globalDict)
            self.instrument = instrument
            self.wavemeter = Wavemeter(self.instrument)
            #logger.info( "LaserWavemeterScan savedValue {0}".format(self.savedValue) )
            self.channel = 1
            self.initializeChannelsToExternals()
            self.initOutput()


        def setDefaults(self):
            ExternalParameterBase.setDefaults(self)
            self.settings.__dict__.setdefault('channel', 1)
            self.settings.__dict__.setdefault('maxDeviation', Q(5, 'MHz'))
            self.settings.__dict__.setdefault('maxAge', Q(2, 's'))

        def setValue(self, channel, value):
            """
            Move one steps towards the target, return current value
            """
            logger = logging.getLogger(__name__)
            if value is not None:
                self.currentFrequency = self.wavemeter.set_frequency(value, self.settings.channel, self.settings.maxAge)
            logger.debug( "setFrequency {0}, current frequency {1}".format(self.settings.channelSettings[None].value, self.currentFrequency) )
            #print("self.currentFrequency is", self.currentFrequency, ". self.settings.channelSettings[None].value is", self.settings.channelSettings[None].value, "self.settings.maxDeviation is", self.settings.maxDeviation)
            #arrived = self.currentFrequency is not None and abs(
            #    self.currentFrequency - self.settings.channelSettings[None].value) < self.settings.maxDeviation
            #print(arrived)
            arrived = True
            return value, arrived

        def currentExternalValue(self, channel):
            logger = logging.getLogger(__name__)
            self.lastExternalValue = self.wavemeter.get_frequency(self.settings.channel, self.settings.maxAge )
            logger.debug( str(self.lastExternalValue) )
            self.detuning=(self.lastExternalValue)
            self.currentFrequency = self.wavemeter.get_frequency(self.settings.channel, self.settings.maxAge )
            return self.lastExternalValue

        def paramDef(self):
            superior = ExternalParameterBase.paramDef(self)
            superior.append({'name': 'channel', 'type': 'int', 'value': self.settings.channel})
            superior.append({'name': 'maxDeviation', 'type': 'magnitude', 'value': self.settings.maxDeviation})
            superior.append({'name': 'maxAge', 'type': 'magnitude', 'value': self.settings.maxAge})
            return superior
            


SLSoflEnabled = project.isEnabled('hardware','SLS Offset Frequency Lock')

if SLSoflEnabled:
    import paramiko

    class OffsetFrequencyLock(ExternalParameterBase):

        className = "SLS Offset Frequency Lock"
        _outputChannels = OrderedDict([("SLSOffsetFrequency", "MHz"),
                                       ("SLSAmplitude", "")])
        _outputLookup = { "SLSOffsetFrequency": ("setOffsetFrequency.py", "MHz"),
                          "SLSAmplitude": ("setRFAmplitude.py", "")}
        def __init__(self, name, config, globalDict, instrument):
            logger = logging.getLogger(__name__)
            ExternalParameterBase.__init__(self, name, config, globalDict)
            project = getProject()
            instrument_list = project.hardware.get('SLS Offset Frequency Lock')
            instrument = instrument_list[instrument]
            ip_addr = instrument.get('ipAddress')
            user=instrument.get('user')
            pwd=instrument.get('password')
            port_no = instrument.get('port')
            self.ssh_client = paramiko.SSHClient()
            self.ssh_client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
            self.ssh_client.connect(ip_addr, username=user, password=pwd, port=port_no)
            self.setDefaults()
            self.initializeChannelsToExternals()
            self.qtHelper = qtHelper()
            self.newData = self.qtHelper.newData
            self.initOutput()	

        def setDefaults(self):
            ExternalParameterBase.setDefaults(self)
            #self.settings.__dict__.setdefault('channel', 1)
            #self.settings.__dict__.setdefault('maxDeviation', Q(5, 'MHz'))
            #self.settings.__dict__.setdefault('maxAge', Q(2, 's'))
                
        def setValue(self, channel,v):
            logger = logging.getLogger(__name__)
            function, unit = self._outputLookup[channel]
            if unit == "MHz":
                factor = "e6"
            else:
                factor = ""
            #command = "{0} {1}".format(function, v)
            v_channel = self._outputChannels[channel]
            command = "python {0} {1}{2}".format(function, v.m_as(unit), factor)
            #print(command)
            self.ssh_client.exec_command(command)
            return v, True

        def connectedInstruments(self):
            project = getProject()
            instrument_list = project.hardware.get('SLS Offset Frequency Lock').keys()
            return instrument_list

        def currentExternalValue(self, channel):
            return 0

DC_Controller_Enabled = project.isEnabled('hardware', 'Senkolab Four rod DC Controller')    

if DC_Controller_Enabled:
    try:
        from DC_Voltage_Control.src.DC_voltage_control_python.dc_ctr_rpc_client import FourRodDCControllerClient
        from DC_Voltage_Control.src.DC_voltage_control_python.dc_ctr_enum import *
    except ImportError:
        importErrorPopup('DC Voltage Control')


    class DCVoltageControl(ExternalParameterBase):
        """
        Control the voltages on rods and needles for the four rod trap
        """
        className = "Four rod DC Voltage Control"
        _outputChannels = OrderedDict([
            ('Enable Remote Control', ''),
            ('Needle_1_Voltage', 'V'),
            ('Needle_2_Voltage', 'V'),
            ('Rod_1_Voltage', 'V'),
            ('Rod_2_Voltage', 'V'),
            ('Rod_3_Voltage', 'V'),
            ('Rod_4_Voltage', 'V')])

        _outputLookup = {
            'Needle_1_Voltage': CHANNEL_N1,
            'Needle_2_Voltage': CHANNEL_N2,
            'Rod_1_Voltage': CHANNEL_R1,
            'Rod_2_Voltage': CHANNEL_R2,
            'Rod_3_Voltage': CHANNEL_R3,
            'Rod_4_Voltage': CHANNEL_R4
        }
        _inputChannels = {"Needle_1_Voltage": "V",
                          "Needle_1_Voltage": "V",
                          "Rod_1_Voltage": "V",
                          "Rod_2_Voltage": "V",
                          "Rod_3_Voltage": "V",
                          "Rod_4_Voltage": "V"}
        def __init__(self, name, config, globalDict, instrument):
            logger = logging.getLogger(__name__)
            ExternalParameterBase.__init__(self, name, config, globalDict)
            project = getProject()
            instrument_list = project.hardware.get('Senkolab Four rod DC Controller')
            instrument = instrument_list[instrument]
            ip_addr = instrument.get('ipAddress')
            port = instrument.get('port')
            self.dc_client = FourRodDCControllerClient(address=ip_addr + ':' + port)
            self.setDefaults()
            self.initializeChannelsToExternals()
            self.qtHelper = qtHelper()
            self.newData = self.qtHelper.newData
            self.initOutput()

        def setDefaults(self):
            ExternalParameterBase.setDefaults(self)
            #self.settings.__dict__.setdefault('channel', 1)
            #self.settings.__dict__.setdefault('maxDeviation', Q(5, 'MHz'))
            #self.settings.__dict__.setdefault('maxAge', Q(2, 's'))

        def setValue(self, channel, val):
            if channel == 'Enable Remote Control':
                v = val.m_as('')
                v = int(v)
                if v not in (0, 1, 255):
                    raise ValueError("Not an available mode!!!!!")
                self.dc_client.set_mode_all(v)
            else:
                v = val.m_as('V')
                v = float(v)
                v_channel = self._outputLookup[channel]
                #print(v_channel, v)
                self.dc_client.set_volt(v_channel, v)
            return val, True

        def getExternalValue(self, channel=None):
            if channel == 'Enable Remote Control':
                mode = self.dc_client.get_mode(CHANNEL_N1)
                return Q(mode, '')
            else:
                v_channel = self._outputLookup[channel]
                voltage = self.dc_client.get_volt_adc(v_channel)
                voltage = round(voltage,4)
                return Q(voltage, 'V')

        def connectedInstruments(self):
            project = getProject()
            instrument_list = project.hardware.get('Senkolab Four rod DC Controller').keys()
            return instrument_list















class DummyParameter(ExternalParameterBase):
    """
    DummyParameter, used to debug this part of the software.
    """
    className = "Dummy"
    _outputChannels = { 'O1':"Hz",'O7': "Hz"}
    def __init__(self, name, settings, globalDict, instrument=''):
        logger = logging.getLogger(__name__)
        ExternalParameterBase.__init__(self, name, settings, globalDict)
        logger.info( "Opening DummyInstrument {0}".format(instrument) )
        self.initializeChannelsToExternals()
        self.initOutput()

    def setValue(self, channel, value):
        logger = logging.getLogger(__name__)
        logger.info( "Dummy output channel {0} set to: {1}".format( channel, value ) )
        return value
            

class DummySingleParameter(ExternalParameterBase):
    """
    DummyParameter, used to debug this part of the software.
    """
    className = "DummySingle"
    _outputChannels = {None: "Hz"}

    def __init__(self, name, settings, globalDict, instrument=''):
        logger = logging.getLogger(__name__)
        ExternalParameterBase.__init__(self, name, settings, globalDict)
        logger.info( "Opening DummyInstrument {0}".format(instrument) )
        self.initializeChannelsToExternals()
        self.initOutput()

    def setValue(self, channel, value):
        logger = logging.getLogger(__name__)
        logger.info("Dummy output channel {0} set to: {1}".format(channel, value))
        return value

    @classmethod
    def connectedInstruments(cls):
        return ['Anything will do']





if visaEnabled and wavemeterEnabled:
    class LaserWavemeterScan(AgilentPowerSupply):
        """
        Scan a laser by changing the voltage on a HP power supply. The frequency is controlled via a VCO.
        setValue is voltage of vco
        currentValue is applied voltage
        currentExternalValue are frequency read from wavemeter
        """

        className = "Laser VCO Wavemeter"
        _dimension = Q(1, 'V')
        def __init__(self, name, config, globalDict, instrument="power_supply_next_to_397_box"):
            AgilentPowerSupply.__init__(self, name, config, globalDict, instrument)
            self.setDefaults()
            self.wavemeter = None
            self.initOutput()

        def setDefaults(self):
            AgilentPowerSupply.setDefaults(self)
            self.settings.__dict__.setdefault('wavemeter_address', 'http://132.175.165.36:8082')       # if True go to the target value in one jump
            self.settings.__dict__.setdefault('wavemeter_channel', 6 )       # if True go to the target value in one jump
            self.settings.__dict__.setdefault('use_external', True )       # if True go to the target value in one jump

        def currentExternalValue(self, channel):
            self.wavemeter = Wavemeter(self.settings.wavemeter_address)
            logger = logging.getLogger(__name__)
            self.lastExternalValue = self.wavemeter.get_frequency(self.settings.wavemeter_channel)
            logger.debug( str(self.lastExternalValue) )
            self.detuning=(self.lastExternalValue)
            counter = 0
            while self.detuning is None or numpy.abs(self.detuning)>=1 and counter<10:
                self.lastExternalValue = self.wavemeter.get_frequency(self.settings.wavemeter_channel)
                self.detuning=(self.lastExternalValue-self.settings.value[channel])
                counter += 1
            return self.lastExternalValue

        def asyncCurrentExternalValue(self, callbackfunc ):
            self.wavemeter = Wavemeter(self.settings.wavemeter_address) if self.wavemeter is None else self.wavemeter
            self.wavemeter.asyncGetFrequency(self.settings.wavemeter_channel, callbackfunc)

        def paramDef(self):
            superior = AgilentPowerSupply.paramDef(self)
            superior.append({'name': 'wavemeter_address', 'type': 'str', 'value': self.settings.wavemeter_address})
            superior.append({'name': 'wavemeter_channel', 'type': 'int', 'value': self.settings.wavemeter_channel})
            superior.append({'name': 'use_external', 'type': 'bool', 'value': self.settings.use_external})
            return superior

        def useExternalValue(self, channel):
            return self.settings.use_external

if wavemeterEnabled:
    class LaserWavemeterLockScan(ExternalParameterBase):
        """
        Scan a laser by setting the lock point on the wavemeter lock.
        setValue is laser frequency
        currentValue is currently set value
        currentExternalValue is frequency read from wavemeter
        """
        className = "Laser Wavemeter Lock"
        _outputChannels = { None: "GHz"}
        def __init__(self, name, config, globalDict, instrument=None):
            logger = logging.getLogger(__name__)
            ExternalParameterBase.__init__(self, name, config, globalDict)
            self.wavemeter = Wavemeter(instrument)
            #logger.info( "LaserWavemeterScan savedValue {0}".format(self.savedValue) )
            self.setDefaults()
            self.initializeChannelsToExternals()
            self.initOutput()

        def setDefaults(self):
            ExternalParameterBase.setDefaults(self)
            self.settings.__dict__.setdefault('channel', 6)
            self.settings.__dict__.setdefault('maxDeviation', Q(5, 'MHz'))
            self.settings.__dict__.setdefault('maxAge', Q(2, 's'))

        def setValue(self, channel, value):
            """
            Move one steps towards the target, return current value
            """
            logger = logging.getLogger(__name__)
            if value is not None:
                self.currentFrequency = self.wavemeter.set_frequency(value, self.settings.channel, self.settings.maxAge)
            logger.debug( "setFrequency {0}, current frequency {1}".format(self.settings.channelSettings[None].value, self.currentFrequency) )
            arrived = self.currentFrequency is not None and abs(
                self.currentFrequency - self.settings.channelSettings[None].value) < self.settings.maxDeviation
            return value, arrived

        def currentExternalValue(self, channel):
            logger = logging.getLogger(__name__)
            self.lastExternalValue = self.wavemeter.get_frequency(self.settings.channel, self.settings.maxAge )
            logger.debug( str(self.lastExternalValue) )
            self.detuning=(self.lastExternalValue)
            self.currentFrequency = self.wavemeter.get_frequency(self.settings.channel, self.settings.maxAge )
            return self.lastExternalValue

        def paramDef(self):
            superior = ExternalParameterBase.paramDef(self)
            superior.append({'name': 'channel', 'type': 'int', 'value': self.settings.channel})
            superior.append({'name': 'maxDeviation', 'type': 'magnitude', 'value': self.settings.maxDeviation})
            superior.append({'name': 'maxAge', 'type': 'magnitude', 'value': self.settings.maxAge})
            return superior
         