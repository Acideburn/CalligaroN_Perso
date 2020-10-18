import subprocess
import pickle #sérialisation des objets
import os
import sys
import argparse

    
username = [username] #Mettre votre username sous forme d'une STRING        
direct = f"/tmp/{username}/"  #directory de travail machine distante   
fichier = "deploy_list.py" #Fichier référence contenant la liste des machines à contacter
data = 'DATA.txt'
timeout_ref = 2

    #le répertoire de travail pour tout copier sur une machine de l'école à n'utiliser que pour le deploy
#home = r"C:\Users\AcideBurn\OneDrive\Documents\727_sys_reparti\ncalligaro"

def Get_Hostname_From_Fic_Ref(fichier, mon_hostname):
    """Lit le fichier de référence.
    retire son nom de la liste
    Stock l'objet dans un fichier
    retourne une liste avec tous les hostnames
    """
    with open(fichier, 'r') as f:
        text = f.read()
    #print(f"je lit le fichier {le_fichier}")
    """
    comment écrire dans un fichier en supprimant le contenu avant (option W)
    with open(le_fichier, 'w') as f:
        f.write(text)
    Mode d'ouverture d'un fichier    
    # Option d'ouverture de open:
    # r: ouverture en lecture.
    # w: ouverture en écriture(mais supprime le contenu avant)
    # a: ouverture en écrivant à la suite
    # x: Créer le fichier avant ouverture. Rien si le fichier existe
    # Ecrire dans un fichier inexistant le créé !!
    """
    list_hostname = list()
    for hostname in text.split():
        if hostname != mon_hostname: #retire son hostname de la liste
            list_hostname.append(hostname)
            #print(f"j'ai ajouté le hostname suivant {adr_ip}")
        else:
            #print("je retire mon nom de la liste:", my_hostname)
            pass
    #print(f"J'ia lu {len(list_adr_ip)} @")
    return list_hostname


def Set_Obj_In_File(objet_a_serialiser, fichier): 
    """
    Sérialise un objet dans un fichier
    Fonctionne comme open mais on manipule des objets et non des chaines de caratère
    Ecriture sans append (on purge le fichier avant de l'ouvrir)
    """
    #print(f"je sérialise l'objet {objet_to_store}")
    with open(fichier, 'wb') as fic_tool:  #on ouvre le fichier en lecture + binaire
        pickler_tool = pickle.Pickler(fic_tool) #on créer un outil
        pickler_tool.dump(objet_a_serialiser) #on écrit l'objet dans le fichier
    #print(f"objet sérialisé")
    return True


def Get_Obj_In_File(le_fichier):
    """ On lit et obtiens un objet depuis un fichier
    """
    #print (f"je désérialise depuis le fichier {le_fichier}")
    with open(le_fichier,'rb') as fic_tool:  #on ouvre le fichier en écriture + binaire
        unpickler_tool = pickle.Unpickler(fic_tool) #on créer un outil
        nouvel_objet = unpickler_tool.load() #on lit et on obtiens un objet
         #on obtiens un objet
    #print(f"objet désérialisé : {my_new_object}")
    del(le_fichier)
    return nouvel_objet  


def CmdOnSsh(cmd,timeout=timeout_ref,mute=False):
    """lance run et gère l'erreur le timeout
    retourne TRUE si la commande s'est exécuté.
    retourne FALSE sinon.
    Ne retourne pas les sortie Std et Err donc je rien faire afficher.    
    """
    if not (mute):
        print (f"je suis sur la cmd :{cmd}")
    try: #protège le timeOut
        mon_process = subprocess.run(cmd, shell=True, capture_output=True, timeout = timeout)
    except subprocess.TimeoutExpired:
        print("process trop long sur la cmd :",cmd)
    else:
        if not mon_process.returncode: #si returncode vaux 0 tout se passe bien
            #print("ok -Debug-")
            return True
        if mon_process.returncode == '255':
            print ("Connexion Ssh refusé ")
            print("Nok -Debug-",mon_process.returncode)
        else:            
            print("Nok -Debug-",mon_process.returncode)
            print(mon_process.stderr.decode('cp850')) #return la sortie d'erreur et l'affiche
            return False
    return False


def CmdOnSsh_Return(cmd):
    """identique à CmdOnSsh mais en retournant la sortie standard et d'erreur
    Les chaines de caractère retourné sont traitable directement
    """
    try:
        mon_process = subprocess.run(cmd, shell=True, capture_output=True, timeout = timeout_ref) 
    except subprocess.TimeoutExpired:
        print("process trop long sur la cmd :",cmd)
    else:
        if not mon_process.returncode:
            return mon_process.stdout.decode("utf-8").rstrip()
        else:            
            return mon_process.stderr.decode("cp850").rstrip()

      
def Test_Ssh(list_adr_ip):
    """fait une connexion ssh sur les items de la liste.
    retire de la liste les @ip qui ne répondent pas
    
    """
    action  = "test Ssh"
    for adr_ip in list_adr_ip:
        if(CmdOnSsh(f"ssh {username}@{adr_ip} hostname")):
            #print("exécution de "+action+" ok pour:",adr_ip) #affiche que la machine a répondu en ssh
            pass
        else:
            print("exécution de "+action+" Nok pour:",adr_ip) #affiche que la machine n'a pas répondu en ssh
            list_adr_ip.remove(adr_ip) #retire la machine qui ne répond pas de la liste
    #print(f"j'ai {len(list_adr_ip)} adresse(s) ok pour: "+action) #fait un point de site à la fin        
    return list_adr_ip