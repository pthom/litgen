#include "single_instance_app.h"

#include <string>
#include <future>
#include <iostream>
#include <fstream>
#include <filesystem>

/**
 SingleInstanceApp: Helper to create a single instance application
 =================================================================

 Anatomy of an example app with `SingleInstanceApp`:
 ---------------------------------------------------

````cpp
int main()
{
    using namespace std::literals;

    SingleInstanceApp singleInstanceApp("MyLock");
    if (! singleInstanceApp.RunSingleInstanceListener())
    {
        std::cout << "Other instance found!\n";
        return 0;
    }

    while(true)
    {
        std::this_thread::sleep_for(100ms);
        if (singleInstanceApp.WasPinged())
            std::cout << "Ping received!\n";

      // For example, scan keyboard key 'q' to quit
      // if (scan_key() == 'q')
      //     break;
    }
}
````
**/
class SingleInstanceAppPImpl
{
public:
    //
    // SingleInstanceApp enables to make sure that only one instance of an app runs on a given system
    //

    // Construct a Single Instance
    SingleInstanceAppPImpl(const std::string& lockName) : mLockName(lockName){}

    // RunSingleInstanceListener will run an async loop
    // that will wait for signals from possible other instances launches
    // If a signal is received:
    // - It will tell the other instance that an instance is launched already
    //   (i.e for the other instance, RunSingleInstanceListener() will return false)
    // - It will store a "ping" in the main instance
    //   (so that in the main loop, one can for example bring the main instance app to the front)
    bool RunSingleInstanceListener() // Will return false if another instance was detected!
    {
        if (HasOtherInstance())
            return false;
        mFutureResult = std::async(std::launch::async, [this](){ PingLoop(); });
        return true;
    }

    // Returns true if a ping was received from another instance
    bool WasPinged() const // Blah
    {
        if (mPingReceived)
        {
            mPingReceived = false;
            return true;
        }
        return false;
    }

    // The destructor will stop the async listener loop
    ~SingleInstanceAppPImpl() { mExit = true; }

private:
    bool HasOtherInstance()
    {
        using namespace std::literals;

        if (HasPingFile())
        {
            std::cout << "Ooops : stale ping file!\n";
            RemovePingFile();
            std::this_thread::sleep_for(100ms);
        }

        CreatePingFile();
        std::this_thread::sleep_for(120ms);
        if ( ! HasPingFile())
        {
            std::cout << "Other instance already launched!\n";
            return true;
        }
        else
        {
            // Master process not answering
            std::cout << "First instance!\n";
            RemovePingFile();
            return false;
        }
    }

    void AnswerPings()
    {
        if (std::filesystem::is_regular_file(PingFilename()))
        {
            std::cout << "Answering ping!\n";
            mPingReceived = true;
            std::filesystem::remove(PingFilename());
        }
    }

    void PingLoop()
    {
        using namespace std::literals;
        while(!mExit)
        {
            AnswerPings();
            std::this_thread::sleep_for(60ms);
        }
    }

    bool HasPingFile() { return std::filesystem::is_regular_file(PingFilename()); }
    void CreatePingFile() {  std::ofstream os(PingFilename()); os << "Lock"; }
    void RemovePingFile() { std::filesystem::remove(PingFilename()); }
    std::string PingFilename()
    {
        return std::filesystem::temp_directory_path().string() + "/" +mLockName + ".ping";
    }

    std::string mLockName;
    std::atomic<bool> mExit = false;
    mutable std::atomic<bool> mPingReceived = false;
    std::future<void> mFutureResult;
};


SingleInstanceApp::SingleInstanceApp(const std::string & lockName) : mPImpl(std::make_unique<SingleInstanceAppPImpl>(lockName)) { }
bool SingleInstanceApp::RunSingleInstanceListener() { return mPImpl->RunSingleInstanceListener(); }
bool SingleInstanceApp::WasPinged() const { return mPImpl->WasPinged(); }
SingleInstanceApp::~SingleInstanceApp() = default;


int main()
{
    using namespace std::literals;

    SingleInstanceApp singleInstanceApp("MyLock");
    if (! singleInstanceApp.RunSingleInstanceListener())
    {
        std::cout << "Other instance found!\n";
        return 0;
    }

    while(true)
    {
        std::this_thread::sleep_for(100ms);
        if (singleInstanceApp.WasPinged())
            std::cout << "Ping received!\n";

        // For example, scan keyboard key 'q' to quit
        // if (scan_key() == 'q')
        //     break;
    }

}
