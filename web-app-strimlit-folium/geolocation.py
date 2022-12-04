import re
import time
from collections import namedtuple

import numpy as np
from geopy.geocoders import Nominatim
import pandas as pd
import folium
import requests
import streamlit as st
from geopy.distance import GreatCircleDistance

locator = Nominatim(user_agent='myGeocoder')

def get_directions(lat1, long1, lat2, long2, mode='drive'):
    url = "https://route-and-directions.p.rapidapi.com/v1/routing"
    key = "c58ed86ed0msh397699f14655a79p175000jsn0f9a5156f508"
    host = "route-and-directions.p.rapidapi.com"
    headers = {"X-RapidAPI-Key": key, "X-RapidAPI-Host": host}
    querystring = {"waypoints":f"{str(lat1)},{str(long1)}|{str(lat2)},{str(long2)}","mode":mode}
    response = requests.request("GET", url, headers=headers, params=querystring)
    return response


def get_lat_long_address(address):
   location = locator.geocode(address)
   return location.latitude, location.longitude


def create_map(responses, lat_lons, m):
    df = pd.DataFrame()
    for response in responses:
        mls = response.json()['features'][0]['geometry']['coordinates']
        points = [(i[1], i[0]) for i in mls[0]]
        # додати рядки
        folium.PolyLine(points, weight=5, opacity=1).add_to(m)
        temp = pd.DataFrame(mls[0]).rename(columns={0: 'Lon', 1: 'Lat'})[['Lat', 'Lon']]
        df = pd.concat([df, temp])
    # створити оптимальне масштабування
    sw = df[['Lat', 'Lon']].min().values.tolist()
    sw = [sw[0] - 0.0005, sw[1] - 0.0005]
    ne = df[['Lat', 'Lon']].max().values.tolist()
    ne = [ne[0] + 0.0005, ne[1] + 0.0005]
    m.fit_bounds([sw, ne])
    return m

def get_time_distance(responses):
    total_distance = 0
    total_distance_time = 0
    for response in responses:
        timee = response.json()['features'][0]['properties']['time']
        distance = response.json()['features'][0]['properties']['distance']
        total_distance += distance
        total_distance_time += int(timee)
    distance2 = round(float(total_distance)/1000, 2)
    timee2 = time.strftime("%H:%M:%S", time.gmtime(total_distance_time))
    st.success(f'Прокладений шлях має {distance2} км. Приблизний час, щоб обійти всі книгарні та бібліотеки {timee2}', icon="✅")


def html_li(market, address):
    st.markdown(f"""<ul><li>{market}: {address}</li></ul>""", unsafe_allow_html=True)


def distance_marker(distance,Source, lat,lon):
    for lat,lon in zip(lat,lon):
        dist = GreatCircleDistance(Source,(lat,lon))
        distance.append(dist)
    return distance


def write_info_distance(distance,Source, lat,lon, market, address, radius, m):
    count = 0
    for distance,lat,lon, market, address \
            in zip(distance,lat,lon, market, address):
        if (distance > 0) and (distance <= 0.2) and radius == 200.0:
            html_li(market, address)
            count += 1
        elif (distance > 0) and (distance <= 0.5) and radius == 500.0:
            html_li(market, address)
            count += 1
        elif (distance > 0) and (distance <= 1.0) and radius == 1000.0:
            html_li(market, address)
            count += 1
        elif (distance > 0) and (distance <= 3.0) and radius == 3000.0:
            html_li(market,address)
            count += 1
    return count


def book_table_html(name,marker_info):
    return f"""<!DOCTYPE html>
    <html>
    <head>
    <link rel="stylesheet" href="https://stackpath.bootstrapcdn.com/bootstrap/4.3.1/css/bootstrap.min.css" integrity="sha384-ggOyR0iXCbMQv3Xipma34MD+dH/1fQ784/j6cY/iJTQUOhcWr7x9JvoRxT2MZw1T" crossorigin="anonymous">
    <script src="https://code.jquery.com/jquery-3.3.1.slim.min.js" integrity="sha384-q8i/X+965DzO0rT7abK41JStQIAqVgRVzpbzo5smXKp4YfRvH+8abtTE1Pi6jizo" crossorigin="anonymous"></script>
    <script src="https://cdnjs.cloudflare.com/ajax/libs/popper.js/1.14.7/umd/popper.min.js" integrity="sha384-UO2eT0CpHqdSJQ6hJty5KVphtPhzWj9WO1clHTMGa3JDZwrnQq4sF86dIHNDz0W1" crossorigin="anonymous"></script>
    <script src="https://stackpath.bootstrapcdn.com/bootstrap/4.3.1/js/bootstrap.min.js" integrity="sha384-JjSmVgyd0p3pXB1rRibZUAYoIIy6OrQ6VrjIEaFf/nJGzIxFDsf4x0xIM+B07jRM" crossorigin="anonymous"></script>
    </head>
    <body>
    <p class="font-weight-bold">Книги для замовлення</p>
    {str(marker_info).replace(''", [", '').replace('", "', '').
    replace('", "', '').replace('"])','').replace('""', '').replace('("','')}
    </body>
        </html>
        """

def windowBookshop(name, address, work, contacts):
    css = "{text-align: center;}"
    return f'''<!DOCTYPE html>
    <html>
    <head>
    <link rel="stylesheet" href="https://stackpath.bootstrapcdn.com/bootstrap/4.3.1/css/bootstrap.min.css" integrity="sha384-ggOyR0iXCbMQv3Xipma34MD+dH/1fQ784/j6cY/iJTQUOhcWr7x9JvoRxT2MZw1T" crossorigin="anonymous">
    <script src="https://code.jquery.com/jquery-3.3.1.slim.min.js" integrity="sha384-q8i/X+965DzO0rT7abK41JStQIAqVgRVzpbzo5smXKp4YfRvH+8abtTE1Pi6jizo" crossorigin="anonymous"></script>
    <script src="https://cdnjs.cloudflare.com/ajax/libs/popper.js/1.14.7/umd/popper.min.js" integrity="sha384-UO2eT0CpHqdSJQ6hJty5KVphtPhzWj9WO1clHTMGa3JDZwrnQq4sF86dIHNDz0W1" crossorigin="anonymous"></script>
    <script src="https://stackpath.bootstrapcdn.com/bootstrap/4.3.1/js/bootstrap.min.js" integrity="sha384-JjSmVgyd0p3pXB1rRibZUAYoIIy6OrQ6VrjIEaFf/nJGzIxFDsf4x0xIM+B07jRM" crossorigin="anonymous"></script>
    <style>
    p {css}
    </style>
    </head>
    <body>
   <table class="table table-hover">
  <thead>
    <tr>
      <p class="font-weight-bold">{name}</p>
    </tr>
  </thead>
  <tbody>
    <tr>
      <td colspan="2">Адреса</td>
      <td>{address}</td>
    </tr>
    <tr>
      <td colspan="2">Графік роботи</td>
      <td>{work}</td>
    </tr>
    <tr>
      <td colspan="2">Телефон</td>
      <td>{contacts}</td>
    </tr>
  </tbody>
 </table>
</body>
        </html>'''


def get_city(my_adress_text, city):
    if not my_adress_text:
        st.write("Ведійть свою точну адресу, щоб визнати найближчі книгарні в межах міста!")
    else:
        text = re.findall(r'\w+', my_adress_text)
        for name in city:
            if name in text:
                return name


def get_near_market(address, city):
    for address in zip(address):
        address = ' '.join(address)
        address = str(address)
        word = address.replace(',', '').split()
        if city in word:
            st.write(f'\t  - {address}')


def get_ip():
    response = requests.get('https://api64.ipify.org?format=json').json()
    return response["ip"]


def get_location():
    ip_address = get_ip()
    response = requests.get(f'https://ipapi.co/{ip_address}/json/').json()
    location_data = {
        "ip": ip_address,
        "city": response.get("city"),
        "region": response.get("region"),
        "country": response.get("country_name"),
        "latitude": response.get("latitude"),
        "longitude": response.get("longitude")
    }
    return location_data


def get_location_by_address(address, locator):
    location = locator.geocode(address).raw
    time.sleep(1)
    return location



