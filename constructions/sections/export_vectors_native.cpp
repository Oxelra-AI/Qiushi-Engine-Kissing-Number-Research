// Enumerate candidate section vectors and retain only exact integer-norm rows.
// Build: g++ -O3 -std=c++17 -fopenmp export_vectors_native.cpp -o export-vectors
// Input: prepared geometry JSON. Output: signed-int8 Cartesian row shards.
#include <algorithm>
#include <array>
#include <atomic>
#include <chrono>
#include <cmath>
#include <cstdint>
#include <filesystem>
#include <fstream>
#include <iostream>
#include <limits>
#include <stdexcept>
#include <string>
#include <vector>
#include <omp.h>
#include <boost/property_tree/ptree.hpp>
#include <boost/property_tree/json_parser.hpp>

namespace pt = boost::property_tree;
using Clock = std::chrono::steady_clock;
using Row = std::array<int, 48>;
using RealRow = std::array<long double, 48>;

long double rational(const std::string& text) {
    const auto slash = text.find('/');
    if (slash == std::string::npos) return std::stold(text);
    return std::stold(text.substr(0, slash)) / std::stold(text.substr(slash + 1));
}

struct Component {
    RealRow center{};
    Row offset{};
    long double radius;
};
struct Geometry {
    int n, norm;
    std::uint64_t expected;
    std::array<RealRow, 48> lower{};
    RealRow diagonal{};
    std::array<Row, 48> transform{};
    std::vector<Component> components;
    explicit Geometry(const std::string& name) {
        pt::ptree tree;
        pt::read_json(name, tree);
        n = tree.get<int>("dimension");
        norm = tree.get<int>("squared_norm");
        expected = tree.get<std::uint64_t>("expected_rows");
        if (n <= 0 || n > 48 || norm <= 0 || norm > 127 * 127)
            throw std::runtime_error("Invalid geometry dimensions or norm");
        std::array<RealRow, 48> gram{};
        int i = 0;
        for (const auto& r : tree.get_child("gram")) {
            int j = 0;
            for (const auto& x : r.second) gram.at(i).at(j++) = rational(x.second.data());
            if (j != n) throw std::runtime_error("Invalid Gram row");
            ++i;
        }
        if (i != n) throw std::runtime_error("Invalid Gram size");
        for (i = 0; i < n; ++i) {
            lower[i][i] = 1;
            diagonal[i] = gram[i][i];
            for (int k = 0; k < i; ++k)
                diagonal[i] -= lower[i][k] * lower[i][k] * diagonal[k];
            if (diagonal[i] <= 0) throw std::runtime_error("Nonpositive Gram pivot");
            for (int j = i + 1; j < n; ++j) {
                long double value = gram[j][i];
                for (int k = 0; k < i; ++k)
                    value -= lower[j][k] * lower[i][k] * diagonal[k];
                lower[j][i] = value / diagonal[i];
            }
        }
        i = 0;
        for (const auto& r : tree.get_child("transform")) {
            int j = 0;
            for (const auto& x : r.second) transform.at(i).at(j++) = x.second.get_value<int>();
            if (j != 48) throw std::runtime_error("Invalid Cartesian row");
            ++i;
        }
        if (i != n) throw std::runtime_error("Invalid transform size");
        for (const auto& item : tree.get_child("components")) {
            Component c;
            i = 0;
            for (const auto& x : item.second.get_child("center")) c.center.at(i++) = rational(x.second.data());
            if (i != n) throw std::runtime_error("Invalid centre");
            i = 0;
            for (const auto& x : item.second.get_child("offset")) c.offset.at(i++) = x.second.get_value<int>();
            if (i != 48) throw std::runtime_error("Invalid offset");
            c.radius = rational(item.second.get<std::string>("radius_squared"));
            components.push_back(c);
        }
    }
};
struct Task { Row row{}; long double remaining; int component; };

struct Search {
    const Geometry& g;
    const Component& c;
    Row row{};
    RealRow shifted{};
    std::uint64_t nodes = 0, rows = 0;
    std::ofstream* output;
    std::atomic<bool>& stopped;
    Clock::time_point deadline;

    void emit() {
        std::array<std::int64_t, 48> point{};
        for (int j = 0; j < 48; ++j) point[j] = c.offset[j];
        for (int i = 0; i < g.n; ++i) if (row[i])
            for (int j = 0; j < 48; ++j)
                point[j] += static_cast<std::int64_t>(row[i]) * g.transform[i][j];
        std::int64_t norm = 0;
        for (auto x : point) norm += x * x;
        if (norm != g.norm) return;
        std::array<std::int8_t, 48> packed;
        for (int j = 0; j < 48; ++j) packed[j] = static_cast<std::int8_t>(point[j]);
        output->write(reinterpret_cast<const char*>(packed.data()), 48);
        if (!*output) throw std::runtime_error("Coordinate write failed");
        ++rows;
    }

    void walk(int level, long double remaining, int split,
              std::vector<Task>* tasks, int component) {
        if (stopped.load(std::memory_order_relaxed)) return;
        ++nodes;
        if ((nodes & ((1u << 18) - 1)) == 0 && Clock::now() >= deadline) {
            stopped.store(true);
            return;
        }
        if (tasks && level == split) {
            tasks->push_back({row, remaining, component});
            return;
        }
        if (level < 0) { emit(); return; }
        if (remaining < 0) return;
        long double middle = c.center[level];
        for (int j = level + 1; j < g.n; ++j) middle -= g.lower[j][level] * shifted[j];
        const long double extent = std::sqrt(remaining / g.diagonal[level]);
        const int first = static_cast<int>(std::ceil(middle - extent));
        const int last = static_cast<int>(std::floor(middle + extent));
        for (int x = first; x <= last; ++x) {
            row[level] = x;
            shifted[level] = x - c.center[level];
            const long double displacement = x - middle;
            walk(level - 1, remaining - g.diagonal[level] * displacement * displacement,
                 split, tasks, component);
        }
    }
};

int main(int argc, char** argv) {
    try {
        if (argc < 3 || argc > 6)
            throw std::runtime_error("Usage: export-vectors geometry.json NEW_OUTPUT_DIR [threads=8] [tail_depth=7] [seconds=0]");
        const Geometry g(argv[1]);
        const std::filesystem::path destination(argv[2]);
        const int threads = argc > 3 ? std::stoi(argv[3]) : 8;
        const int depth = argc > 4 ? std::stoi(argv[4]) : 7;
        const int seconds = argc > 5 ? std::stoi(argv[5]) : 0;
        if (threads < 1 || depth < 1 || depth >= g.n || seconds < 0)
            throw std::runtime_error("Invalid enumeration controls");
        if (!std::filesystem::create_directory(destination))
            throw std::runtime_error("Output directory must be new");
        const auto start = Clock::now();
        const auto deadline = seconds ? start + std::chrono::seconds(seconds) : Clock::time_point::max();
        std::atomic<bool> stopped(false);
        std::vector<Task> tasks;
        const int split = g.n - depth - 1;
        for (unsigned c = 0; c < g.components.size(); ++c) {
            Search search{g, g.components[c], {}, {}, 0, 0, nullptr, stopped, deadline};
            // Rounded navigation can only propose candidates. Every accepted
            // row is checked in integers, then independently validated in bulk.
            search.walk(g.n - 1, g.components[c].radius + 1e-8L, split, &tasks, c);
        }
        std::cerr << "tasks=" << tasks.size() << " threads=" << threads << std::endl;
        std::atomic<std::uint64_t> total_rows(0), total_nodes(0), done(0);
        std::vector<std::uint64_t> component_rows(g.components.size(), 0);
        #pragma omp parallel num_threads(threads)
        {
            const int thread = omp_get_thread_num();
            std::ofstream output(destination / ("part-" + std::to_string(thread) + ".i8"), std::ios::binary);
            #pragma omp for schedule(dynamic, 1)
            for (std::size_t index = 0; index < tasks.size(); ++index) {
                if (Clock::now() >= deadline) stopped.store(true);
                if (stopped.load()) continue;
                const auto& task = tasks[index];
                const auto& c = g.components[task.component];
                Search search{g, c, task.row, {}, 0, 0, &output, stopped, deadline};
                for (int j = split + 1; j < g.n; ++j) search.shifted[j] = task.row[j] - c.center[j];
                search.walk(split, task.remaining, -2, nullptr, task.component);
                total_rows.fetch_add(search.rows);
                total_nodes.fetch_add(search.nodes);
                #pragma omp atomic update
                component_rows[task.component] += search.rows;
                auto finished = done.fetch_add(1) + 1;
                if (finished % 1000 == 0) {
                    #pragma omp critical
                    std::cerr << "tasks_done=" << finished << " rows=" << total_rows.load()
                              << " nodes=" << total_nodes.load() << std::endl;
                }
            }
        }
        pt::ptree report;
        report.put("dimension", g.n);
        report.put("rows", total_rows.load());
        report.put("nodes", total_nodes.load());
        report.put("expected_rows", g.expected);
        report.put("stopped", stopped.load());
        report.put("elapsed_seconds", std::chrono::duration<double>(Clock::now() - start).count());
        report.put("navigation", "long-double LDL; enlarged radius; exact integer output norms");
        report.put("status", "candidate export; run verify_vector_binary.py before publication");
        pt::ptree counts;
        for (auto value : component_rows) { pt::ptree child; child.put("", value); counts.push_back({"", child}); }
        report.add_child("component_rows", counts);
        pt::write_json((destination / "enumeration.json").string(), report);
        std::cerr << "rows=" << total_rows.load() << " nodes=" << total_nodes.load()
                  << " seconds=" << report.get<double>("elapsed_seconds") << std::endl;
        return stopped.load() || total_rows.load() != g.expected ? 2 : 0;
    } catch (const std::exception& e) {
        std::cerr << e.what() << std::endl;
        return 1;
    }
}
