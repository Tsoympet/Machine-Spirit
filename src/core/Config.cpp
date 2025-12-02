#include "Config.hpp"
#include <fstream>
#include <filesystem>

std::unordered_map<std::string, std::string> Config::s_values;

// Return path of the config file (in user's directory)
std::string Config::getConfigFilePath() {
#ifdef _WIN32
    char* user = getenv("USERPROFILE");
#else
    char* user = getenv("HOME");
#endif
    std::string path = std::string(user) + "/.machine_spirit/config.ini";
    return path;
}

void Config::load() {
    std::string file = getConfigFilePath();

    if (!std::filesystem::exists(file)) {
        save(); // Create default config file
        return;
    }

    std::ifstream in(file);
    if (!in.is_open()) return;

    std::string line;
    while (std::getline(in, line)) {
        auto pos = line.find('=');
        if (pos == std::string::npos) continue;

        std::string key = line.substr(0, pos);
        std::string val = line.substr(pos + 1);
        s_values[key] = val;
    }
}

void Config::save() {
    std::string file = getConfigFilePath();
    std::filesystem::create_directories(
        std::filesystem::path(file).parent_path()
    );

    std::ofstream out(file);
    for (auto& [k, v] : s_values) {
        out << k << "=" << v << "\n";
    }
}

std::string Config::get(const std::string& key) {
    if (s_values.count(key)) return s_values[key];
    return "";
}

void Config::set(const std::string& key, const std::string& value) {
    s_values[key] = value;
    save();
}
