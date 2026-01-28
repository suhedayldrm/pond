#rank the things based on frequency level and level them as A1, A2, B1, B2, C1, C2

"""
"lemma","url","wortklasse","artikeldatum","artikeltyp","frequenzklasse"
"$","https://www.dwds.de/wb/%24","Substantiv","1967","Basisartikel-D","3"
"%","https://www.dwds.de/wb/%25","Substantiv","1974","Vollartikel","4"
"&","https://www.dwds.de/wb/%26","Konjunktion","1976","Vollartikel","5"
"-abel","https://www.dwds.de/wb/-abel","Affix","2021-09-13","Basisartikel-D","n/a"
"-ade","https://www.dwds.de/wb/-ade","Affix","1999","Basisartikel-D","n/a"
"-al","https://www.dwds.de/wb/-al","Affix","1999","Basisartikel-D","n/a"
"-algie","https://www.dwds.de/wb/-algie","Affix","2024-09-14","Minimalartikel","n/a"
"-an","https://www.dwds.de/wb/-an","Affix","2024-06-19","Basisartikel-D","n/a"
"-and","https://www.dwds.de/wb/-and","Affix","2022-01-19","Basisartikel-D","n/a"
"-aner","https://www.dwds.de/wb/-aner","Affix","2025-10-17","Minimalartikel","n/a"
"-anfällig","https://www.dwds.de/wb/-anf%C3%A4llig","Affix","1999","Basisartikel-D","n/a"
"""

import pandas as pd

import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from collections import Counter
# 6 is most frequent, 1 is least frequent

def rank_frequenzklasse(df, column='frequenzklasse'):
    # Define the mapping from frequenzklasse to levels
    level_mapping = {
        '1': "C2",
        '2': "C1",
        '3': "B2",
        '4': "B1",
        '5': "A2",
        '6': "A1"
    }
    
    # Convert to string (handle floats like 3.0 -> '3') and apply mapping
    df['level'] = df[column].apply(lambda x: level_mapping.get(str(int(x)) if pd.notna(x) else None, None))
    return df


if __name__ == "__main__":
    # Load the data
    df = pd.read_csv('dwds_data.csv')
    
    # Rank the frequenzklasse
    df_ranked = rank_frequenzklasse(df)
    
    # Save the updated dataframe
    #app/german/B2.json
    #app/german/C1.json
    #App/german/C2.json
    #write these below levels to separate json files above
    
    for level in ['B2', 'C1', 'C2']:
        df_level = df_ranked[df_ranked['level'] == level]
        df_level.to_json(f'app/german_base/{level}.json', orient='records', force_ascii=False, indent=4)
    
    # Print the first few rows to verify
    print(df_ranked.head())