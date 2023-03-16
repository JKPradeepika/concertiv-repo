import os

import nox
from nox.sessions import Session


nox.options.sessions = "test", "lint", "format_check"
locations = ("komodo_backend", "api", "noxfile.py", "conftest.py")

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "komodo_backend.settings")


@nox.session(python=False, venv_backend="venv")
def test(session: Session) -> None:
    session.run("pytest", "--cov=.", "--cov-report", "term-missing", *session.posargs)


@nox.session(python=False, venv_backend="venv")
def test_ci(session: Session) -> None:
    session.run(
        "pytest",
        "--cov=.",
        "--cov-report",
        "xml:coverage/coverage.xml",
        "--junitxml=pytest_reports/pytest_report.xml",
        *session.posargs
    )


@nox.session(python=False, venv_backend="venv")
def format(session: Session) -> None:
    args = session.posargs or locations
    session.run("black", *args)


@nox.session(python=False, venv_backend="venv")
def format_check(session: Session) -> None:
    args = session.posargs or locations
    session.run("black", "--check", *args)


@nox.session(python=False, venv_backend="venv")
def lint(session: Session) -> None:
    args = session.posargs or locations
    session.run("flake8", *args)
