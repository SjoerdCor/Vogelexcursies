
import json
import ast

import pandas as pd    
import requests
import yaml


class DataCollector:

    def get_raw_data(self):
        """ Get raw data about excursions from vogelbescherming online"""
        url = 'https://www.vogelbescherming.nl/?act=excursies.json&&type=Excursie&'
        response = requests.get(url)
        return response

    def _select_relevant_data(self, response: bytes):
        """
        Select the JSON with excursies from the response
        
        The response is a bytestring with a js dictionary. Read only the relevant values, which is a json that
        can be read into pandas

        Parameters
        ----------
        response: bytes that are returned from vogelbescherming.nl

        Returns
        -------

        activities: json that has an entry for each excursion
        """

        data = response.content.decode('UTF-8').strip('var kaartpunten = ')
        activities = ast.literal_eval(data)['features']
        return activities

    def _clean_data(self, activities) -> pd.DataFrame:
        """
        Transforms json into dataframe that is easily manipulated
        """
        df = pd.json_normalize(activities)
        df['geometry.coordinates'] = df['geometry.coordinates'].apply(tuple)
        return df

    def _engineer_features(self, df: pd.DataFrame) -> pd.DataFrame:
        """ 
        Extract relevant features from excursion DataFrame

        Loses the JSON prefixes, and splits the text into relevant features
        """
        df_new = df[[]].copy()
        df_new['ID'] = df['properties.customID']
        df_new['Longitude'] = df['geometry.coordinates'].apply(lambda x: x[0])
        df_new['Latitude'] = df['geometry.coordinates'].apply(lambda x: x[1])
        
        df_new['Titel'] = df['properties.popupContent'].str.extract('^<strong>(.+)</strong>')
        # TODO: parse Datum as date
        df_new['Datum'] = df['properties.popupContent'].str.extract('Excursie<br />(.+)<br />')
        
        base_url = 'https://www.vogelbescherming.nl'
        df_new['URL'] = base_url + df['properties.popupContent'].str.extract("<a href='(.+)'>")
        # TODO: add number of available spots
        return df_new

    def save_current_excursions(self, df: pd.DataFrame) -> None:
        """
        Writes dataframe to config for future comparison
        """
        with open("config.yaml", "r") as stream:
            try:
                config = (yaml.safe_load(stream))
            except yaml.YAMLError as exc:
                print(exc)

        df.to_csv(config['location-known-excursions'], index=False)

    def collect_current_excursions(self):
        """
        Collect all current excursions from the vogelbescherming
        """
        response = self.get_raw_data()
        activities = self._select_relevant_data(response)
        df = (self._clean_data(activities)
                  .pipe(self._engineer_features)
            )
        return df
