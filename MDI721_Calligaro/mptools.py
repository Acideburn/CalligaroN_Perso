# -*- coding: utf-8 -*-
"""
Created on Sat Nov 21 22:27:11 2020

@author: Calligaro Nicolas MS BDG
"""

import requests
from bs4 import BeautifulSoup
import re

def Get_Xlsx(url):
    
    req = requests.get(url,stream=True)
    try:
        with open(f"temp/{url[59:]}", "wb") as fp:
            for partie in req.iter_content():
                fp.write(partie)
    except MaxRetryError:
        return False
    return True

def Get_Skipper(html):
    """
    On scrap la page web et 
    On produit un dictionnaire {détail tech : valeur}
    """
    print(html)
    r = requests.get(html)
    soup = BeautifulSoup(r.content)
    dico={}
    masque = "[0-9]*,[0-9]*"
    masque2 = "[0-9]+"
    #On va produire le champ skipper
    #Il a été vu que le champ skipper n'est pas fiable
    #dico['Skipper']=html.split('/')[-1].replace('-',' ').lower()
    #On créé la cle cle qui contient le nom de famille pour la jointure des 2 DF
    dico['Cle'] = html.split('/')[-1].replace('-',' ').lower().split(' ')[-1]
    for tag in soup.findAll('li', attrs={'class': 'skipper-boat-list-specs-list__item'}) :
        categorie = tag.text.split(':')[0]
        text = tag.text.split(':')[1][1:]
        if categorie == 'Numéro de voile ':
            #dico['N']= (int(re.compile(masque2).search(text).group()))
            #print(dico['N'])
            pass
        elif categorie == 'Architecte ':
            dico['constructeur'] = text
            pass
        elif categorie == 'Chantier ':
            dico['chantier'] = text
            pass
        elif categorie == 'Date de lancement ':
            dico['age'] = 2020-int(text.split(' ')[-1])
            pass
        elif categorie == 'Longueur ':
            dico['longueur'] = float(re.compile(masque).search(text).group().replace(',','.'))
            pass
        elif categorie == 'Largeur ':
            dico['largeur'] = float(re.compile(masque).search(text).group().replace(',','.'))
            pass
        elif categorie == "Tirant d'eau ":
            dico['tirant'] = float(re.compile(masque).search(text).group().replace(',','.'))
            pass
        elif categorie == 'Déplacement (poids) ':
            if text.lower() != 'nc':
                dico['poids'] = float(re.compile(masque2).search(text).group())
            else : 
                #dico['poids'] = 'na'
                pass
        elif categorie == 'Nombre de dérives ':
            if text[:4] == 'foil':
                dico['foils'] = True
                #dico['derive'] = False
            else :
                dico['foils'] = False
                #dico['derive'] = float(re.compile(masque2).search(text).group())
            pass
        elif categorie == 'Hauteur mât ':
            dico['mat'] = int(re.compile(masque2).search(text).group())
            pass
        elif categorie == 'Voile quille ':
            dico['voile_quille'] = text
            pass
        elif categorie == 'Surface de voiles au près ':
            dico['surface'] = int(re.compile(masque2).search(text).group())
            pass
        elif categorie == 'Surface de voiles au portant ':
            dico['surface_portant'] = int(re.compile(masque2).search(text).group())
            pass
    
    return dico
    