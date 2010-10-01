#!/usr/bin/env python

from distutils.core import setup

setup(name          = 'Freesound',
      version       = '0.1',
      description   = 'Client library for accessing the Freesound API.',
      author        = 'Gerard Roma',
      author_email  = 'gerard.roma@upf.edu',
      url           = 'http://www.freesound.org',
      packages      = ['freesound'],
      install_requires = ['simplejson',
                          'poster',
                          'httplib2']
     )
