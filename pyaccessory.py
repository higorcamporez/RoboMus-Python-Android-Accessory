#!/usr/bin/env python
# coding=utf-8
#
# Copyright 2016 Arn-O. See the LICENSE file at the top-level directory of this
# distribution and at
# https://github.com/Arn-O/py-android-accessory/blob/master/LICENSE.

#adaptação do código original descrito acima

"""
Simple Android Accessory client in Python.
"""

import usb.core
import usb.util
import sys
import time
import random
import array
import csv
from thread import start_new_thread


VID_ANDROID_ACCESSORY = 0x22B8   
PID_ANDROID_ACCESSORY = 0x2E82

#VID_ANDROID_ACCESSORY = 0x18d1   
#PID_ANDROID_ACCESSORY = 0x4ee7


def get_accessory_dev(ldev):
    """Trigger accessory mode and send the dev handler"""
    for d in ldev:
        set_protocol(d)
        set_strings(d)
        set_accessory_mode(d)
 
    devs = usb.core.find(
        find_all=True,
        idVendor=0x18d1, 
        idProduct=0x2d00
    )
    for d in devs:
        print("d.address=")
        print(d.address)
        
    if devs:
        print("Android accessory mode started")

    return devs


def get_android_dev():
    """Look for a potential Android device"""
    ldev = usb.core.find(bDeviceClass=0)

    if ldev:
        # give time for a mount by the OS
        time.sleep(2)
        # request again a device handler
        ldev = usb.core.find(bDeviceClass=0)
        print ("Device found")
        print ("VID: {:#04x} PID: {:#04x}".format(
            ldev.idVendor,
            ldev.idProduct
        ))
    return ldev


def set_protocol(ldev):
    """Set the USB configuration"""
    try:
        ldev.set_configuration()
    except usb.core.USBError as e:
        if  e.errno == 16:
            pass
        else:
            sys.exit(e)
    ret = ldev.ctrl_transfer(0xC0, 51, 0, 0, 2)
    protocol = ret[0]
    print ("Protocol version: {}".format(protocol))
    return


def set_strings(ldev):
    """Send series of strings to activate accessory mode"""
    send_string(ldev, 0, 'RoboMus')
    send_string(ldev, 1, 'blink')
    #send_string(ldev, 0, 'aang')
    #send_string(ldev, 1, 'AndroidAccessory')
    send_string(ldev, 2, 'A Python based Android accessory')
    send_string(ldev, 3, '1.0')
    send_string(
        ldev,
        4,
        'https://github.com/higorcamporez/RoboMus-Python-Android-Accessory'
    )
    return


def set_accessory_mode(ldev):
    """Trigger the accessory mode"""
    ret = ldev.ctrl_transfer(0x40, 53, 0, 0, '', 0)    
    assert not ret
    time.sleep(1)
    return


def send_string(ldev, str_id, str_val):
    """Send a given string to the Android device"""
    ret = ldev.ctrl_transfer(0x40, 52, 0, str_id, str_val, 0)
    assert ret == len(str_val)
    return 


def sensor_variation(toss):
    """Return sensor variation"""
    return {
        -10: -1,
        10: 1
    }.get(toss, 0)


def sensor_output(lsensor, variation):
    """Keep the sensor value between 0 and 100"""
    output = lsensor + variation
    if output < 0:
        output = 0
    else:
        if output > 100:
            output = 100
    return output


def communication_loop(ldev, times_read):
    """Accessory client to device communication loop"""
    #print("loopsss")
    t = time.time()
    while True:
        # read from device 
        try:
            ret = ldev.read(0x81,1, 1500)
            if len(ret) > 0:
                
                times_read.append([ret[0],time.time()])
                #print("ret ",ret[0]," t ",time.time())

        except usb.core.USBError as e:
            
            if e.errno == 19:
                print(e)
                break
            if e.errno == 110:
                # a timeout is OK, no message has been sent
                pass
            else:
                print(e)
        #time.sleep(0.2)
    return


def main():
    """Where everything starts"""
    print("Looking for an Android device")
    devices = tuple(
		usb.core.find(
				find_all=True, 
				idVendor = VID_ANDROID_ACCESSORY, 
				idProduct = PID_ANDROID_ACCESSORY
                                )
                    )

    if not devices:
        print(len(devices))
        print("1deu ruim, brother")
        devices = tuple(usb.core.find(
            find_all=True,
            idVendor=0x18d1, 
            idProduct=0x2d00
        ))
        #return
    
    #print devices[0].bus, devices[0].address
    #print devices[1].bus, devices[1].address
    
    adev = get_accessory_dev(devices)
    
    adev = tuple(usb.core.find(
        find_all=True,
        idVendor=0x18d1, 
        idProduct=0x2d00
    ))
    '''
    adev = tuple(usb.core.find(
        find_all=True,
        idVendor=0x18d1, 
        idProduct=0x2d00
    ))
    '''
    if not adev:
        print(len(adev))
        print("2deu ruim, brother")
        return
    
    times_read = list();    

    for d in adev:
        print("d.address=")
        print(d.address)
        times_read.append(list())

    for i in range(len(adev)):
        start_new_thread(communication_loop,(adev[i],times_read[i]))

    raw_input("Aperte Qualquer Tecla para Encerrar")

    for i in range(len(times_read)):
        c = csv.writer(open("times_read"+str(i)+".csv", "wb"))
        c.writerow([usb.util.get_string(adev[i], adev[i].iProduct)])
        for j in range(len(times_read[i])):
            c.writerow(times_read[i][j])
  

if __name__ == '__main__':
    main()
