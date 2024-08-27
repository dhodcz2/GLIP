# Copyright (c) Facebook, Inc. and its affiliates. All Rights Reserved.
#!/usr/bin/env python

import glob
import os
import sys
import ensurepip
import subprocess
from pkg_resources import get_distribution, DistributionNotFound
from setuptools import find_packages, setup
from setuptools.command.install import install
from setuptools.command.build_ext import build_ext
from torch.utils.cpp_extension import CUDA_HOME, CppExtension, CUDAExtension

def ensure_torch_installed():
    try:
        get_distribution('torch')
    except DistributionNotFound:
        print("Torch not found. Installing Torch...")
        ensurepip.bootstrap()
        subprocess.check_call([sys.executable, '-m', 'pip', 'install', 'torch'])

def check_cuda_availability():
    try:
        import torch
        if not torch.cuda.is_available():
            raise RuntimeError("CUDA is not available. Please ensure that CUDA is installed and properly configured.")
    except ImportError:
        raise RuntimeError("Torch is not installed. Cannot check for CUDA availability.")

class CustomInstallCommand(install):
    def run(self):
        ensure_torch_installed()
        check_cuda_availability()
        install.run(self)

class CustomBuildExtCommand(build_ext):
    def run(self):
        ensure_torch_installed()
        check_cuda_availability()
        self.distribution.ext_modules = get_extensions()
        build_ext.run(self)

def get_extensions():
    this_dir = os.path.dirname(os.path.abspath(__file__))
    extensions_dir = os.path.join(this_dir, "glip.maskrcnn_benchmark", "csrc")

    main_file = glob.glob(os.path.join(extensions_dir, "*.cpp"))
    source_cpu = glob.glob(os.path.join(extensions_dir, "cpu", "*.cpp"))
    source_cuda = glob.glob(os.path.join(extensions_dir, "cuda", "*.cu"))

    sources = main_file + source_cpu
    extension = CppExtension
    extra_compile_args = {"cxx": []}
    define_macros = []
    import torch.cuda

    if torch.cuda.is_available() and CUDA_HOME is not None:
        extension = CUDAExtension
        sources += source_cuda
        define_macros += [("WITH_CUDA", None)]
        extra_compile_args["nvcc"] = [
            "-DCUDA_HAS_FP16=1",
            "-D__CUDA_NO_HALF_OPERATORS__",
            "-D__CUDA_NO_HALF_CONVERSIONS__",
            "-D__CUDA_NO_HALF2_OPERATORS__",
        ]

    sources = [os.path.join(extensions_dir, s) for s in sources]
    include_dirs = [extensions_dir]
    ext_modules = [
        extension(
            "glip.maskrcnn_benchmark._C",
            sources,
            include_dirs=include_dirs,
            define_macros=define_macros,
            extra_compile_args=extra_compile_args,
        )
    ]
    return ext_modules

with open('requirements.txt') as f:
    install_requires = f.read().splitlines()

setup(
    name="glip",
    version="1.0",
    author="Facebook, Inc.",
    description="Object detection in PyTorch",
    classifiers=[
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3.11",
    ],
    python_requires='>=3.11',
    include_package_data=True,
    install_requires=install_requires,
    packages=find_packages(
        include=[
            'glip',
            'glip.*',
            'glip.maskrcnn_benchmark.*',
            'glip.tools.*',
            'glip.configs.*'
        ],
    ),
    cmdclass={
        'install': CustomInstallCommand,
        'build_ext': CustomBuildExtCommand,
    },
    entry_points={},
)
