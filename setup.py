import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="p2pnetwork",
    version="0.0.3",
    author="Maurice Snoeren",
    author_email="macsnoeren@gmail.com",
    description="Python decentralized peer-to-peer network application framework.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/macsnoeren/python-p2p-network",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: GNU General Public License v3 (GPLv3)",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.6',
    test_suite='nose.collector',
    tests_require=['nose'],
)