// A separately implemented exact verifier. C++17; no Python or CAS dependency.
#include <algorithm>
#include <cstdint>
#include <fstream>
#include <iostream>
#include <set>
#include <sstream>
#include <stdexcept>
#include <string>
#include <vector>
using Word = std::uint64_t;
void require(bool condition, const std::string& message) {
    if (!condition) throw std::runtime_error(message);
}
int weight(Word x) { return __builtin_popcountll(x); }
std::vector<Word> read_words(const std::string& path, int n) {
    std::ifstream input(path);
    require(input.good(), "Cannot open input");
    std::vector<Word> result;
    std::string line;
    while (std::getline(input, line)) {
        auto begin = line.find_first_not_of(" \t\r");
        if (begin == std::string::npos || line[begin] == '#' || line[begin] == '$') continue;
        std::istringstream row(line.substr(begin));
        std::string token, extra;
        row >> token;
        require(!(row >> extra), "Unexpected extra token");
        require(!token.empty() && token.find_first_not_of("0123456789abcdefABCDEF") == std::string::npos,
                "Invalid unsigned hexadecimal word");
        std::size_t used = 0;
        Word value = std::stoull(token, &used, 16);
        require(used == token.size() && (value >> n) == 0, "Word out of range");
        result.push_back(value);
    }
    require(!result.empty(), "Empty input");
    return result;
}
int main(int argc, char** argv) {
    try {
        require(argc == 9, "Usage: checker n n0 A N top_size kernel reps supports");
        int n = std::stoi(argv[1]), n0 = std::stoi(argv[2]);
        require(32 <= n0 && n0 <= n && n <= 63, "Invalid dimensions");
        Word expected_a = std::stoull(argv[3]), expected_n = std::stoull(argv[4]);
        Word expected_top = std::stoull(argv[5]);
        auto generators = read_words(argv[6], n0);
        auto reps = read_words(argv[7], n0);
        auto supports = read_words(argv[8], n);
        // Low-pivot elimination differs from the Python high-pivot reduction.
        std::vector<Word> pivots(n0, 0), basis;
        for (Word x : generators) {
            for (int i = 0; i < n0 && x; ++i) {
                if (!((x >> i) & 1)) continue;
                if (pivots[i]) x ^= pivots[i];
                else { pivots[i] = x; basis.push_back(x); break; }
            }
        }
        require(!basis.empty() && basis.size() <= 22, "Kernel rank unsupported");
        std::vector<Word> words{0};
        for (Word b : basis) {
            auto count = words.size();
            for (std::size_t i = 0; i < count; ++i) words.push_back(words[i] ^ b);
        }
        require(std::set<Word>(words.begin(), words.end()).size() == words.size(), "Span duplicates");
        int kernel_distance = n0 + 1;
        for (Word w : words) if (w) kernel_distance = std::min(kernel_distance, weight(w));
        int distance = kernel_distance;
        for (std::size_t i = 0; i < reps.size(); ++i)
            for (std::size_t j = 0; j < i; ++j) {
                int between = n0 + 1;
                for (Word w : words) between = std::min(between, weight(w ^ reps[i] ^ reps[j]));
                require(between > 0, "Repeated affine coset");
                distance = std::min(distance, between);
            }
        require(4 * distance >= n0, "Insufficient top distance");
        require(std::set<Word>(supports.begin(), supports.end()).size() == supports.size(), "Duplicate support");
        int maximum = 0;
        for (Word w : supports) require(weight(w) == 8, "Support weight is not eight");
        for (std::size_t i = 0; i < supports.size(); ++i)
            for (std::size_t j = 0; j < i; ++j) {
                int intersection = weight(supports[i] & supports[j]);
                require(intersection <= 4, "Support intersection exceeds four");
                maximum = std::max(maximum, intersection);
            }
        int even_signs = 0;
        for (int s = 0; s < 256; ++s) if (weight(s) % 2 == 0) ++even_signs;
        require(even_signs == 128, "Parity enumeration failed");
        Word top = words.size() * reps.size();
        Word total = top + even_signs * supports.size() + Word(2) * n * (n - 1);
        require(supports.size() == expected_a && top == expected_top && total == expected_n,
                "Claim cardinalities do not match");
        std::cout << "{\"valid\":true,\"dimension\":" << n << ",\"lower_bound\":" << total
                  << ",\"support_size\":" << supports.size() << ",\"kernel_rank\":" << basis.size()
                  << ",\"kernel_min_distance\":" << kernel_distance << ",\"top_min_distance\":" << distance
                  << ",\"cosets\":" << reps.size() << ",\"top_size\":" << top
                  << ",\"max_support_intersection\":" << maximum << "}\n";
    } catch (const std::exception& error) {
        std::cerr << "REJECTED: " << error.what() << '\n';
        return 1;
    }
}
