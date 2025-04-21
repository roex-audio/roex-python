from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="roex_python",
    version="1.1.1",
    author="RoEx Audio",
    author_email="support@roexaudio.com",
    description="Pip package for the RoEx Tonn API",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/roexaudio/roex-python",
    packages=find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.7",
    install_requires=[
        "requests>=2.25.0",
    ],
)