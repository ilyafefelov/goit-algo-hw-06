import h5py
import matplotlib.pyplot as plt
import numpy as np
import random
import networkx as nx

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
graph_subset = {station_names[i]: {} for i in station_indices}

# Додамо ребра (зв'язки між станціями) для ненульових значень
for edge in edges_subset:
    i, j, weight = edge
    graph_subset[station_names[i]][station_names[j]] = weight
    graph_subset[station_names[j]][station_names[i]] = weight

# Аналізуємо характеристики графа
num_nodes_subset = len(graph_subset)
num_edges_subset = sum(len(edges) for edges in graph_subset.values()) // 2
degrees_subset = {node: len(edges) for node, edges in graph_subset.items()}
edge_weights = {(node, neighbor): weight for node, edges in graph_subset.items() for neighbor, weight in edges.items()}

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
        shortest_path, path_length = dijkstra(graph_subset, from_station, to_station)
        print(f"\nShortest path from {from_station} to {to_station}: {shortest_path}")
        print(f"Path length: {path_length}")

        with open("readme.md", "w") as file:
            file.write(f"\n### Shortest Path from {from_station} to {to_station}\n")
            file.write(f"Path: {shortest_path}\n")
            file.write(f"Path length: {path_length}\n")

    except Exception as e:
        print(f"No path found between {from_station} and {to_station}.")
        with open("readme.md", "a") as file:
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
G = nx.Graph()
for node, edges in graph_subset.items():
    G.add_node(node)
    for neighbor, weight in edges.items():
        G.add_edge(node, neighbor, weight=weight)

pos = nx.spring_layout(G, k=0.15, iterations=20)
plt.figure(figsize=(12, 12))
nx.draw(G, pos, with_labels=True, node_size=50, node_color="skyblue", font_size=8, width=2, edge_color="black")

# Додавання ваг ребер
edge_labels = nx.get_edge_attributes(G, 'weight')
nx.draw_networkx_edge_labels(G, pos, edge_labels=edge_labels)

plt.title(f"Subset of London Underground Network ({num_stations} Stations)")
plt.show()

# Реалізація алгоритмів BFS, DFS та Дейкстри
def bfs(graph, start):
    visited = []
    queue = [start]

    while queue:
        node = queue.pop(0)
        if node not in visited:
            visited.append(node)
            queue.extend(set(graph[node]) - set(visited))
    return visited

def dfs(graph, start):
    visited = []
    stack = [start]

    while stack:
        node = stack.pop()
        if node not in visited:
            visited.append(node)
            stack.extend(set(graph[node]) - set(visited))
    return visited

def dijkstra(graph, start, goal):
    shortest_distance = {}
    predecessor = {}
    unseen_nodes = dict(graph)
    infinity = float('inf')
    path = []
    for node in unseen_nodes:
        shortest_distance[node] = infinity
    shortest_distance[start] = 0

    while unseen_nodes:
        min_node = None
        for node in unseen_nodes:
            if min_node is None:
                min_node = node
            elif shortest_distance[node] < shortest_distance[min_node]:
                min_node = node

        for child_node, weight in graph[min_node].items():
            if weight + shortest_distance[min_node] < shortest_distance[child_node]:
                shortest_distance[child_node] = weight + shortest_distance[min_node]
                predecessor[child_node] = min_node
        unseen_nodes.pop(min_node)

    current_node = goal
    while current_node != start:
        try:
            path.insert(0, current_node)
            current_node = predecessor[current_node]
        except KeyError:
            print('Path not reachable')
            break
    path.insert(0, start)
    if shortest_distance[goal] != infinity:
        return path, shortest_distance[goal]
    return None, None

# Реалізація алгоритмів DFS і BFS
start_node = station_names[station_indices[0]]
dfs_path = dfs(graph_subset, start_node)
bfs_path = bfs(graph_subset, start_node)

# Реалізація алгоритму Дейкстри
dijkstra_path = {}
for target in graph_subset:
    if target != start_node:
        path, _ = dijkstra(graph_subset, start_node, target)
        if path:
            dijkstra_path[target] = path

# Порівняння результатів і обґрунтування
comparison_results = []

# Порівняння DFS і BFS
common_nodes_dfs_bfs = set(dfs_path).intersection(set(bfs_path))

comparison_results.append("### Comparison of DFS and BFS Paths\n")
comparison_results.append(f"DFS Path: {dfs_path}\n")
comparison_results.append(f"BFS Path: {bfs_path}\n")
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
    for node in dfs_path:
        file.write(f"{node}\n")
    file.write("\n## BFS Path\n")
    for node in bfs_path:
        file.write(f"{node}\n")
    file.write("\n## Dijkstra Shortest Paths\n")
    for target, path in dijkstra_path.items():
        file.write(f"{start_node} to {target}: {path}\n")
    file.write("\n## Comparison and Explanation\n")
    file.writelines(comparison_results)

# Виводимо результати алгоритмів на консоль
print("\nDFS Path:")
for node in dfs_path:
    print(node)

print("\nBFS Path:")
for node in bfs_path:
    print(node)

print("\nDijkstra Shortest Paths:")
for target, path in dijkstra_path.items():
    print(f"{start_node} to {target}: {path}")

