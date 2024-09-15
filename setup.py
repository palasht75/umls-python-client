from setuptools import setup, find_packages

setup(
    name="umls-python-client",
    version="1.0.3",
    author="Palash Thakur",
    author_email="palasht75@gmail.com",
    description="UMLS Client for interacting with UMLS APIs including Search, Source, CUI, Semantic Network, and Crosswalk APIs.",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    url="https://palasht75.github.io/umls-python-client-homepage/",
    project_urls={
        "Source": "https://github.com/palasht75/umls-python-client",
        "Tracker": "https://github.com/palasht75/umls-python-client/issues",
        "Documentation": "https://github.com/palasht75/umls-python-client",
    },
    license="Apache License 2.0",
    packages=find_packages(),
    install_requires=[
        "requests",
        "rdflib",
    ],
    keywords="UMLS, API client, Python, Unified Medical Language System, healthcare data, umls-python, umls-pyton-client, umls-client, umls-api, py-umls",
    classifiers=[
        "Programming Language :: Python :: 3.9",
        "License :: OSI Approved :: Apache Software License",
        "Operating System :: OS Independent",
        "Intended Audience :: Developers",
        "Intended Audience :: Science/Research",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Topic :: Scientific/Engineering :: Medical Science Apps.",
    ],
    python_requires=">=3.9",
)
