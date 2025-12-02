#include "Paths.hpp"
#include <filesystem>

std::string Paths::s_root = "";

void Paths::init() {
#ifdef _WIN32
    char* user = getenv("USERPROFILE");
#else
    char* user = getenv("HOME");
#endif
    s_root = std::string(user) + "/.machine_spirit/";

    std::filesystem::create_directories(config());
    std::filesystem::create_directories(logs());
    std::filesystem::create_directories(models());
    std::filesystem::create_directories(knowledge());
    std::filesystem::create_directories(memory());
    std::filesystem::create_directories(backups());
    std::filesystem::create_directories(themes());
    std::filesystem::create_directories(hive());
    std::filesystem::create_directories(tmp());
}

std::string Paths::root()      { return s_root; }
std::string Paths::config()    { return s_root + "config/"; }
std::string Paths::logs()      { return s_root + "logs/"; }
std::string Paths::models()    { return s_root + "models/"; }
std::string Paths::knowledge() { return s_root + "knowledge/"; }
std::string Paths::memory()    { return s_root + "memory/"; }
std::string Paths::backups()   { return s_root + "backups/"; }
std::string Paths::themes()    { return s_root + "themes/"; }
std::string Paths::hive()      { return s_root + "hive/"; }
std::string Paths::tmp()       { return s_root + "tmp/"; }
