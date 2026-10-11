// Convert raw signed-int8 Cartesian rows (48 columns) to CSV on standard output.
// Build: g++ -O3 -std=c++17 vector_data_csv.cpp -o vector-data-csv
// Usage: vector-data-csv section.i8 | pigz -p 8 > section.csv.gz
#include <array>
#include <charconv>
#include <cstdint>
#include <fstream>
#include <iostream>
#include <stdexcept>

int main(int argc, char** argv) {
    try {
        if (argc != 2) throw std::runtime_error("Usage: vector-data-csv input.i8");
        std::ifstream input(argv[1], std::ios::binary);
        if (!input) throw std::runtime_error("Cannot open input");
        std::array<std::int8_t, 48> row;
        std::array<char, 48 * 5> text;
        while (input.read(reinterpret_cast<char*>(row.data()), row.size())) {
            char* next = text.data();
            for (int i = 0; i < 48; ++i) {
                next = std::to_chars(next, text.data() + text.size(), static_cast<int>(row[i])).ptr;
                *next++ = i == 47 ? '\n' : ',';
            }
            std::cout.write(text.data(), next - text.data());
        }
        if (input.gcount() || !input.eof()) throw std::runtime_error("Incomplete row or read error");
        std::cout.flush();
        if (!std::cout) throw std::runtime_error("CSV write failed");
        return 0;
    } catch (const std::exception& error) {
        std::cerr << error.what() << std::endl;
        return 1;
    }
}
