import setuptools

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setuptools.setup(
    name="lrc_kit",
    version="0.1",
    author="Peter Stenger",
    author_email="peter.promotions.stenger@gmail.com",
    description="A library to search for LRC files online and parse their contents",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/reteps/lrc_kit",
    packages=setuptools.find_packages(),
    install_requires=[
        'bs4',
        'requests'
    ],
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.6',
)