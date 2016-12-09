import os
import math
import pandas as pd
import matplotlib.pyplot as plt; plt.rcdefaults()
import numpy as np
import re
from datetime import datetime
from scipy.stats import ttest_ind

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
	# row['date'] = datetime.strptime(row['date'], '%Y-%m-%d')
	row['date'] = datetime.strptime(row['date'], '%m/%d/%Y')
	users_reviews = user_reviews.get(row['user id'], [])
	users_reviews.append(row)
	user_reviews[row['user id']] = users_reviews

# sort reviews
for key in user_reviews.keys():
	reviews = user_reviews[key]
	reviews = sorted(reviews, key=lambda review: review['date'])
	user_reviews[key] = reviews

x_user_num_reviews = []
y_user_review_avg = []
for key in user_reviews.keys():
	reviews = user_reviews[key]
	# if len(reviews) < 10: continue
	avg_rating = sum([float(r['stars']) for r in reviews]) / float(len(reviews))
	x_user_num_reviews.append(len(reviews))
	y_user_review_avg.append(avg_rating)


below_ten_reviews_ratings = []
above_ten_reviews_ratings = []
min_reviews = 50
for key in user_reviews.keys():
	reviews = user_reviews[key]
	if len(reviews) <= min_reviews: 
		for r in reviews: below_ten_reviews_ratings.append(r['stars'])
	else:
		for r in reviews: above_ten_reviews_ratings.append(r['stars'])

t, p = ttest_ind(below_ten_reviews_ratings, above_ten_reviews_ratings)
below_ten_avg = float(sum(below_ten_reviews_ratings)) / float(len(below_ten_reviews_ratings))
above_ten_avg = float(sum(above_ten_reviews_ratings)) / float(len(above_ten_reviews_ratings))
print 'below ' +str(min_reviews)+ ' avg: ' + str(below_ten_avg)
print 'above '+str(min_reviews)+' avg: ' + str(above_ten_avg)
print 't: ' + str(t) + ', p: ' + str(p)
print 'len of above: ' + str(len(above_ten_reviews_ratings))
print 'len of below: ' + str(len(below_ten_reviews_ratings))


print 'plotting'
# plt.scatter(y_user_review_avg, x_user_num_reviews)
# plt.xlabel('User average review rating')
# plt.ylabel('Number of reviews')
# plt.show()


# with open('user_locations.csv', 'w') as f:
# 	f.write('user_id,lat,lon\n')
# 	for key in users_average_location.keys():
# 		f.write(','.join(users_average_location[key]) + '\n')


