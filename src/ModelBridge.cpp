#include <pl/Mod.hpp>
#include <filesystem>
#include <fstream>
#include <string>
class ModelBridgeMod {
public:
    static ModelBridgeMod& instance() { static ModelBridgeMod value; return value; }
    ModelBridgeMod() : self_(*ll::mod::NativeMod::current()) {}
    bool load() {
        auto& log = self_.getLogger();
        std::filesystem::create_directories(self_.getConfigDir());
        log.info("ModelBridge native bootstrap loaded (no block renderer hooks installed)");
        log.info("ModelBridge geometry conversion currently runs offline");
        return true;
    }
    bool enable() { self_.getLogger().info("ModelBridge enabled; model replacement unavailable in this build"); return true; }
    bool disable() { return true; }
    bool unload() { return true; }
private:
    ll::mod::NativeMod& self_;
};
PL_REGISTER_MOD(ModelBridgeMod, ModelBridgeMod::instance())
