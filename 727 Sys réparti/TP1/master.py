# -*- coding: utf-8 -*-
"""
Created on Sat Oct 17 22:36:41 2020

@author: AcideBurn
"""
from biblio import *



def Made_Dico_Machine(list_hostname):
    
    print("je suis dans la création du dictionnaire")
    ind_machine = {}
    for i in range (len(list_hostname)) :
        ind_machine[i] = list_hostname[i]

    Set_Obj_In_File(ind_machine, f'{direct}ind_machine.txt')
    return ind_machine

def Splitting(nb_machine,fichier_source):
    """
    On découpe les données d'entrée en Sx.txt en fonction du nb de machine et de la taille moyenne d'un mot
    
    """
    print(f"je suis dans le Splitting")
    word_size = 5
        
    #On fait une répartition du fichier input en fct du nombre de machine 
    #et de la taille std d'un mot
    mots = []
    with open (fichier_source,'r') as f :
        text = f.read()
    
    Split_size = len(text)//(nb_machine)
    
    #Production des Sx.txt
    for i in range (nb_machine):
        tmp = []
        tmp = text[i*Split_size:(i+1)*Split_size]
        with open (f'{direct}Splits/S{i}.txt','w') as f :
            f.write(tmp)
            print(f"Ecriture du S{i}.txt ok")
    return True

def Dispatching(ind_machine):
    #On possède un dictionnaire {Indice : Hostname}
    #On a créer les splits en s'appuyant sur l'indice
    #On va ainsi pouvoir distribuer le S[indice] au hostname associé (nb : ne supporte pas l'envoie de multiple Split)
    #On transmet également le dictionnaire au slave
    #On transmet également l'host du master
    
    print(f"je suis dans le Dispatching")
    
    Set_Obj_In_File(CmdOnSsh_Return ('hostname'), 'master.txt')
    
    for key,val in ind_machine.items() :
        CmdOnSsh(f"scp -r {direct}Splits/S{key}.txt {username}@{val}:{direct}Splits/")
        CmdOnSsh(f"scp -r {direct}ind_machine.txt {username}@{val}:{direct}")
        CmdOnSsh(f"scp -r {direct}master.txt {username}@{val}:{direct}")
    
    return True


def Activate_Process_Salves(ind_machine,mode):
    """
    Fonction d'appel des slaves avec différent mode :
        0 Mapping
        1 shuffle
        2 Reduce
    """
    
    print(f"je suis dans l'activation de process")
    for hostname in ind_machine.values() :
        cmd = f"ssh {username}@{hostname} python3 {direct}slave.py {mode}"
        print(f"déclanchement du slave : {hostname}")
        os.system(cmd) #on lance les slaves sans controle du timeout ni réception du retour
    return

def Fusion_Final():
    
    print(f"je suis dans la fusion final")
    toto = CmdOnSsh_Return (f"cd {direct}Final/; find *")
    #print (toto)
    
    #Phase FINAL de concaténation
    fichiers = toto.split()
    for fichier in fichiers :
        with open (f"{direct}Final/{fichier}",'r') as ficsource :
            with open (f"{direct}Final/Final.txt",'a') as ficdest :
                #print (f"j'écrit de {fichier} vers {new_name}")
                ficdest.write(f"{ficsource.read()} ")

    with open (f"{direct}Final/Final.txt",'r') as f :
        final = f.read()
    print (final)






def main():
    
    list_hostname = Get_Obj_In_File(f"{direct}Machines.txt")
    
    print(f"Etape 0 : Splitting. je découpe input.txt en Sx.txt")
    Splitting(len(list_hostname),data)

    print(f"Etape 1 : Dispatching. Je copie les Sx.txt dans les Slaves")
    #Cration du dictionnaire des machines
    ind_machine = Made_Dico_Machine(list_hostname)
    Dispatching(ind_machine)

    print(f"Etape 2 : Je délanche la phase de MAPPING sur l'ensemble des slaves")

    print(f"début du chronomètre et de la phase de multithrearding")
    Activate_Process_Salves(ind_machine,0)
    print (f"J'attends le retour des slaves")
    print(f"fin du chronomètre synchroniser sur le multithreading")
    
    print(f"dans l'attente du threading on met une tempo de 5s")
    time.sleep(5)
    
    print (f"--- MAPPING COMPLETED ---")

    print (f"Etape 3 : Je délanche la phase de SHUFFLE")

    print(f"début du chronomètre et de la phase de multithrearding")
    Activate_Process_Salves(ind_machine,1)
    print (f"J'attends le retour des slaves")
    print(f"fin du chronomètre synchroniser sur le multithreading")
    
    print(f"dans l'attente du threading on met une tempo de 5s")
    time.sleep(5)
    print(f"--- SHUFFLE COMPLETED ---")
    
    #Question, à la fin du shuffle, le transfert des SM<hash>-<hostname> doit etre compris dans la phase ou non ?
    #Question j'ai des hash négatif ? on les passe en positif ou comment aug la taille du int    
    
    print(f"Etape 3 : Je délcanche la phase de REDUCE")

    print(f"début du chronomètre et de la phase de multithrearding")
    Activate_Process_Salves(ind_machine,2)
    print (f"J'attends le retour des slaves")
    print(f"fin du chronomètre synchroniser sur le multithreading")

    print(f"dans l'attente du threading on met une tempo de 5s")
    time.sleep(5)
    print(f"--- REDUCE COMPLETED ---")

    print(f"Etape 4 : Calcul du résultat")
    
    Fusion_Final()
    

    print(f"""Le résultat est disponible ici : {direct}Final/Final.txt""")


if __name__ == '__main__':
    main()