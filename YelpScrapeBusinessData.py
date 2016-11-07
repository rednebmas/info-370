import requests
import os, re
from bs4 import BeautifulSoup
import pandas as pd
import numpy as np
from numpy import random as rnd
import time
import pickle as pkl
import json

"""
##############################################################################################################################
INPUT:
    1. SanDiego_biz_collection.csv -- contains all of the businesses scraped from Yelp using their API.
OUTPUT:
    1. pickled_biz_data.pkl -- scraped data that's saved along the way
    2. SanDiego_biz_addendum.csv -- if successful then scraped data is saved into this csv file.
    3. count.txt -- keeps track of the number of pages processed. 
    4. biz_reviews_collection.txt -- the collection of business reviews from the scraped websites.
##############################################################################################################################
DESCRIPTION:
    The URLs for all of the businesses we are interested in have been acquired and are stored in the INPUT file. This code
    goes through the unique business URLs and scrapes the information that Yelp did not provide through their API, such as
    a. price range
    b. opening-closing hours
    c. reviews and related user IDs
    d. ...etc   
##############################################################################################################################
"""

#################################### 0. SETUP ##################################################
data_path='/data'
print(os.path.dirname(os.path.realpath(__file__)))
os.chdir(os.path.dirname(os.path.realpath(__file__)) + data_path)

businesses_file_path = 'Seattle_businesses.csv' 
api_data=pd.read_csv(businesses_file_path, encoding='latin-1')
api_data=api_data[~(api_data.categories.isnull())]

food_list=['restaurant','grill','bar','cafe','bakery','pub','bbq','sushi','coffee',
'food','eat','food truck','juice','drinks', 'tea', 'deli', 'seafood', 'cajun', 'icecream',
'brunch', 'lunch', 'dinner', 'breakfast', 'bars', 'sandwiches', 'fast food', 'pizza', 'sandwiches',
'buffet', 'mediterrenean', 'bakeries', 'steak', 'divebar', 'mexican','italian', 'hawaiian', 'french', 
'dessert', 'yogurt', 'korean', 'bagels','asian fusion', 'chinese', 'soup', 'vegan', 'vegetarian', 'burgers']
food_str="|".join(food_list)

shop_list=['shop', 'shopping', 'candy store', 'candy', 'store','beer, wine & spirits', 'wine' ]
shop_str="|".join(shop_list)

food_data=api_data[api_data.categories.str.contains(food_str)]; food_data.reset_index(inplace=True, drop=True)
shopping_data=api_data[api_data.categories.str.contains(shop_str)]; shopping_data.reset_index(inplace=True, drop=True)
################################################################################################
##################################### 1. FUNCTIONS ############################################# 

############################### I. Scraping Functions ###############################
def fetch_website(url):
    """
    To hide that the scraping is being done via Python, I change the user-agent to a Firefox
    browser so that Yelp believes it is a chrome browser accessing them. Hope it works.
    """
    user_agent={'User-agent':'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/52.0.2725.0 Safari/537.36'}
    r=requests.get(url, headers=user_agent)
    try:
        print("Accessed and downloaded URL data")
        return(r.content)
    except ConnectionError:
        print("Incurred the infamous connection error")
        print("Skipping this url")
        return("Skip")

########################## II. Processing Functions ################################## 
def check_empty(s_result):
    if s_result is None:
        return(np.nan)
    else:
        return(s_result.getText())
        
    
def extract_data(response, url):
    """INPUT: response -- the data given by response.content() from Requests module.
    OUTPUT: 1. data_dict -- the data dictionary of desired data.
            2. appended reviews file. See [append_reviews_txt()]
    EXTERNAL function"""
    print(url)
    data_dict={}
    data_dict['url']=[url]
    soup=BeautifulSoup(response, "html.parser")
    
    #Price Range:
    data_dict['priceRange']=[check_empty(soup.find('span', class_='business-attribute price-range'))]
    
    #Hours:
    hour_table=soup.find('table', class_="table table-simple hours-table")
    if hour_table is not None:
        days=[day.getText() for day in hour_table.findAll('th')]
        hours=[str.strip(row.text) for row in hour_table.findAll('td') if len(str.strip(row.text))!=0]
        hours=[x for x in hours if re.search('\d', x)]
        if len(days)==len(hours):
            entry=["~".join([d,h]) for (d, h)in zip(days, hours)]
            entry=", ".join(entry)
            data_dict['hours']=entry
        if len(days)!=len(hours):
            print("\nMismatch in number of days and hours open! " + str(hours) + ", " + str(days))
            data_dict['hours']=[', '.join(["~".join([d,h]) for (d, h)in zip(days, hours)])]

    if hour_table is None:
        print("Couldn't find the business hours")
        data_dict['hours']=[np.nan]
    
    #Business Info:
    info_table=soup.find('div', class_='short-def-list') 
    if info_table is not None:
        fields=info_table.findAll('dl')
        entry=[":".join([str.strip(field.find("dt").getText()), str.strip(field.find("dd").getText())]) for field in fields]
        data_dict['more_info']=", ".join(entry)
        
    if info_table is None:
        print("Couldn't find [More Business Info] section")
        data_dict['more_info']=[np.nan]

        
    #Reviews Info:
    print("looking for reviews")
    print()
    print()
    print()
    # print(soup)
    review_text = soup.find('span', itemprop='reviewCount')
    if review_text is not None:
        data_dict['num_reviews']=int(soup.find('span', itemprop='reviewCount').getText()) #new line
    Master_reviews_list=soup.findAll("div", class_='review review--with-sidebar')
    list_reviewsList = None
    num_review_pages = 0
    if review_text is not None:
        num_review_pages = re.search(r'\d+ of (\d+)', soup.find("div", class_='page-of-pages arrange_unit arrange_unit--fill').getText()).group(1)
        num_review_pages = int(num_review_pages)
    print("num_review_pages: " + str(num_review_pages))
    if num_review_pages > 1:
        review_links=[url + "&start=" + str(x) for x in range(2, num_review_pages + 1)]
        print("len of review_links: " + str(len(review_links)))
        rev_soup_list=[BeautifulSoup(fetch_website(url)) for url in review_links]
        list_reviewsList=[rev_soup.findAll("div", class_='review review--with-sidebar')[1:] for rev_soup in rev_soup_list]  
        for reviewsList in list_reviewsList:
            Master_reviews_list.extend(reviewsList)
            
    if Master_reviews_list is not None:
        #data_dict['num_reviews_recorded']=len(reviews_list)
        
        to_dump=[]
        #get review items
        for review in Master_reviews_list:
            # print(review)

            review_author=review.find('a', class_='user-display-name')
            if review_author is None:
                # yelp bought a company called qype and has integrated their reviews, but the regular soup.find will not work
                # for the qype ghost user
                review_author = review.find('span', class_='ghost-user ghost-qype-user').string
            else:
                review_author=review_author.string
            review_auth_id=review.attrs['data-signup-object']
            review_auth_location=str.strip(review.find('li', class_='user-location').getText())
            review_date=review.find('span', class_='rating-qualifier').getText().strip()
            review_stars=re.search(r'\d',''.join(review.find('i', class_='star-img').attrs['class'])).group()
            review_text=str.strip(review.find('p').getText())
            to_dump.append({'author':review_author, 
            'id':review_auth_id,
            'location':review_auth_location,
            'date': review_date,
            'stars':review_stars,
            'text':review_text} )
        reviews={url:to_dump}
        append_reviews_txt(reviews)
            
    print(str(len(to_dump)) + " reviews found")

    #Overall Output:
    print()
    return(data_dict)
    
def append_reviews_txt(reviews):
    """INPUT: reviews -- review text and data in dictionary/json format 
        scraped from the website. 
       OUTPUT: appended file created in [make_json()].
    INTERNAL function"""
    with open('biz_reviews_collection.json', 'a') as f:
        f.write(",")
        json.dump(reviews, f, indent=2)
       
def process_dict(data_dict):
    """INPUT: data_dict -- contains the keys as columns and values as data frame values.
    OUTPUT: pd.DataFrame containing the scraped data
    EXTERNAL function """
    len_list=[len(data_dict[key]) for key in data_dict.keys() if data_dict[key] is list]
    #print("--"*20)
    if all([item==len_list[0] for item in len_list]):
        #print("Making data frame using the data dictionary")
        df=pd.DataFrame(data_dict).drop_duplicates()
        #df.to_csv(csv_name, index=False)
        #print("\nData saved to: %s" %csv_name)
    else:
        print("Data length in keys are not of the same length")
        print(data_dict.keys())
        print(len_list)
        df=None
    return(df)        
        
def append_df(df, biz_df="Seattle_biz_addendum.csv"):
    """INPUT: df -- the output of [process_dict()] or a pd.DataFrame with aligned columns. 
    OUTPUT: df -- updated biz_df
    DESCRIPTION: This function reads biz_df and appends it with new results.
    EXTERNAL function"""
    try:
        update_df=pd.read_csv(biz_df)
    except UnicodeDecodeError:
        update_df=pd.read_csv(biz_df, encoding='latin-1')
    except FileNotFoundError:
        # hacky...
        update_df = df
    try:
        updated_df=pd.concat([update_df.sort(axis=1), df.sort(axis=1)], axis=0)
        updated_df.to_csv(biz_df, index=False)
        print("--"*30)
        print("%s updated" %biz_df)
        print("=="*30)
        return(updated_df)
    except:
        print("Couldn't create the DataFrame, there must be an error of some type")   
        
############################ III. Convenience Functions ################################            
def make_json(file_name='biz_reviews_collection.json'):
    """file_name -- the file where scraped reviews will be saved.
    EXTERNAL function. """
    if os.path.isfile(file_name)==False:
        with open(file_name, 'w') as f:
            json.dump('', f)
        
def make_update_df(data_dict, file_name="Seattle_biz_addendum.csv"):
    empty_data_dict={}
    for key in data_dict.keys():
        empty_data_dict[key]=[]
    pd.DataFrame(empty_data_dict).to_csv(file_name, index=False) 
    
def Pickle(data,file_name='business_addendum.pkl'):
        with open(file_name, 'wb') as f:
            pkl.dump(data, f)
        print("Downloaded JSON data pickled to [%s]" %file_name)    
def eat_pickle(file_name='business_addendum.pkl'):
    with open(file_name, 'rb') as f:
        return(pkl.load(f))        

def write_count(count):
    with open('Count_GENE.txt', 'w') as the_file:
        the_file.write(str(count))
 
def read_count(file_name='Count_GENE.txt'):
    with open(file_name) as f:
        count=f.readline()
        return(int(count))    
        
def counter_reset():
    answer='the cake is a lie!'
    while (answer!='Y') & (answer!='N'):
        answer=input("Would you like to reset the counter to 0? [Y/N]: ")
    if answer == "Y":    
        write_count(0)
        print("Counter reset")      

def step_display(i):
    if i%50==0:
        print("On number: %s" %i)

def wait():
    wait_time=int(rnd.uniform(low=2,high=7))
    print("\nPausing for: %d seconds..." %wait_time)
    time.sleep(wait_time)
    #print('seconds: [%d%%]\r' %seconds_elapsed)
    print("--"*20)        
        
#######################################################################################        
########################### IV. MAIN Function ########################################
def main():
    make_json(file_name='biz_reviews_collection.json')
    counter_reset()
    count=read_count()
    
    try:
        api_data=pd.read_csv(businesses_file_path)[count:] #needs to change in order to accommodate for different categories.
    except UnicodeDecodeError:
        api_data=pd.read_csv(businesses_file_path, encoding='latin-1')[count:]
        
    for (i,url) in zip(api_data.index.tolist(),api_data.url.tolist()):
        print(time.ctime())
        print("--"*20)
        step_display(i)
        response=fetch_website(url)
        Pickle(response)
        if response=='Skip':
            pass
        if response !='Skip':
            data_dict=extract_data(response, url)
            biz_df=process_dict(data_dict)
            append_df(biz_df)

        #if response == 'Error':
        #    print("Error occurred in fetching website content. Loop is terminated")
        #    break
        #end of it
        write_count(i)
        wait()

if "__main__"==__name__:
    main()
