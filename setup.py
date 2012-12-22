from setuptools import setup, find_packages
requires = [
    ]


setup(name='glue',
      version='0.0.0',
      description='glue is glue. don\'t use this',
      package_dir={'': '.'},
      packages=find_packages('.'),
      install_requires = requires,
      test_suite = "unittest2.collector",
      entry_points = """
      """,
      )

