#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import tempfile
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
    requires = "zlib/1.2.11@conan/stable"
    install_dir = tempfile.mkdtemp(name)

    def source(self):
        source_url = "https://github.com/uclouvain/openjpeg"
        tools.get("{0}/archive/v{1}.tar.gz".format(source_url, self.version))
        extracted_dir = self.name + "-" + self.version
        os.rename(extracted_dir, "sources")

    def build(self):
        cmake = CMake(self)
        cmake.definitions["CMAKE_INSTALL_PREFIX"] = self.install_dir
        cmake.configure()
        cmake.build()
        cmake.install()

    def package(self):
        lib_dir = os.path.join(self.install_dir, "lib")
        bin_dir = os.path.join(self.install_dir, "bin")
        self.copy(pattern="LICENSE", dst=".", src=os.path.join("source", "LICENSE"))
        self.copy("*.h", dst="include", src=os.path.join(self.install_dir, "include"))
        self.copy("*.cmake", dst="res", src=lib_dir, keep_path=False)
        if self.options.build_codec:
            self.copy("opj_*", dst="bin", src=bin_dir, keep_path=False)
        if self.settings.os == "Windows":
            if self.options.shared:
                self.copy(pattern="*.dll", dst="bin", src="bin", keep_path=False)
            self.copy(pattern="*.lib", dst="lib", src="lib", keep_path=False)
        elif str(self.settings.os) in ['Linux', 'Android']:
            if self.options.shared:
                self.copy("*.so*", dst="lib", src="lib", keep_path=False)
            else:
                self.copy("*.a", dst="lib", src="lib", keep_path=False)
        elif str(self.settings.os) in ['Macos', 'iOS', 'watchOS', 'tvOS']:
            if self.options.shared:
                self.copy("*.dylib", dst="lib", src="lib", keep_path=False)
            else:
                self.copy("*.a", dst="lib", src="lib", keep_path=False)

    def package_info(self):
        self.cpp_info.libs = tools.collect_libs(self)
        if self.settings.os == "Linux":
            self.cpp_info.libs.append("pthread")
