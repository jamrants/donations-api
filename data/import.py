import csv
import re
import firebase_admin
from firebase_admin import credentials
from firebase_admin import firestore

# Use a service account
cred = credentials.Certificate('serviceAccount.key.json')
firebase_admin.initialize_app(cred)
db = firestore.client()

# Canada FSAs
# Source: Census Profile, 2016 Census, Statistics Canada
# https://www12.statcan.gc.ca/census-recensement/2016/dp-pd/prof/details/download-telecharger/comp/page_dl-tc.cfm?Lang=E
def canData():
  path = 'raw/98-401-X2016046_English_CSV_data.csv'
  with open(path, encoding='utf-8-sig') as f:
    collection = db.collection(u'postcode-income-ca')
    reader = csv.DictReader(f)
    for row in reader:
      # Filter out median income values
      if row['GEO_LEVEL'] != '2': continue
      if row['DIM: Profile of Forward Sortation Areas (2247)'] != 'Median total income of households in 2015 ($)': continue
      FSA = row['GEO_NAME']
      incomeStr = row['Dim: Sex (3): Member ID: [1]: Total - Sex']
      income = int(incomeStr if incomeStr != 'x' else 0)
      collection.document(FSA).set({
        'code': FSA,
        'income': income
      })

# US ZIP Code Tabulation Areas
# Source: Table S1903, American Community Survey 2018
# https://data.census.gov/cedsci/table?g=0100000US.860000&text=S1903&tid=ACSST5Y2018.S1903&hidePreview=false&vintage=2018&layer=VT_2018_860_00_PY_D1&cid=S1903_C01_001E
def usaData():
  path = 'raw/ACSST5Y2018.S1903_data_with_overlays_2020-06-10T221947.csv'
  with open(path, encoding='utf-8') as f:
    collection = db.collection(u'postcode-income-us')
    reader = csv.DictReader(f)
    for row in reader:
      if row['NAME'][:5] != 'ZCTA5': continue
      ZCTA = row['NAME'][6:]
      incomeStr = re.sub('[^0-9]', '', row['S1903_C03_001E'])
      income = int(incomeStr if incomeStr != '' else 0)
      collection.document(ZCTA).set({
        'code': ZCTA,
        'income': income
      })

canData()
usaData()