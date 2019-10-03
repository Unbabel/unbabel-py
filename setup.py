from setuptools import setup

setup(name='unbabel-py',
      version='0.52',
      description='Python Wrapper around Unbabel HTTP API',
      author='Joao Graca',
      author_email='joao@unbabel.com',
      packages=['unbabel'],
      package_dir={'unbabel': 'unbabel', },
      install_requires=[
          'requests',
          'beautifulsoup4',
          'six',
      ],
      tests_require=[
          'requests_mock',
      ],
      url='https://github.com/Unbabel/unbabel-py',
      download_url='https://github.com/Unbabel/unbabel-py/archive/0.50.tar.gz',
      classifiers=[
          'Development Status :: 4 - Beta',
          'Intended Audience :: Developers',
          'Programming Language :: Python ',
          'Topic :: Text Processing'
      ])
