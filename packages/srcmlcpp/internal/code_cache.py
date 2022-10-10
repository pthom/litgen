from typing import Dict, Optional


_Filename = str
_Code = str
_CODE_CACHE: Dict[Optional[_Filename], _Code] = {}


def get_cached_code(filename: Optional[str]) -> str:
    global _CODE_CACHE
    if filename not in _CODE_CACHE.keys():
        raise ValueError(f"filename {filename} not in code cache!")
    return _CODE_CACHE[filename]


def store_cached_code(filename: Optional[str], code: str) -> None:
    global _CODE_CACHE
    _CODE_CACHE[filename] = code
