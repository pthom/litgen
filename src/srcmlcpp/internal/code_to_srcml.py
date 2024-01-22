"""
Calls the external program srcml (https://www.srcml.org/)
"""
from __future__ import annotations

import sys

# mypy: warn_unused_ignores=False
from typing import Optional
import logging
import os
import random
import subprocess
import tempfile
import time
from xml.etree import ElementTree as ET

# srcML can be used either via the python module srcml_caller or via the executable srcml
try:
    import srcml_caller as srcml_nativecaller  # type: ignore # noqa

    _USE_PYTHON_SRCML_CALLER_MODULE = True
except ImportError:
    _USE_PYTHON_SRCML_CALLER_MODULE = False


# Count the total time used by call to the exe srcml
_FLAG_PROFILE_SRCML_CALLS: bool = True


def _embed_element_into_unit(element: ET.Element) -> ET.Element:
    if element.tag.endswith("unit"):
        return element
    else:
        new_element = ET.Element("unit")
        new_element.append(element)
        return new_element


class _TimeStats:
    nb_calls: int = 0
    total_time: float = 0.0
    _last_start_time: float = 0.0

    def start(self) -> None:
        self.nb_calls += 1
        self._last_start_time = time.time()

    def stop(self) -> None:
        self.total_time += time.time() - self._last_start_time

    def stats_string(self) -> str:
        if self.nb_calls == 0:
            return ""
        return f"calls: {self.nb_calls} total time: {self.total_time:.3f}s average: {self.total_time / self.nb_calls * 1000:.0f}ms"


class _SrcmlCaller:
    _stats_code_to_srcml: _TimeStats = _TimeStats()
    _stats_srcml_to_code: _TimeStats = _TimeStats()

    def _call_subprocess(self, encoding: str, input_filename: str, output_filename: str, dump_positions: bool) -> None:
        position_arg = "--position" if dump_positions else ""

        shell_command = f"srcml -l C++ {input_filename} {position_arg} --xml-encoding {encoding} --src-encoding {encoding} -o {output_filename}"
        logging.debug(f"_SrcmlCaller.call: {shell_command}")
        try:
            subprocess.check_call(shell_command, shell=True)
        except subprocess.CalledProcessError as e:
            logging.error(f"_SrcmlCaller.call, error {e}")
            logging.error(
                """
            srcmlcpp requires the installation of srcML ( https://www.srcml.org )
            (the command "srcml" needs to be available in your PATH)
            Did you install it?
            See install instructions at:
                https://pthom.github.io/litgen/litgen_book/01_05_10_install.html
            """
            )
            sys.exit(1)

    def _random_filename(self) -> str:
        characters = "abcdefghijklmnopqrstuvwxyz0123456789_"
        r = "".join(random.choices(characters, k=14))
        r = tempfile.gettempdir() + "/" + r
        return r

    def _make_xml_str_by_subprocess(self, encoding: str, input_str: str, dump_positions: bool = False) -> str:
        input_header_filename = self._random_filename() + ".h"
        output_xml_filename = self._random_filename() + ".xml"

        with open(input_header_filename, "wb") as input_header_file:
            input_header_file.write(input_str.encode(encoding))
            input_header_file.close()

        self._call_subprocess(
            encoding,
            input_header_filename,
            output_xml_filename,
            dump_positions,
        )

        with open(output_xml_filename, "rb") as output_xml_file:
            output_bytes = output_xml_file.read()
            output_xml_file.close()

        os.remove(input_header_file.name)
        os.remove(output_xml_file.name)
        output_str = output_bytes.decode(encoding)
        return output_str

    def _make_cpp_str_by_subprocess(self, xml_bytes: bytes, encoding: str) -> str:
        input_xml_filename = self._random_filename() + ".xml"
        output_header_filename = self._random_filename() + ".h"
        with open(input_xml_filename, "wb") as input_xml_file:
            input_xml_file.write(xml_bytes)
            input_xml_file.close()

        self._call_subprocess(encoding, input_xml_filename, output_header_filename, False)

        with open(output_header_filename, "rb") as output_header_file:
            output_bytes = output_header_file.read()
            output_header_file.close()
        os.remove(input_xml_filename)
        os.remove(output_header_filename)
        code_str = output_bytes.decode(encoding)
        return code_str

    def _make_xml_str_by_module(self, input_str: str, encoding: str, dump_positions: bool = False) -> str:
        r = srcml_nativecaller.to_srcml(  # type: ignore
            code=input_str,
            language=srcml_nativecaller.CodeLanguage.c_plus_plus,  # type: ignore
            encoding_src=encoding,
            encoding_xml=encoding,
            include_positions=dump_positions,
        )  # type: ignore  # noqa: F821
        assert r is not None

        def patch_xml(s: str) -> str:
            xml_prefix = '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>\n'
            search = '<unit revision="1.0.0"'
            replace = '<unit xmlns="http://www.srcML.org/srcML" xmlns:pos="http://www.srcML.org/srcML/position" xmlns:cpp="http://www.srcML.org/srcML/cpp" revision="1.0.0"'
            xml_patched = s.replace(search, replace)
            xml_patched = xml_prefix + xml_patched
            return xml_patched

        patched = patch_xml(r)
        return patched

    def _make_cpp_str_by_module(self, input_str: str, encoding: str) -> str:
        import srcml_caller as srcml_nativecaller

        r: Optional[str] = srcml_nativecaller.to_code(xml_str=input_str, encoding_xml=encoding, encoding_src=encoding)  # type: ignore
        assert r is not None
        return r

    def code_to_srcml(self, encoding: str, input_str: str, dump_positions: bool = False) -> ET.Element:
        """
        Calls srcml with the given code and return the srcml as xml Element
        """
        self._stats_code_to_srcml.start()

        if _USE_PYTHON_SRCML_CALLER_MODULE:
            output_str = self._make_xml_str_by_module(input_str, encoding, dump_positions)
        else:
            output_str = self._make_xml_str_by_subprocess(encoding, input_str, dump_positions)

        ET.register_namespace("pos", "http://www.srcML.org/srcML/position")
        ET.register_namespace("", "http://www.srcML.org/srcML/src")
        element = ET.fromstring(output_str)
        if "filename" in element.attrib.keys():
            del element.attrib["filename"]

        self._stats_code_to_srcml.stop()
        return element

    def srcml_to_code(self, encoding: str, element: ET.Element) -> str:
        """
        Calls srcml with the given srcml xml element and return the corresponding code
        """
        if element is None:
            return "<srcml_to_code(None)>"

        unit_element = _embed_element_into_unit(element)
        xml_bytes: bytes = ET.tostring(unit_element, encoding="utf8", method="xml")
        xml_str = xml_bytes.decode("utf8")

        self._stats_srcml_to_code.start()

        code_str: str
        if _USE_PYTHON_SRCML_CALLER_MODULE:
            code_str = self._make_cpp_str_by_module(xml_str, encoding)
        else:
            code_str = self._make_cpp_str_by_subprocess(xml_bytes, encoding)

        self._stats_srcml_to_code.stop()
        return code_str

    def total_time(self) -> float:
        total_time = self._stats_code_to_srcml.total_time + self._stats_srcml_to_code.total_time
        return total_time

    def profiling_stats(self) -> str:
        from codemanip import code_utils

        r = code_utils.unindent_code(
            f"""
        Time taken by calls to srcML:
            code_to_srcml {self._stats_code_to_srcml.stats_string()}
            srcml_to_code {self._stats_srcml_to_code.stats_string()}
            total time: {self.total_time():.3f}s
        """,
            flag_strip_empty_lines=True,
        )
        return r


_SRCML_CALLER = _SrcmlCaller()


def code_to_srcml(code: str, dump_positions: bool = True, encoding: str = "utf-8") -> ET.Element:
    return _SRCML_CALLER.code_to_srcml(encoding, code, dump_positions)


def srcml_to_code(element: ET.Element, encoding: str = "utf-8") -> str:
    return _SRCML_CALLER.srcml_to_code(encoding, element)
