import yaml
import yagmail
import pandas as pd

class Notifier:
    def __init__(self, print=True, email=True, notify_no_activities=False):
        """
        Parameters
        ----------
        print: whether to notify by printing to console
        email: whether to notify by sending an email (see config for from and to addresses)
        notify_no_activities: whether to notify the user if there are _no_ new activities
        """
        self.print = print
        self.email = email
        self.notify_no_acitivities = notify_no_activities

    def create_message(self, df: pd.DataFrame):
        """
        Create subject and message to notify user with

        Parameters
        ----------
        df: the DataFrame with the Datum, Titel and URL of the new activities
        
        Returns
        -------
        subject: header of the message
        msg: a message based on the new activities
        """
        if len(df) == 1:
            subject = 'Er is 1 nieuwe excursie!'
        else:
            subject = f'Er zijn {len(df)} nieuwe excursies!'

        msg = ''
        for i, row in df.iterrows():
            msg += row['Datum'] + ' - ' + row['Titel'] + '\n'
            msg += f'Voor meer informatie, zie {row["URL"]}\n\n'

        return subject, msg

    def print(self, subject: str, msg: str):
        """Notify by printing to console"""
        print(subject)
        print(msg)

    def send_email(self, subject: str, msg: str):
        """Notify by sending an email"""
        with open("config.yaml", "r") as stream:
            try:
                config = (yaml.safe_load(stream))
            except yaml.YAMLError as exc:
                print(exc)

        email_from = config['email-from']
        email_to = config['email-to']
        yag = yagmail.SMTP(email_from)
        yag.send(
            to=email_to,
            subject=subject,
            contents=msg, 
        )
    
    def notify(self, df: pd.DataFrame):
        """
        Notify user as desired

        Parameters
        ----------
        df: the DataFrame containing the new activities
        
        """
        if not self.notify_no_acitivities and df.empty:
            return
        
        subject, msg = self.create_message(df)
        if self.print:
            self.print(subject, msg)
        if self.email:
            self.send_email(subject, msg)
