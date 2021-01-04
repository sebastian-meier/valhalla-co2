# valhalla-co2
Using the valhalla routing service to build co2-based routing

# Pipeline

## #1 Transform OSM to textfile

```
osmium cat germany-latest.osm.pbf -o germany-latest.opl
```

## #2 Generate maxspeed

### Using Postgres (osm2pgsql) - slow but more possibilites

Generate a csv with all the maxspeeds you would like to change. I did this by using osm2pgsql with a custom style, adding this line:

```
node,way   maxspeed     text      linear
```
Note: we use text as data type. Because this attribute also contains weird speed specifications

```
osm2pgsql --create --database osm_europe --port 5432 --host localhost -U opendataservices --slim --cache 16000 -W --style /home/sebastian/Documents/GitHub/osm2pgsql.default.style --bbox=2.4609375,45.67548217560647,17.490234375,56.04749958329888  europe-latest.osm.pbf
```

Afterwards simply run and export the following query on roads:
```
SELECT maxspeed, COUNT(*) FROM osm_roads GROUP BY maxspeed ORDER BY COUNT(*) DESC
```

### Using osmium-tool - very fast but less possibilities

You need at least v1.12.0. At the time of writing this, this version was not yet available through apt-get and i, therefore, needed to build this from source. In v1.12.0 a new feature was added to osmium-tool: tags-count. This allows you to quickly count tags in very large osm.pbf files:

```
osmium tags-count -s count-desc -o maxspeed.txt europe-latest-co2.osm.pbf 'maxspeed=*'
osmium tags-count -s count-desc -o maxspeed:hgv.txt europe-latest-co2.osm.pbf 'maxspeed:hgv=*'
osmium tags-count -s count-desc -o maxspeed:advisory.txt europe-latest-co2.osm.pbf 'maxspeed:advisory=*'
osmium tags-count -s count-desc -o maxspeed:practical.txt europe-latest-co2.osm.pbf 'maxspeed:practical=*'
osmium tags-count -s count-desc -o maxspeed:backward.txt europe-latest-co2.osm.pbf 'maxspeed:backward=*'
osmium tags-count -s count-desc -o maxspeed:forward.txt europe-latest-co2.osm.pbf 'maxspeed:forward=*'
```

### Using taginfo.openstreetmap.org - very fast but incomplete

https://taginfo.openstreetmap.org/api/4/key/values?key=maxspeed&filter=all&lang=en&sortname=count&sortorder=desc&page=1&rp=999&qtype=value&format=json_pretty

## #3 Transform speed to co2 and change osm textfile

The index.py file uses co2 measuring data extracted from a study by Germany's federal environmental agency (https://www.umweltbundesamt.de/sites/default/files/medien/1410/publikationen/2020-06-15_texte_38-2020_wirkung-tempolimit_bf.pdf). This is then used to calculate new maxspeeds that will help us in the end use co2 consumption instead of time.

Those new maxspeeds are then inserted into the opl file from above.

Depending on the size of your osm file... be patient this might take a while...

## #4 Back to the beginning

```
osmium cat germany-latest.opl -o germany-latest.osm.pbf
```

## #5 Modifing the costing function in valhalla

We had to modify valhalla in several files due to hard coded parameters. We create a branch on a fork for our changes, see here: https://github.com/sebastian-meier/valhalla/tree/co2 

## #6 build valhalla

## #7 build valhalla tiles

## #8 go!