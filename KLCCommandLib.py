from ctypes import *

#region import dll functions

klcLib = cdll.LoadLibrary(r"C:\Users\Laboratorio\AppData\Local\Programs\Python\Python312\KLCCommandLib_x64.dll")

cmdList = klcLib.List
cmdList.argtypes=[c_char_p, c_int]
cmdList.restype=c_int

cmdOpen = klcLib.Open
cmdOpen.restype=c_int
cmdOpen.argtypes=[c_char_p, c_int, c_int]

cmdSetEnable = klcLib.SetEnable
cmdSetEnable.restype=c_int
cmdSetEnable.argtypes=[c_int, c_byte]

cmdGetEnable = klcLib.GetEnable
cmdGetEnable.restype=c_int
cmdGetEnable.argtypes=[c_int, POINTER(c_byte)]

cmdSetVoltage1 = klcLib.SetVoltage1
cmdSetVoltage1.restype=c_int
cmdSetVoltage1.argtypes=[c_int, c_float]

cmdSetVoltage2 = klcLib.SetVoltage2
cmdSetVoltage2.restype=c_int
cmdSetVoltage2.argtypes=[c_int, c_float]

cmdGetVoltage1 = klcLib.GetVoltage1
cmdGetVoltage1.restype=c_int
cmdGetVoltage1.argtypes=[c_int, POINTER(c_float)]

cmdGetVoltage2 = klcLib.GetVoltage2
cmdGetVoltage2.restype=c_int
cmdGetVoltage2.argtypes=[c_int, POINTER(c_float)]

cmdSetFrequency1 = klcLib.SetFrequency1
cmdSetFrequency1.restype=c_int
cmdSetFrequency1.argtypes=[c_int, c_ushort]

cmdSetFrequency2 = klcLib.SetFrequency2
cmdSetFrequency2.restype=c_int
cmdSetFrequency2.argtypes=[c_int, c_ushort]

cmdGetFrequency1 = klcLib.GetFrequency1
cmdGetFrequency1.restype=c_int
cmdGetFrequency1.argtypes=[c_int, POINTER(c_ushort)]
   
cmdGetFrequency2 = klcLib.GetFrequency2
cmdGetFrequency2.restype=c_int
cmdGetFrequency2.argtypes=[c_int, POINTER(c_ushort)]

cmdSetSWFrequency = klcLib.SetSWFrequency
cmdSetSWFrequency.restype=c_int
cmdSetSWFrequency.argtypes=[c_int, c_float]

cmdGetSWFrequency = klcLib.GetSWFrequency
cmdGetSWFrequency.restype=c_int
cmdGetSWFrequency.argtypes=[c_int, POINTER(c_float)]

cmdSetInputMode = klcLib.SetInputMode
cmdSetInputMode.restype=c_int
cmdSetInputMode.argtypes=[c_int, c_ubyte]

cmdGetInputMode = klcLib.GetInputMode
cmdGetInputMode.restype=c_int
cmdGetInputMode.argtypes=[c_int, POINTER(c_ubyte)]

cmdSetTrigIOConfigure = klcLib.SetTrigIOConfigure
cmdSetTrigIOConfigure.restype=c_int
cmdSetTrigIOConfigure.argtypes=[c_int, c_ubyte]

cmdGetTrigIOConfigure = klcLib.GetTrigIOConfigure
cmdGetTrigIOConfigure.restype=c_int
cmdGetTrigIOConfigure.argtypes=[c_int, POINTER(c_ubyte)]

cmdSetChannelEnable = klcLib.SetChannelEnable
cmdSetChannelEnable.restype=c_int
cmdSetChannelEnable.argtypes=[c_int, c_ubyte]

cmdGetChannelEnable = klcLib.GetChannelEnable
cmdGetChannelEnable.restype=c_int
cmdGetChannelEnable.argtypes=[c_int, POINTER(c_ubyte)]

cmdSetKcubeMMIParams = klcLib.SetKcubeMMIParams
cmdSetKcubeMMIParams.restype=c_int
cmdSetKcubeMMIParams.argtypes=[c_int, c_ushort, c_ushort]

cmdGetKcubeMMIParams = klcLib.GetKcubeMMIParams
cmdGetKcubeMMIParams.restype=c_int
cmdGetKcubeMMIParams.argtypes=[c_int, POINTER(c_ushort), POINTER(c_ushort)]

cmdSetKcubeMMILock = klcLib.SetKcubeMMILock
cmdSetKcubeMMILock.restype=c_int
cmdSetKcubeMMILock.argtypes=[c_int, c_ubyte]

cmdGetKcubeMMILock = klcLib.GetKcubeMMILock
cmdGetKcubeMMILock.restype=c_int
cmdGetKcubeMMILock.argtypes=[c_int, POINTER(c_ubyte)]

cmdGetOutPutStatus = klcLib.GetOutPutStatus
cmdGetOutPutStatus.restype=c_int
cmdGetOutPutStatus.argtypes=[c_int, POINTER(c_ushort), POINTER(c_float), POINTER(c_ushort),POINTER(c_ushort)]

cmdGetStatus = klcLib.GetStatus
cmdGetStatus.restype=c_int
cmdGetStatus.argtypes=[c_int, POINTER(c_ubyte), POINTER(c_float), POINTER(c_ushort), POINTER(c_float), POINTER(c_ushort), POINTER(c_float), POINTER(c_ushort),POINTER(c_ushort),POINTER(c_ubyte),POINTER(c_ubyte),POINTER(c_ubyte),POINTER(c_ushort)]

cmdUpdateOutputLUT = klcLib.UpdateOutputLUT
cmdUpdateOutputLUT.restype=c_int
cmdUpdateOutputLUT.argtypes=[c_int, c_ushort, c_float]

cmdRemoveLastOutputLUT = klcLib.RemoveLastOutputLUT
cmdRemoveLastOutputLUT.restype=c_int
cmdRemoveLastOutputLUT.argtypes=[c_int, c_ushort]

cmdSetOutputLUT = klcLib.SetOutputLUT
cmdSetOutputLUT.restype=c_int
cmdSetOutputLUT.argtypes=[c_int, POINTER(c_float), c_ushort]

cmdSetOutputLUTParams = klcLib.SetOutputLUTParams
cmdSetOutputLUTParams.restype= c_int
cmdSetOutputLUTParams.argtypes=[c_int, c_ushort, c_ulong, c_ulong, c_ulong]

cmdGetOutputLUTParams = klcLib.GetOutputLUTParams
cmdGetOutputLUTParams.restype=c_int
cmdGetOutputLUTParams.argtypes=[c_int, POINTER(c_ushort), POINTER(c_ulong), POINTER(c_ulong), POINTER(c_ulong)]

#endregion

def klcListDevices():
    """ List all connected KLC devices
    Returns: 
       The klc device list, each deice item is serialNumber/COM
    """
    str = create_string_buffer(1024, '\0')
    result = cmdList(str,1024)
    devicesStr = str.raw.decode("utf-8","ignore").rstrip('\x00').split(',')
    length = len(devicesStr)
    i=0
    devices=[]
    devInfo=["",""]
    discription="Kinesis LC Controller"
    while(i<length):
        str = devicesStr[i]
        if (i%2 == 0):
            if str != '':
                devInfo[0] = str
            else:
                i+=1
        else:
            if(str.find(discription)>=0):
                #info = str.split('&')
                devInfo[1] = discription
                devices.append(devInfo.copy())
        i+=1
    return devices

def klcOpen(serialNo, nBaud, timeout):
    """ Open device
    Args:
        serialNo: serial number of KLC device
        nBaud: bit per second of port
        timeout: set timeout value in (s)
    Returns: 
        non-negative number: hdl number returned Successful; negative number: failed.
    """
    return cmdOpen(serialNo.encode('utf-8'), nBaud, timeout)

def klcIsOpen(serialNo):
    """ Check opened status of device
    Args:
        serialNo: serial number of device
    Returns: 
        0: device is not opened; 1: device is opened.
    """
    return klcLib.IsOpen(serialNo.encode('utf-8'))

def klcClose(hdl):
    """ Close opened device
    Args:
        hdl: the handle of opened device
    Returns: 
        0: Success; negative number: failed.
    """
    return klcLib.Close(hdl)

def klcSetEnable(hdl, enable):
    """ Set output enable state
    Args:
        hdl: the handle of opened device
        enable: 0x01 enable, 0x02 disable
    Returns: 
        0: Success; negative number: failed.
    """
    return cmdSetEnable(hdl, enable);

def klcGetEnable(hdl, enable):
    """ Get output enable state
    Args:
        hdl: the handle of opened device
        enable: 0x01 enable, 0x02 disable
    Returns: 
        0: Success; negative number: failed.
    """
    e = c_byte(0)
    ret = cmdGetEnable(hdl, e)
    enable[0] = e.value
    return ret

def klcGetVoltage1(hdl, voltage):
    """ Get output Voltage 1.
    Args:
        hdl: the handle of opened device
        voltage: the output voltage
    Returns: 
        0: Success; negative number: failed.
    """
    vol = c_float(0)
    ret = cmdGetVoltage1(hdl, vol)
    voltage[0] = vol.value
    return ret 

def klcSetVoltage1(hdl, voltage):
    """ Set the output voltage 1.
    Args:
        hdl: the handle of opened device
        voltage: the output voltage 0~25 V.
    Returns: 
        0: Success; negative number: failed.
    """
    return cmdSetVoltage1(hdl, voltage)

def klcGetVoltage2(hdl, voltage):
    """ Get output Voltage 2.
    Args:
        hdl: the handle of opened device
        voltage: the output voltage
    Returns: 
        0: Success; negative number: failed.
    """
    vol = c_float(0)
    ret = cmdGetVoltage2(hdl, vol)
    voltage[0] = vol.value
    return ret 

def klcSetVoltage2(hdl, voltage):
    """ Set the output voltage 2.
    Args:
        hdl: the handle of opened device
        voltage: the output voltage 0~25 V.
    Returns: 
        0: Success; negative number: failed.
    """
    return cmdSetVoltage2(hdl, voltage)

def klcGetFrequency1(hdl, freqency):
    """ Get output Frequency 1.
    Args:
        hdl: the handle of opened device
        freqency: the output voltage
    Returns: 
        0: Success; negative number: failed.
    """
    freq = c_ushort(0)
    ret = cmdGetFrequency1(hdl, freq)
    freqency[0] = freq.value
    return ret 

def klcSetFrequency1(hdl, freqency):
    """ Set the output Frequency 1.
    Args:
        hdl: the handle of opened device
        freqency: the output frequency 500~10000 Hz.
    Returns: 
        0: Success; negative number: failed.
    """
    return cmdSetFrequency1(hdl, freqency)

def klcGetFrequency2(hdl, freqency):
    """ Get output Frequency 2.
    Args:
        hdl: the handle of opened device
        freqency: the output freqency
    Returns: 
        0: Success; negative number: failed.
    """
    freq = c_ushort(0)
    ret = cmdGetFrequency2(hdl, freq)
    freqency[0] = freq.value
    return ret 

def klcSetFrequency2(hdl, freqency):
    """ Set the output Frequency 2.
    Args:
        hdl: the handle of opened device
        freqency: the output frequency 500~10000 Hz.
    Returns: 
        0: Success; negative number: failed.
    """
    return cmdSetFrequency2(hdl, freqency)

def klcGetSWFrequency(hdl, freqency):
    """ Get frequency of switch mode.
    Args:
        hdl: the handle of opened device
        freqency: the output frequency
    Returns: 
        0: Success; negative number: failed.
    """
    freq = c_float(0)
    ret = cmdGetSWFrequency(hdl, freq)
    freqency[0] = freq.value
    return ret 

def klcSetSWFrequency(hdl, freqency):
    """ Set frequency of switch mode.
    Args:
        hdl: the handle of opened device
        freqency: the output frequency 0.1~150 Hz.
    Returns: 
        0: Success; negative number: failed.
    """
    return cmdSetSWFrequency(hdl, freqency)

def klcGetInputMode(hdl, mode):
    """ Get device analog input mode.
    Args:
        hdl: the handle of opened device
        mode: 0 disable; 1 enable
    Returns: 
        0: Success; negative number: failed.
    """
    m = c_ubyte(0)
    ret = cmdGetInputMode(hdl, m)
    mode[0] = m.value
    return ret 

def klcSetInputMode(hdl, mode):
    """ Set device analog input mode.
    Args:
        hdl: the handle of opened device
        mode: 0 disable; 1 enable
    Returns: 
        0: Success; negative number: failed.
    """
    return cmdSetInputMode(hdl, mode)

def klcGetTrigIOConfigure(hdl, mode):
    """ Get device trigger pin mode.
    Args:
        hdl: the handle of opened device
        mode:  01 -Trigger Pin1 output, Pin2 output; 02- Trigger Pin1 In, Pin2 out; 03- Trigger Pin1 out, Pin2 in
    Returns: 
        0: Success; negative number: failed.
    """
    m = c_ubyte(0)
    ret = cmdGetTrigIOConfigure(hdl, m)
    mode[0] = m.value
    return ret 

def klcSetTrigIOConfigure(hdl, mode):
    """ Set device trigger pin mode.
    Args:
        hdl: the handle of opened device
        mode: 01 -Trigger Pin1 output, Pin2 output; 02- Trigger Pin1 In, Pin2 out; 03- Trigger Pin1 out, Pin2 in.
    Returns: 
        0: Success; negative number: failed.
    """
    return cmdSetTrigIOConfigure(hdl, mode)

def klcGetChannelEnable(hdl, enable):
    """ Get device channel enable state.
    Args:
        hdl: the handle of opened device
        enable: 0x01 V1 Enable , 0x02  V2 Enable, 0x03  SW Enable, 0x00 channel output disable.
    Returns: 
        0: Success; negative number: failed.
    """
    e = c_ubyte(0)
    ret = cmdGetChannelEnable(hdl, e)
    enable[0] = e.value
    return ret 

def klcSetChannelEnable(hdl, enable):
    """ Set device channel enable state.
    Args:
        hdl: the handle of opened device
        enable: 0x01 V1 Enable , 0x02  V2 Enable, 0x03  SW Enable, 0x00 channel output disable.
    Returns: 
        0: Success; negative number: failed.
    """
    return cmdSetChannelEnable(hdl, enable) 

def klcGetKcubeMMIParams(hdl, dispBrightness, dispTimeout):
    """ Get device configure the operating parameters.
    Args:
        hdl: the handle of opened device
        dispBrightness: display brightness
        dispTimeout: display timeout
    Returns: 
        0: Success; negative number: failed.
    """
    db = c_ushort(0)
    dt = c_ushort(0)
    ret = cmdGetKcubeMMIParams(hdl, db, dt)
    dispBrightness[0] = db.value
    dispTimeout[0] = dt.value
    return ret 

def klcSetKcubeMMIParams(hdl, dispBrightness, dispTimeout):
    """ Set device configure the operating parameters.
    Args:
        hdl: the handle of opened device
        dispBrightness: display brightness 0~100
        dispTimeout: display timeout 1~480; set nerver should set to 0xFFFF
    Returns: 
        0: Success; negative number: failed.
    """
    return cmdSetKcubeMMIParams(hdl, dispBrightness, dispTimeout)

def klcGetKcubeMMILock(hdl, lock):
    """ Get the device lock/unlock the wheel control on the top pannel.
    Args:
        hdl: the handle of opened device
        lock: x02 unlock the wheel; 0x01 Lock the wheel
    Returns: 
        0: Success; negative number: failed.
    """
    l = c_ubyte(0)
    ret = cmdGetKcubeMMILock(hdl, l)
    lock[0] = l.value
    return ret 

def klcSetKcubeMMILock(hdl, lock):
    """ Set the device lock/unlock the wheel control on the top pannel .
    Args:
        hdl: the handle of opened device
        lock: x02 unlock the wheel; 0x01 Lock the wheel
    Returns: 
        0: Success; negative number: failed.
    """
    return cmdSetKcubeMMILock(hdl, lock)

def klcGetOutPutStatus(hdl, isOutputActive, outputVoltage, outputFrequency, errFlag):
    """ Get the device output status.
    Args:
        hdl: the handle of opened device
        isOutputActive: 0x00 Inactive; 0x01 Active
        outputVoltage: output voltage
        outputFrequency: output frequency
    Returns: 
        0: Success; negative number: failed.
    """
    active = c_ushort(0)
    vol = c_float(0)
    freq = c_ushort(0)
    err = c_ushort(0)
    ret = cmdGetOutPutStatus(hdl, active, vol, freq, err)
    isOutputActive[0] = active.value
    outputVoltage[0] = vol.value
    outputFrequency[0] = freq.value
    errFlag[0] = err.value
    return ret 

def klcGetStatus(hdl, channelenable, v1, freq1, v2, freq2, swFreq, dispBrightness, dipTimeout, adcMod, trigConfig, wheelMod, errFlag):
    """ Get the device status update value.
    Args:
        hdl: the handle of opened device
        channelenable: channel enable state
        v1: output voltage 1
        freq1: output frequency 1
        v2: output voltage 2
        freq2: output frequency 2
        swFreq: switch frequency
        dispBrightness: display pannel brightness
        dipTimeout: display pannel timeout
        adcMod: ADC mod in
        trigConfig: trigger config
        wheelMod: wheel locked mode
        errFlag: error flag
    Returns: 
        0: Success; negative number: failed.
    """
    enable = c_ubyte(0)
    vol1 = c_float(0)
    f1 = c_ushort(0)
    vol2 = c_float(0)
    f2 = c_ushort(0)
    sw = c_float(0)
    db = c_ushort(0)
    dt = c_ushort(0)
    am = c_ubyte(0)
    t = c_ubyte(0)
    w = c_ubyte(0)
    err = c_ushort(0)
    ret = cmdGetStatus(hdl, enable, vol1, f1,vol2,f2,sw,db,dt,am,t,w, err)
    channelenable[0] = enable.value
    v1[0] = vol1.value
    freq1[0] = f1.value
    v2[0] = vol2.value
    freq2[0] = f2.value
    swFreq[0] = sw.value
    dispBrightness[0] = db.value
    dipTimeout[0] = dt.value
    adcMod[0] = am.value
    trigConfig[0] = t.value
    wheelMod[0] = w.value
    errFlag[0] = err.value
    return ret

def klcRestoreFactorySettings(hdl):
    """ Reset default factory seetings.
    Args:
        hdl: the handle of opened device
    Returns: 
        0: Success; negative number: failed.
    """
    return klcLib.RestoreFactorySettings(hdl)

def klcUpdateOutputLUT(hdl, index, voltage):
    """ Update LUT value.
    Args:
        hdl: the handle of opened device
        index: index of the LUT array
        voltage: output voltage 0~25
    Returns: 
        0: Success; negative number: failed.
    """
    return cmdUpdateOutputLUT(hdl, index, voltage)

def klcRemoveLastOutputLUT(hdl, count):
    """ Remove the last of LUT array.
    Args:
        hdl: the handle of opened device
        count: the count values will be removed from LUT array
    Returns: 
        0: Success; negative number: failed.
    """
    return cmdRemoveLastOutputLUT(hdl, count)

def klcSetOutputLUT(hdl, vols, size):
    """ Set the LUT array data.
    Args:
        hdl: the handle of opened device
        vols: the LUT values array
        size: the count of the array 0~512
    Returns: 
        0: Success; negative number: failed.
    """
    return cmdSetOutputLUT(hdl, vols, size)

def klcStartLUTOutput(hdl):
    """ Start LUT output.
    Args:
        hdl: the handle of opened device
    Returns: 
        0: Success; negative number: failed.
    """
    return klcLib.StartLUTOutput(hdl)

def klcStopLUTOutput(hdl):
    """ Stop LUT output.
    Args:
        hdl: the handle of opened device
    Returns: 
        0: Success; negative number: failed.
    """
    return klcLib.StopLUTOutput(hdl)

def klcSetOutputLUTParams(hdl, mode, numCycles, delayTime,preCycleRest):
    """ Set LUT parameters.
    Args:
        hdl: the handle of opened device
        mode: 1 continuous; 2 cycle
        numCycles: number of cycles 1~ 2147483648
        delayTime: the sample intervals[ms] 1~ 2147483648
        preCycleRest: the delay time before the cycle start[ms] 0~ 2147483648
    Returns: 
        0: Success; negative number: failed.
    """
    return cmdSetOutputLUTParams(hdl, mode, numCycles, delayTime,preCycleRest)

def klcGetOutputLUTParams(hdl, mode, numCycles, delayTime,preCycleRest):
    """ Get LUT parameters.
    Args:
        hdl: the handle of opened device
        mode: 1 continuous; 2 cycle
        numCycles: number of cycles 1~ 2147483648
        delayTime: the sample intervals[ms] 1~ 2147483648
        preCycleRest: the delay time before the cycle start[ms] 0~ 2147483648
    Returns: 
        0: Success; negative number: failed.
    """
    m = c_ushort(0)
    n = c_ulong(0)
    d = c_ulong(0)
    p = c_ulong(0)
    ret = cmdGetOutputLUTParams(hdl, m, n, d,p)
    mode[0] = m.value
    numCycles[0] = n.value
    delayTime[0] = d.value
    preCycleRest[0] = p.value
    return ret 