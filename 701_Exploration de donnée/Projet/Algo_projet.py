# -*- coding: utf-8 -*-
"""
Created on Thu Nov 12 18:03:25 2020

@author: Calligaro Nicolas \ Calvet Rodolphe
"""

"""
Bibliothèque pour projet explo big data
"""

import pandas as pd
import numpy as np
import networkx as nx
from datetime import time
from ipyleaflet import Marker, MarkerCluster, AntPath, Polyline
import pickle
import geocoder
import seaborn as sns

##############################################################################
#                   Travail sur le DataFrame                                 #
##############################################################################

def Prod_Clean_Df():
    """
    On lit un fichier xls et on le transforme en DataFrame.
    On y applique les corrections identifées. On corrige les types des champs date.
    On le Data Frame est sauvegarder en mémoire pour une réutilisation future.
    """
    #On vérifie si le DF existe déjà sur le disque
    try:
        df_Trajet=pickle.Unpickler(open("df_Trajet.pkl",'rb')).load()
    except:
        #On lance la fct de dl des fichiers xls
        print(f"DF non présent sur le disque")
        #Par défault on en charge un sur le disque
        df_Trajet = pd.read_csv('103JourneyDataExtract28Mar2018-03Apr2018.csv')
        #On retire les non trajets
        df_Trajet.drop(df_Trajet[df_Trajet['StartStation Id'] == df_Trajet['EndStation Id']].index,inplace=True)
        #On retire les trajets de +8h
        df_Trajet.drop(df_Trajet[df_Trajet['Duration']>28800].index,inplace=True)
        #On structure les champs date
        df_Trajet['Start Date'] = pd.to_datetime(df_Trajet['Start Date'], format="%d/%m/%Y %H:%M")
        df_Trajet['End Date'] = pd.to_datetime(df_Trajet['End Date'], format="%d/%m/%Y %H:%M")
        #On l'enregistre sur le disque
        print(f"DF produit et sauvegardé")
        pickle.Pickler(open("df_Trajet.pkl",'wb')).dump(df_Trajet)
    else :
        print(f"load from disque OK")
    return df_Trajet

def Prod_Coord_Df(df):
    """
    On produit le DataFrame qui contiendra les coordonnées Gps des stations
    Voir la fonction prod_Coord_Gps pour générer la location gps des stations
    On sauvegarde sur le disque le DataFrame ainsi produit pour une future réutilisation 
    """
    try :
        df_Coord_Gps=pickle.Unpickler(open("df_Coord_Gps.pkl",'rb')).load()
    except:
        print("Je télécharge les Coord ETA 10 minutes")
        df_Coord_Gps = pd.DataFrame({'Station_Id': df['StartStation Id'].unique(), 'Station_Name': df['StartStation Name'].unique()})
        df_Coord_Gps[['latitude','longitude']]=list(df_Coord_Gps['Station_Name'].apply(lambda x:prod_Coord_Gps(x)))
        df_Coord_Gps=df_Coord_Gps.set_index('Station_Id').sort_index()
        print(f"DF produit et sauvegardé")
        pickle.Pickler(open("df_Coord_Gps.pkl",'wb')).dump(df_Coord_Gps)
    else:
        print(f"load from disque OK")

    return df_Coord_Gps

def Get_Slice (df, work, heure_deb, heure_end) :
    """
    Entrée :
        Df : le DF complet de travail
        work : week si on prend la semaine.
               wend
              Su ou Sa pour le Dimanche ou Samedi
        heure_deb : tuple (heure,minute)
        Permet de récupérer un slice du DF par rapport à une journée (semaine ou week end)
        et un créneau horaire
    """
    h1 = time(heure_deb[0],heure_deb[1])
    h2 = time(heure_end[0],heure_end[1])

    if work=='sun' :
        df1 = df.loc[df['Start Date'].dt.strftime('%a').str.contains('Su')]
    elif work=='sat' :
        df1 = df.loc[df['Start Date'].dt.strftime('%a').str.contains('Sa')]
    elif work=='week': 
        df1 = df.loc[~df['Start Date'].dt.strftime('%a').str.contains('^[S]')]
    elif work=='wend':
        df1 = df.loc[df['Start Date'].dt.strftime('%a').str.contains('^[S]')]
    df_slice = df1.loc[(df1['Start Date'].dt.time >= h1) & (df1['Start Date'].dt.time <= h2)]
    #print(df_slice.shape)
    return df_slice
    
def prod_Coord_Gps(x):
    """
    On fait appel à la bibliothèque geocoder et au service arcgis afin de récupérer des 
    coordonées Gps en fonction du nom des stations
    Certaines Stations ont des coordonées erronées, donc on les corriges à la main.
    """
    if x == 'Christopher Street, Liverpool Street':
        return 51.52,-0.08
    elif x == 'Shadwell Station, Shadwell':
        return 51.5112, -0.0569
    elif x == 'Mile End Stadium, Mile End':
        return 51.519411, -0.031000
    g = geocoder.arcgis(f"{x},Londres,Royaume Uni")
    print(f"{g.json['lat']:.10}/{g.json['lng']:.10}/{x}")
    return g.json['lat'],g.json['lng']    

##############################################################################
#                   Travail sur les Graph                                    #
##############################################################################

def Prod_Graph(df,deep=4,Rdeep=10):
    """
    On extrait du DataFrame les trajets dans l'ordre croissant des départs d'une meme station.
    deep : est le nombre de station de départprise en compte
    Rdeep : est le nombre d'arrivé pris en compte
    Retourne un graph orienté et non orienté on rajoute un attribut 
    qui est le nombre de fois que le trajet est réalisé.
    """
    DG = nx.DiGraph()
    G = nx.Graph()
    for StartStation_Id,Freq_app_Ss in df['StartStation Id'].value_counts()[:deep].items():
        for EndStation_Id,Freq_app_Es in  df.loc[df['StartStation Id'] == StartStation_Id]['EndStation Id'].value_counts()[:Rdeep].items():
            DG.add_edge(StartStation_Id, EndStation_Id, freq=Freq_app_Es )
            G.add_edge(StartStation_Id,EndStation_Id, freq=Freq_app_Es )

    return G,DG

def Nettoyage (Graph) :
    """
    On extrait 3 types de noeud
    Ilot : noeud avec une forte connectivité (< max /2)
    passerelle : noeud avec une connectivité relative (+1)
    out : noeud avec une connectivité de 1
    """
    ilot = []
    out = []
    passerelle = []
    best = max(dict(Graph.degree).values())
    for i in list(Graph.degree) :
        if i[1] >= (best/2) :
            ilot.append(i[0])
        elif i[1] == 1 :
            out.append(i[0])
        else :
            passerelle.append(i[0])
    return ilot,passerelle,out

def reduced_graph(Graph,DirectGraph):
    """
    En utilisant le graph et les sommets identifié nous allons produire 2 graphs :
    LitleGraph : contiendra les sommets les plus connexes (on retires les sommets ayant qu'une seule arrête)
    Small Graph : contindra les sommets ayant une seules arrete et le sommet à l'origine de cette arrête)
    Sémantiquement : 
    le graph LitleGraph mettra en évidence les cyles (Station A > B > A) ou flux (Station A > B)
    le graph SmalGraph mettra en évidence les toutes les stations desservi par une seule station (Station A > B et C ...)
    """
    _,passerelle,out = Nettoyage (Graph)

    LitleGraph = DirectGraph.copy()
    for i in out :
        LitleGraph.remove_node(i)

    SmallGraph = Graph.copy()
    for i in passerelle :
        SmallGraph.remove_node(i)
    return SmallGraph,LitleGraph

def makeGraphTopBikes(df_we, nb_of_top_bikes=10):
    """
    Crée le graph de ce df du weekend. La fréquence vaut un pour chaque trajet!
    ----
    PARAMS : 
    nb_of_top_bikes : le nbre de vélos les plus utilisés retenus pour le graphe
    """
    #On détruit le graph avant
    try :
        G_Bikes.clear()
    except :
        pass
    #Test des deux listes

    #On construit le graph vide
    G_Bikes = nx.DiGraph(Title = 'Graph de ' + str(df_we))
    for Bike_Id,Freq_app_ in df_we['Bike Id'].value_counts()[:nb_of_top_bikes].items(): # les nb_of_top_bikes plus utilisés
        listeDesStationsDepartDeCeVelo = list(df_we.loc[df_we['Bike Id'] == Bike_Id]['StartStation Id'].values)
        listeDesStationsArriveeDeCeVelo = list(df_we.loc[df_we['Bike Id'] == Bike_Id]['EndStation Id'].values)
        for i in range(len(listeDesStationsDepartDeCeVelo)):
            # Le poids ici toujours égal à UN : Point de vue du vélo, pas de la station !!
            edge = [listeDesStationsDepartDeCeVelo[i],listeDesStationsArriveeDeCeVelo[i]]
            #On construit le graph par ces arrêtes
            G_Bikes.add_edge(edge[0], edge[1], freq=1)
            #print(f"Vélo {Bike_Id}: edge : {edge} > poids toujours 1")
            
    return G_Bikes

def makeGraphLowBikes(df_we, nb_of_low_bikes=30):
    """
    Crée le graph de ce df, la fréquence vaut un pour chaque trajet.
    ----
    PARAMS : 
    nb_of_low_bikes : le nbre de vélos les moins utilisés retenus pour le graphe
    """

    #On détruit le graph avant
    try :
        G_Bikes_L.clear()  # Les MOINS utilisés
    except :
        pass
    #Test des deux listes
    #print(list(dF_We_14_15.loc[df_we['Bike Id'] == 14389]['StartStation Id'].values),list(df_we.loc[dF_We_14_15['Bike Id'] == 14389]['EndStation Id'].values))

    #On construit le graph vide
    G_Bikes_L = nx.Graph(Title ='Graph de ' + str(df_we))
    for Bike_Id,Freq_app_ in df_we['Bike Id'].value_counts().sort_values(ascending=True)[:nb_of_low_bikes].items():
        listeDesStationsDepartDeCeVelo = list(df_we.loc[df_we['Bike Id'] == Bike_Id]['StartStation Id'].values)
        listeDesStationsArriveeDeCeVelo = list(df_we.loc[df_we['Bike Id'] == Bike_Id]['EndStation Id'].values)
        for i in range(len(listeDesStationsDepartDeCeVelo)):
            edge = (listeDesStationsDepartDeCeVelo[i],listeDesStationsArriveeDeCeVelo[i])
            #On construit le graph par ces arrêtes
            G_Bikes_L.add_edge(edge[0], edge[1], freq=1)
            #print(f"edge : {edge} > poids toujours 1")

    return G_Bikes_L

##############################################################################
#                   Travail sur la Carte                                     #
##############################################################################

def Give_Marker_Cluster(df) :
    """
    Cette fonction permet de produire une clustered Marquer afin d'affichier l'ensemble des stations
    du DataFrame.
    Les stations se regroupent en fonction du zoom
    """
    markers=[]
    for i in df.index :
        x = df.loc[i].latitude
        y = df.loc[i].longitude
        name = df.loc[i].Station_Name
        markers.append(Marker(location=(x,y),draggable=False,title=name))

    return MarkerCluster(markers=(markers))

def Give_Marker(df,G):
    """
    Cette fonction permet de produire tous les marquers associés au station fourni dans le Graph.
    On s'appuye sur le DataFrame donné pour trouver les stations,leur nom et leurs coordonées
    """
    markers=[]

    for indice in list(G.nodes):
        ###############ICI MA MODIF NICO###################################
        #if indice in df.index:
        ###############ICI MA MODIF NICO###################################
        markers.append(Marker(location=(df.loc[indice].latitude,df.loc[indice].longitude),
                draggable=False,title=df.loc[indice].Station_Name))
    return tuple(markers)

def Give_Colored_Marker(df,Station,icone):
    """
    Cette fonction permet de produire tous les marquers associés au station fourni dans le Graph.
    On s'appuye sur le DataFrame donné pour trouver les stations,leur nom et leurs coordonées
    """
    markers=[]
    for indice in Station:
        markers.append(Marker(
            location=(df.loc[indice].latitude,df.loc[indice].longitude)
            ,draggable=False,title=df.loc[indice].Station_Name
            ,icon=icone
            ))
    return tuple(markers)    

def Prod_Ant_Path(df,DG, col=False):
    """
    Cette fonction permet de produire un ensemble de Ant_Path (chemin de fourmi)
    On s'appuye sur le Graph et le DataFrame fourni pour identifier les trajets et les coordonées
    """
    max_ant = list(DG.edges.data('freq'))[0][2]
    pal = sns.color_palette('rainbow', max_ant+1)
    path = {}
    for indice in list(DG.edges.data('freq')):
        ###############ICI MA MODIF NICO###################################
        #if ((indice[0] in df.index) & (indice[1] in df.index)):
        ###############ICI MA MODIF NICO###################################
        ori=[df.loc[indice[0]].latitude,df.loc[indice[0]].longitude]
        des=[df.loc[indice[1]].latitude,df.loc[indice[1]].longitude]
        freq = indice[2]
        color = pal.as_hex()[freq%max_ant+1]
        path[indice] = AntPath(
                            locations=[ ori,des  ]
                        #,use = 'polyline' #‘polyline’, ‘polygon’, ‘rectangle’ and ‘circle’ 
                        #,radius= 10 #Radius of the circle, if use is set to ‘circle’
                        ,weight =5 #Epaisseur du trait
                        ,dash_array=[1, 50] #nb de fourmi sur le chemin
                        ,delay=1000 #vitesse des fourmis
                        ,color=(col if col else pal.as_hex()[(max_ant+1)//2]) #couleur de fond
                        ,pulse_color=color #couleur de la fourmi
                        #,name=''
                        )
    return path

def Prod_Polyline(df,G):
    """
    Identique à Prod_Ant_Path, les polylines sont plus légère à l'affichage.
    """
    max_ant = list(G.edges.data('freq'))[0][2]
    pal = sns.color_palette('rainbow', max_ant+1)
    line={}
    for indice in list(G.edges.data('freq')):
        x = indice[0]
        ori=[df.loc[indice[0]].latitude,df.loc[indice[0]].longitude]
        des=[df.loc[indice[1]].latitude,df.loc[indice[1]].longitude]
        line[indice] = Polyline(locations=[ori,des ]
                           ,color= pal.as_hex()[ x%(max_ant+1) ] #Couleur
                           ,fill= False
                           ,stroke = True #Bordure
                           ,opacity=1.0
                           ,weight=2 #largeur en pixel
                           #,fill_color = None #couleur du remplissage
                           #,fill_opacity = 0.2 #opacité du remplissage
                           #,dash_array = None
                           #,line_cap = 'round'
                           #,line_join = 'round'
                           #,name='' 
                          )
    return line
