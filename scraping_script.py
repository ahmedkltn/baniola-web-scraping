# Importing libraries :
from time import sleep
from bs4 import BeautifulSoup as bs
import requests
import pandas as pd
import numpy as np
from unidecode import unidecode
#Getting all the information related to the car:
def get_car_info(car_url,params):
    #Getting the response from the car page url
    response = requests.get(car_url)
    soup = bs(response.content,"lxml")
    #Getting all informations about the car :
    all_specs = soup.findAll("div",attrs={"class","info"})

    #General information which it contain Price and the city
    general = all_specs[0].find("div", attrs={"class", "general"})
    #Getting the car price
    try:
        params["price"].append(general.find("div",attrs={"class","prix"}).text)
    except:
        params["price"].append(np.nan)
    #Getting the car city
    try:
        params["city"].append(general.find("span", attrs={"class", "col-5"}).text)
    except:
        params["city"].append(np.nan)
    
    #All the other informations brand,model,year,..,gearbox...
    table = all_specs[0].find("table", attrs={"class", "table"})
    all_info_table = table.findAll("td")[:-2]
    #The table contain td with the needed informations we will loop all td and added to params :
    #the array with all td contain [info_name,info,...,info] so will loop over odd values
    i = 2
    for index,info in enumerate(all_info_table):
        if(index % 2 !=0 ):
            #Using unidecode to change special French characters into English characters
            params[list(params.keys())[i]].append(unidecode(info.text))
            i+=1
    
    #Informations about the equipements i will try to put them as String:
    try:
        #Getting all equipements in p tag
        equipements = all_specs[0].find("div", attrs={"class", "equipement"}).find_all("p")
        equips = []
        for equip in equipements:
            #Using unidecode to change special French characters into English characters
            #Append equipements in equips
            equips.append(unidecode(equip.text))
        #Join equips with /
        params["equipement"].append("/".join(equips))
    except:
        #If no equips found append null value
        params["equipement"].append(np.nan)


# Function that will return the page url which it will need page_num to
# Params will contain {Price:[],city:[],Brand:[]} ..
def get_cars_url(basic_url, page_num):
    #Init cars_url 
    cars_urls = []
    #Concat the base url with page number
    url = basic_url + page_num
    #Getting the response of page url
    response = requests.get(url)
    soup = bs(response.content, "lxml")
    #Selecting all the cars urls to loop over them
    res = soup.findAll("div", attrs={"class", "row p-1"})[0].findAll("div", attrs={"class", "Box-list-image"})
    for i in range(len(res)):
        #selecting the car url
        cars_urls.append(res[i].find("a")["href"])
    return cars_urls

def main(basic_url):
    #Init params : 
    params = dict(price=[], city=[], brand=[], model=[], year=[],
                  fiscal_power=[], mileage=[], fuel=[], gearbox=[], equipement=[])
    #Number of pages (169): 
    pages_list = 169
    #the pages are increasing by 40 
    # for exemple : /voitures-occasion/0 , /voitures-occasion/40 .... /voitures-occasion/n:
    page_num = 0
    for i in range(pages_list):
        print(f"Page list : {i+1} - Page num : {page_num}")
        #Getting all cars urls for the page
        cars_urls = get_cars_url(basic_url,str(page_num))
        #Looping over all cars_urls and get information from every car
        for car_url in cars_urls:
            get_car_info(car_url,params)
        page_num+=40
    return params


#Calling the main function
basic_url = "https://baniola.tn/voitures-occasion/"
params = main(basic_url)
#Export it as csv file
i = range(1, len(params["price"])+1)
df = pd.DataFrame(params,index=i)
df.to_csv("baniola_scraping.csv")