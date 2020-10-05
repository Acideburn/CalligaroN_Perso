# -*- coding: utf-8 -*-
"""
Lance une cmd vouée à l'échec.
rend un obj CompletedProcess contenant le returncode!=0 stdout (vide), sdterr (l'explication de l'erreur)
"""

import subprocess
import sys



#print ("je suis un process distant")
test = subprocess.run("dire", shell=True,capture_output=True)
print (test)



"""
if not Mon_Process.returncode :
    print ("tout ce passe bien")
    print (Mon_Process.stdout.decode('cp850'))
else :
    print ("Il y a eu un soucis")
    print (Mon_Process.stderr.decode('cp850'))
"""