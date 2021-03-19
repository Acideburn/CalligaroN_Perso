# -*- coding: utf-8 -*-
"""
Created on Sun Feb 21 10:11:29 2021

Projet réalisé par :
Mahmoud Benboubker
Nicolas Calligaro
Aïcha Lalhou
"""

#########################################################################
#                                                                       #
#         Création des outils ipyleaflet                                #
#                                                                       # 
#########################################################################

from ipyleaflet import Marker,MarkerCluster,AwesomeIcon,Circle,Polyline

def Give_Marker_Cluster(df) :
    markers=[]
    for i in df.index :
        x = df.loc[i][df.columns[0]]
        y = df.loc[i][df.columns[1]]
        name = str(i)
        markers.append(Marker(location=(x,y),draggable=False,title=str(round(x,3))+str(round(y,3))))

    return MarkerCluster(markers=(markers))


def Give_Colored_Marker(df,color='blue',type='d') :
    if type == 'b':
        name='fa-podcast'
    elif type == 'd' :
        name='fa-user-circle-o'
    else :
        name='fa-user-circle-o'

    icon1 = AwesomeIcon(name=name,marker_color=color,spin=False)

    markers=[]
    for i in df.index :
        x = df.loc[i][df.columns[0]]
        y = df.loc[i][df.columns[1]]
        name = str(i)
        markers.append(Marker(icon=icon1, location=(x,y),draggable=False,title=name))
        
    return markers

def Draw_Dot(df,color):
    circles=[]
    for i in df.index :
        x = df.loc[i][df.columns[0]]
        y = df.loc[i][df.columns[1]]
        name = str(i)
        circles.append(Circle(location=(x,y),radius=1,color=color))
        
    return circles

def Get_line (df,pal,color):
    line={}
    for i in range(df.shape[0]-1):
        ori = (df.iloc[i].lat,df.iloc[i].lng)
        des = (df.iloc[i+1].lat,df.iloc[i+1].lng)
        line[i] = Polyline(locations=[ori,des ]
                           ,color= pal.as_hex()[color] #Couleur
                           ,fill= False
                           ,stroke = True #Bordure
                           ,opacity=1.0
                           ,weight=1 #largeur en pixel
                           #,fill_color = None #couleur du remplissage
                           #,fill_opacity = 0.2 #opacité du remplissage
                           #,dash_array = None
                           #,line_cap = 'round'
                           #,line_join = 'round'
                           #,name='' 
                          )
    return line