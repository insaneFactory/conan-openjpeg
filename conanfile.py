#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import shutil
from conans import ConanFile, CMake, tools


class OpenjpegConan(ConanFile):
    name = "openjpeg"
    version = "2.3.1"
    description = "OpenJPEG is an open-source JPEG 2000 codec written in C language."
    topics = ("conan", "openjpeg", "codec")
    options = {"shared": [True, False], "build_codec": [True, False], "fPIC": [True, False]}
    default_options = {'shared': False, 'build_codec': True, 'fPIC': True}
    settings = "os", "compiler", "build_type", "arch"
    generators = "cmake"
    exports = "LICENSE.md"
    exports_sources = "CMakeLists.txt"
    author = "Bincrafters <bincrafters@gmail.com>"
    url = "https://github.com/bincrafters/conan-openjpeg"
    homepage = "https://github.com/uclouvain/openjpeg"
    license = "BSD-2-Clause"

    _source_subfolder = "source_subfolder"

    requires = (
        "zlib/1.2.11",
        "lcms/2.9",
        "libpng/1.6.37",
        "libtiff/4.0.9"
    )

    def config_options(self):
        if self.settings.os == "Windows":
            self.options.remove("fPIC")

    def source(self):
        sha256 = "63f5a4713ecafc86de51bfad89cc07bb788e9bba24ebbf0c4ca637621aadb6a9"
        tools.get("{0}/archive/v{1}.tar.gz".format(self.homepage, self.version), sha256=sha256)
        extracted_dir = self.name + "-" + self.version
        os.rename(extracted_dir, self._source_subfolder)

        os.rename(os.path.join(self._source_subfolder, "CMakeLists.txt"),
                  os.path.join(self._source_subfolder, "CMakeListsOriginal.txt"))
        shutil.copy("CMakeLists.txt",
                    os.path.join(self._source_subfolder, "CMakeLists.txt"))

    def build(self):
        # ensure our lcms is used
        os.unlink(os.path.join(self._source_subfolder, 'cmake', 'FindLCMS2.cmake'))

        # fix installing libs when only shared or static library built
        tools.replace_in_file(os.path.join(self._source_subfolder, 'src', 'lib', 'openjp2', 'CMakeLists.txt'),
                              'add_library(${OPENJPEG_LIBRARY_NAME} ${OPENJPEG_SRCS})',
                              'add_library(${OPENJPEG_LIBRARY_NAME} ${OPENJPEG_SRCS})\n'
                              'set(INSTALL_LIBS ${OPENJPEG_LIBRARY_NAME})')

        cmake = CMake(self)
        cmake.definitions['BUILD_SHARED_LIBS'] = self.options.shared
        cmake.definitions['BUILD_STATIC_LIBS'] = not self.options.shared
        cmake.definitions['BUILD_PKGCONFIG_FILES'] = True
        cmake.configure(source_folder=self._source_subfolder)
        cmake.build()
        cmake.install()

    def package(self):
        self.copy(pattern="LICENSE", dst="licenses", src=self._source_subfolder)
        if self.settings.os == 'Windows':
            tools.replace_in_file(os.path.join(self.package_folder, 'lib', 'pkgconfig', 'libopenjp2.pc'),
                                  'Libs.private: -lm', '')
        elif self.settings.os == 'Linux':
            tools.replace_in_file(os.path.join(self.package_folder, 'lib', 'pkgconfig', 'libopenjp2.pc'),
                                  'Libs.private: -lm', 'Libs.private: -lm -lpthread')

    def package_info(self):
        tokens = self.version.split('.')
        self.cpp_info.includedirs.append(os.path.join('include', 'openjpeg-%s.%s' % (tokens[0], tokens[1])))
        self.cpp_info.libs = tools.collect_libs(self)
        if not self.options.shared:
            self.cpp_info.defines.append('OPJ_STATIC')
        if self.settings.os == "Linux":
            self.cpp_info.libs.append("pthread")
