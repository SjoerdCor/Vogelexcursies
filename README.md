# Vogelexcursie
 A script to periodically poll the site of the [Dutch Vogelbescherming](www.vogelbescherming.nl) for new excursions.

 The Vogelbescherming (an organisation for the preservation of bird-life) sometimes organises bird watching excursions. However, these fill up quickly, because of the popularity, relatively small group sizes and low costs. Since I do not want to miss out, I wrote a python script that pulls the current activity from the website and notifies me whenever there are new activities. The notification happens by sending an email. 

 ## Installation
 This directory contains `find_new_vogelexcursies.bat`, which can then be run by Windows Task Scheduler periodically. If you need help on Windows Task Scheduler, see for instance [this StackOverflow question](https://stackoverflow.com/questions/4437701/run-a-batch-file-with-windows-task-scheduler). See `config.yaml` and edit appropriately for the email adresses that are used to send and receive the notifications.
