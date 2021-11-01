import pandas as pd
import yaml

class ActivityDetector:

    def find_known_excursions(self) -> pd.DataFrame:
        """ Find the known excursions"""
        with open("config.yaml", "r") as stream:
            try:
                config = (yaml.safe_load(stream))
            except yaml.YAMLError as exc:
                print(exc)
        file_loc = config['location-known-excursions']
        try:
            df = pd.read_csv(file_loc)
        except FileNotFoundError:
            df = pd.DataFrame()
        return df
    
    def find_new_activities(self, df_current: pd.DataFrame) -> pd.DataFrame:
        """
        Find the new excursions

        By comparing the current excursions to the last saved DataFrame
        """
        def quick_clean_df(df):
            rounding_dict = {'Longitude': 5, 'Latitude': 5}  # make sure the match does not fail on float imprecision
            return df.round(rounding_dict).drop_duplicates()

        df_known = self.find_known_excursions().pipe(quick_clean_df)
        df_current = df_current.pipe(quick_clean_df)
        new_activities = (df_current.merge(df_known, how='left', indicator=True)
                        .query('_merge == "left_only"')
                        .drop(columns=['_merge'])
                        )
        return new_activities

