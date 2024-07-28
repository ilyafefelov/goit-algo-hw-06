import h5py
import networkx as nx
import matplotlib.pyplot as plt
import numpy as np
import random

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
def extract_edges_check_zeros(station_indices):
    edges_subset = []
    for i in station_indices:
        for j in station_indices:
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
total_stations = len(station_names)

# Запитуємо користувача
print(f"There are {total_stations} stations available.")
num_stations = int(input("Enter the number of stations to analyze (or enter 0 to analyze all stations): "))
if num_stations == 0 or num_stations > total_stations:
    num_stations = total_stations

selection_method = input("Select method of selection (random, start, end, index): ").strip().lower()

if selection_method == "random":
    station_indices = random.sample(range(total_stations), num_stations)
elif selection_method == "start":
    station_indices = list(range(num_stations))
elif selection_method == "end":
    station_indices = list(range(total_stations - num_stations, total_stations))
elif selection_method is type(int):
    start_index = selection_method
    station_indices = list(range(start_index, start_index + num_stations))
else:  # Default to 'start'
    station_indices = list(range(num_stations))

# Витягуємо зв'язки для обраних станцій
edges_subset = extract_edges_check_zeros(station_indices)

# Створимо граф для обраних станцій
graph_subset = nx.Graph()

# Додамо вузли (станції)
for i in station_indices:
    graph_subset.add_node(station_names[i])

# Додамо ребра (зв'язки між станціями) для ненульових значень
for edge in edges_subset:
    i, j, weight = edge
    graph_subset.add_edge(station_names[i], station_names[j], weight=weight)

# Аналізуємо характеристики графа
num_nodes_subset = graph_subset.number_of_nodes()
num_edges_subset = graph_subset.number_of_edges()
degrees_subset = dict(graph_subset.degree())
edge_weights = nx.get_edge_attributes(graph_subset, 'weight')

# Записуємо результати в файл
with open("results.md", "w") as file:
    file.write(f"## Analysis Results for {num_stations} Stations\n")
    file.write(f"Number of nodes: {num_nodes_subset}\n")
    file.write(f"Number of edges: {num_edges_subset}\n")
    file.write("Degrees:\n")
    for node, degree in degrees_subset.items():
        file.write(f"{node}: {degree}\n")
    file.write("Edge Weights:\n")
    for edge, weight in edge_weights.items():
        file.write(f"{edge}: {weight}\n")

# Виводимо результати на консоль
print(f"Analysis Results for {num_stations} Stations")
print(f"Number of nodes: {num_nodes_subset}")
print(f"Number of edges: {num_edges_subset}")
print("Degrees:")
for node, degree in degrees_subset.items():
    print(f"{node}: {degree}")
print("Edge Weights:")
for edge, weight in edge_weights.items():
    print(f"{edge}: {weight}")

print("\nResults saved to 'results.md'.")
print("\n--------------------")
print("Building graph...")

# Візуалізуємо граф з відображенням ваг при наведенні
pos = nx.spring_layout(graph_subset, k=0.15, iterations=20)
plt.figure(figsize=(12, 12))
nx.draw(graph_subset, pos, with_labels=True, node_size=50, node_color="skyblue", font_size=8, width=2, edge_color="black")

# Додавання ваг ребер
edge_labels = nx.get_edge_attributes(graph_subset, 'weight')
nx.draw_networkx_edge_labels(graph_subset, pos, edge_labels=edge_labels)

plt.title(f"Subset of London Underground Network ({num_stations} Stations)")
plt.show()
