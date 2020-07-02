from cam import CamTable
import threading
from scapy.all import *
from CDP import CDP
import string

from interfaces import interfaces
from copy import deepcopy
from random import choice
from string import ascii_uppercase
cam_table = None
interfaces_table = None

#pridavanie rozhrani ktore bude switch pouzivat
active_interfaces = []
active_interfaces.append('eth1')
active_interfaces.append('eth2')
active_interfaces.append('eth3')

#premene ktore budu naplnene v hlavnej funkcii
cdp = None          #premenna typu CDP 
buffer=[]           #buffer prijatych sprav
device_id = None    #premena bude obsahovat dva chary charakterizujuce zariadenie

#funkcia je urcena na odchytavanie paketov na rozhrani 
#funkcia je spustena v samostatnom vlakne pre kazde rozhranie 
#odchytene ramce ulozi do bufferu pre neskorsie spracovanie 
def receiver(name,interface):
    print("Receiver on",interface,"started")
    count = 2                                           
    while(True):
        frame = sniff(iface = interface,count=count)
        for x in range(count):  
            buffer.append(frame[x])


#funkcia vlozi do packetu(ramca) VLAN tag z cislom vlany zadanym v parametre
def wlan_inserter(packet,wlan):
    #print("\t\t\tVkladam do packetu wlan",wlan)
    layer = packet.firstlayer()
    while not isinstance(layer, NoPayload):
        if 'chksum' in layer.default_fields:
            del layer.chksum
        if (type(layer) is Ether):
            layer.type = 33024
            dot1q = Dot1Q(vlan=wlan)
            dot1q.add_payload(layer.payload)
            layer.remove_payload()
            layer.add_payload(dot1q)
            layer = dot1q
        layer = layer.payload

#funkcia "odstrani" vlan tag z ramca
def wlan_remover(packet):
    print("\t\t\tOdstranujem vlan ")
    packet[Dot1Q].vlan = 0

#funkcia zisti ci je packet odchadzajuci alebo prichadzajuci
# true - prichadzajuci
# false - odchadzajuci
# tato funkcia bola vytvorena pretoze scapy odchhytava na rozhrani aj ramce ktore sam odosle, takze ich bolo treba odfiltrovat 
def is_packet_ok(packet):
    return (packet.sniffed_on == cam_table.FindEntry(packet.src))

#funkcia odosle ramec vsetkymi rozhraniami
def flood(packet):
    #print("\tFloodujem")
    for x in interfaces_table.interfaces:
        if(packet.sniffed_on != x.name):
            pom = packet.copy()
            pom.sniffed_on= packet.sniffed_on
            send(pom,x.name)

#funkcia sa nauci novy interface a CAM informacie o zariadeni z ramca ktory na danom interfaci ziskal
def learn_cam(packet):
    if(interfaces_table.existsMac(packet.src)==False): #kvoli pridavaniu vlastnych interfacov do tabulky
        wlan = interfaces_table.getWlan(packet.sniffed_on)
        cam_table.CreateEntry(packet.src,packet.sniffed_on,wlan)

#funkcia sluzi na odoslanie ramca danym rozhranim
def send(frame,interface):
    
    is_from_trunk = interfaces_table.isTrunk(frame.sniffed_on) 
    is_to_trunk = interfaces_table.isTrunk(interface)

    dst_wlan = interfaces_table.getWlan(interface)
  
    #pridavanie vlanoveho tagu
    if (frame.haslayer(Dot1Q)==False):
        src_wlan =interfaces_table.getWlan(frame.sniffed_on)
        wlan_inserter(frame,src_wlan)

    src_wlan = frame[Dot1Q].vlan
  
    # v pripade ze nejde do trunkoveho rozhrania (ide k pouzivatelovi) sa vlanovy tag "odstrani"
    if(is_to_trunk == False):
        wlan_remover(frame)
    
    #ak je zdrojove cislo vlany zhodne z cielovym alebo je ramec smerovany do trunku tak sa posle
    if(src_wlan == dst_wlan or is_to_trunk ==True):
        sendp(frame,iface=interface,verbose=0)
    
#funkcia ziskava z buffera zozbierane ramce zo vsetkych informacii a naslende ich spracovava
def sender(name):
    print("Sender thread started")
    while(True):
        if(len(buffer)>0):
            frame=buffer.pop(0)                                                 #ziskanie najstarsieho ramca z buffera
            learn_cam(frame)                                                    #zapisanie informacii do CAM tabulky
            if(frame.dst == '01:00:0c:cc:cc:cc'):                               #CDP filter
                if(frame.src != interfaces_table.getMac(frame.sniffed_on)):     #kontrola ci nejde o odchadzajuci CDP ramec  
                    print("Prijal som CDP")
                    cdp.add_new_cdp_frame(frame)       
            elif(is_packet_ok(frame)):
                #print("Spracovavam packet z "+frame.sniffed_on)
                dst_interface = cam_table.FindEntry(frame.dst)                  #kontrola ci pozname dane cielove rozhranie
                if(dst_interface!= None):
                    send(frame,dst_interface)                                   #v pripade ze pozname tak sa posle
                else:
                    flood(frame)                                                #v pripade ze cielove rozhranie nepozame tak floodujeme vsetkymi rozhraniami (okrem zdrojoveho rozhrania)


# funkcia sluzi na ziskavanie klavesovych vstupov od pouzivatela 
# funkcia bezi v samostatnom vlakne 
def keyboard(name):
    print("Keyboard thread started")
    while(1):
        a=input()
        splited = a.split(" ")
        if(a == "show cdp"):                                # vypis CDP informacii
            cdp.printCDP()
        if(a == "show int"):                                # vypis informacii o rozhraniach 
            interfaces_table.print()
        if(splited[0] == "cdp"):
            if(splited[1]== "enable"):                      # aktivovanie CDP na rozhrani -- cdp enable eth1
                cdp.add_cdp_interface(splited[2])
            if(splited[1]== "disable"):
                cdp.rem_cdp_interface(splited[2])           # deaktivovanie CDP na rozhrani -- cdp disable eth1
        if(a == "show cam"):
            cam_table.PrintTable()                          # vypis cam tabulky
        if(splited[0]=="vlan"):
            cam_table.setWlan(splited[1],splited[2])        #nastavenie vlany na rozhranie 
            interfaces_table.setWlan(splited[1],splited[2])
        if(splited[0]=="trunk"):
            if(splited[1] == "enable"):                 
                interfaces_table.setTrunk(splited[2],True)  #nastavenie trunku na rozhranie -- trunk enable eth1
            if(splited[1] == "disable"):
                interfaces_table.setTrunk(splited[2],False) #nastavenie trunku na rozhranie -- trunk disable eth1
        if(a == "show id"):
            print("Device ID "+device_id)                   #vypis id zariadenia 

#funkcia vygeneruje ID pre zariadenie 
def generateID(length):
    return (''.join(choice(ascii_uppercase) for i in range(length)))

if __name__ == "__main__":

    interfaces_table= interfaces(active_interfaces)                 #inicializacii rozhrani
    cam_table = CamTable()                                          #inicializacia CAM tabulky


    listen_threads=[]
    device_id = generateID(2)                                       #generovanie ID pre zariadenie
    cdp = CDP(device_id)                                            #inicializacia CDP 

    #vytvorenie vlakien na prijimanie ramcov na vsetkych rozhraniach
    for i in interfaces_table.interfaces:
        tem=threading.Thread(target=receiver, args=(1,i.name))
        listen_threads.append(tem)
        tem.start()

    #vytvorenie vlakna pre vstupy z klavesnice
    keyboard_thead = threading.Thread(target=keyboard, args=(1,))
    keyboard_thead.start()

    #vytvorenie vlakna pre odosielanie ramcov
    sender = threading.Thread(target=sender, args=(1,))
    sender.start()
