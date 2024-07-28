import h5py
import networkx as nx
import matplotlib.pyplot as plt
import numpy as np  # Додаємо імпорт numpy

# Завантаження MAT файлу
file_path = 'london_underground_clean.mat'
data = h5py.File(file_path, 'r')

# Функція для витягування станцій
def extract_station_names(data):
    station_names = []
    for ref in data['Station_Names']:
        ref_obj = data[ref]
        station_name = ''.join([chr(c[0]) for c in ref_obj[:]])
        station_names.append(station_name)
    return station_names

# Функція для витягування зв'язків для підмножини станцій
def extract_edges_check_zeros(subset_size, start_index=0):
    edges_subset = []
    for i in range(start_index, start_index + subset_size):
        for j in range(start_index, start_index + subset_size):
            if i < data['Labelled_Network'].shape[0] and j < data['Labelled_Network'].shape[1]:
                ref = data['Labelled_Network'][i, j]
                value = data[ref][0]
                if value != 0.0:
                    if isinstance(value, np.ndarray):
                        value = value[0]
                    edges_subset.append((i, j, value))
    return edges_subset

# Витягуємо назви станцій
station_names = extract_station_names(data)

# Параметри
subset_size = 100

# Витягуємо зв'язки для перших 100 станцій
edges_subset_100 = extract_edges_check_zeros(subset_size)

# Створимо граф для перших 100 станцій
graph_subset_100 = nx.Graph()

# Додамо вузли (станції)
for station in station_names[:subset_size]:
    graph_subset_100.add_node(station)

# Додамо ребра (зв'язки між станціями) для ненульових значень
for edge in edges_subset_100:
    i, j, weight = edge
    graph_subset_100.add_edge(station_names[i], station_names[j], weight=weight)

# Візуалізуємо граф
plt.figure(figsize=(12, 12))
pos = nx.spring_layout(graph_subset_100, k=0.15, iterations=20)
nx.draw(graph_subset_100, pos, with_labels=True, node_size=50, node_color="skyblue", font_size=8, width=2, edge_color="black")
plt.title("Subset of London Underground Network (First 100 Stations)")
plt.show()

# Аналізуємо характеристики графа
num_nodes_subset_100 = graph_subset_100.number_of_nodes()
num_edges_subset_100 = graph_subset_100.number_of_edges()
degrees_subset_100 = dict(graph_subset_100.degree())

print(f'Number of nodes: {num_nodes_subset_100}')
print(f'Number of edges: {num_edges_subset_100}')
print(f'Degrees: {degrees_subset_100}')
