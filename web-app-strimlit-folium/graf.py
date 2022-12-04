from config import hosts


def build_adj_list(data, shop_list):
    books = len(data) # кількість книжок
    shops = len(shop_list) # кількість магазинів
    adj = {node: [] for node in range(books * shops + 2)} # дерево звузлами від 0-25
    for i in range(shops):
        if data[0][shop_list[i]]: # берем тільки по першій книжці
            adj[0].append(i + 1) # 0: [1, 3]
    for j in range(books - 1):
        for i in range(shops):
            for k in range(shops):
                if data[j + 1][shop_list[k]]:
                    adj[j * shops + i + 1].append((j + 1) * shops + k + 1) # заповнюється повністю дерево
    for i in range(shops):
        if data[books - 1][shop_list[i]]: # береться остання книжка
            adj[(books - 1) * shops + i + 1].append(books * shops + 1) # 23: [25], 24: [25]
    return adj



def route_to_order(route):
    markets = list(hosts.keys())  # індексом магазину є його індекс у списку
    order = []
    for node in route[:-1]:
        if node > len(markets):
            order.append((node - 1) % len(markets))
        else:
            order.append(node - 1)
    return order



