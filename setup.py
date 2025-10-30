from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="roex_python",
    version="1.3.0",
    author="RoEx Audio",
    author_email="support@roexaudio.com",
    description="Pip package for the RoEx Tonn API",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/roexaudio/roex-python",
    project_urls={
        "Bug Tracker": "https://github.com/roexaudio/roex-python/issues",
        "Documentation": "https://roex.stoplight.io/",
        "Source Code": "https://github.com/roexaudio/roex-python",
    },
    packages=find_packages(exclude=["tests", "tests.*", "examples"]),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Topic :: Multimedia :: Sound/Audio",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    license="MIT",
    python_requires=">=3.7",
    install_requires=[
        "requests>=2.25.0",
    ],
    extras_require={
        "dev": [
            "pytest>=7.0.0",
            "pytest-cov>=4.0.0",
            "pytest-mock>=3.10.0",
            "requests-mock>=1.9.3",
        ],
    },
)