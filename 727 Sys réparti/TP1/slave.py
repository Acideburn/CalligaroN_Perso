# -*- coding: utf-8 -*-
"""
Created on Sat Oct 17 22:36:41 2020

@author: AcideBurn
"""

from biblio import *

parser = argparse.ArgumentParser()

parser.add_argument('mode')
                    
args = parser.parse_args()

def Mapping_Process (my_hostname,mute=False):
    """
    
    """
    if not mute:
        print(f"je suis dans le Mapping Process de")
    
    #print(f"je lis tous les Sx.txt présent dans mon dossier {direct}Splits/")
    #acquisition de la liste des fichiers présent
    tmp = CmdOnSsh_Return (f"cd {direct}Splits/; find S*")
    fichiers = tmp.split()
    del (tmp)
    #print (fichiers)
    words = []
    #PHASE DE MAPPING a chronométrer
    for fichier in fichiers :
        with open (f"{direct}Splits/{fichier}",'r') as f : #on ouvre tous les fichiers
            text = f.read()
            words.extend(text.split()) #on concatène tout dans une liste
            #Fin PHASE DE MAPPING        
            #print (words)

    #print(f"je produit un UMx.txt associé dans le dossier {direct}Maps/")
    
    #création de UMx.txt contenant un objet liste / x = fichiers[0][1] (attention check pour un seul fichier présent)
    i = fichiers[0][1] #on récupère le x du premier Sx.txt trouvé afin de produire le UMx.txt associé (cas de plusieurs Sx.txt)

    with open(f'{direct}/Maps/UM{i}.txt','wb') as f: #On ouvre et créée le fichier UMx.txt
        pickle.dump(words,f) #On y stock l'objet liste 
        #print (f"ce qui a été écrit : {words}")
    #print (f"ce qui a été écrit : {words}")
    
    return True  #on sort du Mapping_Process avec exit(1) pour que le master sache que tout c'est bien passé
    #return False #On sort avec exit(0) si problème

def Shuffle_Process(my_hostname,mute=False):
    """
    
    """
    if not mute :
        print(f"je suis dans le Shuffle Process")
    
    if not mute :
        print(f"je lis le UMx.txt présent dans mon dossier {direct}Maps/")
    #acquisition de la liste du fichier présent
    mon_um = CmdOnSsh_Return(f"cd {direct}Maps/; find UM*")
    #print (mon_um)
    #On monte en mémoire l'objet dans UMx.txt
    words = Get_Obj_In_File(f"{direct}Maps/{mon_um}")
    del(mon_um)
    
    #On récupère le dictionnaire {ind : hostname}
    ind_machine = Get_Obj_In_File(f'{direct}ind_machine.txt')
    #on va créer le dictionnaire {hash : ind} (virtuel)
    hash_name ={}
    nb_machine = len(ind_machine)
    for word in words :
        val_hash = abs(hash(word))
        #print (f"{word} donne le hash {val_hash}")
        #on produit un dictionnaire {hash : hostname (jointure sur ind_machine)}
        #print (word,val_hash)
        hash_name[val_hash] = ind_machine[(val_hash%nb_machine)]
        #print (word,val_hash,val_hash%nb_machine)
    #On produit le SM<hash>-<mon hostname>.txt
    #il contient la liste de toutes les itérations d'un même mot
        #print(f"je vais créer SM{val_hash}-{my_hostname}")
        #print(f"depuis {val_hash}")
        with open (f'{direct}/Shuffles/SM{val_hash}-{my_hostname}','a') as f:
            f.write(word+' ')    
    if not mute :
        print(f"je suis dans le Transfert Process")
    for key,val in hash_name.items() :
        ficname = f"SM{key}-{my_hostname}"
        cmd = f"scp -r {direct}Shuffles/{ficname} {username}@{val}:{direct}ShufflesReceived"
        CmdOnSsh(cmd)
    #print (ficname)
    
    return


def Reduce_Process ():
    print(f"je suis dans le Reduce Process")
    
    print(f"je lis tous les SMx.txt présent dans mon dossier {direct}ShufflesReceived/")
    toto = CmdOnSsh_Return (f"cd {direct}ShufflesReceived/; find SM*")
    #print (toto)
    
    #Phase de PRE REDUCE
    titi=''
    fichiers = toto.split()
    for fichier in fichiers :
        new_name = fichier[2:-12]
        with open (f"{direct}ShufflesReceived/{fichier}",'r') as ficsource :
            with open (f"{direct}Reduces/NR{new_name}",'a') as ficdest :
            #print (f"j'écrit de {fichier} vers {new_name}")
                ficdest.write(ficsource.read())
                titi = titi + f"NR{new_name} "
    
    #print (titi)
    #Phase de REDUCE (CALCUL)            
    #toto = CmdOnSsh_Return ("ssh {username}@{hostname} cd {direct}\\Reduces/; find NR*")            
    toto = titi
    fichiers = toto.split()
    #print (fichiers)
    #Debut PHASE DE REDUCE à chronométrer
    for fichier in fichiers :
        with open (f"{direct}Reduces/{fichier}",'r') as f:
            #print (f"j'ai ouvert {fichier}")
            sentence = f.read()
            #print (f"j'ai lu {sentence}")
    word = sentence.split()
    size = len(word)
    last_file = f"RM{fichier[2:]}"
    with open (f"{direct}Reduces/{last_file}",'w') as f:
        #print (f"j'écris  : {word[0]} : {size}")
        f.write (f"{word[0]} : {size}")
        last_file = f'RM{fichier[2:]}'
        print (f"je pousse au master : {last_file}")            
    master_hostname = Get_Obj_In_File(f"{direct}master.txt")
    CmdOnSsh(f"scp -r {direct}Reduces/{last_file} {username}@{master_hostname}:{direct}Final")
    
    
    return

    
def main():
    
    my_hostname = CmdOnSsh_Return ('hostname')
    
    if args.mode == '0' :
        print(f"Appel du Slave {my_hostname} en mode MAPPING")
        Mapping_Process(my_hostname,mute=True)
    elif args.mode == '1' :
        print(f"Appel du Slave en mode {my_hostname} SHUFFLE")
        Shuffle_Process(my_hostname,mute=True)
        pass
    elif args.mode == '2' :
        print(f"Appel du Slave en mode REDUCE")
        Reduce_Process()
        pass
    else :
        print(f"Appel du Slave sans paramètre")
        print (f"Je suis sur la machine : {my_hostname}")
        exit()
    

    
    



if __name__ == '__main__':
    main()