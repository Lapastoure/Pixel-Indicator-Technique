# -*- coding:utf-8 -*-

""" 
Ce Script permet de lire les messages cachés avec la technique 
"Pixel Indicator Technique"
"""

from PIL import Image
import binascii
import sys

VERBOSE = True

def is_prime(n):
    """ Advanced Prime Number Fn """
    if n == 2 or n == 3: return True
    if n < 2 or n%2 == 0: return False
    if n < 9: return True
    if n%3 == 0: return False
    r = int(n**0.5)
    f = 5
    while f <= r:
        if n%f == 0: return False
        if n%(f+2) == 0: return False
        f +=6
    return True

def get2lsb(n):
    """ Return 2 last LSB as String """
    n = n%4
    if(n == 0):
        return "00"
    if(n == 1):
        return "01"
    if(n == 2):
        return "10"
    if(n == 3):
        return "11"

def int2bytes(i):
    """ Convert int to bytes """
    hex_string = '%x' % i
    n = len(hex_string)
    return binascii.unhexlify(hex_string.zfill(n + (n & 1)))

def text_from_bits(bits, encoding='utf-8', errors='replace'):
    """  bytes to string """
    n = int(bits, 2)
    return int2bytes(n).decode(encoding, errors)

###############################################################################

img = Image.open(sys.argv[1])

pxs = img.load() # 2D Array pxs[x,y] ; pxs[0,0] = top left
w,h = img.size

if(VERBOSE):
    print("Load Image with size: "+str(w)+"*"+str(h))


""" On récupère la taille du message """

toct = []

# On recupère les 8 premiers octets dans toct

for i in range(3): # 3 premiers pxl (3px*3couleurs = 9 octet)
    toct.append(format(pxs[i,0][0],'b')) # format = on recup en binaire
    toct.append(format(pxs[i,0][1],'b'))
    if(i < 2): # On ne met pas le 9 octet
        toct.append(format(pxs[i,0][2],'b'))

for i in range(len(toct)): # On rajoute les "0" prefix manquant
    toct[i] = '0'*(8-len(toct[i]))+toct[i]

N = int(''.join(toct),2) # taille du message caché, 8 octet en binaire


if(VERBOSE):
    print("Taille du message : "+str(N))

"""
Si N pair : indicateur = R
Si N premier : indicateur = B
Sinon : indicateur = V
"""

# IC = Indicator Channel, R = 0 , V = 1 , B = 2


if(N%2 == 0): # Pair --> IC = R
    IC = 0
    if(VERBOSE):
        print("'N' est pair ==> IC = R (0)")
elif(is_prime(N)): # Premier -->  IC = B
    IC = 2
    if(VERBOSE):
        print("'N' est premier ==> IC = B (2)")
else: # Sinon IC = V
    IC = 1 
    if(VERBOSE):
        print("'N' est ni pair ni premier ==> IC = V (1)")

"""
On calcul la "parité binaire":
nombre de bit à 1 pair ==> 0
nombre de bit à 1 impaire ==> 1
"""

parite = format(N,'b').count("1")%2 # Nb de bit % 2

if(VERBOSE):
    print("Parité binaire : "+("paire" if parite == 0 else "impaire"))

c = ["R","G","B"]

if(parite == 1): # Impair (Odd)
    if(IC == 0): # R
        c1 = 1
        c2 = 2
    elif(IC == 2): # B
        c1 = 0
        c2 = 1
    else: # G
        c1 = 0
        c2 = 2
else: # Pair (Even)
    if(IC == 0): # R
        c1 = 2 # B
        c2 = 1 # G
    elif(IC == 2): # B
        c1 = 1
        c2 = 0
    else: # G
        c1 = 2
        c2 = 0


if(VERBOSE):
    print("\n-----------------\n")
    print("Indicator Chanel: "+c[IC])
    print("Data Chanel 1: "+c[c1])
    print("Data Chanel 2: "+c[c2])


""" On commence le parsing """

RMS = N # Taille du message restant

pxsl = list(img.getdata())[w:] # Tableau lineaire des pixels d'info 
# On commence à la 2eme ligne (d'où le w)

binSecret = "" #

i = 0 # pixel courrant
while(RMS > 0): # Tant qu'il nous reste des choses à lire
    indicLSB = pxsl[i][IC]%4 # On récupère les info de l'IC
    if(indicLSB == 1): # 01
        binSecret += get2lsb(pxsl[i][c2])
        RMS -= 2
    elif(indicLSB == 2): # 10
        binSecret += get2lsb(pxsl[i][c1])
        RMS -= 2
    elif(indicLSB == 3): # 11
        binSecret += get2lsb(pxsl[i][c1])
        binSecret += get2lsb(pxsl[i][c2])
        RMS -= 4
    i += 1

if(VERBOSE):
    print("Recover Data length: "+str(len(binSecret)))

print(text_from_bits(binSecret))
