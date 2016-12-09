import os
import math
import pandas as pd
import matplotlib.pyplot as plt; plt.rcdefaults()
import numpy as np
import re

reviews_file_path = '../data/reviews_with_gender.csv'
business_file_path = '../data/businesses.csv'

reviews = pd.read_csv(reviews_file_path)
businesses = pd.read_csv(business_file_path)
print reviews.head(1)
print '-----------------------------------------'
print businesses.head(1)
print '-----------------------------------------'
pd.set_option('display.max_colwidth', -1)

business_to_location = {}
for index, row in businesses.iterrows():
	name = re.search(r'biz/(.*)\?', row['url']).group(1)
	if 'coordinate' in row and isinstance(row['coordinate'], str):
		location = row['coordinate'].split(',')
		business_to_location[name] = location

user_reviews = {}
for index, row in reviews.iterrows():
	users_reviews = user_reviews.get(row['user id'], [])
	users_reviews.append(row)
	user_reviews[row['user id']] = users_reviews

print len(user_reviews)
users_average_location = {}
for key in user_reviews.keys():
	if len(user_reviews[key]) < 5: continue
	coords = [business_to_location[row['business']] for row in user_reviews[key]]
	avg_lat = sum([float(coord[0]) for coord in coords]) / float(len(coords))
	avg_lon = sum([float(coord[1]) for coord in coords]) / float(len(coords))
	users_average_location[key] = (key,str(avg_lat), str(avg_lon))


with open('user_locations.csv', 'w') as f:
	f.write('user_id,lat,lon\n')
	for key in users_average_location.keys():
		f.write(','.join(users_average_location[key]) + '\n')


