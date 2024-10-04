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


def create_block_df(df, block_name, participant_no):
    sub_df=df[df.participant_no==participant_no].reset_index()
    task_df=sub_df[sub_df.task=="main_task"]
    block_df=pd.DataFrame(columns=['n_trial', 'rt', 'stim_selected', 'correct_stim', 'correct', 'feedback', 'feedback_congruent', 'correct_count', 'trial_till_correct', 'reversal', 'block_no', 'participant_no', 'timed_out'])
    block=task_df[task_df.block_type==block_name]
    block.reset_index(inplace=True)
    block.drop(['level_0', 'index'], axis=1, inplace=True)

    for i in set(block.n_trial):
        trial=block[block.n_trial==i]
        trial.reset_index(inplace=True)

        row = []
        if "red" in trial.feedback[2]:
            feedback='incorrect'
        else:
            feedback='correct'

        row.append({
            'n_trial': trial.n_trial[0], #
            'stim_selected': trial.stim_selected[0],#
            'correct_stim': trial.correct_stim[0],#
            'correct': trial.correct[0],#
            'feedback': feedback,
            'feedback_congruent': trial.feedback_congruent[2],
            'correct_count': trial.correct_count[0],#
            'trial_till_correct': trial.trial_till_correct[0],#
            'rt': trial.rt[0],
            'reversal': trial.reversal[0],#
            'block_no': trial.block_no[0],#
            'block_type': trial.block_type[0],
            'participant_no': trial.participant_no[0],#
            'timed_out': 0,
            'time_taken': (block.time_elapsed.iloc[-1]-block.time_elapsed[0])/60000 ##in minutes
        })
        block_df=pd.concat([block_df, pd.DataFrame(row)])
    block_df.reset_index(inplace=True)


    #replace stimuli with 0 and 1 (for plotting)
    stim=list(set(block_df.correct_stim.to_list()))
    stim0="<img src='"+str(stim[0])+"'</img>"
    stim0b="  <img src='"+str(stim[0])+"'</img>"
    stim1="<img src='"+str(stim[1])+"'</img>"
    stim1b="  <img src='"+str(stim[1])+"'</img>"

    block_df.replace([stim[0], stim[1]], [0, 1], inplace=True)
    block_df.replace([stim0, stim1], [0,1], inplace=True)
    block_df.replace([stim0b, stim1b], [0,1], inplace=True)

    #did they time out before reaching 7 reversals
    short_block=block[block.trial_till_correct.notna()] ##removes trials after they timed out (if they did)
    if short_block.iloc[-1].reversal==7.0 and short_block.iloc[-1].correct_count>=5:
        block_df.timed_out=0
    else:
        block_df.timed_out=1
    
    ##did reach reversal criteria for inclusion
    criteria=5
    if short_block.iloc[-1].reversal>=criteria:
        block_df['criteria']=0
    else:
        block_df['criteria']=1

    return block_df

def create_task_df(df, to_do):
    task_df=pd.DataFrame()
    for participant_no in set(df.participant_no):
        if to_do == "plot":
            fig, ax = plt.subplots(3,1, sharey=True)
            fig.tight_layout(pad=4)

            disgust_df=create_block_df(df, "Disgust", participant_no)
            ax[0].plot(disgust_df.stim_selected, 'o')
            ax[0].plot(disgust_df.correct_stim)
            if disgust_df.timed_out[0] == 0:
                timed_out="false"
            else:
                timed_out="true"

            if disgust_df.criteria[0] == 0:
                criteria="false"
            else:
                criteria="true"           

            ax[0].set_title("DISGUST block number: "+str(int(disgust_df.block_no[0]+1))+", timed out: "+timed_out+", criteria:"+criteria)

            fear_df=create_block_df(df, "Fear", participant_no)
            ax[1].plot(fear_df.stim_selected, 'o')
            ax[1].plot(fear_df.correct_stim)
            if fear_df.timed_out[0] == 0:
                timed_out="false"
            else:
                timed_out="true"

            if fear_df.criteria[0] == 0:
                criteria="false"
            else:
                criteria="true"  

            ax[1].set_title("FEAR block number: "+str(int(fear_df.block_no[0]+1))+", timed out: "+timed_out+", criteria:"+criteria )

            points_df=create_block_df(df, "Points", participant_no)
            ax[2].plot(points_df.stim_selected, 'o')
            ax[2].plot(points_df.correct_stim)
            if points_df.timed_out[0] == 0:
                timed_out="false"
            else:
                timed_out="true"

            if points_df.criteria[0] == 0:
                criteria="false"
            else:
                criteria="true"  

            ax[2].set_title("POINTS block number: "+str(int(points_df.block_no[0]+1))+", timed out: "+timed_out+", criteria:"+criteria)

            fig.suptitle("Subject number "+str(participant_no), size=16)
        temp_task=pd.concat([create_block_df(df, "Disgust", participant_no), create_block_df(df, "Fear", participant_no), create_block_df(df, "Points", participant_no)])
        task_df=pd.concat([task_df, temp_task])
    return task_df

def make_task_understood(df, complete_task_df, to_do):
    task_understood=pd.DataFrame()
    for i in set(df.participant_no):
        task_understood_temp=pd.DataFrame({'participant_no': [i]})
        sub_df=df[df.participant_no==float(i)].reset_index()

        #attention checks 
        attention=sub_df[sub_df.trial_var=="attention_check"].reset_index()
        if attention.loc[0].response == "{'Q0': ['Apple', 'Banana']}":
            block1=2
        elif (attention.loc[0].response == "{'Q0': ['Banana']}") or (attention.loc[0].response == "{'Q0': ['Spoon']}"):
            block1=1
        else:
            block1=0
        if attention.loc[1].response== "{'Q0': ['Bowl', 'Spoon']}":
            block2=2
        elif (attention.loc[1].response== "{'Q0': ['Bowl']}") or (attention.loc[1].response== "{'Q0': ['Spoon']}"):
            block2=1
        else:
            block2=0
        if attention.loc[2].response== "{'Q0': ['River', 'Mountain']}":
            block3=2
        elif (attention.loc[2].response== "{'Q0': ['River']}") or (attention.loc[2].response== "{'Q0': ['Mountain']}"):
            block3=1
        else:
            block3=0

        attention_checks = pd.DataFrame({
            'block': ['block 1', 'block 2', 'block 3'],
            'correct' :[block1, block2, block3]
        })
        task_understood_temp['attention_checks']=np.sum(attention_checks.correct)

        #timings - breaks and total time elapsed
        task=sub_df[sub_df.task=="main_task"]
        if len(task[task.rt/60000>10].index) ==0:
            task_understood_temp['long_breaks']="No"
        else:
            task_understood_temp['long_breaks']="Yes"
            task_understood_temp['breaks_details']=[task[task.rt/60000>10].reset_index().rt[0]/60000]
        
        task_understood_temp['total_time']=task.time_elapsed.iloc[-1]/60000

        ##did they reach the right number of reversals
        task_df=complete_task_df[complete_task_df.participant_no==i]
        disgust=task_df[task_df.block_type=="Disgust"]
        task_understood_temp['timed_out_d']=disgust.reset_index().timed_out[0]
        task_understood_temp['criteria_d']=disgust.reset_index().criteria[0]

        fear=task_df[task_df.block_type=="Fear"]
        task_understood_temp['timed_out_f']=fear.reset_index().timed_out[0]
        task_understood_temp['criteria_f']=fear.reset_index().criteria[0]

        points=task_df[task_df.block_type=="Points"]
        task_understood_temp['timed_out_p']=points.reset_index().timed_out[0]
        task_understood_temp['criteria_p']=points.reset_index().criteria[0]

        task_understood_temp['timed_out_total']=task_understood_temp[['timed_out_f', 'timed_out_d', 'timed_out_p']].sum(axis=1)
        task_understood_temp['criteria_total']=task_understood_temp[['criteria_f', 'criteria_d', 'criteria_p']].sum(axis=1)

        ##Checking they learnt the task correctly
        if task_understood_temp.attention_checks[0]>=4 and task_understood_temp.criteria_total[0]<3 and task_understood_temp.long_breaks[0]=="No" and task_understood_temp.total_time[0]<120:
            task_understood_temp['task_understood']="Yes"
        else:
            task_understood_temp['task_understood']="No"
        task_understood=pd.concat([task_understood, task_understood_temp])

    if to_do == "plot_exclusions":
        for participant_no in set(task_understood[task_understood.task_understood=="No"].participant_no):
            fig, ax = plt.subplots(3,1, sharey=True)
            fig.tight_layout(pad=4)

            disgust_df=create_block_df(df, "Disgust", participant_no)
            ax[0].plot(disgust_df.stim_selected, 'o')
            ax[0].plot(disgust_df.correct_stim)
            if disgust_df.timed_out[0] == 0:
                timed_out="false"
            else:
                timed_out="true"

            if disgust_df.criteria[0] == 0:
                criteria="false"
            else:
                criteria="true"           

            ax[0].set_title("DISGUST block number: "+str(int(disgust_df.block_no[0]+1))+", timed out: "+timed_out+", criteria:"+criteria)

            fear_df=create_block_df(df, "Fear", participant_no)
            ax[1].plot(fear_df.stim_selected, 'o')
            ax[1].plot(fear_df.correct_stim)
            if fear_df.timed_out[0] == 0:
                timed_out="false"
            else:
                timed_out="true"

            if fear_df.criteria[0] == 0:
                criteria="false"
            else:
                criteria="true"  

            ax[1].set_title("FEAR block number: "+str(int(fear_df.block_no[0]+1))+", timed out: "+timed_out+", criteria:"+criteria )

            points_df=create_block_df(df, "Points", participant_no)
            ax[2].plot(points_df.stim_selected, 'o')
            ax[2].plot(points_df.correct_stim)
            if points_df.timed_out[0] == 0:
                timed_out="false"
            else:
                timed_out="true"

            if points_df.criteria[0] == 0:
                criteria="false"
            else:
                criteria="true"  

            ax[2].set_title("POINTS block number: "+str(int(points_df.block_no[0]+1))+", timed out: "+timed_out+", criteria:"+criteria)

            fig.suptitle("Subject number "+str(participant_no), size=16)
    return task_understood
