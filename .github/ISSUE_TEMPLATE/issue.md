---
name: Issue
about: Report an issue
title: ""
labels:
assignees: ''

---
<!--
INSTRUCTIONS
============

Please read these instructions before submitting your issue.

If this is the first time you interact on this project, welcome to the community!
In this case, please give a bit of information on how you are using litgen (which project, how long you have been using it, etc.).

Please check existing issues and discussions for similar reports before submitting a new one.


Describe the issue
------------------
Provide a clear and concise description of what the issue is. Include logs or code snippets if necessary. Also, please make sure that your issue's title reflects this concise description.

Version & Platform
------------------
Mention
- the version of litgen you are using (e.g., a version number or commit hash and/or date)
- the type of bindings you are using: nanobind or pybind11

Minimal reproducible example
----------------------------
Please, please do try to provide a minimal reproducible example that reproduces the issue.

For example, you can use the following code block:

```python
import litgen

code = """
    void foo(); // include your own C++ code here (make it short)
"""

options = litgen.LitgenOptions()
# Customize options if needed

generated_code = litgen.generate_code(options, code)

print(generated_code.pydef_code)  # or generated_code.stub_code
```

Explain how the generated code should look, and how it actually looks.

-->
