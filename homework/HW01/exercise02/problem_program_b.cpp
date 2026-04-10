#include <cstddef>
#include <vector>
#include <filesystem>
#include <fstream>
#include <iostream>
#include <set>
#include <random>
#include <chrono>
#include <ranges>
#include <numeric>
#include <cassert>
#include <nlohmann/json.hpp>

using Index = std::size_t;

/**
 * You are free to change the graph representation,
 * if you want, as long as the behavior of the program remains identical,
 * i.e., the probability with which a certain clique is selected is unchanged,
 * (under the idealized assumption that the RNG behaves truly randomly
 * instead of having a fixed seed).
 */
class Graph {
  public:
    explicit Graph(std::vector<std::vector<Index>> adjacencies) :
        m_adjacencies(std::move(adjacencies))
    {
        // the adjacency list should be sorted
        assert(
            std::ranges::all_of(m_adjacencies, [] (const std::vector<Index>& neighbors) {
                return std::ranges::is_sorted(neighbors);
            })
        );
        // the adjacency list should not contain duplicates
        assert(
            std::ranges::all_of(m_adjacencies, [] (const std::vector<Index>& neighbors) {
                return std::ranges::adjacent_find(neighbors) == neighbors.end();
            })
        );
        // the adjacency list should stay in range
        std::size_t num_vertices = m_adjacencies.size();
        assert(
            std::ranges::all_of(m_adjacencies, [num_vertices] (const std::vector<Index>& neighbors) {
                return std::ranges::all_of(neighbors, [num_vertices] (Index v) {
                    return v < num_vertices;
                });
            })
        );
    }

    const std::vector<Index>& neighbors(Index v) const {
        return m_adjacencies[v];
    }

    std::size_t n() const {
        return m_adjacencies.size();
    }

  private:
    std::vector<std::vector<Index>> m_adjacencies;
};

/**
 * Load a graph from a file.
 * This may be quite slow; we do not care about
 * the time it takes here.
 */
Graph load_graph(const std::filesystem::path& path) {
    std::ifstream input;
    input.exceptions(std::ios::failbit | std::ios::badbit);
    input.open(path);
    input.exceptions(std::ios::badbit);
    auto parsed = nlohmann::json::parse(input);
    auto vec = parsed.get<std::vector<std::vector<Index>>>();
    return Graph(std::move(vec));
}

/**
 * Computes a greedy clique as follows:
 * - iterate through the vertices of the graph in random order,
 * - add the next vertex in that order if it is still 
 *   a viable extension of the current clique.
 */
class GreedyClique {
  public:
    GreedyClique(const Graph* graph) :
        rng(1337),
        graph(graph),
        order(graph->n())
    {
        std::iota(order.begin(), order.end(), Index(0));
    }

    const std::vector<Index>& random_order_greedy_clique() {
        std::ranges::shuffle(order, rng);
        Index v0 = order[0];
        clique_members.assign(1, v0);
        possible_extensions.clear();
        possible_extensions.insert(graph->neighbors(v0).begin(), 
                                   graph->neighbors(v0).end());
        for(Index v : order | std::views::drop(1)) {
            if(!possible_extensions.count(v)) {
                continue;
            }
            clique_members.push_back(v);
            // remove all the elements from possible_extensions that
            // are not neighbors of v, using the fact that the adjacency
            // list is sorted
            const auto& neighbors = graph->neighbors(v);
            auto next_neighbor_it = neighbors.begin();
            auto end_neighbor_it = neighbors.end();
            for(auto it = possible_extensions.begin(); 
                it != possible_extensions.end();) 
            {
                // binary search for *it in remaining neighbors
                auto first_not_lower = std::lower_bound(
                    next_neighbor_it, end_neighbor_it, *it);
                if(first_not_lower == end_neighbor_it) {
                    // all remaining possible extensions are larger than any neighbor
                    possible_extensions.erase(it, possible_extensions.end());
                    break;
                }
                // restrict future binary searches to the remaining neighbors
                next_neighbor_it = first_not_lower;
                if(*first_not_lower == *it) {
                    // *it is a neighbor, keep it as possible extension
                    ++it;
                } else {
                    // *it is not a neighbor, remove it from possible extensions
                    it = possible_extensions.erase(it);
                }
            }
            if(possible_extensions.empty()) break;
        }
        return clique_members;
    }

  private:
    const Graph* graph;
    std::mt19937_64 rng;
    std::vector<Index> order;
    std::set<Index> possible_extensions;
    std::vector<Index> clique_members;
};

std::vector<Index> greedy_clique(const Graph& graph, std::size_t num_attempts) {
    GreedyClique greedy_clique(&graph);
    std::vector<Index> best_clique;
    for(std::size_t i = 0; i < num_attempts; ++i) {
        const auto& clique = greedy_clique.random_order_greedy_clique();
        if(clique.size() > best_clique.size()) {
            best_clique = clique;
        }
    }
    return best_clique;
}

void validate_clique(const Graph& graph, const std::vector<Index>& clique) {
    for(std::size_t i = 0; i < clique.size(); ++i) {
        for(std::size_t j = i + 1; j < clique.size(); ++j) {
            Index v1 = clique[i];
            Index v2 = clique[j];
            const auto& neighbors = graph.neighbors(v1);
            if(!std::binary_search(neighbors.begin(), neighbors.end(), v2)) {
                std::cerr << "You done goofed, the clique is invalid:\n";
                std::cerr << "vertices " << v1 << " and " << v2 
                          << " are not connected!\n";
                std::exit(1);
            }
        }
    }
}

int main(int argc, char** argv) {
    if(argc != 2) {
        std::cerr << "Expected JSON graph file as single argument!\n";
        return 1;
    }

    Graph input_graph = load_graph(argv[1]);
    auto before = std::chrono::steady_clock::now();
    std::vector<Index> result = greedy_clique(input_graph, 50'000);
    auto after = std::chrono::steady_clock::now();
    std::cout << "Clique with " << result.size() << " vertices!\n";
    for(Index v : result) {
        std::cout << "\t" << v << std::endl;
    }
    std::cout << "Found in " << 
        std::chrono::duration_cast<std::chrono::duration<double>>(after - before).count() << " seconds.\n";
    validate_clique(input_graph, result);
    return 0;
}
