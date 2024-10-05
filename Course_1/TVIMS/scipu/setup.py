from setuptools import setup, find_packages


def readme():
  with open('README.md', 'r') as f:
    return f.read()



setup(
    name='scipu',
    version='0.1',
    packages=find_packages(),
    description='A simple TVIMS library',
    author='Ackrome',
    author_email='ivansergeyevicht@gmail.com',
    url='https://github.com/Ackrome/scipu',
    classifiers=[
        'Programming Language :: Python :: 3',
        'License :: None',
        'Operating System :: OS Independent'
    ],
    python_requires='>=3.6'
)
