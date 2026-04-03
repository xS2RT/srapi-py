from setuptools import find_packages, setup

with open("README.md", encoding="utf-8") as f:
    long_description = f.read()

setup(
    name="srapi-py",
    version="0.1.0",
    description="Python client for the speedrun.com REST API v1",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/your-username/srapi-py",
    license="MIT",
    packages=find_packages(),
    python_requires=">=3.8",
    install_requires=["requests>=2.28.0"],
    classifiers=[
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Operating System :: OS Independent",
        "Topic :: Internet :: WWW/HTTP",
        "Topic :: Software Development :: Libraries :: Python Modules",
    ],
    keywords="speedrun speedrunning speedrun.com api client",
)
