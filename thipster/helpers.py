"""Helper functions for thipster."""
import logging
from pathlib import Path


def create_logger(class_name: str) -> logging.Logger:
    """Create a logger for the given class."""
    return logging.getLogger(class_name)


def set_logging_config(
    log_level: str = 'INFO',
    filename: str | None = None,
    filemode: str = 'w',
) -> None:
    """Set logging configuration.

    Parameters
    ----------
    log_level : str
        Log level, defaults to INFO
    filename : str, optional
        Log filename, defaults to None

    """
    logging.basicConfig(
        level=log_level,
        format='%(asctime)s %(levelname)s %(name)s %(message)s',
        filename=filename,
        filemode=filemode,
        encoding='utf-8',
    )


def execute_subprocess(
    command: list[str] | str,
    cwd: Path = Path.cwd(),
    shell: bool = False,
) -> tuple[int, str]:
    """Execute a subprocess and return the exit code and output.

    Parameters
    ----------
    command : list[str] | str
        Command to execute
    cwd : Path, optional
        Current working directory, defaults to Path.cwd()
    shell : bool, optional
        Whether to use the shell, defaults to False

    Returns
    -------
    tuple[int, str]
        Exit code and output

    """
    import subprocess

    process = subprocess.Popen(
        command,
        cwd=cwd,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        shell=shell,
    )
    stdout, stderr = process.communicate()
    return process.returncode, stdout.decode() + stderr.decode()
