import re
from folium import plugins
from branca.element import Figure
import streamlit.components.v1 as components

import scrap
import funs
import graf
from threading import Thread
import pickle
from config import hosts
from itertools import product
from math import inf
import pickle
from datetime import datetime
import pandas as pd
import streamlit as st
from streamlit_folium import folium_static
import folium
import os
from PIL import Image
from requests.exceptions import ConnectionError
import requests
from datetime import datetime as dt
import branca
from folium import plugins
from geopy.geocoders import Nominatim
import time
import geolocation


file_path = "./img/"
img = Image.open(os.path.join(file_path, 'logo2.ico'))
st.set_page_config(page_title='Замовлення', page_icon=img, layout="wide", initial_sidebar_state="expanded")

info_img, info_text = st.columns(2)
logo_img = Image.open(os.path.join(file_path, 'booklogo_.png'))
with info_img:
    st.image(logo_img, width= 270)
with info_text:
    css_text = "p {text-align: justify;}"
    st.markdown(f"""<style>{css_text }</style><p>За допомогою цього застосунку ви можете сформувати мінімальне за вартістю замовлення набору книг, комплексно враховуючи ціни та умови різних книгарень. Він надає геопросторові дані, щоб допомогти з'ясувати, де найближча книгарня чи бібліотека та прокласти маршрут до них для здійсненя самовивозу замовлення.</p>""", unsafe_allow_html=True)
    st.markdown(f""" <p>Книгарні, в яких відбувася збір інформаці:</p>
    <ul>
      <li>Клуб сімейного дозвіля</li>
      <li>Yakaboo</li>
    </ul>""",unsafe_allow_html=True)

st.title('Замовлення')

if "myauthor" not in st.session_state:
    st.session_state.myauthor = []

if "list_author" not in st.session_state:
    st.session_state.list_author = []

if "mytitle" not in st.session_state:
    st.session_state.mytitle = []

if "list_title" not in st.session_state:
    st.session_state.list_title = []

if "myamount" not in st.session_state:
    st.session_state.myamount = []

if "list_amount" not in st.session_state:
    st.session_state.list_amount = []

if "chkarr" not in st.session_state:
    st.session_state.chkarr = []

if "rerun" not in st.session_state:
    st.session_state.rerun = False

l1, l2, l3 = st.columns(3)


def cmpltBook(task):
    idx = st.session_state.myauthor.index(task)
    st.session_state.chkarr[idx] = not st.session_state.chkarr[idx]
    st.session_state.rerun = True


def listBook():
    st.session_state.list_author = []
    for i, author in enumerate(st.session_state.myauthor):
        with l1:
            st.session_state.list_author.append(st.write(author,
                value = st.session_state.chkarr[i], key = 'l' + f'{dt.now():%d%m%Y%H%M%S%f}',
                                                    on_change = cmpltBook, args=(author,)))

    st.session_state.list_title = []
    for i, task in enumerate(st.session_state.mytitle):
        with l2:
            st.session_state.list_title.append(
                st.write(task, value=st.session_state.chkarr[i], key='l' + f'{dt.now():%d%m%Y%H%M%S%f}',
                         on_change=cmpltBook, args=(task,)))

    st.session_state.list_amount = []
    for i, task in enumerate(st.session_state.myamount):
        with l3:
            st.session_state.list_amount.append(
                st.write(task, value=st.session_state.chkarr[i], key='l' + f'{dt.now():%d%m%Y%H%M%S%f}',
                         on_change=cmpltBook, args=(task,)))


if st.session_state.rerun == True:
    st.session_state.rerun = False
    st.experimental_rerun()

else:
    with l1:
        title = st.text_input('Прізвище автора', placeholder = 'Прізвище автора')
    with l2:
        title2 = st.text_input('Назва книги', placeholder = 'Назва книги')
    with l3:
        title3 = st.text_input('Кількість примірників', placeholder = 'Кількість примірникі')

    if st.button('Добавити до списку замовлення'):
        if title != "" and title2 != "" and title3 != "":
            st.session_state.myauthor.append(title)
            st.session_state.mytitle.append(title2)
            st.session_state.chkarr.append(False)
            st.session_state.myamount.append(title3)
            st.session_state.chkarr.append(False)


listBook()
list_author = st.session_state.myauthor
list_title = st.session_state.mytitle
list_amount = st.session_state.myamount
list_ = []
for i in range(len(list_amount)):
    if list_amount[i] == '':
        amount_int = 1
    else:
        amount_int = list_amount
        list_.append({"id": i, "author": list_author[i],
                      "title": list_title[i],
                      "amount": int(amount_int[i])})

if "list_dict" not in st.session_state:
    st.session_state.list_dict = []
st.session_state.list_dict = list_
st.write(" ")
st.write("Ви можете видалити останю книгу зі списку")
if st.button('Видалити книгу ❌'):
    try:
        author = st.session_state.myauthor.pop()
        title = st.session_state.mytitle.pop()
        amount = st.session_state.myamount.pop()
        st.error(f'Видалено {author} - {title}')
        st.session_state.list_dict.pop()
        st.write(st.session_state.list_dict)
    except IndexError:
        st.error("Список повністю очищений ❌")

order_list = st.session_state.list_dict

if "price_info_state" not in st.session_state:
    st.session_state.price_info_state = {}

if "order_state" not in st.session_state:
    st.session_state.order_state = []

if "delivery_info_state" not in st.session_state:
    st.session_state.delivery_info_state = {}


if st.button('Пошук замовлення'):
    with st.spinner('За чекайте, будь ласка...'):
        def thread(order_list, host):
            for item in order_list:
                args = (item['author'], item['title'], host)
                price_info[item['id']][host] = scrap.get_price(*args)
            delivery_info[host] = scrap.get_delivery(host)

        price_info = {key: {} for key in range(len(order_list))}
        delivery_info = {key: None for key in hosts.keys()}

        threads = [Thread(target=thread, args=(order_list, host)) for host in hosts]
        for item in threads:
            item.start()
        for item in threads:
            item.join()

        with open('data.pickle', 'wb') as f:
            pickle.dump(price_info, f)

        with open('data.pickle', 'rb') as f:
            price_info = pickle.load(f)

        my_order = funs.check_book(price_info, order_list)
        price_info = my_order[0]
        st.session_state.price_info_state = price_info
        order_list = my_order[1]
        delivery_info = {'bookclub.ua': (60.0, 390.0),
                     'yakaboo.ua': (60.0, inf)}
        st.session_state.delivery_info_state = delivery_info

        markets = list(hosts.keys())
        if "markets_state" not in st.session_state:
            st.session_state.markets_state = markets
        def dfs_find_routes(tree, start, end):
            global min_price, order
            if start == end:
                p = funs.price(price_info, delivery_info, graf.route_to_order(route), order_list)
                if p and p[0] < min_price:
                    min_price, order = p
            else:
                for node in tree[start]:
                    if not visited.get(node, False):
                        visited[node] = True
                        route.append(node)
                        dfs_find_routes(tree, node, end)
                        visited[node] = False
                        route.remove(node)

        adj = graf.build_adj_list(price_info, markets)
        visited, route = {}, []
        min_price, order = inf, None
        dfs_find_routes(adj, 0, max(adj.keys()))
        st.session_state.order_state = order

col1, col2 = st.columns(2)
col0 = [col1,col2]
image_bookclub = Image.open(os.path.join(file_path, 'bookclub2.png'))
image_yakaboo = Image.open(os.path.join(file_path, 'yakaboo.png'))
list_img0 = [image_bookclub, image_yakaboo]
tab1, tab2 = st.tabs(["Замовленя з вартісю доставки", "Без вартості доставки"])
try:
    with tab1:
        funs.display(st.session_state.order_state, st.session_state.markets_state,
        st.session_state.price_info_state, st.session_state.delivery_info_state,order_list, col0, list_img0)


    with tab2:
        total_price = 0
        for market_id in range(len(st.session_state.order_state)):
            if not st.session_state.order_state[market_id]:
                continue
            with col0[market_id]:
                market_total = 0
                for item in st.session_state.order_state[market_id]:
                    amount = order_list[item]["amount"]
                    price = st.session_state.price_info_state[item][st.session_state.markets_state[market_id]][0]
                    total = price * amount
                    market_total += total
                total_price += market_total
        st.info(f"Загальна вартість замовлення: {total_price} грн.")
except IndexError:
    pass

with st.expander("Інформація про доставку 📮"):
    funs.get_delivery_info(st.session_state.delivery_info_state)

with st.expander("Інформація про знайдені книги 📚"):
    funs.get_book_info(st.session_state.price_info_state, order_list)

st.header('Карта')
container = st.container()
st.write("Ведіть свою точну адресу, щоб дізнатися які книгарні є поряд 📍")
title = st.text_input('Ваша адреса', placeholder = 'Ваша адреса', value = "Україна")


app = Nominatim(user_agent='myapp')

location = geolocation.get_location_by_address(title, app)
latitude = location["lat"]
longitude = location["lon"]

st.write("Ви можете прокласти маршрут до потрібних книнарень 🏣, ведіть їхні адреси в наступне поле")
if "myaddress" not in st.session_state:
    st.session_state.myaddress = []

if "tskaddress" not in st.session_state:
    st.session_state.tskaddress = []

if "loopaddress" not in st.session_state:
    st.session_state.loopaddress = []

if "returnn" not in st.session_state:
    st.session_state.returnn = False

addresses_marker = [title,]
def cmpltAddress(addr):
    idx = st.session_state.myaddress.index(addr)
    st.session_state.loopaddress[idx] = not st.session_state.loopaddress[idx]
    st.session_state.returnn = True


def listAddress():
    st.session_state.tskaddress = []
    for i, addr in enumerate(st.session_state.myaddress):
        st.session_state.tskaddress.append(st.write(addr,
                value = st.session_state.loopaddress[i], key = 'l2' + f'{dt.now():%d%m%Y%H%M%S%f}',
                                                    on_change = cmpltAddress, args=(addr,)))
        addresses_marker.append(addr)


if st.session_state.returnn == True:
    st.session_state.returnn = False
    st.experimental_rerun()

else:
    listaddress = st.text_input('Адреса книгарні', placeholder='Адреса книгарні')
    if st.button('Добавити адресу книгарні'):
        if listaddress != "":
            st.session_state.myaddress.append(listaddress)
            st.session_state.loopaddress.append(False)

listAddress()
st.write("Ви можете видалити адресу книгарні чи бібліотеки")
if st.button('Видалити адресу ❌'):
    try:
        streat_addreess = st.session_state.myaddress.pop()
        st.error(f'Видалино {streat_addreess} !')
        st.write(streat_addreess)
        addresses_marker.pop()
    except IndexError:
        st.error("Список повністю очищений ❌")

if "radius" not in st.session_state:
    st.session_state.radius = "200 м"

if "type_map" not in st.session_state:
    st.session_state.type_map = "Відкрита карта вулиць"


data = {
    "200 м": 200,
    "500 м": 500,
    "1 км": 1000,
    "3 км": 3000,
}
st.sidebar.header("Параметри карти")
st.sidebar.selectbox(
    label="Який радіус ви хочете призначити?",
    options=("200 м","500 м","1 км", "3 км"),
    key="radius"
)
radius = data[st.session_state.radius]
data_map = {
    "Відкрита карта вулиць": "OpenStreetMap",
    "Ландшафтна карта": "Stamen Terrain",
    "Чорно-біла карта":"Stamen Toner"

}
add_select = st.sidebar.selectbox(label="Яку карту хочете обрати?",
                                  options=("Відкрита карта вулиць", "Ландшафтна карта","Чорно-біла карта"),
                                  key="type_map")
my_adress = geolocation.get_location()
type_map = data_map[st.session_state.type_map]


def folium_static(fig, width=1350, height=550):
    if isinstance(fig, folium.Map):
        fig = folium.Figure().add_child(fig)
        return components.html(
            fig.render(), height=(fig.height or height) + 10, width=width
        )

    elif isinstance(fig, plugins.DualMap):
        return components.html(
            fig._repr_html_(), height=height + 10, width=width
        )


Source = ()
try:
    if title == "Україна":
        m = folium.Map(tiles=type_map,location=[my_adress['latitude'], my_adress['longitude']], zoom_start=15)
        folium.Marker([my_adress['latitude'], my_adress['longitude']], popup="Моє місце знаходження",
                      tooltip="Моє місце знаходження",
                      icon=folium.Icon(color='purple', prefix='fa', icon='anchor')).add_to(m)
        folium.Circle([my_adress['latitude'], my_adress['longitude']], radius=radius).add_to(m)
        Source = (my_adress['latitude'], my_adress['longitude'])
    else:
        m = folium.Map(tiles=type_map, location=[latitude, longitude], zoom_start=15)
        Source = (float(latitude), float(longitude))
        folium.Marker([latitude, longitude], popup="Моє місце знаходження",
                      tooltip="Моє місце знаходження", icon=folium.Icon(color='purple',
                                                                        prefix='fa', icon='male')).add_to(m)
        folium.Circle([latitude, longitude], radius=radius).add_to(m)
except:
    container.error('Сталася помилка з отриманям ваших кординатів', icon="🚨")
    m = folium.Map(tiles=type_map, location=[48.98947939673382, 31.38346472589481], zoom_start=6)


def color_change(data):
    if int(data) == 10:
        return 'red'
    elif int(data) == 20:
        return 'blue'
    elif int(data) == 30:
        return 'orange'
    else:
        return 'blue'


data_libraries = pd.read_csv("libraries.csv")
lat_libraries = data_libraries['lat']
lon_libraries = data_libraries['lon']
value_libraries = data_libraries['value']
name_libraries = data_libraries['name']
address_libraries = data_libraries['address']
work_libraries = data_libraries['work schedule']
contacts_libraries = data_libraries['contacts']

try:
    for lat, lon, value, name, address, work, contacts\
            in zip(lat_libraries, lon_libraries,value_libraries, name_libraries, address_libraries,
                   work_libraries, contacts_libraries):
        iframe_deep = branca.element.IFrame(html=geolocation.windowBookshop(name, address, work, contacts), width=350, height=310)
        popup_deep = folium.Popup(iframe_deep, parse_html=True)
        folium.Marker(location=[lat, lon], popup=popup_deep, tooltip="Бібліотека",
                      icon=folium.Icon(color=color_change(value), icon='glyphicon glyphicon-book'
                                       )).add_to(m)
except IndexError:
    pass

data_shop = pd.read_csv("bookshop.csv")
lat_shop = data_shop['lat']
lon_shop = data_shop['lon']
value_shop = data_shop['value']
name_shop = data_shop['name']
address_shop = data_shop['address']
work_shop = data_shop['work schedule']
contacts_shop = data_shop['contacts']

try:
    for lat, lon, value, name, address, work, contacts in zip(lat_shop, lon_shop, value_shop, name_shop,
                                                              address_shop, work_shop, contacts_shop):
        iframe_deep = branca.element.IFrame(html=geolocation.windowBookshop(name, address, work, contacts), width=350, height=310)
        popup_deep = folium.Popup(iframe_deep, parse_html=True)
        folium.Marker(location=[lat, lon], popup=popup_deep, tooltip="Книгарння",
                      icon=folium.Icon(color=color_change(value), prefix='fa', icon='fa-shopping-cart'
                                       )).add_to(m)
except IndexError:
    pass


data_order = pd.read_csv("shop_order.csv")
lat = data_order['lat']
lon = data_order['lon']
value = data_order['value']
name = data_order['name']
address = data_order['adress']
work = data_order['work schedule']
contacts = data_order['contacts']
market = data_order['market']
try:
    for lat, lon, value, name, market, address, work, contacts \
            in zip(lat, lon, value, name, market, address, work, contacts):
        html = geolocation.book_table_html(name,funs.marker_info(name, st.session_state.order_state, st.session_state.markets_state,
        st.session_state.price_info_state, order_list))
        iframe_deep = branca.element.IFrame(html=geolocation.windowBookshop(market, address, work, contacts)+html,
                                            width=350, height=310)
        popup_deep = folium.Popup(iframe_deep, parse_html=True)
        folium.Marker(location=[lat, lon], popup= popup_deep, tooltip=market,
                      icon=folium.Icon(color=color_change(value)
                                       )).add_to(m)
except IndexError:
    pass

if "type" not in st.session_state:
    st.session_state.type = "Пішки"

typedata = {
    "Пішки": 'walk',
    "Автомобіль": 'drive',
    "Велосипед": 'bicycle',
    "Міський транспорт": 'transit',
    "Вантажівка": 'truck'

}
radiotype = st.radio(
    label="Оберіть тип пересування:",
    options=("Пішки", "Автомобіль", "Велосипед", "Міський транспорт", "Вантажівка"),
    key="type",
    horizontal = True)

type = typedata[st.session_state.type]
if "responses" not in st.session_state:
    st.session_state.responses = []
if "lat_lons" not in st.session_state:
    st.session_state.lat_lons = []

if st.button('Пошук маршруту'):
    if st.session_state.responses is not []:
        st.session_state.responses.clear()
        st.session_state.lat_lons.clear()
    st.session_state.lat_lons = [geolocation.get_lat_long_address(addr) for addr in addresses_marker]
    for n in range(len(st.session_state.lat_lons)-1):
      lat1, lon1, lat2, lon2 = st.session_state.lat_lons[n][0], st.session_state.lat_lons[n][1],\
                               st.session_state.lat_lons[n+1][0], st.session_state.lat_lons[n+1][1]
      response = geolocation.get_directions(lat1, lon1, lat2, lon2, mode=type)
      st.session_state.responses.append(response)
try:
    m = geolocation.create_map(st.session_state.responses, st.session_state.lat_lons, m)
    geolocation.get_time_distance(st.session_state.responses)
except KeyError as ke:
    pass


city = ['Львів', 'Київ', 'Харків', 'Чернівці', 'Чернівці', 'Черкаси', 'Черкаси', 'Черкаси', 'Суми', 'Рівне','Кременчук',
        'Миргород', 'Полтава', 'Одеса', 'Миколаїв', 'Кропивницький', 'Івано-Франківськ', 'Франківськ', 'Запоріжжя', 'Ужгород', 'Житомир',
         'Дніпро', 'Кривий', 'Павлоград', 'Луцьк', 'Вінниця', 'Бориспіль', 'Церква' 'Київська','Кам`янець-Подільський', 'Тернопіль']
my_adress_text = location["display_name"]
geolocation.get_city(my_adress_text, city)
address = data_order['adress']

c1, c2 = st.columns(2)
if "distance" not in st.session_state:
    st.session_state.distance = []

if "distance_shop" not in st.session_state:
    st.session_state.distance_shop = []

if "distance_libraries" not in st.session_state:
    st.session_state.distance_libraries = []

lat_shop = list(data_shop['lat'])
lon_shop = list(data_shop['lon'])
lat = list(data_order['lat'])
lon = list(data_order['lon'])
market = list(data_order['market'])
address = list(data_order['adress'])
name_shop = list(data_shop['name'])
address_shop = list(data_shop['address'])
lat_libraries = list(data_libraries['lat'])
lon_libraries = list(data_libraries['lon'])
value_libraries = list(data_libraries['value'])
name_libraries = list(data_libraries['name'])
address_libraries = list(data_libraries['address'])


def check(work):
    if work == 0:
        st.write("Поряд немає даних книгарень")


with st.expander("Найближчі книгарні та бібліотнки🏃🏪🔖‍"):
    if Source == (float(latitude), float(longitude)):
        st.subheader('Найближчі книгарнні для самовивозу в межах вашого міста')
        geolocation.get_near_market(address, geolocation.get_city(my_adress_text, city))
        st.write(" ")
        st.subheader('Найближчі книгарні згідно замовлення')
        geolocation.distance_marker(st.session_state.distance, Source, lat, lon)
        work = geolocation.write_info_distance(st.session_state.distance, Source, lat, lon, market, address, radius, m)
        check(work)
        st.subheader('Найближчі книгарні')
        geolocation.distance_marker(st.session_state.distance_shop,Source, lat_shop,lon_shop)
        work = geolocation.write_info_distance(st.session_state.distance_shop,Source, lat_shop,lon_shop, name_shop,
                                               address_shop, radius, m)
        check(work)
        st.subheader('Найближчі бібліотеки')
        geolocation.distance_marker(st.session_state.distance_libraries, Source, lat_libraries, lon_libraries)
        work = geolocation.write_info_distance(st.session_state.distance_libraries,
                                               Source, lat_libraries, lon_libraries, name_libraries,
                                               address_libraries, radius, m)
        check(work)
    else:
        st.warning("Ведіть свою точну адресу, щоб отрмати дані", icon="⚠️")

minimap = plugins.MiniMap()
m.add_child(minimap)
folium_static(m)

agree = st.checkbox('Показати адреси книгарень')
address = pd.DataFrame({
    'Книгарня': [ data_order.iloc[n]['market'] for n in range(0,len(data_order))],
    'Адреса': [data_order.iloc[n]['adress'] for n in range(0,len(data_order))],
    'Графік роботи': [data_order.iloc[n]['work schedule'] for n in range(0,len(data_order))],
    'Контакти': [data_order.iloc[n]['contacts'] for n in range(0,len(data_order))],
})

text = f"{address}"
if agree:
    st.write(address)

st.download_button(label='Завантажити', data=text)
