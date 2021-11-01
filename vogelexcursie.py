import json
import ast

import pandas as pd    
import requests
import yagmail


def get_all_excursies():
    url = 'https://www.vogelbescherming.nl/?act=excursies.json&&type=Excursie&'
    response = requests.get(url)
    return response

def select_relevant_data(response):
    data = response.content.decode('UTF-8').strip('var kaartpunten = ')
    activities = ast.literal_eval(data)['features']
    return activities

def clean_data(activities):
    df = pd.json_normalize(activities)
    df['geometry.coordinates'] = df['geometry.coordinates'].apply(tuple)
    return df

def validate_df(df):
    assert not df.duplicated().any()  # Duplicates are used to filter old activities later
    return df

def engineer_features(df):
    base_url = 'https://www.vogelbescherming.nl'

    df_new = df[[]].copy()
    df_new['ID'] = df['properties.customID']
    df_new['Longitude'] = df['geometry.coordinates'].apply(lambda x: x[0])
    df_new['Latitude'] = df['geometry.coordinates'].apply(lambda x: x[1])
    
    df_new['Titel'] = df['properties.popupContent'].str.extract('^<strong>(.+)</strong>')
    df_new['Datum'] = df['properties.popupContent'].str.extract('Excursie<br />(.+)<br />')
    df_new['URL'] = base_url + df['properties.popupContent'].str.extract("<a href='(.+)'>")
    return df_new

def select_new_activities(df_last: pd.DataFrame, df_current: pd.DataFrame):
    assert df_last.columns.equals(df_current.columns)
    def quick_clean_df(df):
        rounding_dict = {'Longitude': 5, 'Latitude': 5}
        return df.round(rounding_dict).drop_duplicates()

    new_activities = (df_current.pipe(quick_clean_df).merge(df_last.pipe(quick_clean_df), how='left', indicator=True)
                    .query('_merge == "left_only"')
                    .drop(columns=['_merge'])
                    )
    return new_activities


def create_message(df):
    if len(df) == 1:
        subject = 'Er is 1 nieuwe excursie!'
    else:
        subject = f'Er zijn {len(df)} nieuwe excursies!'

    msg = ''
    for i, row in df.iterrows():
        msg += row['Datum'] + ' - ' + row['Titel'] + '\n'
        msg += f'Voor meer informatie, zie {row["URL"]}\n\n'

    return subject, msg

def send_email(subject, msg):
    yag = yagmail.SMTP("sjoersvogelexcursies@gmail.com")
    yag.send(
        to='sjoerdcornelissen@gmail.com',
        subject=subject,
        contents=msg, 
    )


def main():
    file_loc = r'Data\vogelexcursies.csv'

    # read current activities
    response = get_all_excursies()
    activities = select_relevant_data(response)
    # TODO: we should probably log the incoming data as well, for auditibility and debugging
    df_current = clean_data(activities).pipe(validate_df).pipe(engineer_features)
    
    # find new activities
    df_last = pd.read_csv(file_loc).pipe(validate_df)
    df_new_activities = select_new_activities(df_last, df_current)

    # email new activities
    if not df_new_activities.empty:
        subject, msg = create_message(df_new_activities)
        send_email(subject, msg)

    # Save current activities
    df_current.to_csv(file_loc, index=False)

main()
