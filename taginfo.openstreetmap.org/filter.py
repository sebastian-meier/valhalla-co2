import json

speeds = []
csv = 'maxspeed'
road_types = { 'country':[], 'types':[] }
  
# Opening JSON file 
with open('maxspeed.json') as json_file: 
  data = json.load(json_file) 

  for speed in data['data']:
    if speed['count'] > 10 and speed['value'].find('mph') == -1 and speed['value'].find('knots') == -1:
      if (speed['value'].find(':rural') != -1 or 
          speed['value'].find(':urban') != -1 or 
          speed['value'].find(':living_street') != -1 or 
          speed['value'].find(':motorway') != -1 or 
          speed['value'].find(':trunk') != -1 or 
          speed['value'].find(':walk') != -1):

        el = speed['value'].split(':')
        if el[0] not in road_types['country']:
          road_types['country'].append(el[0])
        if el[1] not in road_types['types']:
          road_types['types'].append(el[1])
      else:
        speeds.append([speed['value'], speed['count']])
        csv += '\n' + speed['value']

  with open('maxspeed-filter.json', 'w') as fp:
    json.dump(speeds, fp)
  with open('data-new.csv', 'w') as fp:
    fp.write(csv)
  with open('maxspeed-types.json', 'w') as fp:
    json.dump(road_types, fp)