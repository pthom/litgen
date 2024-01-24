from __future__ import annotations
from typing import Optional

from flask import Flask, render_template, request  # type: ignore
from markupsafe import escape

from codemanip.html_code_viewer.html_code_viewer import (
    # COLLAPSIBLE_CSS, HALF_WIDTH_DIVS_CSS,
    CodeAndTitle,
    CodeLanguage,
    collapsible_code_and_title,
    collapsible_code_and_title_two_columns,
)

from srcmlcpp_tools.pimpl_my_class.pimpl_my_class import pimpl_my_code


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
    code: Optional[str] = None
    if request.method == "POST":
        code = request.form["code"]
    elif request.method == "GET":
        code = request.args.get("code")
    if code is None:
        return "no code provided"
    pimpl_result = pimpl_my_code(code)
    if pimpl_result is None:
        return "No impl struct found!"

    original = CodeAndTitle(
        CodeLanguage.Cpp, code, "Original PImpl (your private impl, present in the original C++ file)"
    )
    published = CodeAndTitle(
        CodeLanguage.Cpp, pimpl_result.header_code, "Published Header (paste this in the header file)"
    )
    glue = CodeAndTitle(
        CodeLanguage.Cpp, pimpl_result.glue_code, "Cpp Glue (paste this in the C++ file, below your PImpl)"
    )

    html = collapsible_code_and_title(glue, initially_opened=True)
    html += "<br/>" + collapsible_code_and_title_two_columns(
        published, original, max_visible_lines=60, initially_opened=True
    )
    return html


@app.route("/")
def landing_page():
    return render_template("code_input.html")
