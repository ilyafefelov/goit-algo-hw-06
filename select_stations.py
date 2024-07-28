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
elif selection_method == "end":
    station_indices = list(range(total_stations - num_stations, total_stations))
elif selection_method == "index":
    start_index = int(input(f"Enter the start index (0 to {total_stations - num_stations}): "))
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


# Додаткове запитання для користувача про пошук найкоротших шляхів між заданими станціями
search_paths = input("Do you want to find the shortest path between specific stations? (yes/no): ").strip().lower()
if search_paths == "yes":
    from_station = input("Enter the name or index of the starting station: ").strip()
    to_station = input("Enter the name or index of the ending station: ").strip()

    if from_station.isdigit():
        from_station = station_names[int(from_station)]
    if to_station.isdigit():
        to_station = station_names[int(to_station)]

    try:
        shortest_path = nx.shortest_path(graph_subset, source=from_station, target=to_station, weight='weight')
        path_length = nx.shortest_path_length(graph_subset, source=from_station, target=to_station, weight='weight')
        print(f"\nShortest path from {from_station} to {to_station}: {shortest_path}")
        print(f"Path length: {path_length}")

        with open("readme.md", "w") as file:
            file.write(f"\n### Shortest Path from {from_station} to {to_station}\n")
            file.write(f"Path: {shortest_path}\n")
            file.write(f"Path length: {path_length}\n")

    except nx.NetworkXNoPath:
        print(f"No path found between {from_station} and {to_station}.")
        with open("readme.md", "wa") as file:
            file.write(f"\n### Shortest Path from {from_station} to {to_station}\n")
            file.write(f"No path found.\n")

print("\nResults saved to 'readme.md'.")

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
print(f"# Analysis Results for {num_stations} Stations")
print(f"Number of nodes: {num_nodes_subset}")
print(f"Number of edges: {num_edges_subset}")
print("Degrees:")
for node, degree in degrees_subset.items():
    print(f"{node}: {degree}")
print("\n--------------")
print("## Edge Weights:")
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

# Реалізація алгоритмів DFS і BFS
start_node = station_names[station_indices[0]]
dfs_path = list(nx.dfs_edges(graph_subset, source=start_node))
bfs_path = list(nx.bfs_edges(graph_subset, source=start_node))

# Реалізація алгоритму Дейкстри
dijkstra_path = nx.single_source_dijkstra_path(graph_subset, source=start_node)

# Порівняння результатів і обґрунтування
comparison_results = []

# Порівняння DFS і BFS
dfs_path_nodes = [edge[1] for edge in dfs_path]
bfs_path_nodes = [edge[1] for edge in bfs_path]
common_nodes_dfs_bfs = set(dfs_path_nodes).intersection(set(bfs_path_nodes))

comparison_results.append("### Comparison of DFS and BFS Paths\n")
comparison_results.append(f"DFS Path: {dfs_path_nodes}\n")
comparison_results.append(f"BFS Path: {bfs_path_nodes}\n")
comparison_results.append("### Common Nodes\n")
comparison_results.append(f"Common Nodes in DFS and BFS Paths: {common_nodes_dfs_bfs}\n")
comparison_results.append("### DFS and BFS Explanation\n")
comparison_results.append("\nDFS (Depth-First Search) explores as far as possible along each branch before backtracking, which means it goes deep into the graph before moving horizontally. This can lead to longer paths and cycles being discovered before moving to the next branch. BFS (Breadth-First Search), on the other hand, explores all the neighbors of a node before moving on to the next level of nodes. This leads to discovering the shortest path in terms of the number of edges in an unweighted graph.\n")

# Порівняння з алгоритмом Дейкстри
comparison_results.append("### Dijkstra Shortest Paths\n")
for target, path in dijkstra_path.items():
    comparison_results.append(f"{start_node} to {target}: {path}\n")

comparison_results.append("### Dijkstra Explanation\n")
comparison_results.append("\nDijkstra's algorithm finds the shortest path between nodes in a graph considering edge weights. This algorithm ensures the shortest total path cost from the source to any other node, which is not necessarily the case for DFS or BFS since they do not consider edge weights.\n")

# Записуємо результати порівняння у файл readme.md
with open("readme.md", "a") as file:
    file.write(f"# Analysis and Pathfinding Results for {num_stations} Stations\n")
    file.write("## DFS Path\n")
    for edge in dfs_path:
        file.write(f"{edge}\n")
    file.write("\n## BFS Path\n")
    for edge in bfs_path:
        file.write(f"{edge}\n")
    file.write("\n## Dijkstra Shortest Paths\n")
    for target, path in dijkstra_path.items():
        file.write(f"{start_node} to {target}: {path}\n")
    file.write("\n## Comparison and Explanation\n")
    file.writelines(comparison_results)

# Виводимо результати алгоритмів на консоль
print("\nDFS Path:")
for edge in dfs_path:
    print(edge)

print("\nBFS Path:")
for edge in bfs_path:
    print(edge)

print("\nDijkstra Shortest Paths:")
for target, path in dijkstra_path.items():
    print(f"{start_node} to {target}: {path}")


