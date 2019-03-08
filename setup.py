import setuptools

with open("Readme.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="pylmeasure",
    version="0.1.6",
    author="Ajayrama Kumaraswamy, Justas Birgiolas",
    author_email="justas@asu.edu",
    description="A Python wrapper for L-Measure",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/justasb/pylmeasure",
    packages=setuptools.find_packages(),
    include_package_data = True,
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: Apache Software License",
        "Operating System :: OS Independent",
    ],
)