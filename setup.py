from setuptools import setup, find_packages

setup(name='Website Scrubber',
      version='0.2',
      description='Download files from an open directory.',
      author='Derek Santos',
      license='The MIT License (MIT)',
      packages=['website_scrubber'],
      scripts=['website_scrubber/main.py'],
      entry_points={
          'console_scripts':
              ['ws = website_scrubber.main:main']
      },
      install_requires=[
          'requests',
          'bs4'
      ],
      )
