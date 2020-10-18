# -*- coding: utf-8 -*-
"""
Created on Sat Oct 17 22:36:41 2020

@author: AcideBurn
"""

from biblio import *
    
def deploy():

    """
    Monte la liste des machines à traiter
    Test la connexion ssh, retire les machines ne répondant pas
    Créer le dossier de travail distant : "/tmp/ncalligaro/"
    Copie l'ensemble du dossier en local vers la rep distant
    
    """
    
    list_hostname = Get_Obj_In_File(f"{direct}Machines.txt")

    #Création de l'arborescence du Master
    action  = "Création de l'arborescence complète du master en local"
    cmd=[]
    cmd.append(f"mkdir -p {direct}")
    cmd.append(f"{cmd[0]}Splits")
    cmd.append(f"{cmd[0]}Final")
    for i in range(len(cmd)):
        if (CmdOnSsh(cmd[i],mute=True)) :
            pass
        else :
            print(f"exécution de {action} Nok pour :Master")
            break
    print(f"exécution de {action} ok pour : Master") 
    
    #Création de l'arborescence de tous les slaves
    action  = "Création de l'arborescence complète du Slave à distance"

    for hostname in list_hostname :
        cmd=[]
        cmd.append(f"ssh {username}@{hostname} mkdir -p {direct}")
        cmd.append(f"{cmd[0]}Splits")
        cmd.append(f"{cmd[0]}Shuffles")
        cmd.append(f"{cmd[0]}ShufflesReceived")
        cmd.append(f"{cmd[0]}Reduces")
        cmd.append(f"{cmd[0]}Maps")
        for i in range(len(cmd)):
            if CmdOnSsh(cmd[i],mute=True) :
                pass
            else :
                print(f"exécution de {action} Nok pour :{hostname}")
                list_hostname.remove(hostname)
                break
        #print(f"exécution de {action} ok pour :{hostname}")
    print (f"j'ai {len(list_hostname)} adresse(s) ok pour : {action}")
    
    #On copie le fichier slave.py et le package biblio
    action  = "Upload Slave"
    for hostname in list_hostname :
        if (CmdOnSsh(f"scp -r -p {direct}slave.py {username}@{hostname}:{direct}",mute=True)) :
            CmdOnSsh(f"scp -r -p {direct}biblio.py {username}@{hostname}:{direct}",mute=True)
            #print(f"exécution de {action} ok pour :{hostname}")
            pass
        else :
            print(f"exécution de {action} Nok pour :{hostname}")
            list_hostname.remove(hostname) 
    print (f"{list_hostname} traitées : {action}")
    
if __name__ == '__main__':
    deploy()