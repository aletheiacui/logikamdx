from setuptools import setup, find_packages

setup(
    name='logikamdx',
    version='0.1',
    install_requires = ['markdown>=3.0'],
    packages=find_packages(),
    entry_points={
        'markdown.extensions': ['logikamdx = logikamdx.logika_mdx:LogikaExtension']
    }
)