import pathlib

from setuptools import find_packages, setup

here = pathlib.Path(__file__).parent.resolve()
long_description = (here / "README.md").read_text(encoding="utf-8")

requires = [
    "beautifulsoup4~=4.11.1",
    "requests~=2.28.1",
    "python-slugify~=6.1.2"
]

setup(
    name="artvee-scraper",
    author="Zach Duclos",
    author_email="zduclos.github@gmail.com",
    description="Fetch public domain artwork from https://www.artvee.com",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/zduclos/artvee-scraper",
    packages=find_packages(exclude=["tests*"]),
    include_package_data=True,
    install_requires=requires,
    license="MIT",
    scripts=[],
    zip_safe=True,
    python_requires=">= 3.8",
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Intended Audience :: Developers",
        "Natural Language :: English",
        "Environment :: Console",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Operating System :: OS Independent",
    ],
    entry_points={
        "console_scripts": [
            "artvee-scraper = artvee_scraper.runner:main",
        ]
    },
    keywords="artvee, artwork, webscraper",
    project_urls={
        "Bug Reports": "https://github.com/zduclos/artvee-scraper/issues",
        "Funding": "https://artvee.com/donate/",
        "Source": "https://github.com/zduclos/artvee-scraper",
    },
)
