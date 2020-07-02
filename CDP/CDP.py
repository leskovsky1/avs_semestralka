import logging
import threading
import time
from scapy.all import *

from scapy.all import * 
from scapy.contrib import cdp
from getmac import get_mac_address

import string
import random
import sys
import netifaces
import datetime 


class cdp_interface:
    def __init__(self,iface,cdp_frame):
        self.interface=iface    #interface kde bol ramec odchyteny
        self.frame=cdp_frame    #posledny odchyteny CDP ramec
        self.version=0
        self.time=None          #cas kedy bol ramec odchyteny


    def frame_toString(self):
        if(self.frame == None):
            return(self.interface,"No informations")
        else:
            # print(frame[0].show())
            id      =self.frame["CDPMsgDeviceID"].val.decode()
            port    =self.frame["CDPMsgPortID"].iface.decode()
            #version=self.frame[0]["CDPMsgSoftwareVersion"].val.decode()
            #platform=self.frame[0]["CDPMsgPlatform"].val.decode()
            mac_src =self.frame.src
            mac_dst =self.frame.dst
            time=str(( self.time - datetime.datetime.now()).seconds)
            platform = "platform"

            return (id+"\t"+self.interface+"\t"+time+"\t"+platform+"\t"+port)



class CDP:
    send_interval=10
    cdp_frames=[]

    #konstruktor
    def __init__(self,device_id):
        sender = threading.Thread(target=self.cdpSender, args=(1,)) #spustenie vlakna na odosielanie CDP ramcov
        sender.start()
        self.device_id = device_id

        killer=threading.Thread(target=self.old_time_killer, args=(1,)) #spustenie vlakna na mazanie starych zaznamov
        killer.start()

    #funkcia na odstranovanie starych informacii z CDP tabulky
    def old_time_killer(self,name):
        print ("old time killer zapnuty")
        while(1):
            for x in self.cdp_frames:
                if(x.time != None):
                    if(x.time < datetime.datetime.now()):                 
                        x.time = None
                        x.frame=None

    #funkcia sluzi na pridavanie noveho CDP zaznamu do tabulky
    def add_new_cdp_frame(self,frame):
        interface = frame.sniffed_on
        for x in self.cdp_frames:
            if(x.interface==interface):
                x.frame=frame
                x.version+=1
                time = frame.ttl
                x.time=datetime.datetime.now()+datetime.timedelta(seconds=time)     
#                print("Prijal som CDP na interfaci",interface)
     

    #funkcia sluzi na generovanie CDP ramcov
    def cdppacketgen(self,interface):
        etherframe      = Ether()     #Start definition of Ethernet Frame
                          
        etherframe.dst  = '01:00:0c:cc:cc:cc'           #Set Ethernet Frame destination MAC to Ciscos Broadcast MAC
        etherframe.src  = get_mac_address(interface=interface)               #Set Random source MAC address
        etherframe.type = 0x010c                 #CDP uses Type field for length information

        llcFrame      = LLC()                           #Start definition of Link Layer Control Frame
        llcFrame.dsap = 170                             #DSAP: SNAP (0xaa) IG Bit: Individual
        llcFrame.ssap = 170                             #SSAP: SNAP (0xaa) CR Bit: Command
        llcFrame.ctrl = 3                               #Control field Frame Type: Unumbered frame (0x03)

        snapFrame      = SNAP()                         #Start definition of SNAP Frame (belongs to LLC Frame)
        snapFrame.OUI  = 12                             #Organization Code: Cisco hex(0x00000c) = int(12)
        snapFrame.code = 8192                           #PID (EtherType): CDP hex(0x2000) = int(8192)


        cdpHeader      =  cdp.CDPv2_HDR()                    #Start definition of CDPv2 Header
        cdpHeader.vers = 2                             #CDP Version: 1 - its always 1
        cdpHeader.ttl  = 180                            #TTL: 180 second


        cdpDeviceID      = cdp.CDPMsgDeviceID()             #Start definition of CDP Message Device ID
        cdpDeviceID.type = 1                            #Type: Device ID hex(0x0001) = int(1)
        cdpDeviceID.len  = 6                            #Length: 6 (Type(2) -> 0x00 0x01) + (Length(2) -> 0x00 0x0c) + (DeviceID(2))                            
        cdpDeviceID.val  = self.device_id.encode()             #Generate random Device ID (2 chars uppercase + int = lowercase)
    

        cdpAddrv4         = cdp.CDPAddrRecordIPv4()         #Start Address Record information for IPv4 belongs to CDP Message Address
        cdpAddrv4.ptype   = 1                           #Address protocol type: NLPID
        cdpAddrv4.plen    = 1                           #Protocol Length: 1
        cdpAddrv4.proto   = '\xcc'     
        cdpAddrv4.addrlen = 4                           #Address length: 4 (e.g. int(192.168.1.1) = hex(0xc0 0xa8 0x01 0x01)
        #cdpAddrv4.addr    = str(RandIP())               #Generate random source IP address
        cdpAddrv4.addr    = '122.2.7.82'              #Generate random source IP address

        cdpAddr       = cdp.CDPMsgAddr()                    #Start definition of CDP Message Address
        cdpAddr.type  = 2                               #Type: Address (0x0002)                  
        cdpAddr.len   = None                              #Length: hex(0x0011) = int(17)
        cdpAddr.naddr = None                             #Number of addresses: hex(0x00000001) = int(1)
        cdpAddr.addr  = []
        #cdpAddr.addr  = [cdpAddrv4]                     #Pass CDP Address IPv4 information



        cdpPortID       = cdp.CDPMsgPortID()                #Start definition of CDP Message Port ID
        cdpPortID.type  = 3                             #type: Port ID (0x0003)
        cdpPortID.len   = None                           #Length: 13
        cdpPortID.iface = interface.encode()                 #Interface string (can be changed to what you like - dont forget the length field)
        etherframe.type += len(cdpPortID.iface)



        cdpCapabilities        = cdp.CDPMsgCapabilities()   #Start definition of CDP Message Capabilities
        cdpCapabilities.type   = 16                     #Type: Capabilities (0x0004)
        cdpCapabilities.length = 8                      #Length: 8
        cdpCapabilities.cap    = 1                      #Capability: Router (0x01), TB Bridge (0x02), SR Bridge (0x04), Switch that provides both Layer 2 and/or Layer 3 switching (0x08), Host (0x10), IGMP conditional filtering (0x20) and Repeater (0x40)



        cdpSoftVer      = cdp.CDPMsgSoftwareVersion()       #Start definition of CDP Message Software Version
        cdpSoftVer.type = 5                             #Type: Software Version (0x0005)
        cdpSoftVer.len  = 216                           #Length: 216
        cdpSoftVer.val  = 'Cisco Internetwork Operating System Software \nIOS (tm) 1600 Software (C1600-NY-L), Version 11.2(12)P, RELEASE SOFTWARE (fc1)\nCopyright (c) 1986-1998 by cisco Systems, Inc.\nCompiled Tue 03-Mar-98 06:33 by dschwart'
       

       
        cdpPlatform      = cdp.CDPMsgPlatform()             #Statr definition of CDP Message Platform
        cdpPlatform.type = 6                            #Type: Platform (0x0006)
        cdpPlatform.len  = 14                           #Length: 14
        cdpPlatform.val  = 'cisco 1601'                 #Platform = cisco 1601 (can be changed, dont forget the Length)
      
        cdppacket = etherframe   
        cdppacket /=llcFrame
        cdppacket /=snapFrame 
        cdppacket /=cdpHeader
        cdppacket /=cdpDeviceID
        cdppacket /=cdpAddr
        cdppacket /=cdpPortID
        cdppacket /=cdpCapabilities

        cdppacket /=cdpSoftVer
        cdppacket /=cdpPlatform

        print("Posielam CDP packet",interface)
        sendp(cdppacket,iface = interface,verbose=0) 

    #funkcia sluzi na odosielanie CDP ramcov 
    def cdpSender(self,name):
        print("CDP sender started")
        while(1==1):
            time.sleep(self.send_interval)
            for x in self.cdp_frames:
                self.cdppacketgen(x.interface)

    #funkcia zisti ci rozhranie zadane v parametre je typu TRUNK
    def is_cdp_interface(self,interface):
        for x in self.cdp_frames:
            if(x.interface == interface):
                return True
        return False

    #funkcia sluzi na aktivovanie CDP na danom rozhrani
    def add_cdp_interface(self,interface):
        if(self.is_cdp_interface(interface) == False):
            self.cdp_frames.append(cdp_interface(interface,None))
            print("SUCCESS_CDP on",interface,"is activated")  
        else:
            print ("FAIL_",interface,"is already CDP active")

    #funkcia sluzi na dektivovanie CDP na dom rozhrani
    def rem_cdp_interface(self,interface):
        for x in self.cdp_frames:
            if(x.interface == interface):
                self.cdp_frames.remove(x)
                print("CDP on interface",x.interface,"deactivated")

    #vypis CDP tabulky 
    def printCDP(self):
        if(len(self.cdp_frames)==0):
            print("No cdp neighbours")
        else:
            for x in self.cdp_frames:
                print(x.frame_toString())
        
