"""
Calls the external program srcml (https://www.srcml.org/)
"""

import logging
import os
import platform
import random
import subprocess
import tempfile
import time
from xml.etree import ElementTree as ET


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
            raise

    def _random_filename(self) -> str:
        characters = "abcdefghijklmnopqrstuvwxyz0123456789_"
        r = "".join(random.choices(characters, k=14))
        r = tempfile.gettempdir() + "/" + r
        return r

    def code_to_srcml(self, encoding: str, input_str: str, dump_positions: bool = False) -> ET.Element:
        """
        Calls srcml with the given code and return the srcml as xml Element
        """
        self._stats_code_to_srcml.start()
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
        element = ET.fromstring(output_str)
        self._stats_code_to_srcml.stop()
        return element

    def srcml_to_code(self, encoding: str, element: ET.Element) -> str:
        """
        Calls srcml with the given srcml xml element and return the corresponding code
        """
        if element is None:
            return "<srcml_to_code(None)>"

        input_xml_filename = self._random_filename() + ".xml"
        output_header_filename = self._random_filename() + ".h"

        self._stats_srcml_to_code.start()
        unit_element = _embed_element_into_unit(element)

        with open(input_xml_filename, "wb") as input_xml_file:
            element_tree = ET.ElementTree(unit_element)
            element_tree.write(input_xml_file.name)
            input_xml_file.close()

        self._call_subprocess(encoding, input_xml_filename, output_header_filename, False)

        with open(output_header_filename, "rb") as output_header_file:
            output_bytes = output_header_file.read()
            output_header_file.close()

        os.remove(input_xml_filename)
        os.remove(output_header_filename)

        code_str = output_bytes.decode(encoding)
        self._stats_srcml_to_code.stop()
        return code_str

    def __del__(self):
        global _FLAG_PROFILE_SRCML_CALLS
        if _FLAG_PROFILE_SRCML_CALLS:
            print(
                f"_SrcmlCaller: code_to_srcml {self._stats_code_to_srcml.stats_string()}    |    srcml_to_code {self._stats_srcml_to_code.stats_string()}"
            )


_SRCML_CALLER = _SrcmlCaller()


def code_to_srcml(code: str, dump_positions: bool = True, encoding: str = "utf-8") -> ET.Element:
    return _SRCML_CALLER.code_to_srcml(encoding, code, dump_positions)


def srcml_to_code(element: ET.Element, encoding: str = "utf-8") -> str:
    return _SRCML_CALLER.srcml_to_code(encoding, element)
