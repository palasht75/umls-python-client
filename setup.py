from setuptools import setup, find_packages

setup(
    name="umls-python-client",                          # Name of the package
    version="1.0.1",                               # Version of your package
    author="Palash Thakur",
    author_email="palasht75@gmail.com",
    description="UMLS Client for interacting with UMLS APIs including Search, Source, CUI, Semantic Network, and Crosswalk APIs.",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    url="https://github.com/palasht75/umls-client/tree/main",  # Replace with your repo URL
    license="Apache License 2.0",                                # License
    packages=find_packages(),                     # Automatically find packages
    install_requires=[
        "requests",
        "rdflib"                                 # If RDF conversion is use
    ],
    classifiers=[
        "Programming Language :: Python :: 3.9",
        "License :: OSI Approved :: Apache Software License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.9",                      # Minimum Python version required
)
