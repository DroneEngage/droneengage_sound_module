from setuptools import setup, find_packages

setup(
    name='de_sound_module',
    version='2.0.0',
    author='Mohammad Hefny',
    author_email='mohammad.hefny@gmail.com',
    packages=find_packages(),
    install_requires=[
        'colorama',
        'pyttsx3',  # Install pyttsx3 for broader compatibility
    ],
    extras_require={
        'rpi': ['espeak-ng'],  # Optional dependency for RPi
        'ubuntu': ['espeak-ng'],  # Optional dependency for Ubuntu
    },
    # Other setup arguments, such as author, description, etc.
)