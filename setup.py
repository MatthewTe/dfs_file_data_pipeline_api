import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="dfsu_api",
    version="0.0.1",
    author="MatthewTe",
    author_email="teelucksingh.matthew1@gmail.com",
    description="An API that allows for the exploration/extraction of DHI dfsu files ",
    long_description=long_description,
    url="https://github.com/MatthewTe/dfsu_visualization_pipeline",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
)
