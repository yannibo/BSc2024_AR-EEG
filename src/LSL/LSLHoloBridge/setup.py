from setuptools import setup

setup(
    name='LSLHoloBridge',
    version='0.1',
    description='A tcp client server bridge between Microsoft\'s HoloLens and Lab Streaming Layer',
    keywords= 'labstreaminglayer lsl hololens',
    url='https://gitlab.csl.uni-bremen.de/fkroll/LSLHoloBridge',
    author='Felix Kroll',
    author_email='fe_kr@uni-bremen.de',
    # license='MIT',
    packages=['bridge'],
    # entry_points = {
    #    'console_scripts' : [
    #        'lsl=lsl_apps.__main__:main',
    #        'capture=lsl_apps.video.capture:main',
    #        ],
    # },
    # install_requires=[
    #    'numpy',
    #    'pandas',
    # ],
    zip_safe=False, install_requires=['pylsl', 'pyxdf', 'pykka', 'numpy', 'pytest']
)
