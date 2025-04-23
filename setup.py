from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="roex_python",  # Consider changing to match poetry.name "roex-python" if desired for PyPI
    version="1.2.0",  # Updated version
    author="RoEx",  # Updated Author to match poetry
    author_email="info@roexaudio.com",  # Updated email
    description="Pip package for the RoEx Tonn API",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/roex-audio/roex-python",  # Primary repo URL
    project_urls={
        "Homepage": "https://www.roexaudio.com",
        "Repository": "https://github.com/roex-audio/roex-python",
        "Bug Tracker": "https://github.com/roex-audio/roex-python/issues",
    },
    packages=find_packages(),
    keywords=["audio", "mixing", "mastering", "enhancement", "api"], # Added keywords
    classifiers=[
        # Updated classifiers to match pyproject.toml
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Operating System :: OS Independent",
        "Topic :: Multimedia :: Sound/Audio :: Analysis",
        "Topic :: Multimedia :: Sound/Audio :: Mixers",
        "Topic :: Software Development :: Libraries :: Python Modules"
    ],
    python_requires=">=3.7,<4.0", # Matched python requirement format
    install_requires=[
        "requests>=2.25.0",
        "soundfile>=0.10.0", # Added soundfile dependency
        "tenacity>=8.2.0"    # Added for retry logic
    ],
    extras_require={
        'dev': [
            'pytest>=6.2.5',
            'black>=21.6b0',
            'isort>=5.9.2',
            'mypy>=0.910'
        ],
        'docs': [
            'sphinx>=7.0.0', # Added for documentation generation
            'sphinx-rtd-theme>=2.0.0' # Added theme for Sphinx
        ]
    },
)