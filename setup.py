import os
from distutils.core import setup

def localopen(fname):
    return open(os.path.join(os.path.dirname(__file__), fname))

setup(name='figshare',
      version='0.1.3',
      packages=['figshare'],
      author='Robert T. McGibbon',
      author_email='rmcgibbo@gmail.com',
      url='https://github.com/rmcgibbo/figshare',
      description='Command-line client for figshare API',
      license='MIT',
      install_requires=localopen('requirements.txt').readlines(),
      scripts=['scripts/figshare'])
