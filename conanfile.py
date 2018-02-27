#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import shutil
from conans import ConanFile, CMake, tools


class OpenjpegConan(ConanFile):
    name = "openjpeg"
    version = "2.3.0"
    description = "OpenJPEG is an open-source JPEG 2000 codec written in C language."
    options = {"shared": [True, False], "build_codec": [True, False], "fPIC": [True, False]}
    default_options = "shared=False", "build_codec=True", "fPIC=True"
    settings = "os", "compiler", "build_type", "arch"
    generators = "cmake"
    exports = "LICENSE.md"
    exports_sources = "CMakeLists.txt"
    url = "https://github.com/bincrafters/conan-openjpeg"
    homepage = "https://github.com/uclouvain/openjpeg"
    license = "BSD 2-Clause"

    source_subfolder = "source_subfolder"

    def requirements(self):
        self.requires.add("zlib/1.2.11@conan/stable")
        self.requires.add("lcms/2.9@bincrafters/stable")
        self.requires.add("libpng/1.6.34@bincrafters/stable")
        self.requires.add("libtiff/4.0.8@bincrafters/stable")

    def config_options(self):
        if self.settings.os == "Windows":
            self.options.remove("fPIC")

    def source(self):
        source_url = "https://github.com/uclouvain/openjpeg"
        tools.get("{0}/archive/v{1}.tar.gz".format(source_url, self.version))
        extracted_dir = self.name + "-" + self.version
        os.rename(extracted_dir, self.source_subfolder)

        os.rename(os.path.join(self.source_subfolder, "CMakeLists.txt"),
                  os.path.join(self.source_subfolder, "CMakeListsOriginal.txt"))
        shutil.copy("CMakeLists.txt",
                    os.path.join(self.source_subfolder, "CMakeLists.txt"))

    def build(self):
        # ensure our lcms is used
        os.unlink(os.path.join(self.source_subfolder, 'cmake', 'FindLCMS2.cmake'))

        # fix installing libs when only shared or static library built
        tools.replace_in_file(os.path.join(self.source_subfolder, 'src', 'lib', 'openjp2', 'CMakeLists.txt'),
                              'add_library(${OPENJPEG_LIBRARY_NAME} ${OPENJPEG_SRCS})',
                              'add_library(${OPENJPEG_LIBRARY_NAME} ${OPENJPEG_SRCS})\n'
                              'set(INSTALL_LIBS ${OPENJPEG_LIBRARY_NAME})')

        cmake = CMake(self)
        cmake.definitions['BUILD_SHARED_LIBS'] = self.options.shared
        cmake.definitions['BUILD_STATIC_LIBS'] = not self.options.shared
        if self.settings.os != "Windows":
            cmake.definitions["CMAKE_POSITION_INDEPENDENT_CODE"] = self.options.fPIC
        cmake.configure(source_folder=self.source_subfolder)
        cmake.build()
        cmake.install()

    def package(self):
        self.copy(pattern="LICENSE", dst="licenses", src=self.source_subfolder)
        # remove binaries
        for bin_program in ['opj_dump', 'opj_compress', 'opj_decompress']:
            for ext in ['', '.exe']:
                try:
                    os.remove(os.path.join(self.package_folder, 'bin', bin_program+ext))
                except:
                    pass


    def package_info(self):
        self.cpp_info.libs = tools.collect_libs(self)
        if not self.options.shared:
            self.cpp_info.defines.append('OPJ_STATIC')
        if self.settings.os == "Linux":
            self.cpp_info.libs.append("pthread")
