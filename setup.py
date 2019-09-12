import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="StreamFork",
    version="0.1",
    author="Marc Horlacher",
    author_email="marc.horlacher@gmail.com",
    description="Stream Data to multiple Clients",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/mhorlacher/StreamFork",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.6',
)

