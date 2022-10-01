#pragma once
#include <string>
#include <memory>

class SingleInstanceAppPImpl;

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
        std::cout << "Other instance found!
";
        return 0;
    }

    while(true)
    {
        std::this_thread::sleep_for(100ms);
        if (singleInstanceApp.WasPinged())
            std::cout << "Ping received!
";

      // For example, scan keyboard key 'q' to quit
      // if (scan_key() == 'q')
      //     break;
    }
}
````
**/
class SingleInstanceApp {
public:
    //
    //  SingleInstanceApp enables to make sure that only one instance of an app runs on a given system
    //

    static bool HasOtherInstance(const std::string & lockName);

    // Construct a Single Instance
    SingleInstanceApp(const std::string & lockName);

    // RunSingleInstanceListener will run an async loop
    // that will wait for signals from possible other instances launches
    // If a signal is received:
    // - It will tell the other instance that an instance is launched already
    //   (i.e for the other instance, RunSingleInstanceListener() will return false)
    // - It will store a "ping" in the main instance
    //   (so that in the main loop, one can for example bring the main instance app to the front)
    bool RunSingleInstanceListener();// Will return false if another instance was detected!

    // Returns true if a ping was received from another instance
    bool WasPinged() const;// Blah

    ~SingleInstanceApp();
private:
    std::unique_ptr<SingleInstanceAppPImpl> impl;
};
