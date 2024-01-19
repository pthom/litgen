from __future__ import annotations
import lg_mylib


def test_call_guard():
    assert lg_mylib.CallGuardLogger.nb_construct == 0
    assert lg_mylib.CallGuardLogger.nb_destroy == 0
    lg_mylib.call_guard_tester()
    assert lg_mylib.CallGuardLogger.nb_construct == 1
    assert lg_mylib.CallGuardLogger.nb_destroy == 1
