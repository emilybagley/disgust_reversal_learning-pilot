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

def make_digit_span(df):
    digit_span=pd.DataFrame()
    for i in range(1,len(set(df.participant_no))+1):
        sub_df=df[df.participant_no==float(i)]
        digit_span_df=sub_df.dropna(subset=['digit_span']).reset_index()
        if len(digit_span_df.index)==0:
            temp_digit_span=pd.DataFrame({'digit_span': "task failed", 'participant_no': [sub_df.participant_no.iloc[0]] })
        else:
            temp_digit_span=pd.DataFrame({'digit_span': [digit_span_df.digit_span[0]], 'participant_no': [digit_span_df.participant_no[0]]})
        digit_span=pd.concat([digit_span, temp_digit_span])
    return digit_span