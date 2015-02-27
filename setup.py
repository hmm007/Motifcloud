
from distutils.core import setup
from Cython.Build import cythonize

setup(
    name='VisMotif',
    version='0.9',
    url='https://github.com/hmm007/VisMotif',
    license='See License File',
    ext_modules=cythonize('VisMotif/query_integral_image.pyx'),
    packages=['VisMotif'],
    package_data={'VisMotif'}
)
