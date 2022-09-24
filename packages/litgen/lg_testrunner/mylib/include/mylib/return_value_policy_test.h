#include "mylib/api_marker.h"

//
//struct MyConfig            // MY_API
//{
//    int sum = 0;
//
//    // Instance() is a method that returns a pointer that should use `return_value_policy::reference`
//    MY_API static MyConfig& Instance() // return_value_policy::reference
//    {
//        static MyConfig instance;
//        return instance;
//    }
//};
//
//MY_API MyConfig* MyConfigInstance() { return & MyConfig::Instance(); } // return_value_policy::reference
