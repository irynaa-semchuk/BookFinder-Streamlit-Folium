import pandas as pd
from config import hosts
from itertools import product
import streamlit as st
from math import inf


def repeat_placements(m, n):  # генерує список розміщень з повтореннями
    return [tpl for tpl in product(range(m), repeat=n)]


def get_order_list(filename, sep="---"):
    id_, list_ = 0, []
    with open(filename, encoding="utf-8") as order:
        for line in order:
            info = line.split(sep)
            list_.append({"id": id_, "author": info[0].strip(),
                          "title": info[1].strip(),
                          "amount": int(info[2].strip())})
            id_ += 1
    return list_


order_list_2 = get_order_list("order.txt")


def price(price_info, delivery_info, placement, order_list):  # повертає ціну і склад замовлення
    markets = list(hosts.keys())  # індексом магазину є його індекс у списку
    shop_numbers, book_numbers = len(price_info[0]), len(price_info)
    orders = [[] for _ in range(shop_numbers)]
    for i in range(len(placement)):  # формуємо склад замовлення
        orders[placement[i]].append(i)
    # обчислюємо вартість замовлення:
    prices = [0 for _ in range(shop_numbers)]
    for shop in range(shop_numbers):
        for book in orders[shop]:
            try:
                amount = order_list[book]['amount']
                prices[shop] += price_info[book][markets[shop]][0] * amount
            except:
                return False  # такий варіант замовлення неможливий
        # уточнюємо вартість замовлення з урахуванням доставки:
        if orders[shop]:
            if prices[shop] < delivery_info[markets[shop]][1]:
                prices[shop] += delivery_info[markets[shop]][0]
    return sum(prices), orders

def check_book(price_info, order_list):
    list_del_price = []
    list_del_order = []
    for key, value in list(price_info.items()):
        if value['bookclub.ua'] is None and value['yakaboo.ua'] is None:
            list_del_price.append(key)
            list_del_order.append(order_list[key]['id'])
            notfind = order_list[key]['title']
            st.error(f'В жодній книгарні немає книги <<{notfind}>> 📗📢❌')
            del price_info[key]
            order_list.remove(order_list[key])
        for id in list_del_price:
            if id < key:
                price_info[key - 1] = price_info.pop(key)
    for book in range(len(order_list)):
        for id in list_del_order:
            if id < order_list[book]['id']:
                element = order_list[book]['id']
                order_list[book]['id'] = element - 1
    return price_info,order_list


def display(order_state, markets_state, price_info_state, delivery_info_state, order_list, col0, list_img0):
    total_price = 0
    for market_id in range(len(order_state)):
        if not order_state[market_id]:
            continue
        with col0[market_id]:
            st.image(list_img0[market_id], width=350)
            st.header(f"{markets_state[market_id]}:")
            market_total = 0
            for item in order_state[market_id]:
                title = order_list[item]["title"]
                author = order_list[item]["author"]
                amount = order_list[item]["amount"]
                price = price_info_state[item][markets_state[market_id]][0]
                total = price * amount
                market_total += total
                st.write(f"\t*<<{title}>> {author}* : **{amount} * {price} = {total} грн.**")
                st.write(f"\t  - **Кількість екземплярів книги : {amount}**")
                st.write(f"\t  - **Ціна за один кеземпляр книги : {price}**")
                if price_info_state[item][markets_state[market_id]][1].strip('https:https:'):
                    url = f"https:{price_info_state[item][markets_state[market_id]][1].strip('https:')}"
                    st.write(f"[Замовити книгу]({url})📖")
            if market_total < delivery_info_state[markets_state[market_id]][1]:
                delivery = delivery_info_state[markets_state[market_id]][0]
            else:
                delivery = 0.
            st.warning(f"\tДоставка: {delivery} грн.")
            total_price += market_total + delivery
    st.info(f"Загальна вартість замовлення: {total_price} грн.")


def get_delivery_info(delivery_info_state):
    st.write("Вартість доставки для служби доставки “Нова пошта”")
    delivery = ''
    dict_delivery = delivery_info_state.copy()
    for key, value in dict_delivery.items():
        if value[1] is inf:
            price_delivery = list(value)
            price_delivery[1] = 0
            not_inf = tuple(price_delivery)
            dict_delivery[key] = not_inf
            delivery = pd.DataFrame({
        'Книгарня': [key for key in delivery_info_state.keys() ],
        'Вартість доставки': [delivery_info_state.get(key)[0] for key in delivery_info_state.keys()],
        'Сума після якої доставка безкоштовна': [dict_delivery.get(key)[1]  for key in dict_delivery.keys()]})
    st.write(delivery)


def get_book_info(price_info_state, order_list):
    list_markert = ["bookclub.ua", "yakaboo.ua"]
    shop1, shop2 = st.columns(2)
    data_info = {"bookclub.ua":shop1,"yakaboo.ua": shop2,}
    for m in list_markert:
        with data_info[m]:
            st.write(f'**{m}**')
    try:
        for key, data in price_info_state.items():
            for site, info in data.items():
                with data_info[site]:
                    if info is None:
                        st.write("Книга не знайдена ❌")
                        continue
                    st.write(f'{order_list[key]["title"]} - {info[0]}')
    except IndexError:
        st.write('Немає даних')

def marker_info(name, order_state, markets_state, price_info_state, order_list):
    for market_id in range(len(order_state)):
        if not order_state[market_id]:
            continue
        if markets_state[market_id] == str(name):
            for item in order_state[market_id]:
                return f"<ul class='list-group'><li class='list-group-item active'>{markets_state[market_id]}</li>", [
                f"<li class='list-group-item'> <<{order_list[item]['title']}>> " \
                f"{order_list[item]['author']}: {price_info_state[item][markets_state[market_id]][0]} </li> </ul>"
                    for item in order_state[market_id]]
