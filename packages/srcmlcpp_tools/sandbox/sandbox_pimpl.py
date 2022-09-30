from typing import cast

import srcmlcpp
from srcmlcpp_tools import pimpl_my_class
from srcmlcpp.srcml_types import *

code = """
    // Manages a single instance of the application
    class SingleInstanceAppPImpl
    {
    public:
        //
        // An important intro
        //

        // Construct a Single Instance
        SingleInstanceAppPImpl(const std::string& lockName) : mLockName(lockName){}

        ~SingleInstanceAppPImpl() { mExit = true; }

        // Launch the instance
        void RunSingleInstance(bool v, int k = 2) // Launch!
        {
            if (HasOtherInstance())
                return false;
            mFutureResult = std::async(std::launch::async, [this](){ PingLoop(); });
            return true;
        }

        // Returns true if a ping was received
        bool WasPinged() const // Blah
        {
            if (mPingReceived)
            {
                mPingReceived = false;
                return true;
            }
            return false;
        }

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
        std::atomic<bool> mPingReceived = false;
        std::future<void> mFutureResult;
    };
"""


options = srcmlcpp.SrcmlOptions()
cpp_unit = srcmlcpp.code_to_cpp_unit(options, code)
first_struct = cast(CppStruct, cpp_unit.first_element_of_type(CppStruct))

pimpl_options = pimpl_my_class.PimplOptions()
pimpl_options.line_feed_before_block = False
pimpl_options.impl_member_name = "impl"
p = pimpl_my_class.PimplMyClass(pimpl_options, first_struct)
r = p.result()
print(r.glue_code)
print(r.header_code)
