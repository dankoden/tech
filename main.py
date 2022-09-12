from oauth2client.service_account import ServiceAccountCredentials
from datetime import datetime
from bs4 import BeautifulSoup
from random_user_agent.user_agent import UserAgent
from model import Ad, session
from model import Base,engine
import httplib2
import apiclient
import aiohttp
import asyncio
import re


# Get random user-agent
user_agent = {'user-agent': UserAgent().get_random_user_agent()}

# Get access to API
CREDENTIALS_FILE = 'techtask.json'
spreadsheet_id = '1xC0NVYzGDcSVaHvf3B7tDmnSzDxpnvIGWVALsMQu3-c'

services = None


def auth_to_google_sheet():
    """Create connect to Google API
     :return service object above API google sheet"""
    credentials = ServiceAccountCredentials.from_json_keyfile_name(
        CREDENTIALS_FILE,
        ['https://www.googleapis.com/auth/spreadsheets',
         'https://www.googleapis.com/auth/drive'])
    httpAuth = credentials.authorize(httplib2.Http())
    global services
    services = apiclient.discovery.build('sheets', 'v4', http=httpAuth)


async def write_data_to_google_sheet(price: str, currency: str, title: str, posted: datetime, description: str,
                                     image: str,
                                     bedroom: str,t_counter):
    """write data at Google sheets"""
    services.spreadsheets().values().batchUpdate(
        spreadsheetId=spreadsheet_id,
        body={
            "valueInputOption": "USER_ENTERED",
            "data": [
                {"range": f"A{t_counter}:H{t_counter}",
                 "majorDimension": "ROWS",
                 "values": [[title, image, str(posted), price, currency, description, bedroom]]}
            ]}).execute()
    await asyncio.sleep(0)


async def fetch(client: aiohttp.ClientSession, url: str) -> str:
    """Make requests to url
     :return HTML of response"""
    async with client.get(url, ssl=False, headers=user_agent) as resp:
        assert resp.status == 200
        return await resp.text()


async def write_db_data(price: str, currency: str, title: str, posted: datetime, description: str, image: str,
                        bedroom: str):
    ad = Ad(price=price, currency=currency, title=title, posted=posted,
            description=description, image=image, bedroom=bedroom)
    session.add(ad)
    session.commit()
    await asyncio.sleep(0.1)


async def get_ad_data(url: str, client: aiohttp.ClientSession):
    """Get data about ad from page ,and pass this data to function,
    which write them to databaswe
    :url - pagination url
    :client - session client """

    html = await fetch(client, url)
    soup = BeautifulSoup(html, 'html.parser')
    list_of_divs = soup.find_all('div', class_="search-item")
    c_bedroom = None
    t_counter = 2
    for div in list_of_divs:
        price = div.find(class_='price').contents[0].strip()
        if price != "Please Contact":
            currencys = {"$": "USD",
                         "S": "USD",
                         "€": "EUR"}
            currency = currencys[price[0]]
            price = price.split(".")[0].replace(",", ".")[1:]
        else:
            currency, price = None, None
        title = div.find('a', class_='title').contents[0].strip()
        posted = div.find('span', class_="date-posted").contents[0].strip()
        res = re.match(r'\d+/\d+/\d+', posted)
        if not res:
            posted = datetime.today()
        else:
            posted = datetime.strptime(posted, '%d/%m/%Y')
        description = div.find('div', class_="description").contents[0].strip()
        try:
            image = div.find('picture').find('img').get('data-src')
        except AttributeError:
            continue
        bedroom = div.find('span', class_='bedrooms').contents
        for item in bedroom:
            if "Beds" in item:
                c_bedroom = ''.join(item.strip() for item in item.split('\n'))
                break
        print(price, currency, title, posted, description, image, c_bedroom)
        await write_data_to_google_sheet(price, currency, title, posted, description, image, c_bedroom,t_counter)
        await write_db_data(price, currency, title, posted, description, image, c_bedroom)
        t_counter += 1


async def main():
    """Open session and get all pages for parsing"""
    async with aiohttp.ClientSession() as client:
        c = 0
        for page in range(1, 94):
            c += 1
            print(f'{c} of 94')
            url = f'https://www.kijiji.ca/b-apartments-condos\
                    /city-of-toronto/page-{page}/c37l1700273'
            await get_ad_data(url, client)


if __name__ == "__main__":
    Base.metadata.create_all(engine)
    auth_to_google_sheet()
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main())
