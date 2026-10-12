// Convert raw signed-int8 Cartesian rows to CSV (48 columns by default).
// Build: g++ -O3 -std=c++17 vector_data_csv.cpp -o vector-data-csv
// Usage: vector-data-csv section.i8 | pigz -p 8 > section.csv.gz
#include <charconv>
#include <cstdint>
#include <fstream>
#include <iostream>
#include <stdexcept>
#include <string>
#include <vector>

int main(int argc, char** argv) {
    try {
        if (argc != 2 && argc != 3)
            throw std::runtime_error("Usage: vector-data-csv input.i8 [columns=48]");
        const int columns = argc == 3 ? std::stoi(argv[2]) : 48;
        if (columns < 1 || columns > 4096)
            throw std::runtime_error("Invalid column count");
        std::ifstream input(argv[1], std::ios::binary);
        if (!input) throw std::runtime_error("Cannot open input");
        std::vector<std::int8_t> row(columns);
        std::vector<char> text(columns * 5);
        while (input.read(reinterpret_cast<char*>(row.data()), row.size())) {
            char* next = text.data();
            for (int i = 0; i < columns; ++i) {
                next = std::to_chars(next, text.data() + text.size(), static_cast<int>(row[i])).ptr;
                *next++ = i + 1 == columns ? '\n' : ',';
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
