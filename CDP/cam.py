#jeden zaznam tabulky 
class CamEntry:
    #konstruktor
    def __init__(self, paMacAddress, paInterface,wlan):
        self.aMacAddress = paMacAddress
        self.aInterface = paInterface
        self.wlan = wlan


#trieda sluzi na ziskavanie a spracovavanie informacii urecnych pre CAM tabulku
class CamTable:
    def __init__(self):
        self.aEntries = []

    #vytvorenie noveho zaznamu do tabulky
    def CreateEntry(self, paMacAddress, paInterface,wlan):
        if(self.FindEntry(paMacAddress) == None):
            self.aEntries.append(CamEntry(paMacAddress, paInterface,wlan))
            print("Ucim sa macu", str(paMacAddress),"na interfaci",paInterface,"s vlane",wlan)
        
    #najdenie zaznamu podla MAC
    def FindEntry(self, paMacAddress):
        for i in self.aEntries:
            if (paMacAddress == i.aMacAddress):
                return i.aInterface
        return None

    # ziskanie MAC adresi podla nazvu rozhrania
    def FindMacByInterface(self, interface):
        for i in self.aEntries:
            if (interface == i.aInterface):
                return i.aMacAddress
        return None

    #vypis informacii z CAM tabulky   
    def PrintTable(self):
        for i in self.aEntries:
            print(i.aMacAddress + "\t"+ i.aInterface+"\t"+str(i.wlan))
    
    #nastavenie vlan na dane rozhranie 
    def setWlan(self,interface, wlan):
        for x in self.aEntries:
            if (x.aInterface == interface):
                x.wlan = int(wlan)
        print("CAM - Wlan on "+interface+" set to "+str(wlan))

    # ziskanie vlan cisla z daneho rozhrania 
    def getWlan(self, interface):
        for x in self.aEntries:
            if (x.aInterface == interface):
                return x.wlan
