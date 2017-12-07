from setuptools import setup, find_packages
setup(
    name="authtool",
    version="1.0",
    install_requires="pyotp>=2.2",
    scripts=['authtool.py'],
)
