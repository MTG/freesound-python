from distutils.core import setup

setup(
    name="freesound-python",
    version="1.1",
    py_modules=["freesound"],
    install_requires=["requests<3.0,>2.27"],
    python_requires=">=3.6",
)
