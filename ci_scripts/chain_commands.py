import subprocess
import os


def chain_commands(cmd, only_echo=False):
    _run(cmd, chain_commands=True, only_echo=only_echo)


def _run(cmd, chain_commands=False, only_echo = False):
    if only_echo:
        print(cmd)
        return

    if chain_commands and os.name == "nt":
        raise RuntimeError("chain_commands is not supported under windows")

    if chain_commands:
        cmd = _chain_and_echo_commands(cmd)
        subprocess.check_call(cmd, shell=True)
    else:
        if os.name == "nt":
            print("###### Run command ######")
            print(cmd)
            print()
            subprocess.check_call(cmd, shell=True)
        else:
            cmd = _cmd_to_echo_and_cmd(cmd)
            subprocess.check_call(cmd, shell=True)


def _cmd_to_echo_and_cmd_lines(cmd: str) -> [str]:
    lines_with_echo = [
        "echo '###### Run command ######'",
        f"echo '{cmd}'",
        "echo ''",
        cmd
    ]
    return lines_with_echo


def _cmd_to_echo_and_cmd(cmd: str) -> str:
    end_line = " &&         \\\n"
    return end_line.join(_cmd_to_echo_and_cmd_lines(cmd))


def _chain_and_echo_commands(commands: str):
    """
    Take a series of shell command on a multiline string (one command per line)
    and returns a shell command that will execute each of them in sequence,
    while echoing them, and ignoring commented lines (with a #)
    """
    lines = commands.split("\n")
    # strip lines
    lines = map(lambda s: s.strip(), lines)
    # suppress empty lines
    lines = filter(lambda s: not len(s) == 0, lines)

    # add "echo commands" and process comments:
    # comments starting with # are discarded and comments starting with ## are displayed loudly
    lines_with_echo = []
    for line in lines:
        if line.startswith("##"):
            echo_line = f"echo '******************** {line[2:].strip()} ***************'"
            lines_with_echo.append(echo_line)
        elif not line.startswith("#"):
            lines_with_echo = lines_with_echo + _cmd_to_echo_and_cmd_lines(line)

    # End of line joiner
    end_line = " &&         \\\n"

    r = end_line.join(lines_with_echo)
    r = r.replace("&& &&", "&& ")
    return r
