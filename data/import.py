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
    latest = ''
    latestQuery = list(collection.order_by(u'code', direction=firestore.Query.DESCENDING).limit(1).stream())
    if len(latestQuery) > 0:
      latest = latestQuery[0].id
      print(f'[Canada] Continuing from {latest}')
    new = 0
    for row in reader:
      # Filter out median income values
      if row['GEO_LEVEL'] != '2': continue
      if row['DIM: Profile of Forward Sortation Areas (2247)'] != 'Median total income of households in 2015 ($)': continue
      FSA = row['GEO_NAME']
      if FSA <= latest: continue
      incomeStr = row['Dim: Sex (3): Member ID: [1]: Total - Sex']
      income = int(incomeStr if incomeStr != 'x' else 0)
      print(f'[Canada] Writing {FSA}...\r', end='')
      collection.document(FSA).set({
        'code': FSA,
        'income': income
      })
      new += 1
    print(f'\n[Canada] Written {new} rows')

# US ZIP Code Tabulation Areas
# Source: Table S1903, American Community Survey 2018
# https://data.census.gov/cedsci/table?g=0100000US.860000&text=S1903&tid=ACSST5Y2018.S1903&hidePreview=false&vintage=2018&layer=VT_2018_860_00_PY_D1&cid=S1903_C01_001E
def usaData():
  path = 'raw/ACSST5Y2018.S1903_data_with_overlays_2020-06-10T221947.csv'
  with open(path, encoding='utf-8') as f:
    collection = db.collection(u'postcode-income-us')
    reader = csv.DictReader(f)
    latest = ''
    latestQuery = list(collection.order_by(u'code', direction=firestore.Query.DESCENDING).limit(1).stream())
    if len(latestQuery) > 0:
      latest = latestQuery[0].id
      print(f'[USA] Continuing from {latest}')
    new = 0
    for row in reader:
      if row['NAME'][:5] != 'ZCTA5': continue
      ZCTA = row['NAME'][6:]
      if ZCTA <= latest: continue
      incomeStr = re.sub('[^0-9]', '', row['S1903_C03_001E'])
      income = int(incomeStr if incomeStr != '' else 0)
      print(f'[USA] Writing {ZCTA}...\r', end='')
      collection.document(ZCTA).set({
        'code': ZCTA,
        'income': income
      })
      new += 1
    print(f'\n[USA] Written {new} rows')

# UK Middle layer Super Output Areas
# Source: Income estimates for small areas, England and Wales
# https://www.ons.gov.uk/employmentandlabourmarket/peopleinwork/earningsandworkinghours/datasets/smallareaincomeestimatesformiddlelayersuperoutputareasenglandandwales
# Contains data from the Office for National Statistics licensed under the Open Government Licence v3.0.
def gbrData():
  path = 'raw/totalannualincome2018.csv'
  with open(path, encoding='windows-1252') as f:
    # skip first four lines
    for i in range(4):
      next(f)

    collection = db.collection(u'postcode-income-gb')
    reader = csv.DictReader(f)
    new = 0
    # set to last printed MSOA if error
    failed = None
    # failed = 'Portsmouth 007'
    if failed:
      print(f'[UK] Continuing from {failed}')
    for row in reader:
      if failed:
        if row['MSOA name'] == failed:
          failed = None
        else:
          continue
      MSOA = row['MSOA code']
      income = int(row['Total annual income (£)'].replace(',', ''))
      # print names so we know where we left off if error
      print(f'[UK] Writing {row["MSOA name"]}...\r', end='')
      collection.document(row['MSOA name']).set({
        'code': MSOA,
        'income': income
      })
      new += 1
    print(f'\n[UK] Written {new} rows')


canData()
usaData()
# !Note! Can't do partial runs since data is not sorted
gbrData()