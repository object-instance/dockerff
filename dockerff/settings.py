"""
Configuration
"""
import os

DOCKERFF_PREFIX = os.environ.get('DOCKERFF_PREFIX', 'dockerff')

FLUENTD_IMAGE = 'fluent/fluentd'
FIREFOX_IMAGE = 'selenium/standalone-firefox:2.53.1-beryllium'
