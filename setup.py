# Copyright (c) 2017 Stephen Bunn (stephen@bunn.io)
# MIT License <https://opensource.org/licenses/MIT>

import os
import sys
import shutil
import setuptools


CURDIR = os.path.abspath(os.path.dirname(__file__))
REQUIRES = [
    'scrapy',
    'beautifulsoup4',
    'lxml',
    'requests',
    'humanfriendly',
    'dateparser',
    'furl',
    'pygogo',
    'twisted',
    'click',
    'pyperclip',
    'colored',
    'yaspin',
]
EXTRAS_REQUIRE = {
    'dev': [
        'pytest',
        'pytest-cov',
        'pytest-flake8',
        'flake8',
        'sphinx',
        'cprofilev',
        'sphinx-click',
        'coverage',
        'ptpython',
    ]
}

if sys.platform in ('win32', 'win64',):
    REQUIRES.extend(['pypiwin32'])

RELEASE = {}

# NOTE: important dumb setup for complete segregation of module info
with open(
    os.path.join(CURDIR, 'torvend', '__version__.py'), 'r',
    encoding='utf-8'
) as fp:
    exec(fp.read(), RELEASE)


class UploadCommand(setuptools.Command):

    description = 'Build and publish package'
    user_options = []

    @staticmethod
    def status(status):
        print(('... {status}').format(**locals()))

    def initialize_options(self):
        pass

    def finalize_options(self):
        pass

    def run(self):
        try:
            self.status('removing previous builds')
            shutil.rmtree(os.path.join(CURDIR, 'dist'))
        except FileNotFoundError:
            pass

        self.status('building distribution')
        os.system(('{exe} setup.py sdist').format(exe=sys.executable))

        self.status('uploading distribution')
        os.system('twine upload dist/*')

        self.status('pushing git tags')
        os.system(('git tag v{ver}').format(ver=RELEASE['__version__']))
        os.system('git push --tags')

        sys.exit()


setuptools.setup(
    name=RELEASE['__name__'],
    version=RELEASE['__version__'],
    description=RELEASE['__description__'],
    long_description=open(os.path.join(CURDIR, 'README.rst'), 'r').read(),
    license=RELEASE['__license__'],
    author=RELEASE['__author__'],
    author_email=RELEASE['__contact__'],
    url='https://github.com/stephen-bunn/torvend',
    include_package_data=True,
    install_requires=REQUIRES,
    extras_require=EXTRAS_REQUIRE,
    packages=setuptools.find_packages(),
    entry_points={
        'console_scripts': ['torvend=torvend:cli']
    },
    keywords=[
        'web-scraping',
        'torrent',
        'search',
        'python3',
        'asynchronous',
        'command-line',
        'framework',
    ],
    python_requires='>=3.5',
    classifiers=[
        'Development Status :: 2 - Pre-Alpha',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: Implementation :: CPython',
        'License :: OSI Approved :: MIT License',
        'Intended Audience :: Developers',
        'Intended Audience :: System Administrators',
        'Operating System :: POSIX',
        'Operating System :: MacOS :: MacOS X',
        'Natural Language :: English',
        'Topic :: Internet :: WWW/HTTP :: Indexing/Search',
        'Topic :: Utilities'
    ],
    cmdclass={
        'upload': UploadCommand,
    },
)
