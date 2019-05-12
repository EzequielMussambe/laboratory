# Lab 11: Webscraping to Webmapping
# This lab was created by Kyle Redican and Ashton Shortridge 4/3/2019
# Utilizing the basic code from: https://medium.com/@msalmon00/web-scraping-job-postings-from-indeed-96bd588dcb4b

# Lets get started
# IN YOUR KONSOLE (Not in python yet)
#present your working directory
#pwd
# Change working directory to your Lab 11 folder
#cd (/home/425mussa/Desktop/lab11/)

#Did it change it to the right place?
#pwd

# Loading our python module
# Due to the complexity of python and libraries/ packages we (Jim) had to set up a specific module for the GEO 425 lab
# To be able to run the code you need to load this specific GEO 425 module
#module load geo425

#start up python
#python
# Version should be 3.7.1 
#notice how >>> replaced the $, this means you are in python

#Lets start by importing the libraries and packages we will be using
import requests
import bs4
from bs4 import BeautifulSoup
import pandas as pd
import time
import folium
import folium.plugins
from folium.plugins import MarkerCluster
import os
import random
from random import uniform

##Basic commands
# Identify your URL
# In this case we are looking at indeed (job posting company) for GIS jobs
# Notice how the l= does not have anything behind it, this is because there is not location defined yet
URL = "http://www.indeed.com/jobs?q=GIS&l="
#conducting a request of the stated URL above:
page = requests.get(URL)
#specifying a desired format of "page" using the html parser - this allows python to read the various components of the page, rather than treating it as one long string.
soup = BeautifulSoup(page.text, "html.parser")
#printing soup in a more structured tree format that makes for easier reading
print(soup.prettify())

#Setting up our key variables for the web-scrapper
# This one refers to the max number of results per city
max_results_per_city = 50
# This creates a list of the cities you want to look at
# Notice how there is + in all the spaces?
# This is due to how the url defines location after the l= part
city_set = ["Grand+Rapids,+MI", "Lansing,+MI", "Detroit,+MI", "Indianapolis,+IN", "Fort+Wayne,+IN", "Chicago,+IL", "Columbus,+OH"]
# Defining the columns of what we want to pull off of the website
# Start is the starting number added to the url in each iteration
# City is the name from the city_set list
# job_title is the title of the job_post
# company_name is the name of the company
# location is the location
# salary is salary
# summary is the summary provided in the job description
columns = ["start", "city", "job_title", "company_name", "location", "salary", "summary"]
# creating a pandas dataframe with the columns
sample_df = pd.DataFrame(columns = columns)


# Here is the loop that pulls out all of the key parts
# For detailed information about the aspects of this looping code that pulls please see you lab instructions
for city in city_set:
  for i in range(0, max_results_per_city, 10):
    page = requests.get('https://www.indeed.com/jobs?q=GIS&l=' + str(city) + '&radius=0'+'&start=' +str(i))
    time.sleep(1)  #ensuring at least 1 second between page grabs
    soup = BeautifulSoup(page.text, "lxml", from_encoding="utf-8")
    for div in soup.find_all(name="div", attrs={"class":"row"}): 
      sponsered = div.find_all(name="span", attrs={"class":" sponsoredGray "}) 
      if len(sponsered)== 0:
    #specifying row num for index of job posting in dataframe
        num =(len(sample_df) + 1) 
    #creating an empty list to hold the data for each posting
        job_post = [] 
    #append start value
        job_post.append(i) 
    #grabbing job title
        job_post.append(city)
        #job_post.append(str(start)) 
    #grabbing Job Title    
        a = div.find_all(name="a", attrs={"data-tn-element":"jobTitle"})
        if len(a) > 0:
          for a in div.find_all(name="a", attrs={"data-tn-element":"jobTitle"}):
            job_post.append(a["title"])
        else:
          for a in div.find_all(name="a", attrs={"data-tn-component": "organicJob"}):
            job_post.append(a["title"])
        #for a in div.find_all(name="a", attrs={"data-tn-element":"jobTitle"}):
          #job_post.append(a["title"]) 
    #grabbing company name
        company = div.find_all(name="span", attrs={"class":"company"}) 
        if len(company) > 0: 
          for b in company:
            job_post.append(b.text.strip()) 
        else: 
          sec_try = div.find_all(name="span", attrs={"class":"result-link-source"})
          for span in sec_try:
            job_post.append(span.text)
            if len(company)==0:
              job_post.append('none') 
    #grabbing location name
        c = div.find_all("span", attrs={'class': 'location'}) 
        for span in c: 
          job_post.append(span.text)
          if len(c) == 0:
            job_post.append("NA") 
        salary=div.find_all('span', attrs={'class': 'salary no-wrap'})
        if len(salary)>0:
          for span in salary:
            job_post.append(span.text)
        else:
            job_post.append("No Salary Listed")
    #grabbing summary text
        d = div.find_all('span', attrs={'class': 'summary'}) 
        if len(d) > 0:
          for span in d:
            job_post.append(span.text)
        else:
            job_post.append('No summary listed') 
        
        sample_df.loc[num] = job_post

  

# After waiting a couple minutes indeed will have the scrapped jobs
#Checkk out how many records it pulled
#len(sample_df)
# check out what they look like
#print(sample_df)

#one thing you should notice here is that the sample_df has pulled duplicates
# part of this comes from the website itself not playing well with our loop
# Drop the duplicates
sample_df.drop_duplicates(subset= "job_title", keep= 'first', inplace= True)


#Check hwo many records were dropped
# list to hold salary and city as
salary=[i for i in sample_df.salary]
cities=[i for i in sample_df.city]
n=0

for s in salary:
  sal=sal.strip().split()
  
  
len(sample_df)


# Now we need to turn our job records spatial 
# We need to geocode these a bit
# For simplicity purposes in the attached data there is cities_lat_lon, which has the 
# Read in your lat lon csv
Lat_lon = pd.read_csv('/home/425mussa/Desktop/lab11/cities_lat_lon.csv')

#Loading the two pandas dataframes together
result=sample_df.merge(Lat_lon, on=['city'])

## Creating random numbers to jitter our coordinates
result['RANDlat'] = [ random.uniform(-.1, .1)  for k in result.index]
result['RANDlon'] = [ random.uniform(-.1, .1)  for k in result.index]

#Now just add the random value to each column
result['Lat']= result['Lat']+result['RANDlat']
result['Lon']= result['Lon']+result['RANDlon']

# Now the points have been jittered
# Establish the mean coordinates for where to start your map
Mean_coords=(42.959443, -85.742777)
# Creates your map
map=folium.Map(location=Mean_coords, zoom_start=6)

#getting the points to appear clustered at the different scales
marker_cluster= folium.plugins.MarkerCluster().add_to(map)

#Adding the points and popup windows onto the map
# for full details on this for loop look at the lab instructions
for i in range(0, len(result)):
  folium.Marker([result.iloc[i]['Lat'], result.iloc[i]['Lon']], 
  popup=folium.Popup('<b>Job Title: </b>'+result.iloc[i]['job_title']+ '<br>' + 
  '<b>Company: </b>' + result.iloc[i]['company_name'] + 
  '<br>'+'<b>Location: </b>'+result.iloc[i]['location']+'<br>' +'<b> Salary: </b>' + result.iloc[i]['salary']+ '<br>' +'<b>Summary: </b>'+result.iloc[i]['summary'], max_width=450), 
  icon=folium.Icon(color='red')).add_to(marker_cluster)

#saving the map as an html file
map.save(outfile='map.html')

