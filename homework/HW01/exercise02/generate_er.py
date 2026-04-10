import argparse
import json
import random


rng = random.Random(open("/dev/urandom", "rb").read(32))


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Generate Erdös-Renyi graphs for the problem program.")
    parser.add_argument("-n", "--num-vertices", type=int, default=1000, help="Number of vertices in the graph.")
    parser.add_argument("-p", "--edge-probability", type=float, default=0.01, help="Probability of edge creation.")
    parser.add_argument("-o", "--output-file", type=str, default="er_graph.json", help="Output file for the generated graph.")

    args = parser.parse_args()
    n = args.num_vertices
    p = args.edge_probability
    graph = [[] for _ in range(n)]
    for i in range(n):
        for j in range(i + 1, n):
            if rng.random() < p:
                graph[i].append(j)
                graph[j].append(i)
    for neighbors in graph:
        neighbors.sort()
    with open(args.output_file, "w") as f:
        json.dump(graph, f)
