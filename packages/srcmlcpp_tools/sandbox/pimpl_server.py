from flask import Flask
from flask import request, render_template
from markupsafe import escape
from typing import cast

import srcmlcpp
from srcmlcpp.srcml_types import *
from srcmlcpp_tools.pimpl_my_class.pimpl_my_class import PimplMyClass, PimplOptions

PIMPL_OPTIONS = PimplOptions()
LITGEN_OPTIONS = srcmlcpp.SrcmlOptions()
PIMPL_OPTIONS.max_consecutive_empty_lines = 0

# flask --app pimpl_server.py --debug  run

app = Flask(__name__)


@app.route("/user/<username>")
def show_user_profile(username):
    # show the user profile for that user
    return f"User {escape(username)}"


@app.route("/hello/")
@app.route("/hello/<name>")
def hello(name=None):
    return render_template("pimpl_result.html", name=name)


@app.route("/pimpl", methods=["POST", "GET"])
def pimpl_result():
    code: Optional[str]
    if request.method == "POST":
        code = request.form["code"]
    elif request.method == "GET":
        code = request.args.get("code")
    if code is None:
        return "no code provided"

    cpp_unit = srcmlcpp.code_to_cpp_unit(LITGEN_OPTIONS, code)
    first_struct = cast(CppStruct, cpp_unit.first_element_of_type(CppStruct))
    p = PimplMyClass(PIMPL_OPTIONS, first_struct)
    r = p.result()
    out = render_template("pimpl_result.html", header_code=r.header_code, glue_code=r.glue_code)
    return out


@app.route("/")
def landing_page():
    return render_template("code_input.html")
