from setuptools import setup

setup(
    name='logikamdx',
    version='0.1',
    py_modules=['logikamdx'],
    install_requires = ['markdown>=3.0'],
    entry_points={
        'markdown.extensions': ['logikamdx = logika_mdx:LogikaExtension']
    }
)