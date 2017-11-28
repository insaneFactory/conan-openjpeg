#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
from conans import ConanFile, CMake, tools


class OpenJpegConan(ConanFile):
    name = "openjpeg"
    version = "2.3.0"
    description = "OpenJPEG is an open-source JPEG 2000 codec written in C language."
    options = {"shared": [True, False], "build_codec": [True, False]}
    default_options = "shared=False", "build_codec=True"
    settings = "os", "compiler", "build_type", "arch"
    generators = "cmake"
    exports = "LICENSE"
    exports_sources = "CMakeLists.txt"
    url = "https://github.com/bincrafters/conan-openjpeg"
    license = "https://github.com/uclouvain/openjpeg/blob/master/LICENSE"
    author = "Alexander Zaitsev <zamazan4ik@tut.by>"

    def requirements(self):
        self.requires.add('zlib/1.2.11@conan/stable')
        self.requires.add('lcms/2.9@bincrafters/stable')
        self.requires.add('libpng/1.6.34@bincrafters/stable')
        self.requires.add('libtiff/4.0.8@bincrafters/stable')

    def source(self):
        source_url = "https://github.com/uclouvain/openjpeg"
        tools.get("{0}/archive/v{1}.tar.gz".format(source_url, self.version))
        extracted_dir = self.name + "-" + self.version
        os.rename(extracted_dir, "sources")

    def build(self):
        # ensure our lcms is used
        os.unlink(os.path.join('sources', 'cmake', 'FindLCMS2.cmake'))
        cmake = CMake(self)
        cmake.configure()
        cmake.build()
        cmake.install()

    def package(self):
        self.copy(pattern="LICENSE", dst=".", src=os.path.join("source", "LICENSE"))
        self.copy("*.a", dst="lib", src="lib", keep_path=False)

    def package_info(self):
        self.cpp_info.libs = ['openjp2']
        if not self.options.shared:
            self.cpp_info.defines.append('OPJ_STATIC')
        if self.settings.os == "Linux":
            self.cpp_info.libs.append("pthread")
