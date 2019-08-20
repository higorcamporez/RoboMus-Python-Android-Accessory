#!/usr/bin/env python
# coding=utf-8
#
# Copyright 2016 Arn-O. See the LICENSE file at the top-level directory of this
# distribution and at
# https://github.com/Arn-O/py-android-accessory/blob/master/LICENSE.

"""
Simple Android Accessory client in Python.
"""

import usb.core
import sys
import time
import random
import array

VID_ANDROID_ACCESSORY = 0x22B8   
PID_ANDROID_ACCESSORY = 0x2E82


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
    send_string(ldev, 0, 'aang')
    send_string(ldev, 1, 'AndroidAccessory')
    send_string(ldev, 2, 'A Python based Android accessory')
    send_string(ldev, 3, '1.0')
    send_string(
        ldev,
        4,
        'https://github.com/Arn-O/py-android-accessory/'
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


def communication_loop(ldev):
    """Accessory client to device communication loop"""
    #sensor = 50
    while True:
        
        # random sensor variation
        #toss = random.randint(-10, 10)
        #sensor = sensor_output(sensor, sensor_variation(toss))
        '''
        # write to device
        msg = "S{:04}".format(sensor)
        print ("<<< {}".format(msg))
        try:
            #ret = ldev.write(0x02, msg, 150)
            assert ret == len(msg)
        except usb.core.USBError as e:
            if e.errno == 19:
                break
            if e.errno == 110:
                # the application has been stopped
                break
            print(e)
        '''
        # read from device
        for d in ldev: 
            try:
                ret = d.read(0x81,1, 150)
                sret = ''.join([chr(x) for x in ret])
                print(">>> {}".format(sret))
                '''
                ret = ldev[1].read(0x81,1, 150)
                sret = ''.join([chr(x) for x in ret])
                print("1>>> {}".format(sret))
                '''
            except usb.core.USBError as e:
                
                if e.errno == 19:
                    print("deu ruim,brother")
                    print(e)
                    break
                if e.errno == 110:
                    # a timeout is OK, no message has been sent
                    pass
                else:
                    print(e)
        time.sleep(0.2)
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

    print devices[0].bus, devices[0].address
    print devices[1].bus, devices[1].address
    
    adev = get_accessory_dev(devices)
    adev = tuple(usb.core.find(
        find_all=True,
        idVendor=0x18d1, 
        idProduct=0x2d00
    ))
    
    if not adev:
        print("deu ruim")
        
    for d in adev:
        print("d.address=")
        print(d.address)
   
    communication_loop(adev)
        
    '''
    while True:
        ddev = get_android_dev()
        if not ddev:
            continue
        adev = get_accessory_dev(ddev)
        time.sleep(1);
        if not adev:
            continue
        print("Will now communicate with device")
        communication_loop(adev)
        break
    '''

if __name__ == '__main__':
    main()
