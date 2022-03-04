import datetime
import pandas
import tkinter
import tkinter.filedialog
import tkinter.messagebox
import os
from pathlib import Path

FichierLevees = ''
FichierAnomalies = 'init'
listeFich = ''
CheminFichier = ''


## FONCTIONS TKINTER ##


def saisieContrat(*events):
    
    global CodeContrat, labelAttente, FichierLevees, FichierAnomalies
    
    CodeContrat = entree.get()
    labelContrat.configure(text="Code contrat = " + CodeContrat)
    entree.grid_remove()
    button_OK_next.grid_remove()
    labelFichierLevees.grid(column = 1, row = 2, columnspan=2)
    button_explore.grid(column = 1, row = 3, columnspan=2) 
    button_exit.grid(column = 1,row = 4, columnspan=2)


## A. Choix du fichier de levées ##

def choixFichier():
    
    global FichierLevees, FichierAnomalies
    
    if FichierLevees == '':
        FichierLevees = tkinter.filedialog.askopenfilename(filetypes=[('Fichiers CSV', '.csv')])
        labelFichierLevees.configure(text="Fichier de levées : "+FichierLevees)
        button_explore.grid_remove()
        button_exit.grid_remove()
        labelFichierAnomalies.grid(column = 1, row = 3, columnspan=2)
        button_explore.grid(column = 1, row = 4)
        button_skip.grid(column = 2, row = 4)
        button_exit.grid(column = 1,row = 5, columnspan=2)
    else:
        if FichierAnomalies != '':
            FichierAnomalies = tkinter.filedialog.askopenfilename(filetypes=[('Fichiers CSV', '.csv')])
            labelFichierAnomalies.configure(text="Fichier d'anomalies : "+FichierAnomalies)
        else:
            labelFichierAnomalies.configure(text="Pas d'anomalie configurée")
        button_explore.grid_remove()
        button_skip.grid_remove()
        button_exit.grid_remove()
        labelAttente.grid(column = 1, row = 4, columnspan=2)
        button_OK_launch.grid(column = 1, row = 5, columnspan=2)
        button_exit.grid(column = 1,row = 6, columnspan=2)

def skipAnomalies():
    
    global FichierAnomalies
    
    FichierAnomalies = ''
    choixFichier()

    
def validation():
    
    button_OK_launch.grid_remove()
    button_exit.grid_remove()
    labelAttente.configure(text='Création des fichiers en cours...')
    button_exit.grid(column = 1,row = 5, columnspan=2)
    lancementTransformation()

def lancementTransformation():
    transformationData()
    labelAttente.configure(text='Opération terminée')
    button_exit.grid_remove()
    button_liste.grid(column=1, row=5)
    button_fin.grid(column = 2,row = 5)

def listeFichiers():
    
    global listeFich, CheminFichier
    
    if listeFich == '':
        listeFich = 'Pas de fichier généré. Vérifier le contenu du fichier CSV sélectionné.'
    else:
        listeFich = 'Répertoire des fichiers généré :\n\n\t' + CheminFichier + '\n\nListe des fichiers générés :\n\n' + listeFich
    tkinter.messagebox.showinfo("Liste des fichiers générés", listeFich)


## FONCTION PANDAS ##

## C. Import de la table Simpliciti CSV

def transformationData():
    
    global NomFichier, data1, data2, listeFich, CheminFichier
    
    ##### INFO : data1 est la dataframe obtenue avec la liste des identifications de puces
    ##### INFO : data2 est la dataframe obtenue avec la liste des anomalies
    ##### INFO : la fusion de data2 dans data1 est faite à l'étape "Ecriture des anomalies liées aux puces"
    
    data1 = pandas.read_csv(FichierLevees)
    CheminFichier = os.path.dirname(FichierLevees)
    os.chdir(CheminFichier)
    
    if FichierAnomalies == '':
        presenceAnomalies=False
    else:
        presenceAnomalies=True
    
    if presenceAnomalies == True:
        data2 = pandas.read_csv(FichierAnomalies)
    
        ##### Suppression des évènements non liés aux puces #####
        
        data2 = data2[data2.loc[:,'N° Puce'].notna()]
        data2 = data2.reset_index(drop=True)
    
    ##### Modification du champ Circuit #####
    
    data1.loc[:,'Circuit'] = data1.loc[:,'Circuit'].fillna('TFERME')
    data1.loc[:,'Circuit'] = data1.loc[:,'Circuit'].replace(' ', '', regex=True)
    
    if presenceAnomalies == True:
        data2.loc[:,'Circuit'] = data2.loc[:,'Circuit'].fillna('')
    
        ##### Extraction des anomalies uniques #####
        
        Anomalies2 = pandas.Series(0, index=data2.loc[:,'Intitulé'].unique())
        
        ##### Association des numéros de bouton aux anomalies #####
        
        for anomalie in range(len(Anomalies2)):
            print('Saisir le numéro d anomalie pour : ' + Anomalies2.index[anomalie])
            testAnomalie = tkinter.simpledialog.askstring(title="Assignation des boutons", prompt="Saisir le numéro de bouton pour cette anomalie : " + str(Anomalies2.index[anomalie]))
            if testAnomalie is None:
                #Anomalies2.drop(index=Anomalies2.index[anomalie], inplace=True)
                Anomalies2[anomalie] = 0
            else:
                Anomalies2[anomalie] = testAnomalie
            print(Anomalies2.index[anomalie] + " = " + "Bouton anomalie " + str(Anomalies2[anomalie]))
            
        #Suppression des anomalies qui n'ont pas de bouton associé
        
        for i in range(len(Anomalies2[Anomalies2 == 0].index)):
            data2.drop(data2[data2['Intitulé'] == Anomalies2[Anomalies2 == 0].index[i]].index, inplace=True)
            data2 = data2.reset_index(drop=True)
        Anomalies2.drop(Anomalies2[Anomalies2 == 0].index, inplace=True)
    
    print('Transformation des données en cours... Merci de patienter')
    
    ##### Création des colonnes anomalies bouton #####
        
    for bouton in range(6):
        data1.insert(len(data1.columns),'bouton ' + str(bouton + 1), 0)
    
    ##### Création des colonnes positions XY #####
        
    data1.insert(len(data1.columns),'latitude', 0)
    data1.insert(len(data1.columns),'longitude', 0)
    
    ##### Ecriture des anomalies liées aux puces #####
    
    if presenceAnomalies == True:
        for event in range(len(data2)):
            PucesAvecAnomalie = pandas.Series(data1[data1.loc[:,'Puce Fondeur']==data2.loc[event,'N° Puce']].index.tolist())
            for puce in range(len(PucesAvecAnomalie)):
                data1.loc[PucesAvecAnomalie[puce],'bouton ' + str(int(Anomalies2[data2.loc[event,'Intitulé']]))] = 1
    
    ##### Modification de l'immatriculation #####
    
    data1.loc[:,'Véhicule'] = data1.loc[:,'Véhicule'].replace('-','', regex=True)
    
    if presenceAnomalies == True:
        data2.loc[:,'Véhicule'] = data2.loc[:,'Véhicule'].replace('-','', regex=True)
    
    ##### Réarrangement des colonnes #####
    
    if not 'Chaise' in data1:
        data1.insert(len(data1.columns),'Chaise', 0)
    data1 = data1[['Date','Heure','Circuit','Véhicule','Puce Fondeur','Poids','Chaise','Identifié','Stoppé','Blacklisté', 'bouton 1', 'bouton 2', 'bouton 3', 'bouton 4', 'bouton 5', 'bouton 6', 'latitude', 'longitude']]
    data1 = data1.reset_index(drop=True)
    
    ##### Modification de la colonne Chaise #####
        
    data1.loc[:,'Chaise'] = data1.loc[:,'Chaise'].replace('gauche', 0)
    data1.loc[:,'Chaise'] = data1.loc[:,'Chaise'].replace('droite', 1)
    data1.loc[:,'Chaise'] = data1.loc[:,'Chaise'].replace('combiné', 2)
    data1.loc[:,'Chaise'] = data1.loc[:,'Chaise'].replace('Bi-Comp', 3)
    
    for row in range(len(data1)):
            
        ##### Création de la colonne Code levée #####
        
        CodeLevée = ''
        if data1.loc[row,'Identifié'] == 'oui':
            if data1.loc[row, 'Blacklisté'] == 'oui':
                CodeLevée = '10'
            else:
                CodeLevée = '11'
        else:
            CodeLevée = '00'
        if data1.loc[row, 'Stoppé'] == 'non':
            CodeLevée = CodeLevée + '1'
        else:
            CodeLevée = CodeLevée + '0'
            
        data1.loc[row, 'Identifié'] = CodeLevée
    
    data1.rename(columns={'Identifié':'Code Levée'}, inplace=True)
    
    ##### Suppression des colonnes inutiles #####
    
    data1.drop(columns = ['Stoppé', 'Blacklisté'], inplace = True)
    
    ##### Extraction des valeurs uniques #####
    
    Dates1 = pandas.Series(data1.loc[:,'Date'].unique())
    Circuits1 = pandas.Series(data1.loc[:,'Circuit'].unique())
    Véhicules1 = pandas.Series(data1.loc[:,'Véhicule'].unique())
    
    ##### Boucle sur chaque tournée ######
    
    i = 0
    
    for d1 in range(len(Dates1)):
        for c1 in range(len(Circuits1)):
            for v1 in range(len(Véhicules1)):
                
                ##### Extraction des données de la tournée #####
                
                subdata1 = data1[(data1.loc[:,'Date']==Dates1[d1]) & (data1.loc[:,'Circuit']==Circuits1[c1]) & (data1.loc[:,'Véhicule']==Véhicules1[v1])]
                
                ##### Gestion des exceptions dans les noms de circuits #####
                
                if str(Circuits1[c1]).replace('.','',1).isdigit():
                    Circuit = str(int(Circuits1[c1]))
                    subdata1.loc[:,'Circuit'] = Circuit
                else:
                    Circuit = Circuits1[c1]
                
                if len(subdata1) > 0:
                
                    ##### Suppression des doublons #####
                    
                    doublons = subdata1[subdata1.loc[:,'Puce Fondeur'].notna()]
                    doublons = doublons[doublons.loc[:,'Puce Fondeur'].duplicated()==True]
                    
                    for doublon in range(len(doublons)):
                        if doublons.loc[doublons.index[doublon], 'Code Levée'][2] == '1':
                            subdata1.loc[subdata1[subdata1.loc[:,'Puce Fondeur']==doublons.loc[doublons.index[doublon], 'Puce Fondeur']].index.tolist(), 'Code Levée'] = doublons.loc[doublons.index[doublon], 'Code Levée']
                        subdata1 = pandas.concat([
                            subdata1[subdata1['Puce Fondeur'].isna()],
                            subdata1[subdata1['Puce Fondeur'].notna()].drop_duplicates('Puce Fondeur', keep='last')
                        ])
                    
                    ##### Création de la première colonne à partir de l'index #####
                    
                    subdata1 = subdata1.sort_index()
                    subdata1 = subdata1.reset_index(drop=True)
                    subdata1.insert(0,'index', subdata1.index + 1)
                    
                    ##### Création du nom de fichier #####
                    
                    Date = datetime.datetime.strptime(Dates1[d1], '%d/%m/%Y')
                    ajd = datetime.datetime.today()
                    NomFichier = CodeContrat + '_' + datetime.datetime.strftime(Date, '%Y%m%d') + '_' + Véhicules1[v1] + '_' + Circuit + '_' + datetime.datetime.strftime(ajd, '%Y%m%d_%H%M%S')
                    
                    ##### Contrôle de l'existence de 2 tournées sous l même nom #####
                    
                    if os.path.exists(CheminFichier + '/' + NomFichier + '.txt'):
                        NomFichier = NomFichier + str(i)
                        i+=1
                    NomFichier = NomFichier + '.txt'
                    
                    listeFich = listeFich + '\t' + NomFichier + ' (' + str(len(subdata1)) + ' levées)\n'
                    
                    ##### Transformation du subdata en texte #####
                    
                    txt = subdata1.to_csv(index=False, header=False, sep=';')
                    txt = txt.replace('\n', '')
                    txt = txt.replace('\r', '\n')
                    txt = 'BOF;' + datetime.datetime.strftime(ajd, '%d/%m/%Y;%H:%M:%S') + ';' + CodeContrat + '\n' + txt + 'EOF'
        
                    ##### Modification du Poids #####
                    
                    txt = txt.replace('.0','')
                    
                    ##### Enregistrement du fichier #####
                    
                    Fichier = open(NomFichier, 'wt')
                    Fichier.write(txt)
                    Fichier.close()
                    
                    print('Fichier transformé : ' + NomFichier + ' (' + str(Path(CheminFichier + '/' + NomFichier).stat().st_size) + ' octets)')
                    
                else:
                    print('Fichier vide : Tournée ' + Circuit + ' du ' + Dates1[d1] + ' par la BOM ' + Véhicules1[v1])


## SCRIPT ##


## 1 ## Initialisation de la fenêtre Tkinter ##

window = tkinter.Tk()
window.title('Formatage des données RI de Simpliciti pour Chrome')
window.config(background = "white") 


## 2 ## Création des fonctions et éléments à afficher ##

labelContrat = tkinter.Label(window, text = 'Saisir le numéro de contrat :', width = 100, height = 4,  fg = "blue") 
labelFichierLevees = tkinter.Label(window, text = "Sélectionner le fichier de levées\n(le format du fichier doit être en CSV)", width = 100, height = 4, fg = "blue") 
labelFichierAnomalies = tkinter.Label(window, text = "Sélectionner le fichier d'anomalies ou passer à la prochaine étape\n(le format du fichier doit être en CSV)", width = 100, height = 4, fg = "blue") 
labelAttente = tkinter.Label(window, text = 'Prêt ?', width = 100, height = 6,  fg = "blue") 
contrat = tkinter.StringVar(window)
contrat.set("XXXX")
entree = tkinter.Entry(window, textvariable=contrat, width=50)
entree.bind("<Return>", saisieContrat)
button_OK_next = tkinter.Button(window, text = "Valider", command = saisieContrat)
button_explore = tkinter.Button(window, text = "Choisir...", command = choixFichier)
button_skip = tkinter.Button(window, text = "Passer", command = skipAnomalies)
button_exit = tkinter.Button(window, text = "Annuler", command = window.destroy)
button_OK_launch = tkinter.Button(window, text = "Lancer", command = validation)
button_liste = tkinter.Button(window, text = "Liste des fichiers", command = listeFichiers)
button_fin = tkinter.Button(window, text = "Terminer", command = window.destroy)



## 3 ## Ancrage des éléments ##

labelContrat.grid(column = 1, row = 1, columnspan=2)
entree.grid(column = 1, row = 2, columnspan=2)
button_OK_next.grid(column = 1, row = 3, columnspan=2)
button_exit.grid(column = 1,row = 4, columnspan=2)


## 4 ## Lancement de la boucle Tkinter ##

window.mainloop()