import setuptools

with open("README.md", "r", encoding='utf-8') as fh:
    long_description = fh.read()

setuptools.setup(
        name="xiaoxiao_lhy",
        version="0.0.1",
        author="Lhy",
        author_email="lhuaye@163.com",
        description="IC hardware design tools",
        long_description=long_description,
        long_description_content_type="text/markdown",
        url="https://github.com/belang/xiaoxiao",
        packages=setuptools.find_packages(),
        classifiers=[
            "Programming Language :: Python :: 3",
            "License :: BSD-3",
            "Operation System :: OS Independent",
            ],
        python_requires='>=3.6',
        )
