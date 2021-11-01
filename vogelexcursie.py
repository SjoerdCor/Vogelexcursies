
import datacollector
import activitydetector
import notifier

def main():
    dc = datacollector.DataCollector()
    df_current = dc.collect_current_excursions()

    ad = activitydetector.ActivityDetector()
    df_new = ad.find_new_activities(df_current)

    nf = notifier.Notifier()
    nf.notify(df_new)

    dc.save_current_excursions(df_current)

main()
