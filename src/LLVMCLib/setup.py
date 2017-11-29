from distutils.core import setup, Extension

module1 = Extension('arborllvm',
                    define_macros = [('MAJOR_VERSION', '1'),
                                     ('MINOR_VERSION', '0')],
                    include_dirs = ['/usr/local/include', '/usr/lib/llvm-3.8/include'],
                    libraries = ['tcl83'],
                    library_dirs = ['/usr/local/lib'],
                    sources = ['main.cpp'])

setup (name = 'Arbor LLVM Links',
       version = '1.0',
       description = 'This is the LLVM Python extensions for the Arbor Project',
       author = 'Yoseph Radding',
       author_email = 'toseph@shuttl.io',
       url = 'https://docs.python.org/extending/building',
       long_description = '''
This is really just a demo package.
''',
       ext_modules = [module1])