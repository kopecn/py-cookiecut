import datetime
import os
import shlex
import subprocess
import sys
from contextlib import contextmanager

import pytest
from cookiecutter.utils import rmtree
from pytest_cookies.plugin import Cookies


@contextmanager
def insideDir(dirPath):
    """
    Execute code from inside the given directory
    :param dirPath: String, path of the directory the command is being run.
    """
    oldPath = os.getcwd()
    try:
        os.chdir(dirPath)
        yield
    finally:
        os.chdir(oldPath)


@contextmanager
def bakeInTempDir(cookies: Cookies, *args, **kwargs):
    """
    Delete the temporal directory that is created when executing the tests
    :param cookies: pytest_cookies.Cookies,
        cookie to be baked and its temporal files will be removed
    """
    result = cookies.bake(*args, **kwargs)
    try:
        yield result
    finally:
        rmtree(str(result.project))


def runInsideDir(command, dirPath):
    """
    Run a command from inside a given directory, returning the exit status
    :param command: Command that will be executed
    :param dirPath: String, path of the directory the command is being run.
    """
    with insideDir(dirPath):
        return subprocess.check_call(shlex.split(command))


def checkOutputInsideDir(command, dirPath):
    "Run a command from inside a given directory, returning the command output"
    with insideDir(dirPath):
        return subprocess.check_output(shlex.split(command))


def testYearComputeInLicenseFile(cookies: Cookies):
    with bakeInTempDir(cookies) as result:
        if result.project_path is None:
            assert False  # Unable to grab path on created project
        licenseFilePath = result.project_path.joinpath("LICENSE")
        now = datetime.datetime.now()
        with open(licenseFilePath, "r") as f:
            assert str(now.year) in f.read()


def projectInfo(result):
    """Get toplevel dir, projectIdentifier, and project dir from baked cookies"""
    assert result.exception is None
    assert result.project.isdir()

    projectPath = str(result.project)
    projectIdentifier = os.path.split(projectPath)[-1]
    projectDir = os.path.join(projectPath, projectIdentifier)
    return projectPath, projectIdentifier, projectDir


def testBakeWithDefaults(cookies: Cookies):
    with bakeInTempDir(cookies) as result:
        assert result.project.isdir()
        assert result.exit_code == 0
        assert result.exception is None
        foundToplevelFiles = [f.basename for f in result.project.listdir()]
        assert "src" in foundToplevelFiles
        assert "tests" in foundToplevelFiles


def testBakeAndRunTests(cookies: Cookies):
    with bakeInTempDir(cookies) as result:
        assert result.project.isdir()
        runInsideDir("pytest", str(result.project)) == 0
        print("testBakeAndRunTests path", str(result.project))


# @pytest.mark.skip(reason="A rare edge case, probably Cookiecutter's fault")
def testBakeWithSpecialcharsAndRunTests(cookies: Cookies):
    """Ensure that a `full_name` with double quotes does not break pytest"""
    with bakeInTempDir(
        cookies, extra_context={"full_name": 'name "quote" name'}
    ) as result:
        assert result.project.isdir()
        runInsideDir("pytest", str(result.project)) == 0


def testBakeWithApostropheAndRunTests(cookies: Cookies):
    """Ensure that a `full_name` with apostrophes does not break setup.py"""
    with bakeInTempDir(cookies, extra_context={"full_name": "O'connor"}) as result:
        assert result.project.isdir()
        runInsideDir("pytest", str(result.project)) == 0


def testMakeHelp(cookies: Cookies):
    with bakeInTempDir(cookies) as result:
        # The supplied Makefile does not support win32
        if sys.platform != "win32":
            output = checkOutputInsideDir("make help", str(result.project))
            assert b"make targets" in output
