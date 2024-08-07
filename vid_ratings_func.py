import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import scipy.stats as stats
import jsonlines
from functools import reduce
import statistics
import scipy.stats
import seaborn as sns
import math
import os
import json
import ast

def vid_ratings(df, participant_no, to_do):  
    sub_df=df[df.participant_no==float(participant_no)]
    rating_vids_df=sub_df[sub_df.trial_var=="rate_stim"]
    rating_vids_df['response'].replace('  ', np.nan, inplace=True)
    rating_vids_df= rating_vids_df.dropna(subset=['response'])
    rating_vids_df.sort_values(by=["stimulus", "trial_index"], inplace=True) ##groups dataframe by video type - allows you to extract 1st, 2nd and 3rd presentation of each video

    #create a dataframe with all ratings (for one participant)
    rating_vids_a=[]
    rating_vids_b=[]
    rating_vids_c=[]

    vals = range(len(rating_vids_df.index))

    for val in vals: #loop through the dataframe
        stim = str(rating_vids_df.iloc[val].stimulus)
        trial_type=rating_vids_df.iloc[val].type
        response = ast.literal_eval(rating_vids_df.iloc[val].response) #makes it a dictionary
        unpleasant=response['Q0']
        arousing=response['Q1']
        disgusting=response['Q2']
        frightening=response['Q3']

        #extract which video it is
        if "0888.gif" in stim:
            vid="0888"
        elif "1414.gif" in stim:
            vid="1414"
        elif "1765.gif" in stim:
            vid="1765"
        elif "1987.gif" in stim:
            vid="1987"
        elif "2106.gif" in stim:
            vid="2106"
        elif "0046.gif" in stim:
            vid = "0046"
        elif "0374.gif" in stim:
            vid = "0374"
        elif "0548.gif" in stim:
            vid = "0548"
        elif "0877.gif" in stim:
            vid = "0877"
        elif "1202.gif" in stim:
            vid = "1202"
        else:
            vid = "ERROR"

        if val in range(0, 30, 3):
            rating_vids_a.append({
                'Vid' : vid,
                'trial_type': trial_type,
                'unpleasant_1': unpleasant,
                'arousing_1': arousing,
                'disgusting_1': disgusting,
                'frightening_1': frightening,
                'disgust_stim': 0,
                'fear_stim': 0,
            })
        elif val in range(1,30,3):
            rating_vids_b.append({
                'Vid' : vid,
                'trial_type': trial_type,
                'unpleasant_2': unpleasant,
                'arousing_2': arousing,
                'disgusting_2': disgusting,
                'frightening_2': frightening,
                'disgust_stim': 0,
                'fear_stim': 0,
            })
        elif val in range(2,30,3):
            rating_vids_c.append({
                'Vid' : vid,
                'trial_type': trial_type,
                'unpleasant_3': unpleasant,
                'arousing_3': arousing,
                'disgusting_3': disgusting,
                'frightening_3': frightening,
                'disgust_stim': 0,
                'fear_stim': 0,
            })

    rating_vids_a=pd.DataFrame(rating_vids_a)
    rating_vids_b=pd.DataFrame(rating_vids_b)
    rating_vids_c=pd.DataFrame(rating_vids_c)
    rating_vids=rating_vids_a.merge(rating_vids_b, on=['Vid', 'trial_type', 'disgust_stim', 'fear_stim'])
    rating_vids=rating_vids.merge(rating_vids_c, on=['Vid', 'trial_type', 'disgust_stim', 'fear_stim'])
    rating_vids=rating_vids[['Vid', 'trial_type','unpleasant_1', 'unpleasant_2', 'unpleasant_3', 'arousing_1', 'arousing_2', 'arousing_3', 'disgusting_1', 'disgusting_2', 'disgusting_3', 'frightening_1', 'frightening_2', 'frightening_3', 'disgust_stim', 'fear_stim']]

    #add which video was chosen for disgust and fear stim
    fear_stim=str(sub_df.fear_stimulus.dropna())
    disgust_stim=str(sub_df.disgust_stimulus.dropna())

    if "0888.gif" in disgust_stim:
        rating_vids.loc[rating_vids['Vid']=="0888", ['disgust_stim']]=1
    elif "1414.gif" in disgust_stim:
        rating_vids.loc[rating_vids['Vid']=="1414", ['disgust_stim']]=1
    elif "1765.gif" in disgust_stim:
        rating_vids.loc[rating_vids['Vid']=="1765", ['disgust_stim']]=1
    elif "1987.gif" in disgust_stim:
        rating_vids.loc[rating_vids['Vid']=="1987", ['disgust_stim']]=1
    elif "2106.gif" in disgust_stim:
        rating_vids.loc[rating_vids['Vid']=="2106", ['disgust_stim']]=1
    else:
        print("error")

    if "0046.gif" in fear_stim:
        rating_vids.loc[rating_vids['Vid']=="0046", ['fear_stim']]=1
    elif "0374.gif" in fear_stim:
        rating_vids.loc[rating_vids['Vid']=="0374", ['fear_stim']]=1
    elif "0548.gif" in fear_stim:
        rating_vids.loc[rating_vids['Vid']=="0548", ['fear_stim']]=1
    elif "0877.gif" in fear_stim:
        rating_vids.loc[rating_vids['Vid']=="0877", ['fear_stim']]=1
    elif "1202.gif" in fear_stim:
        rating_vids.loc[rating_vids['Vid']=="1202", ['fear_stim']]=1
    else:
        print("error")

    #add participant number and total columns
    rating_vids['participant_no']=sub_df.reset_index().participant_no[0]
    ## remove for later batches
    rating_vids['batch']=sub_df.reset_index().batch[0]
    rating_vids['batch1_participant_no']=sub_df.reset_index()['batch1_participant_no']

    rating_vids['unpleasant_total']=rating_vids['unpleasant_2'] + rating_vids['unpleasant_3']
    rating_vids['arousing_total']= rating_vids['arousing_2'] + rating_vids['arousing_3']
    rating_vids['disgusting_total']= rating_vids['disgusting_2'] + rating_vids['disgusting_3']
    rating_vids['frightening_total']=rating_vids['frightening_2'] + rating_vids['frightening_3']
    
    #create dataframe with just the chosen stimuli for each subject
    chosen_stim=pd.concat([rating_vids[rating_vids.disgust_stim==1], rating_vids[rating_vids.fear_stim==1]])
    chosen_stim['participant_no']=sub_df.reset_index().participant_no[0]
    chosen_stim['unpleasant_total']=chosen_stim['unpleasant_2'] + chosen_stim['unpleasant_3']
    chosen_stim['arousing_total']=chosen_stim['arousing_2'] + chosen_stim['arousing_3']
    chosen_stim['disgusting_total']=chosen_stim['disgusting_2'] + chosen_stim['disgusting_3']
    chosen_stim['frightening_total']= chosen_stim['frightening_2'] + chosen_stim['frightening_3']

    if to_do == "plot":
        #Checking chosen stim
        fig, ax = plt.subplots(nrows=2,ncols=2, sharey=False)
        fig.tight_layout(pad=4)

        ax[0,0].bar(['Disgust', 'Fear'], [np.mean(chosen_stim[chosen_stim.trial_type=="disgust"].unpleasant_2), np.mean(chosen_stim[chosen_stim.trial_type=="fear"].unpleasant_2)])
        ax[0,0].set_title("Valence ratings")

        ax[0,1].bar(['Disgust', 'Fear'], [np.mean(chosen_stim[chosen_stim.trial_type=="disgust"].arousing_2), np.mean(chosen_stim[chosen_stim.trial_type=="fear"].arousing_2)])
        ax[0,1].set_title("Arousal ratings")


        ax[1,0].bar(['Disgust', 'Fear'], [np.mean(chosen_stim[chosen_stim.trial_type=="disgust"].disgusting_2), np.mean(chosen_stim[chosen_stim.trial_type=="fear"].disgusting_2)])
        ax[1,0].set_title("Disgust ratings")

        ax[1,1].bar(['Disgust', 'Fear'], [np.mean(chosen_stim[chosen_stim.trial_type=="disgust"].frightening_2), np.mean(chosen_stim[chosen_stim.trial_type=="fear"].frightening_2)])
        ax[1,1].set_title("Fear ratings")
        fig.suptitle("Subject number "+str(int(sub_df.reset_index().participant_no[0])), size=16)
    elif to_do == "rating_vids":
        return rating_vids
    elif to_do == "chosen_stim":
        return chosen_stim
    else:
        return "ERROR"