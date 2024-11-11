from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="linux-system-probe",
    version="0.1.0",
    author="Your Name",
    author_email="your.email@example.com",
    description="A Linux system monitoring probe with client-server architecture",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/yourusername/linux-system-probe",
    packages=find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: POSIX :: Linux",
    ],
    python_requires=">=3.6",
    install_requires=[
        "psutil>=5.8.0",
        "requests>=2.25.1",
        "flask>=2.0.0",
        "pillow>=8.0.0",
        "PyPDF2>=2.0.0",
        "plyer>=2.0.0"
    ],
    entry_points={
        'console_scripts': [
            'probe-server=probe.server:main',
            'probe-client=probe.client:main',
            'file-renamer=probe.tools.file_renamer:main',
            'pdf-merger=probe.tools.pdf_merger:main',
            'image-compressor=probe.tools.image_compressor:main',
            'folder-sync=probe.tools.folder_sync:main',
            'reminder=probe.tools.reminder:main',
        ],
    },
) 