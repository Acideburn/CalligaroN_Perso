# -*- coding: utf-8 -*-
"""
Created on Sat Oct 17 22:36:41 2020

@author: AcideBurn
"""

from biblio import *

def clean():
    """
    Monte la liste des machines à traiter
    Test la connexion ssh, retire les machines ne répondant pas
    Supprime le dossier de travail distant : "/tmp/ncalligaro/" et tout son contenu
    """
    
    list_hostname = Get_Obj_In_File(f"{direct}Machines.txt")

    #On nettoye
    action = "Nettoyage"
    for hostname in list_hostname:
        if(CmdOnSsh(f"ssh {username}@{hostname} rm -rf {direct}",mute=True)):
            #print(f"exécution de {action} ok pour :{hostname}")
            pass
        else :
            print(f"exécution de {action} Nok pour :{hostname}")
            list_hostname.remove(hostname) 

    print (f"{list_hostname} traitées : {action}")

if __name__ == '__main__':
    clean()