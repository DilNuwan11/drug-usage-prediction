def map_finnish_regions(finnish_region):
    # Finnish to English region translation mapping
    finnish_to_english = {
        "Uusimaa": "Uusimaa",
        "Varsinais-Suomi": "Finland Proper",
        "Satakunta": "Satakunta",
        "Kanta-Häme": "Tavastia Proper",
        "Pirkanmaa": "Pirkanmaa",
        "Päijät-Häme": "Päijät-Häme",
        "Kymenlaakso": "Kymenlaakso",
        "Etelä-Karjala": "South Karelia",
        "Etelä-Savo": "Southern Savonia",
        "Pohjois-Savo": "Northern Savonia",
        "Pohjois-Karjala": "North Karelia",
        "Keski-Suomi": "Central Finland",
        "Etelä-Pohjanmaa": "Southern Ostrobothnia",
        "Pohjanmaa": "Ostrobothnia",
        "Keski-Pohjanmaa": "Central Ostrobothnia",
        "Pohjois-Pohjanmaa": "Northern Ostrobothnia",
        "Kainuu": "Kainuu",
        "Lappi": "Lapland",
        "Ahvenanmaa": "Åland"
    }

    english_name = finnish_to_english.get(finnish_region)
    return english_name

def map_english_regions(english_region):
    # English to Finnish region translation mapping
    english_to_finnish = {
        "Uusimaa": "Uusimaa",
        "Finland Proper": "Varsinais-Suomi",
        "Satakunta": "Satakunta",
        "Tavastia Proper": "Kanta-Häme",
        "Pirkanmaa": "Pirkanmaa",
        "Päijät-Häme": "Päijät-Häme",
        "Kymenlaakso": "Kymenlaakso",
        "South Karelia": "Etelä-Karjala",
        "Southern Savonia": "Etelä-Savo",
        "Northern Savonia": "Pohjois-Savo",
        "North Karelia": "Pohjois-Karjala",
        "Central Finland": "Keski-Suomi",
        "Southern Ostrobothnia": "Etelä-Pohjanmaa",
        "Ostrobothnia": "Pohjanmaa",
        "Central Ostrobothnia": "Keski-Pohjanmaa",
        "Northern Ostrobothnia": "Pohjois-Pohjanmaa",
        "Kainuu": "Kainuu",
        "Lapland": "Lappi",
        "Åland": "Ahvenanmaa"
    }

    finnish_name = english_to_finnish.get(english_region)
    return finnish_name

def melting_data(df, value_name):
    df_melted = pd.melt(df_regions, id_vars=['Year'], 
                    value_vars= ['Uusimaa', 'Southwest Finland', 'Satakunta',
                                'Kanta-Häme', 'Pirkanmaa', 'Päijät-Häme', 'Kymenlaakso',
                                'South Karelia', 'South Savo', 'North Savo', 'North Karelia',
                                'Central Finland', 'South Ostrobothnia', 'Ostrobothnia',
                                'Central Ostrobothnia', 'North Ostrobothnia', 'Kainuu', 'Lapland',
                                'Åland'],
                    var_name='region', value_name=value_name)
    return df_melted

    