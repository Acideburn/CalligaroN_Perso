# -*- coding: utf-8 -*-
"""
Éditeur de Spyder

Ceci est un script temporaire.
"""

import subprocess

Mon_Process = subprocess.run(["ls","-l"], shell=True, capture_output=True)
if not Mon_Process.returncode :
    print ("tout ce passe bien")
    print (Mon_Process.stdout.decode('cp850'))
else :
    print ("Il y a eu un soucis")
    print (Mon_Process.stderr.decode('cp850'))