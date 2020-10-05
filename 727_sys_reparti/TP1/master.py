# -*- coding: utf-8 -*-
"""
Programme lancant une cmd.
avec gestion de l'erreur et affichage du bon flux de sortie
"""

import subprocess
    
def exec_ok (dist_Process) :
    print("Traitement du process distant")
    print (type(dist_Process))
    print (dist_Process)
    if not dist_Process.returncode :
        print ("le process distant est ok, voici la sortie")
        print (dist_Process.stdout.decode('cp850'))
    else :
        print ("le process distant a eu un soucis, voici l'erreur")
        print (dist_Process.stderr.decode('cp850'))

if __name__ == '__main__':
    Mon_Process = subprocess.run("python slave.py", shell=True, capture_output=True)
    print (type(Mon_Process))
    print (Mon_Process)
    if not Mon_Process.returncode :
        print ("le processus distant a été lancé avec succes")
        exec_ok(Mon_Process)
    else :
        print ("le processus distant n' pas été lancé") 
        print (Mon_Process.stderr.decode('cp850'))

    
