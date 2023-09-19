import requests
from bs4 import BeautifulSoup

l=list()
g=list()
o={}
k={}
fac=[]
fac_arr=[]
headers={"User-Agent":"Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/107.0.0.0 Safari/537.36"}

# target_url = "https://www.booking.com/hotel/us/the-lenox.html?checkin=2023-09-28&checkout=2023-09-29&group_adults=2&group_children=0&no_rooms=1&selected_currency=USD"
target_url = r"https://www.booking.com/searchresults.html?label=gen173bo-1DCAsodUIjYXBhLWhvdGUtYXNha3VzYS10YWhhcmFtYWNoaS1la2ltYWVIMVgDaOcBiAEBmAExuAEHyAEM2AED6AEB-AEDiAIBmAICqAIDuAKM9ZWoBsACAdICJDUxZjNkOTY3LTJjZDAtNDI2Zi04N2YyLWY4MmQyYzBmNjJmZdgCBOACAQ&sid=76523d1ceb70ea69f0e00745423032d0&aid=304142&checkin=2023-09-28&checkout=2023-09-29&dest_id=320&dest_type=district&ss=Taito&selected_currency=TWD&offset=25"
resp = requests.get(target_url, headers=headers)

soup = BeautifulSoup(resp.text, 'lxml')
title_list = []
price_list = []

titles = soup.find_all("div", {"data-testid":"title"})
for title in titles:
    clean_title = title.getText()
    title_list.append(clean_title)
prices = soup.find_all("span", {"data-testid":"price-and-discounted-price"})
for price in prices:
    clean_price = price.getText().strip('TWD ').replace('\xa0', ' ')
    price_list.append(clean_price)

print(len(title_list))
print(len(price_list))
result = list(zip(title_list, price_list))
print(result)
# try:
#     o["name"]=soup.find("h2",{"class":"pp-header__title"}).text
# except:
#     o["name"] = None

# try:
#     o["address"]=soup.find("span",{"class":"hp_address_subtitle"}).text.strip("\n")
# except:
#     o["address"] = None

# try:
#     o["rating"]=soup.find("div",{"class":"d10a6220b4"}).text
# except:
#     o["rating"] = None

# fac=soup.find_all("div",{"class":"important_facility"})
# for i in range(0,len(fac)):
#     fac_arr.append(fac[i].text.strip("\n"))


# ids= list()

# targetId=list()
# try:
#     tr = soup.find_all("tr")
# except:
#     tr = None

# for y in range(0,len(tr)):
#     try:
#         id = tr[y].get('data-block-id')

#     except:
#         id = None

#     if( id is not None):
#         ids.append(id)

# print("ids are ",len(ids))


# for i in range(0,len(ids)):

#     try:
#         allData = soup.find("tr",{"data-block-id":ids[i]})
#         try:
#             rooms = allData.find("span",{"class":"hprt-roomtype-icon-link"})
#         except:
#             rooms=None


#         if(rooms is not None):
#             last_room = rooms.text.replace("\n","")
#         try:
#             k["room"]=rooms.text.replace("\n","")
#         except:
#             k["room"]=last_room

#         price = allData.find("div",{"class":"bui-price-display__value prco-text-nowrap-helper prco-inline-block-maker-helper prco-f-font-heading"})
#         k["price"]=price.text.replace("\n","")

        
#         g.append(k)
#         k={}

#     except:
#         k["room"]=None
#         k["price"]=None


# l.append(g)
# l.append(o)
# l.append(fac_arr)
# print(l)