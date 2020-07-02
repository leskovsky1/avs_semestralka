from getmac import get_mac_address
#jeden zaznam o rozhrani
class interface:
    def __init__(self,name, mac):
        self.name = name
        self.mac = mac
        self.trunk=False
        self.wlan= 0
        
    # vrati retazec s informaciami o rozhrani
    def toString(self):
        return (str(self.name)+"\t"+self.mac+"\t"+str(self.trunk)+"\t"+str(self.wlan))

class interfaces:
    #konstruktor
    def __init__(self, interface_names):
        self.interfaces=[]
        self.getMacOfAllInterfaces(interface_names)

    #funkcia sluzi na zistenie MAC adries jednotlivych rozhrani
    def getMacOfAllInterfaces(self,interface_names):
        for x in interface_names:
            self.interfaces.append(interface(x,get_mac_address(x)))

    #funkcia sluzi na ziskanie MAC adresy zadaneho rozhrania 
    def getMac(self,interface_name):
        for x in self.interfaces:
            if(interface_name == x.name):
                return x.mac

    #funkcia sluzi na zistenie ci MAC adresa zadana v parametri uz niekde existuje  
    def existsMac(self,mac):
        for x in self.interfaces:
            if(mac == x.mac):
                return True
        return False

    #funkcia zisti ci dane rozhranie je trunk 
    def isTrunk(self, interface_name):
        for x in self.interfaces:
            if(interface_name == x.name):
                return x.trunk
        return None

    #vypis informacii o vsetkych rozhraniach
    def print(self):
        for x in self.interfaces:
            print(x.toString())

    #nastavenie rozhrania ako trunk
    def setTrunk(self,interface,value):
        for x in self.interfaces:
            if(interface == x.name):
                x.trunk = value
                print("TRUNK on "+interface+" set to "+str(value))

    #nastavenie vlan cisla pre interface 
    def setWlan (self,interface,wlan):
        for x in self.interfaces:
            if(interface == x.name):
                x.wlan = int(wlan)
                print("INTERFACES - Wlan on "+interface+" set to "+str(wlan))
                return
    #zisti ci dane rozhraniae je trunk 
    def getWlan(self,interface):
        for x in self.interfaces:
            if(interface == x.name):
                return x.wlan
