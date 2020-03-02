from setuptools import setup, find_packages

with open("README.md", "r") as fh:
    long_description = fh.read()

setup(
    name="confluence-pusher",
    version="0.1.1",
    license='MIT',
    description="A tool to convert and upload markdown documents into Atlassian Confluence",
    long_description=long_description,
    longs_description_content_type="text/markdown",
    packages=["cfpusher"],
    package_data={
        "cfpusher": ["confluence.lua"],
    },
    install_requires=['atlassian-python-api','click'],
    keywords="confluence markdown",
    url="https://www.servian.com/",
    project_urls={
        "Source Code": "https://github.com/servian/confluence-pusher"},
    python_requires='>=3.6',
    entry_points={
          'console_scripts': [
              'cfpusher = cfpusher.__main__:main'
          ]
    },
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ]
)
