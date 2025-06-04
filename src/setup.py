from setuptools import setup

setup(
    name='ultispress',
    version='1.0',
    py_modules=['main'],
    entry_points={
        'console_scripts': [
            'imagepress = main:bienvenida',
        ],
    },
    install_requires=[
        'rich',
        'Pillow',
    ],
)
