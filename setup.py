from distutils.core import setup

setup(
    name='ansible_rest_api',
    version='0.1',
    packages=['polemarch', 'polemarch.api', 'polemarch.api.v1', 'polemarch.api.v1.filters', 'polemarch.api.v1.serializers', 'polemarch.main', 'polemarch.main.repo', 'polemarch.main.hooks', 'polemarch.main.tasks', 'polemarch.main.tests', 'polemarch.main.models', 'polemarch.main.unittests',
              'polemarch.main.management', 'polemarch.main.management.commands', 'polemarch.main.migrations'],
    url='',
    license='',
    author='dongvt',
    author_email='vothanhdong18@gmail.com',
    description=''
)
