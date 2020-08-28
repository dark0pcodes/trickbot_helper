import setuptools

setuptools.setup(
    name='trickbot_helper',
    version='1.0.0',
    author="dark0pcodes",
    description="Easy-to-use Python library to interact with the Trickbot Botnet.",
    packages=setuptools.find_packages(),
    install_requires=['requests', 'pycrypto'],
    classifiers=[
        "Programming Language :: Python :: 3"
    ]
)
