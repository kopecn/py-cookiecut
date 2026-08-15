import datetime
import os
import shlex
import subprocess
import sys
from collections.abc import Iterator
from contextlib import contextmanager
from typing import Any

from cookiecutter.utils import rmtree
from pytest_cookies.plugin import Cookies, Result


@contextmanager
def insideDir(dirPath: str) -> Iterator[None]:
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
def bakeInTempDir(cookies: Cookies, *args: Any, **kwargs: Any) -> Iterator[Result]:
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


def runInsideDir(command: str, dirPath: str) -> int:
    """
    Run a command from inside a given directory, returning the exit status
    :param command: Command that will be executed
    :param dirPath: String, path of the directory the command is being run.
    """
    with insideDir(dirPath):
        return subprocess.check_call(shlex.split(command))


def checkOutputInsideDir(command: str, dirPath: str) -> bytes:
    "Run a command from inside a given directory, returning the command output"
    with insideDir(dirPath):
        return subprocess.check_output(shlex.split(command))


def testYearComputeInLicenseFile(cookies: Cookies) -> None:
    with bakeInTempDir(cookies) as result:
        if result.project_path is None:
            raise AssertionError("Unable to grab path on created project")
        licenseFilePath = result.project_path.joinpath("LICENSE")
        now = datetime.datetime.now()
        with open(licenseFilePath) as f:
            assert str(now.year) in f.read()


def projectInfo(result: Result) -> tuple[str, str, str]:
    """Get toplevel dir, projectIdentifier, and project dir from baked cookies"""
    assert result.exception is None
    assert result.project.isdir()

    projectPath = str(result.project)
    projectIdentifier = os.path.split(projectPath)[-1]
    projectDir = os.path.join(projectPath, projectIdentifier)
    return projectPath, projectIdentifier, projectDir


def testBakeWithDefaults(cookies: Cookies) -> None:
    with bakeInTempDir(cookies) as result:
        assert result.project.isdir()
        assert result.exit_code == 0
        assert result.exception is None
        foundToplevelFiles = [f.basename for f in result.project.listdir()]
        assert "src" in foundToplevelFiles
        assert "tests" in foundToplevelFiles


def testBakeAndRunTests(cookies: Cookies) -> None:
    with bakeInTempDir(cookies) as result:
        assert result.project.isdir()
        # The generated smoke test must actually pass (non-vacuous): pytest exits 0.
        assert runInsideDir("pytest", str(result.project)) == 0


def testGeneratedModuleIsImportable(cookies: Cookies) -> None:
    """The baked package exposes __version__ and the sentinel function."""
    with bakeInTempDir(
        cookies,
        extra_context={
            "projectIdentifier": "sample-project",
            "packageName": "sample_pkg",
            "moduleName": "sample_mod",
            "version": "1.2.3",
        },
    ) as result:
        assert result.exit_code == 0
        modulePath = result.project.join("src", "sample_pkg", "sample_mod.py")
        assert modulePath.check()
        # The smoke test embedded in the baked project runs green.
        assert runInsideDir("pytest", str(result.project)) == 0


def testFolderNameIsKebabCase(cookies: Cookies) -> None:
    """Default bake produces a kebab-case top-level folder, not snake_case."""
    with bakeInTempDir(cookies) as result:
        assert result.project_path is not None
        assert result.project_path.name == "python-boilerplate"


def testDistributionNameMatchesFolderName(cookies: Cookies) -> None:
    """[project].name in the baked pyproject.toml matches the baked folder name."""
    with bakeInTempDir(cookies) as result:
        assert result.project_path is not None
        pyprojectPath = result.project_path.joinpath("pyproject.toml")
        with open(pyprojectPath) as f:
            contents = f.read()
        assert f'name = "{result.project_path.name}"' in contents


def testGeneratedPackageStaysSnakeCase(cookies: Cookies) -> None:
    """The import package stays snake_case even though the root folder is kebab-case."""
    with bakeInTempDir(cookies) as result:
        assert result.project_path is not None
        packagePath = result.project_path.joinpath("src", "my_package")
        assert packagePath.is_dir()


def testBakeRejectsSnakeCaseProjectIdentifier(cookies: Cookies) -> None:
    """D1: pre_gen hook aborts (does not silently convert) a snake_case projectIdentifier."""
    result = cookies.bake(extra_context={"projectIdentifier": "my_project"})
    assert result.exit_code != 0
    assert result.exception is not None


def testBakeRejectsUppercaseProjectIdentifier(cookies: Cookies) -> None:
    """pre_gen hook aborts the bake on an uppercase projectIdentifier."""
    result = cookies.bake(extra_context={"projectIdentifier": "MyProject"})
    assert result.exit_code != 0
    assert result.exception is not None


def testGithubUrlsMatchFolderName(cookies: Cookies) -> None:
    """Folder name, [project.urls].homepage, and the CONTRIBUTING.md clone dir all match."""
    with bakeInTempDir(cookies) as result:
        assert result.project_path is not None
        folderName = result.project_path.name

        pyprojectPath = result.project_path.joinpath("pyproject.toml")
        with open(pyprojectPath) as f:
            pyprojectContents = f.read()
        homepageLine = next(
            line for line in pyprojectContents.splitlines() if line.startswith("homepage")
        )
        assert homepageLine.rstrip().endswith(f"/{folderName}\"")

        contributingPath = result.project_path.joinpath("CONTRIBUTING.md")
        with open(contributingPath) as f:
            contributingContents = f.read()
        cdLine = next(
            line for line in contributingContents.splitlines() if line.strip().startswith("cd ")
        )
        assert cdLine.strip() == f"cd {folderName}"


def testBakeRejectsUppercasePackageName(cookies: Cookies) -> None:
    """pre_gen hook aborts the bake on an uppercase (non-PEP8) packageName."""
    result = cookies.bake(extra_context={"packageName": "MyPackage"})
    assert result.exit_code != 0
    assert result.exception is not None


def testBakeRejectsHyphenatedModuleName(cookies: Cookies) -> None:
    """pre_gen hook aborts the bake on a hyphenated moduleName."""
    result = cookies.bake(extra_context={"moduleName": "my-module"})
    assert result.exit_code != 0
    assert result.exception is not None


# @pytest.mark.skip(reason="A rare edge case, probably Cookiecutter's fault")
def testBakeWithSpecialcharsAndRunTests(cookies: Cookies) -> None:
    """Ensure that a `full_name` with double quotes does not break pytest"""
    with bakeInTempDir(cookies, extra_context={"full_name": 'name "quote" name'}) as result:
        assert result.project.isdir()
        assert runInsideDir("pytest", str(result.project)) == 0


def testBakeWithApostropheAndRunTests(cookies: Cookies) -> None:
    """Ensure that a `full_name` with apostrophes does not break setup.py"""
    with bakeInTempDir(cookies, extra_context={"full_name": "O'connor"}) as result:
        assert result.project.isdir()
        assert runInsideDir("pytest", str(result.project)) == 0


def testMakeHelp(cookies: Cookies) -> None:
    with bakeInTempDir(cookies) as result:
        # The supplied Makefile does not support win32
        if sys.platform != "win32":
            output = checkOutputInsideDir("make help", str(result.project))
            assert b"make targets" in output
