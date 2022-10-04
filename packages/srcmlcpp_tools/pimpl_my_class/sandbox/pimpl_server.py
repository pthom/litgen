from typing import Optional

from flask import Flask
from flask import request, render_template
from markupsafe import escape

from srcmlcpp_tools.pimpl_my_class.pimpl_my_class import pimpl_my_code

from codemanip.html_code_viewer.html_code_viewer import (
    collapsible_code_and_title,
    CodeAndTitle,
    CodeLanguage,
    COLLAPSIBLE_CSS,
    HALF_WIDTH_DIVS_CSS,
)

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

    pimpl_result = pimpl_my_code(code)

    # out = render_template("pimpl_result.html", header_code=r.header_code, glue_code=r.glue_code)
    # return out

    original = collapsible_code_and_title(CodeAndTitle(CodeLanguage.Cpp, code, "Original Impl"), max_visible_lines=20)
    published = collapsible_code_and_title(
        CodeAndTitle(CodeLanguage.Cpp, pimpl_result.header_code, "Published Header"), initially_opened=True
    )
    glue = collapsible_code_and_title(CodeAndTitle(CodeLanguage.Cpp, pimpl_result.glue_code, "Cpp Glue"))

    out = COLLAPSIBLE_CSS
    out += HALF_WIDTH_DIVS_CSS
    out += f"""
        <div class ="several_columns">
            <div class="half_width">
                {original}
            </div>
            <div class="half_width">
            {published}
            <br/>
            {glue}
            </div>
        </div>
    """

    return out


@app.route("/")
def landing_page():
    return render_template("code_input.html")
