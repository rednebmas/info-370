### SNAK Final Project Repo

* **businesses.csv** (7673 rows): business data
* **reviews.csv** (277070 rows): csv version of reviews.json (I believe the only feature missing is the text content of the reviews.. Omitted because we aren't really using it)
* **merged_table.csv** (274826 rows): is just a natural join of the businesses.csv file and the reviews.csv file
* **breakout_by_category.csv** (1072987 rows): is the merged_table.csv except I split the "categories" feature and wrote a record for each category
