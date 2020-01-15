import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="confluence-pusher",  # Replace with your own username
    version="0.1.0",
    author="Konstantin Vanyushov",
    author_email="Konstantin.Vanyushov@servian.com.au",
    description="A tool to convert and upload markdown documents into Atlassian Confluence",
    long_description=long_description,
    long_description_content_type="text/markdown",
    packages=setuptools.find_packages(),
    keywords="confluence markdown confluence-markup servian servian.com.au",
    url="https://www.servian.com/",
    project_urls={
        "Source Code": "https://github.com/servian/confluence-pusher",
    },
    # classifiers=[
    #     "Programming Language :: Python :: 3",
    #     "License :: OSI Approved :: MIT License",
    #     "Operating System :: OS Independent",
    # ],
    python_requires='>=3.6',
)
