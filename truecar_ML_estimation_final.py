# -*- coding: utf-8 -*-
"""
Created on Tue Dec 12 10:35:35 2023

@author: mohammad
"""
import mysql.connector
from bs4 import BeautifulSoup
import requests
from sklearn.tree import DecisionTreeRegressor
cnx=mysql.connector.connect(user='root',password='12345',host='127.0.0.1',database='learn')
cursor=cnx.cursor()
cursor.execute('DROP TABLE IF EXISTS cars;')
cursor.execute('CREATE TABLE cars(price varchar(20), mileage varchar(20), year varchar(20), accidents varchar(20), owners varchar(20));')
#for used car
base_url='https://www.truecar.com/used-cars-for-sale/listings/'
make=input('Please enter the manufacturer name:')
model=input('Please enter the model name:')
#trim=input('please enter the trim:')
test_mileage=input('please enter the mileage:')
test_year=input('please enter the production year:')
test_accident=input('please enter the number of the accidents the car had before:')
test_owners=input('please enter number of owners the car had before:')
test=[[test_mileage,test_year,test_accident,test_owners]]
def get_car_info(url):
    page=requests.get(url)
    soup=BeautifulSoup(page.text,'html.parser')
    part=soup.find_all('div',attrs={'card-content order-3 vehicle-card-body'})
    
    price=list()
    mileage=list()
    year=list()
    accidents=list()
    owners=list()    
    for i in part:
        #get price
        scrape=i.find('div',attrs={'vehicle-card-bottom vehicle-card-bottom-top-spacing'})
        scrape2=scrape.find('div',attrs={'vehicle-card-bottom-pricing flex w-full justify-between'})
        scrape3=scrape2.find('div',attrs={'vehicle-card-bottom-pricing-secondary pl-3 lg:pl-2 vehicle-card-bottom-max-50'})
        p=scrape3.text
        p=p.split('$')
        price.append(p[-1].replace(',',''))
        
        #get mileage
        scrape=i.find('div',attrs={'mt-2-5 w-full border-t pt-2-5'})
        scrape2=scrape.find('div',attrs={'truncate text-xs'})
        mileage.append(scrape2.text[:-6].replace(',',''))
        
        #get year
        year_i=i.find('div',attrs={'vehicle-card-header w-full'})
        year_i=year_i.text.split(' ')
        year.append(year_i[0][-4:])
        
        #get accidents and owners
        scrape=i.find_all('div',attrs={'vehicle-card-location mt-1 text-xs','vehicleCardCondition'})
        scrape2=scrape[1].text.split(',')
        accident=scrape2[0].split(' ')
        owner=scrape2[1].split(' ')
        accident=accident[0]
        if accident=='No':
            accident='0'
        owner=owner[1]
        accidents.append(accident)
        owners.append(owner)
        
    return price,mileage,year,accidents,owners
def put_info_in_DB(info):
    for j in range(len(info[0])):
        cursor.execute("INSERT INTO cars VALUES (%s,%s,%s,%s,%s)",(info[0][j],info[1][j],info[2][j],info[3][j],info[4][j]))

    cnx.commit()
 
for page in range(1,5):
    vins=list()
    url=base_url + make + '/' + model + '/?page=' + str(page)
    info=get_car_info(url)
    put_info_in_DB(info)

#train model
x=list()
y=list()
query="SELECT * FROM cars;"
cursor.execute(query)
for(price,mileage,year,accidents,owners) in cursor:
    price=int(price)
    mileage=int(mileage)
    year=int(year)
    accidents=int(accidents)
    owners=int(owners)
    y.append(price)
    x.append([mileage,year,accidents,owners])
tree=DecisionTreeRegressor()
tree.fit(x,y)
predict=tree.predict(test)

print(int(predict[0]))
cnx.close() 