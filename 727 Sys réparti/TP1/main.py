# -*- coding: utf-8 -*-
"""
Created on Sat Oct 17 22:36:41 2020

@author: AcideBurn
"""
from biblio import *




    
def main():
    
    mon_hostname = CmdOnSsh_Return ('hostname')

    print(f"Bienvue dans une simulation Map/Redcue \n"
          f"mon 'hostname' :{mon_hostname} \n"
          f"mon 'username' : {username} \n"
          f"Voici ma configuration : \n"
          f"j'ai un timeout de : {timeout_ref}s \n"
          f"je travail sur le fichier {data} \n"
          f"je produit des splits avec l'axiome suivant : \n"
          f"un mot fait 5 caractères (espace compris)")

    list_hostname = Get_Hostname_From_Fic_Ref(fichier,mon_hostname)

    print(f"Contrôle Ssh en cours")
    list_hostname = Test_Ssh(list_hostname)
    
    print(f"{len(list_hostname)} machines ont répondu en Ssh :{list_hostname}")
    Set_Obj_In_File(list_hostname,f"{direct}Machines.txt")

    print(f"lancement de la phase de nettoyage")    
    os.system("python3 clean.py")
    #on appel clean avec os.system afin de voir la SdtOut de clean (sinon le proces n'est pas verbeux.) en revanche si le process plante aucune protection

    print(f"Lancement de la phase de déploiement")
    os.system("python3 deploy.py")    

    print(f"Activation du Master début de Map/Reduce sur le fichier d'entrée : {data}")

    os.system("python3 master.py")  
    
    print(f"fin simulation")
    
if __name__ == '__main__':
    main()       
