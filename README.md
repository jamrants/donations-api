# donations-api

## Data

Raw postcode-level median household gross income data (Canadian FSAs/American ZCTAs) used in [jamrants/donations](https://github.com/jamrants/donations) can be found in the `data` directory.
Canadian data is sourced from the 2016 Census and American data from the 2018 American Community Survey.

Place a Google service account key in `data/serviceAccount.key.json` with permission to write to Firestore and run `import.py` from `data` to import the dataset into a new Firebase project.
Since there are more than 20,000 records, if using the free plan, importing will have to be split over multiple days.
The script will automatically continue from previous runs.
