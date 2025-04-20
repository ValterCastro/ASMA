import heapq

def dijkstra(start, nodes):
    distances = {node: float("inf") for node in nodes}
    distances[start] = 0
    visited = set()
    queue = [(0, start)]

    while queue:
        current_dist, current_node = heapq.heappop(queue)
        if current_node in visited:
            continue
        visited.add(current_node)

        for edge in nodes[current_node].edge_list:
            neighbor = edge.B if edge.A == current_node else edge.A
            weight = float(edge.weight)
            distance = current_dist + weight
            if distance < distances[neighbor]:
                distances[neighbor] = distance
                heapq.heappush(queue, (distance, neighbor))

    return distances
