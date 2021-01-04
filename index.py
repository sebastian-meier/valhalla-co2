import numpy as np
import matplotlib.pyplot as plt
import csv
import os

maxspeed = []

with open('data-new.csv', newline='') as csvfile:
  reader = csv.reader(csvfile, delimiter=',')
  for row in reader:
    if row[0] not in ('maxspeed', 'no', 'default',  'national', 'variable', 'implicit', 'unposted', 'unknown', 'fixme', 'signals', 'Signal', 'variable', 'maxspeed:forward', 'Zs 3 "10" am Signal 55 ZS5', 'NULL', '-1', '0'):
      value = 0
      if (row[0].lower() == 'none'):
        value = '180'
      elif ('trunk' in row[0].lower()):
        value = '100'
      elif ('motorway' in row[0].lower()):
        value = '180'
      elif ('urban' in row[0].lower()):
        value = '50'
      elif ('rural' in row[0].lower()):
        value = '100'
      elif ('walk' in row[0].lower() or 'zone30' in row[0].lower() or 'zone:30' in row[0].lower()):
        value = '30'
      elif ('living_street' in row[0].lower()):
        value = '30'
      elif (';' in row[0]):
        value = row[0].split(';')[0]
      elif ('-' in row[0]):
        value = row[0].split('-')[0]
      elif (',' in row[0]):
        value = row[0].split(',')[0]
      elif ('|' in row[0]):
        value = row[0].split('|')[0]
      else:
        value = row[0]

      value = value.replace('>', '')
      value = value.replace('km/h', '')
      value = value.replace('km', '')
      value = value.replace('<', '')

      if float(value) > 180:
        value = 180

      maxspeed.append([row[0], float(value)])

maxspeed.sort(reverse=True, key=lambda speed: speed[1])

graph = {
  "<50":{
    "values":[
      [87.886, 59.676],
      [31.353, 44.107],
      [26.942, 40.805],
      [11.948, 23.189],
      [9.998, 8.908],
      [108.355, 59.688],
      [125.082, 58.174],
      [135.713, 63.134],
      [141.362, 57.208]
    ],
    "ref":{
      "width": 145.277,
      "height": 86.147,
      "x": [0,80],
      "y": [0,450],
    }
  },
  ">80":{
    "values": [
      [2.593, 56.872],
      [27.838, 54.159],
      [54.168, 49.024],
      [68.116, 45.188],
      [81.657, 39.655],
      [99.527, 33.211],
      [107.774, 29.670],
      [112.149, 23.316],
      [131.941, 17.166],
      [133.771, 14.296]
    ],
    "ref":{
      "width": 145.277,
      "height": 86.147,
      "x": [80,190],
      "y": [0,400],
    }
  }
}

def reverse (value, ref):
  x = value[0] / ref["width"] * (ref["x"][1] - ref["x"][0]) + ref["x"][0]
  y = (ref["height"] - value[1]) / ref["height"] * (ref["y"][1] - ref["y"][0]) + ref["y"][0]
  return [x, y]

ax = []
ay = []

for key in graph:
  for index in range(len(graph[key]["values"])):
    graph[key]["values"][index] = reverse(graph[key]["values"][index], graph[key]["ref"])

  ax = ax + list(map(lambda x: x[0], graph[key]["values"]))
  ay = ay + list(map(lambda y: y[1], graph[key]["values"]))

x = np.array(ax)
y = np.array(ay)

coefficients = np.polyfit(x, y, 4) # depending on your data test the degree

poly = np.poly1d(coefficients)

new_x = np.linspace(np.min(x), np.max(x))

new_y = poly(new_x)

plt.plot(x, y, "o", new_x, new_y)

plt.xlim([np.min(x) - 1, np.max(x) + 1 ])

plt.savefig("line.jpg")

maxco2 = []

for speed in maxspeed:
  maxco2.append(poly(speed[1]))

with open('data-output.csv', 'w', newline='') as csvfile:
  writer = csv.writer(csvfile, delimiter=',')
  for index in range(len(maxco2)):
    writer.writerow([maxspeed[index][0], round(60/maxco2[index]*100)]) # 60 / speed * distance > time


speed_types = ['', ':hgv', ':advisory', ':practical', ':backward', ':forward']

sed_str = ''

for speed_type in speed_types:
  print(speed_type)
  for index in range(len(maxco2)):
    maxspeed[index][0] = maxspeed[index][0].replace('km/h', 'km\/h')
    sed_str += ' -e \'/maxspeed{}={}/ s//maxspeed{}=_{}/g\''.format(speed_type, maxspeed[index][0], speed_type, int(round(60/maxco2[index]*100)))

os.system('sed -i{} /media/data/osm/europe-latest/europe-latest-co2.opl'.format(sed_str))

print('final')
sed_str = ''
for speed_type in speed_types:
  sed_str += ' -e \'/maxspeed{}=_/ s//maxspeed{}=/g\''.format(speed_type, speed_type)
os.system('sed -i{} /media/data/osm/europe-latest/europe-latest-co2.opl'.format(sed_str))
