# -*- coding: utf-8 -*-
"""
Created on Sun Feb 21 10:11:29 2021

Projet réalisé par :
Mahmoud Benboubker
Nicolas Calligaro
Aïcha Lalhou
"""
import pandas as pd
import numpy as np

#########################################################################
#                                                                       #
#         Création des matrices : Feature & Ground Truth                #
#                                                                       # 
#########################################################################

def feat_mat_const(df, listOfBs):
    """On a rajouté une colonne contenant le nombre de détection par msg
    cela servira à identifié la pondération de la prédiction
    """
    
    df_group = df.groupby("messid", as_index=False) 
    nb_mess = len(df.messid.unique())
    df_feat = pd.DataFrame(np.zeros((nb_mess,len(listOfBs))), columns = listOfBs, index=df.messid.unique())
    id_list = [0] * nb_mess

    for i, (key, elmt) in enumerate(df_group): 
        df_feat.loc[key,elmt.bsid]= 1
        id_list[i] = key
    df_feat

    # Pour le barycentre pondéré
    a =df.rssi.values
    df['rssi_reshape'] = (10**(a/10))
    df['bs_lat_pond'] = df.bs_lat * df.rssi_reshape
    df['bs_lng_pond'] = df.bs_lng * df.rssi_reshape
    BCW_lat = df.groupby('messid').bs_lat_pond.sum()/df.groupby('messid').rssi_reshape.sum()
    BCW_lat.name='BCW_lat'
    BCW_lng = df.groupby('messid').bs_lng_pond.sum()/df.groupby('messid').rssi_reshape.sum()
    BCW_lng.name='BCW_lng'

    #Pour le barycentre ajout min , max + mean 

    BC_lat = df.groupby('messid').agg(['mean', 'min', 'max'])[['bs_lat']]
    BC_lat.columns = BC_lat.columns.droplevel()

    BC_lng = df.groupby('messid').agg(['mean', 'min', 'max'])[['bs_lng']]
    BC_lng.columns = BC_lng.columns.droplevel()

    dev_lat =df.groupby(['did','messid']).agg(['mean', 'min', 'max'])[['bs_lat']].reset_index()
    dev_lat.columns = dev_lat.columns.droplevel()
    dev_lat.columns= ['did','messid','bs_l_did_mean', 'bs_l_did_min', 'bs_l_did_max']
    dev_lat=dev_lat.drop('did',axis=1)

    dev_lng =df.groupby(['did','messid']).agg(['mean', 'min', 'max'])[['bs_lng']].reset_index()
    dev_lng.columns = dev_lng.columns.droplevel()
    dev_lng.columns= ['did','messid','bs_L_did_mean', 'bs_L_did_min', 'bs_L_did_max']
    dev_lng=dev_lng.drop('did',axis=1)

    #On fait apparaitre une colonne contenant le messid pour la jointure

    df_feat = df_feat.reset_index()
    df_feat.rename(columns={'index':'messid'}, inplace=True)

    df_feat= pd.merge(df_feat,dev_lat,on='messid')
    df_feat= pd.merge(df_feat,dev_lng,on='messid')

    df_feat= pd.merge(df_feat,BC_lat,on='messid')
    df_feat= pd.merge(df_feat,BC_lng,on='messid')

    df_feat=df_feat.join(BCW_lat, on ='messid',how='left')
    df_feat=df_feat.join(BCW_lng, on ='messid',how='left')

    #On remet le messid dans l'index
    df_feat.set_index('messid',inplace=True)

    return df_feat, id_list 

def ground_truth_const(df_mess_train, pos_train, id_list):

    df_mess_pos = df_mess_train.copy()
    df_mess_pos[['lat', 'lng']] = pos_train #On met les vrai coord en face des messages

    y_full = pd.DataFrame({'messid' : id_list
                       , 'lat' : np.array(df_mess_pos.groupby(['messid']).mean()['lat'])
                       , 'lng' : np.array(df_mess_pos.groupby(['messid']).mean()['lng']) 
                      })
    return y_full


#########################################################################
#                                                                       #
#         Création de la métrique métier                                #
#                                                                       # 
#########################################################################

from vincenty import vincenty

def vincenty_vec(vec_coord):
    vin_vec_dist = np.zeros(vec_coord.shape[0])
    if vec_coord.shape[1] !=  4:
        print('ERROR: Bad number of columns (shall be = 4)')
    else:
        vin_vec_dist = [vincenty(vec_coord[m,0:2],vec_coord[m,2:]) for m in range(vec_coord.shape[0])]
    return vin_vec_dist

def Eval_geoloc(y_train_lat , y_train_lng, y_pred_lat, y_pred_lng):
    vec_coord = np.array([y_train_lat , y_train_lng, y_pred_lat, y_pred_lng])
    err_vec = vincenty_vec(np.transpose(vec_coord))
    return err_vec

#########################################################################
#                                                                       #
#         Correction des bases outliers                                 #
#                                                                       # 
#########################################################################

def Correct_Bases (df_input,debug=True):
    """ Cette fonction controle les bases qui dépasse d'une zone défini
        On considère que la zone est toute latitude supérieur à 64
        Voir jupyter 3_Base Station
    """
    df=df_input.copy() #On protège l'écriture sur le DataFrame donnée en entrée
    base_out = df[df.bs_lat>60].bsid.unique()
    msg_out = df[df.bsid.isin(base_out)].messid.unique()
    base_in = df[df.bs_lat<60].bsid.unique()
    print(f"Nous avons {len(base_out)} bases outliers")
    df_mess_out = df[(df.messid.isin(msg_out))&(~df.bsid.isin(base_out))]
    
    messid=[];coordW=[]
    group = df_mess_out.groupby('messid')

    for i in group.groups:
        tmp=group.get_group(i)
        rssi_reshape= (10**(tmp.rssi.values/10))
        latW = tmp.bs_lat.values * rssi_reshape
        lngW = tmp.bs_lng.values * rssi_reshape
        messid.append(tmp.messid.unique()[0])
        coordW.append((latW.sum()/rssi_reshape.sum(),lngW.sum()/rssi_reshape.sum()))
        msg_coordW = pd.DataFrame(data=coordW,index=messid,columns =['lat','lng'])

    #tous ces messages sont capté uniquement par les bases outliers
    df_clean =df.drop(df[~df.messid.isin(df[df.bsid.isin(base_in)].messid.unique())].index)
    bsid=[];coord=[]
    group = df_clean[df_clean.bsid.isin(base_out)].groupby('bsid')
    for i in group.indices:
        bsid.append(i)
        coord.append((msg_coordW.loc[group.get_group(i).messid.values].lat.mean(),msg_coordW.loc[group.get_group(i).messid.values].lng.mean()))
    bsid_relocated=pd.DataFrame(data=coord,index=bsid,columns =['lat','lng'])

    for i in bsid_relocated.index:
        df.loc[df.index[df.bsid==i],'bs_lat']=bsid_relocated.loc[i].lat
        df.loc[df.index[df.bsid==i],'bs_lng']=bsid_relocated.loc[i].lng

    if ((df[df.bsid==9949].index.values).size != 0) & debug:
        print(f"Correction manuelle de la bsid 9949")
        df.loc[df[df.bsid==9949].index.values,'bs_lat']=48.072889
        df.loc[df[df.bsid==9949].index.values,'bs_lng']=-110.957181
    else :
        print(f"Base 9949 non vu")
    print(f"il reste {df[df.bs_lat>60].shape[0]} base avec lat >60")

    return df

#########################################################################
#                                                                       #
#         Correction des distances trop élevé                           #
#                                                                       # 
#########################################################################

def Correct_Distance(df_input,pos_train):

    df=df_input.copy() #On protège l'écriture sur le DataFrame donnée en entrée
    pos_train['messid'] = df.messid
    msg_coord = pos_train.groupby('messid').mean()

    df['dist']=0
    for i in df.index:
        base_coord = (df.iloc[i].bs_lat,df.iloc[i].bs_lng)
        mess_coord = (msg_coord.loc[df.iloc[i].messid].lat,msg_coord.loc[df.iloc[i].messid].lng)
        df.loc[i,'dist']=vincenty(base_coord,mess_coord)

    Q2,Q3 = np.quantile(df[['dist']],[0.5,0.75])
    Qmax = Q3+(1.5*(Q3-Q2))
    print(f)
    df_reduce = df[df['dist']<=Qmax]
    df_reduce.drop('dist',axis=1,inplace=True)

    return df_reduce

#########################################################################
#                                                                       #
#         Récupération des hyper paramêtres d'un modèle                 #
#                                                                       # 
#########################################################################
import ast
def get_hyperparameter(model_name, coord):
    '''Modèles disponibles : XGBRegressor, ExtraTreeRegressor, GradientBoostingRegressor, RandomForestRegressor, BaggingRegressor'''
    df = pd.read_csv("best_params.csv")
    return ast.literal_eval(df[df["Model"] == model_name][coord].values[0])