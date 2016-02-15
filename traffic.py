import fiona
import geohash
import pandas as pd
import matplotlib.pyplot as plt


print(geohash.encode(1, 2))


def enc_hash(long_lat):
    return geohash.encode(longitude=long_lat[0], latitude=long_lat[1], precision=8)


def enc_coord(geometry):
    if geometry['type'] == 'LineString':
        return [enc_hash(line) for line in geometry['coordinates']]
    elif geometry['type'] == 'MultiLineString':
        return [enc_hash(line) for lines in geometry['coordinates'] for line in lines]
    else:
        print(geometry['type'])


def segments_geohash():
    segments = {}
    with fiona.collection('Street_Segments/Street_Segments.shp') as f:
        print(len(f))
        for ind, point in enumerate(f):
            # print(point)
            seg_id = point['properties']['STREETSEGI']
            segments[seg_id] = enc_coord(point['geometry'])
        return segments
        # print(ind, point['geometry'])
        # print(geom.shape(point['geometry']))


# print(list(segments.values())[1:3])

segs = segments_geohash()

crash = pd.read_csv('Vehicular_Crash_Data.csv')

print(crash.head())
print(crash.columns.tolist())
print(crash.shape)


def dayofweek(day):
    day = day.lower()
    if 'mon' in day:
        return 0
    if 'tue' in day:
        return 24
    if 'wed' in day:
        return 24 * 2
    if 'thu' in day:
        return 24 * 3
    if 'fri' in day:
        return 24 * 4
    if 'sat' in day:
        return 24 * 5
    if 'sun' in day:
        return 24 * 6


crash['hour'] = crash['MILITARYTIME'] // 100
crash['day_of_week'] = crash['DAYOFWEEK'].apply(dayofweek)
crash['day_hour'] = crash['day_of_week'] + (crash['MILITARYTIME'] // 100)
crash['month'] = crash['ACCIDENTDATE'].str.split('-')[1]

print(crash.groupby(['DAYOFWEEK', 'hour']).size())
print(crash.groupby('day_hour').size())

plt.interactive(False)

crash.groupby('day_hour').size().plot()
# plt.show()

crash['geohash'] = crash[['LATITUDE', 'LONGITUDE']].apply(lambda x: enc_hash(x), axis=1)
crash_list = crash['geohash'].value_counts().sort_values(ascending=False).head(50)
print(crash_list.index.tolist())
print(crash.index.tolist())
crash_list.plot(kind='bar')
plt.show()

moving = pd.read_csv('Moving_Violations_Summary_for_2015.csv')
moving['geohash'] = moving['STREETSEG'].apply(lambda x: segs.get(int(x), [' ']))
mask = moving['geohash'] != ' '
geohash_df = moving[mask]['geohash'].apply(pd.Series, 1).stack()
ticket_list = geohash_df.value_counts().sort_values(ascending=False).head(50)
print(ticket_list)
ticket_list.plot(kind='bar')
plt.show()
