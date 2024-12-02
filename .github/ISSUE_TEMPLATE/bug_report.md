---
name: Bug Report
about: Report a bug
title: ""
labels:
assignees: ''

---

<!-- INSTRUCTIONS

Please fill in the sections below:
* Remove the comments (like this one) before submitting your issue:
  anything between `<! --` and `-->` is a comment and should be removed.
* Remove the sections which are not applicable to your issue.


If this is the first time you interact on this project, welcome to the community!

In this case, please give a bit of information about yourself, and how you are using litgen (which project, how long you have been using it, etc.).

Note:
- The author is French, so remember that saying "Hello" or "Bonjour" is a good way to get him more willing to help you! ;-)
- Please do check existing [issues](../issues) and [discussions](../discussions) for similar reports.
-->


### Describe the bug

<!-- Include here a clear and concise description of what the bug is -->

**Minimal reproducible example**
<!--
Provide a minimal reproducible example that reproduces the bug, in Python.
If applicable, please include the error message or any relevant logs.
-->


For example, you can use the following code:
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


### Environment and configuration
**Version**:
- Version of litgen: Version number or commit hash and/or date
