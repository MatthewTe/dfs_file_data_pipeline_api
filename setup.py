import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="dfs_pipeline_api",
    version="0.1.1",
    author="MatthewTe",
    description="An API that allows for the exploration/extraction of DHI dfsu files ",
    long_description=long_description,
    url="https://github.com/MatthewTe/dfs_file_data_pipeline_api",
    packages=setuptools.find_packages(),
    classifiers=[
        "Development Status :: - Beta",
        "Topic :: Data Science :: Pipeline API",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Operating System :: Windows"
    ],
    install_requires=[
        'pandas', 'numpy', 'matplotlib', 'plotly', 'dash', 'mikeio', ]
)
