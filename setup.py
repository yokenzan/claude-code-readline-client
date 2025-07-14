from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="ccrc",
    version="0.1.0",
    author="CCRC Contributors",
    description="Claude Code Readline Client - A readline-enabled CLI for Claude Code",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/yourusername/readline-claude-code",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: GNU General Public License v3 (GPLv3)",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Operating System :: POSIX :: Linux",
        "Operating System :: MacOS",
        "Environment :: Console",
    ],
    python_requires=">=3.8",
    install_requires=[
        "claude-code-sdk-python",
        "pyyaml>=6.0",
        "rich>=13.0",
        "prompt-toolkit>=3.0",
    ],
    extras_require={
        "dev": [
            "pytest>=7.0",
            "pytest-asyncio>=0.21",
            "pytest-cov>=4.0",
            "black>=23.0",
            "flake8>=6.0",
            "mypy>=1.0",
        ]
    },
    entry_points={
        "console_scripts": [
            "ccrc=ccrc.main:main",
        ],
    },
)