#### Zadanie: 
 Program implementovaný tímom študentov (4 študenti v tíme). Komentáre zdrojového kódu a dokumentácia sú povinné. Implementácia môže byť vytvorená v jazyku C (preferovane), po konzultácii aj v jazykoch Python, C++ a iné.
- Téma:
    Prepínač s podporou VLAN a CDP/LLDP protokolu.
    
- CDP parser: https://github.com/GoreNetwork/CDP-parser/blob/master/cdp_parse.py

- CDP link1: https://github.com/CiscoSE/cdp_discover/blob/master/cdp.py?fbclid=IwAR2e8Xwr96jraHP04wbcM5jmYxIGyxtxqeFSkw_r8U1n6ADiqZ2Ti42Wtu0

- CDP link2: https://pypi.org/project/cdp-py/
  Docs: https://cuwb.io/docs/v3.3/application-notes/using-cdp-python/#using-cdp-python

# Používateľská príručka

# Téma 
* Vytvorenie virtuálneho switcha s podporou VLAN a CDP

# Programovací jazyk
* python 3.7.3 64-bit

# Knižnice
* getmac 0.8.2
* pcapy 0.11.4
* scapy 2.4.3

# Príkazy
## Show 
### show cdp
* vypíše informácie získané pomocou protokolu CDP
### show int
* vypíše informácie o rozhraniach prepínača
### show id
* vypíše ID prepínača posielané v CDP rámcoch 
### show cam
* vypíše CAM tabuľku smerovača

## VLAN
Defaultne všetky rozhrania majú vlan číslo 0
### vlan `<interface> <vlan>`
*  nastavenie čísla vlan na rozhranie 
  * `<interface>` - názov rozhrania
  * `<vlan>` - číslo vlany
* VZOR `vlan eth1 1`

## TRUNK
Nastavenie trunku
### trunk `<state> <interface>`
* nastaví trunk rozhrania na zadaný stav
  * `<state>` - enable/disable
  * `<interface>` - názov rozhrania
* VZOR `trunk enable eth1`
* VZOR `trunk disable eth1`


## CDP
Nastavenie CDP
### cdp `<state> <interface>`
* nastaví rozhranie na zadaný stav
  * `<state>` - enable/disable
  * `<interface>` - názov rozhranie

* VZOR `cdp enable eth1`
* VZOR `cdp disable eth1`

# Spustenie programu 
* Hlavným súborom je súbor `bridge.py`   
* V terminály spustite program pomocou príkazu `"python3 bridge.py"`   
* Pred sputením je potrebné aby sieťové rozhrania našeho virtuálneho prepínača boli v stave UP a bez statickej IP adresy
* Takisto pred spustením je potreba v súbore bridge.py do poľa `active_interfaces` pridať názvy rozhraní ktoré bude prepínač používať 