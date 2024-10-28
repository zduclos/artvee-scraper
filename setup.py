from setuptools import find_packages, setup

requires = ["beautifulsoup4==4.12.3", "requests==2.32.3"]

setup(
    name="artvee-scraper",
    author="Zach Duclos",
    author_email="zduclos.github@gmail.com",
    description="Fetch public domain artwork from Artvee (https://www.artvee.com)",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    url="https://github.com/zduclos/artvee-scraper",
    packages=find_packages(exclude=["tests*"]),
    include_package_data=True,
    package_data={"artvee_scraper": ["py.typed"]},
    install_requires=requires,
    license="MIT",
    scripts=[],
    zip_safe=True,
    python_requires=">= 3.10",
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Intended Audience :: Developers",
        "Natural Language :: English",
        "Environment :: Console",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Operating System :: OS Independent",
    ],
    keywords="artvee, artwork, webscraper",
    project_urls={
        "Bug Reports": "https://github.com/zduclos/artvee-scraper/issues",
        "Source": "https://github.com/zduclos/artvee-scraper",
    },
)
