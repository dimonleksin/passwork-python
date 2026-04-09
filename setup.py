from setuptools import setup


def read_version() -> str:
    import pathlib
    import re

    init_path = pathlib.Path(__file__).parent / "passwork_client" / "__init__.py"
    init_text = init_path.read_text(encoding="utf-8")
    match = re.search(r'__version__\s*=\s*[\'"]([^\'"]+)[\'"]', init_text)
    if not match:
        raise RuntimeError("Unable to find __version__ in passwork_client/__init__.py")
    return match.group(1)


def read_long_description() -> str:
    import pathlib

    readme_path = pathlib.Path(__file__).parent / "README.md"
    return readme_path.read_text(encoding="utf-8")


setup(
    name="passwork-python",
    version=read_version(),
    description="Python client for Passwork 7 API",
    long_description=read_long_description(),
    long_description_content_type="text/markdown",
    author="Passwork Team",
    url="https://github.com/passwork-me/passwork-python",
    project_urls={
        "Documentation": "https://passwork.pro/tech-guides/api-and-integrations/python-connector/",
        "CLI Utility": "https://passwork.pro/tech-guides/api-and-integrations/cli-utility/",
        "Issues": "https://github.com/passwork-me/passwork-python/issues",
    },
    license="MIT",
    license_files=["LICENSE"],
    packages=["passwork_client", "passwork_client.modules", "passwork_client.constants", "cli", "cli.commands"],
    python_requires=">=3.10",
    install_requires=[
        "requests>=2.31,<3.0",
        "python-dotenv>=1.0,<2.0",
        "cryptography>=42,<47",
        "pbkdf2>=1.3,<2.0",
    ],
    entry_points={
        'console_scripts': [
            'passwork-cli=cli.main:main',
        ],
    },
    classifiers=[
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3 :: Only",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Operating System :: OS Independent",
        "Intended Audience :: Developers",
        "Topic :: Security :: Cryptography",
        "Topic :: Software Development :: Libraries",
    ],
)
