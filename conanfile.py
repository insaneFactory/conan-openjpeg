#!/usr/bin/env python
# -*- coding: utf-8 -*-

from conans import ConanFile, CMake, tools
import os

class OpenJpegConan(ConanFile):
    name = "openjpeg"
    version = "2.3.0"
    description = "OpenJPEG is an open-source JPEG 2000 codec written in C language."
    options = {"shared": [True, False]}
    default_options = "shared=False"
    generators = "cmake"
    settings = "os", "compiler", "build_type", "arch"
    exports = ["CMakeLists.txt", "LICENSE"]
    url="https://github.com/bincrafters/conan-openjpeg"
    license="https://github.com/uclouvain/openjpeg/blob/master/LICENSE"

    def source(self):
        source_url = "https://github.com/uclouvain/openjpeg"
        tools.get("{0}/archive/v{1}.tar.gz".format(source_url, self.version))
        extracted_dir = self.name + "-" + self.version
        os.rename(extracted_dir, "sources")

    def build(self):
        cmake = CMake(self.settings)
        self.run('cmake %s %s' % (self.conanfile_directory, cmake.command_line))
        self.run("cmake --build . %s" % cmake.build_config)

    def package(self):
        dst_folder=self.name + '-2.3'
        self.copy("*.h", dst="include/openjpeg-2.3", keep_path=False)
        self.copy("*.lib", dst="lib", src="lib", keep_path=False)
        self.copy("*.dll", dst="bin", src="sources", keep_path=False)
        self.copy("*.dylib", dst="lib", src="sources", keep_path=False)
        self.copy("*.so*", dst="lib", src="sources", keep_path=False)
        self.copy("*.a", dst="lib", src="lib", keep_path=False)

    def package_info(self):
        self.cpp_info.libs = ["openjp2"]

