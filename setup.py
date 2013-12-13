from distutils.core import setup

setup(name='unbabel-py',
      version='0.1',
      description='Python Wrapper around Unbabel HTTP API',
      author='Joao Graça',
      author_email='gracaninja@unbabel.co',
      url='https://github.com/Unbabel/unbabel-py',
      packages=[
          'unbabel',
          ],
      package_dir={
        'unbabel': 'unbabel/',
        },
      install_requires=[
        'requests',
          ],
      )
