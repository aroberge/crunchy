'''
version plugin.

Enable the insertion of Crunchy's version anywhere in a page.
'''

from src.interface import plugin

version = "post 1.1"

def register():
    '''registers a simple tag handler'''
    plugin['register_tag_handler']("span", "title", "version", insert_version)

def insert_version(page, elem, dummy):
    '''inserts the version, replacing the text previously used as a placeholder'''
    elem.text = version