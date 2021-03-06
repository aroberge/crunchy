""" configuration.py:
    Keeps track of user based settings, some automatically set
    by Crunchy, others ajustable by the user.
"""

### Important:
#
# In order to reduce the list of variables displayed in the popup
# "tooltip" when the user enters "crunchy.", some methods have been
# prefixed by a leading underscore; Crunchy (in tooltip.py) filters
# out such methods from the display.

import os

import pickle

from src.interface import config, u_print, translate, additional_vlam, accounts, python_version

if python_version < 3:
    ask_user = raw_input
    from urlparse import urlsplit
else:
    ask_user = input
    from urllib.parse import urlsplit

import src.interface as interface

ANY = '*'

_ = translate['_']
translate['init_translation']()

# Existing translations for Crunchy messages
trans_path = os.path.join(config['crunchy_base_dir'], "translations")
trans_path2 = os.path.join(config['crunchy_base_dir'], "server_root",
                                                          "edit_area", "langs")
# Different Pickle protocol in Python 3.
if python_version < 3:
    settings_path = "settings.pkl"
else:
    settings_path = "settings-3.pkl"

options = {
    'analyzer': [None],
    'dir_help': [True, False],
    'doc_help': [True, False],
    'popups': [True, False],
    'forward_accept_language': [True, False],
    'friendly': [True, False],
    'menu_position': ['default'],
    'alternate_python_version': [ANY],
    'user_dir': [ANY],
    'temp_dir': [ANY],
    'power_browser': [None],
    'security': [ 'trusted', 'display trusted',
                  'normal', 'display normal',
                  'strict', 'display strict'],
    'modify_markup': [True, False],
    'no_markup': [None],
    'override_default_interpreter' : [None],
    # allow languages values like "en" or "en_GB"; str(f) converts u"en" to "en"
    'language': [str(f) for f in os.listdir(trans_path)
                             if (len(f)==2 or (len(f) == 5 and f[2] == '_'))
                                    and not f.startswith('.')],
    # language file names end in ".js"
    'editarea_language': [str(f[0:-3]) for f in os.listdir(trans_path2)
                             if (len(f)==5 or (len(f) == 8 and f[2] == '_'))
                                    and not f.startswith('.')]
}
options['site_security'] = options['local_security'] = options['security']

def make_property(name, default=None, doc=None): # tested
    '''creates properties within allowed values (if so specified)
       with some defaults, and enables automatic saving of new values'''
    allowed = options[name]
    if default is None:
        default = allowed[0]

    def fget(obj): # indirectly tested
        '''simply returns the attribute for the requested object'''
        return getattr(obj, "_"+name)

    def _set_and_save(obj, _name, value, initial=False): # indirectly tested
        '''sets the value and make the required call to save the new status'''
        setattr(obj, "_" + _name, value)
        getattr(obj, '_save_settings')(_name, value, initial)
        return

    def _only_set_and_save_if_new(obj, name, val): # indirectly tested
        '''sets the value (and save the new status) only if there is
           a change from the current value; this is to prevent
           needlessly writing to files'''
        try:  # don't save needlessly if there is no change
            current = getattr(obj, "_"+name)
            if val == current:
                return
            else:
                _set_and_save(obj, name, val)
        except:
            _set_and_save(obj, name, val)
        return

    def fset(obj, val): # indirectly tested
        '''assigns a value within an allowed set (if defined),
           and saves the result'''
        prefs = getattr(obj, "_preferences")
        # some properties are designed to allow any value to be set to them
        if ANY in allowed and val != ANY:
            allowed.append(val)

        if val not in allowed:
            try:
                current = getattr(obj, "_"+name) # can raise AttributeError
                                                   # if not (yet) defined...
                u_print(_("%s is an invalid choice for %s.%s" % (val,
                                                        prefs['_prefix'], name)))
                u_print(_("The valid choices are: "), allowed)
                u_print(_("The current value is: "), current)
            except AttributeError: # first time; set to default!
                _set_and_save(obj, name, default, initial=True)
        else:
            if val == ANY:
                try:
                    current = getattr(obj, "_"+name)
                except:
                    current = default
                val = current
            _only_set_and_save_if_new(obj, name, val)
        return
    if doc is None:
        return property(fget, fset)
    else:
        return property(fget, fset, None, doc)

class Base(object):
    '''Base class for all objects that keeps track of
       configuration values in properties.  On its own, it does nothing;
       see test_configuration.rst for sample uses.'''

    def _init_properties(self, cls): # indirectly tested
        '''automatically assigns all known properties.'''
        # Note: properties are class variables which is why we need
        # to pass the class name as a parameter.
        for key in cls.__dict__:
            val = cls.__dict__[key]
            if isinstance(val, property):
                val.fset(self, ANY)
        return

class UserPreferences(Base):
    """
    class containing various default values that can be set by user according
    to their preferences.

    IMPORTANT: you can specify the value of a given "Data descriptor" by entering
    crunchy.descriptor = value
    """
    def __init__(self, prefs, name):
        self.name = name
        self._preferences = prefs
        self._preferences.update({'_prefix': 'crunchy',
                            'page_security_level': self._page_security_level,
                            '_set_site_security': self._set_site_security})
        self._not_saved = list(self._preferences.keys())
        self._not_saved.extend(['user_dir', 'log', 'logging_uids', 'symbols',
                                'initial_security_set', 'page_security_level'])

        self.site_security = {}
        #self.styles = {}
        self._modification_rules = []
        self._preferences.update({'site_security': self.site_security,
                            #'styles': self.styles,
                            '_modification_rules': self._modification_rules})
        self._not_loaded = True
        self._set_dirs()
        # self.logging_uids is needed by comitIO.py:87
        self.logging_uids = {}  # {uid : (name, type)}
                               # name is defined by tutorial writer
                               # type is one of 'interpreter', 'editor',...
        # the following two variables will be replaced by Tao's improved logging
        self.log_filename = os.path.join(os.path.expanduser("~"),
                                          "crunchy_log.html")
        self.log = {}
        # Make sure to initialize properties so that they exist before
        # retrieving saved values
        self._init_properties(UserPreferences)
        self._load_settings()

    analyzer = make_property('analyzer',
                            doc="""\
Specifies the code analyzer to use (e.g. pylint, pyflakes, etc.) if available.""")

    dir_help = make_property('dir_help',
        doc="""\
If True, when a '.' is pressed for 'object.', a popup window
appears displaying the available methods and attributes, with
the exception of those that start with a leading underscore.""")

    doc_help = make_property('doc_help',
        doc="""\
If True, displays the result of help(fn) where fn is either a
function or method when an open parenthese "fn(" is typed.""")

    forward_accept_language = make_property('forward_accept_language',
        doc="""\
If True, the browser will forward the default language chosen
by the user to the website so that pages in that language
will be sent back if they are available.""")

    friendly = make_property('friendly',
        doc="""\
If True, Crunchy will try to simplify some tracebacks and doctest
results so that they are easier to understand for beginners.""")

    override_default_interpreter = make_property('override_default_interpreter',
        doc="""\
If a value other than None is specified, Crunchy will replace
any interpreter type specified by a tutorial writer by this value.""")

    language = make_property('language', default='en',
        doc="""Specifies the language used by Crunchy for output, menus, etc.""")

    editarea_language = make_property('editarea_language', default='en',
        doc="""\
Specifies the language used by the embedded editor 'editarea' for tooltips, etc.""")

    local_security = make_property('local_security',
        doc="""\
Specifies the security setting for tutorials loaded from
the local server (127.0.0.1) running Crunchy.""")

    menu_position = make_property('menu_position',
        doc="""Specifies the position where the menu should appear.""")

    modify_markup = make_property('modify_markup', default=False,
        doc="""\
If True, invokes a set of user-defined rules to modify the existing
markup on a page (currently restricted to changing the title attributes
of <pre> html elements).  This is disabled when viewing a slideshow.""")

    no_markup = make_property('no_markup', default='python_tutorial',
        doc="""\
Specifies the 'interactive element' to be included whenever
Crunchy encounters a <pre> html tag with no Crunchy-related markup.
This is disabled when viewing a slideshow.""")

    power_browser = make_property('power_browser',
        doc="""\
If the value is not None, inserts the requested file browser
at the bottom of every page displayed by Crunchy.""")

#    my_style = make_property('my_style', default=False,
#        doc="""\
#If True, indicates that Crunchy will replace some styling (css)
#by some values specified by the user in crunchy.styles""")

    popups = make_property('popups', doc="""\
If True, will insert helpful images with informative text displayed as a popup
when the mouse is hovering over; it will also insert similar popups over
other images that are always included for some interactive elements.""")

    alternate_python_version = make_property('alternate_python_version',
                                             default="python",
        doc="""\
Specifies the command to be used when launching a script using
a possibly different python version than the one that was
used to launch Crunchy.""")

    user_dir = make_property('user_dir',
        doc="""\
Location of the user directory, where the configuration file
is saved; please do not attempt to change from inside Crunchy.""")

    temp_dir = make_property('temp_dir',
        doc="""\
Location of a 'temporary' directory from which external scripts
are usually launched.""")

    def _set_dirs(self):
        '''sets the user directory, creating it if needed.
           Creates also a temporary directory'''
        if self.name != "Unknown User":
            self.user_dir = accounts[self.name][0]
        else:
            self.user_dir = os.path.join(os.path.expanduser("~"), ".crunchy")
        self.temp_dir = os.path.join(self._user_dir, "temp")

        if not os.path.exists(self.user_dir):  # first time ever
            try:
                os.makedirs(self.user_dir)
                if not os.path.exists(self.temp_dir):
                    try:
                        os.makedirs(self.temp_dir)
                    except:
                        # Note: we do not translate diagnostic messages
                        # sent to the terminal
                        u_print("Created successfully home directory.")
                        u_print("Could not create temporary directory.")
                        self.temp_dir = self.user_dir
                    return
            except:
                u_print("Could not create the user directory.")
                self.user_dir = os.getcwd()  # use crunchy's as a default.
                self.temp_dir = os.path.join(self.user_dir, "temp")
                if not os.path.exists(self.temp_dir):
                    try:
                        os.makedirs(self.temp_dir)
                    except:
                        u_print("Could not create temporary directory.")
                        self.temp_dir = self.user_dir
                    return
                return
        # we may encounter a situation where a ".crunchy" directory
        # had been created by an old version without a temporary directory
        if not os.path.exists(self.temp_dir):
            try:
                os.makedirs(self.temp_dir)
            except:
                u_print("home directory '.crunchy' exists; however, ")
                u_print("could not create temporary directory.")
                self.temp_dir = self.user_dir
            return
        return

    def _load_settings(self):
        '''
        loads the user settings from a configuration file; uses default
        values if file specific settings is not found.
        '''
        success = False
        pickled_path = os.path.join(self.user_dir, settings_path)
        try:
            pickled = open(pickled_path, 'rb')
            success = True
        except:
            u_print("No configuration file found.")
            u_print("user_dir = ", self.user_dir)
        if success:
            try:
                saved = pickle.load(pickled)
                pickled.close()
            except EOFError:
                self._not_loaded = False
                self._save_settings()
                return
        else:
            # save the file with the default value
            self._not_loaded = False
            self._save_settings()
            return

        for key in saved:
            try:
                val = UserPreferences.__dict__[key]
                if isinstance(val, property):
                    val.fset(self, saved[key])
                else:
                    u_print("*"*50)
                    u_print("Unless Crunchy has just been updated,")
                    u_print("this should not happen.")
                    u_print("saved variable: %s is not a property", key)
            except:
                try:
                    val = getattr(self, key)
                    setattr(self, key, saved[key])
                    self._preferences[key] = saved[key]
                except:
                    u_print("*"*50)
                    u_print("Unless Crunchy has just been updated,")
                    u_print("this should not happen.")
                    u_print("saved variable: %s is not recognized" % key)
        self._not_loaded = False
        return

    def _save_settings(self, name=None, value=None, initial=False):
        '''Update user settings and save results to a configuration file'''
        if name is not None: # otherwise, we need to save all...
            self._preferences[name] = value
            if initial:
                return
            if name == 'language':
                self._select_language(value)
            if self._not_loaded:  # saved configuration not retrieved; do not overwrite
                return

        # update values of non-properties
        self._preferences['site_security'] = self.site_security
        #self._preferences['styles'] = self.styles
        self._preferences['_modification_rules'] = self._modification_rules
        saved = {}
        for name in self._preferences:
            if not (name in self._not_saved or name.startswith('_')):
                saved[name] = self._preferences[name]
        saved['_modification_rules'] = self._modification_rules
        pickled_path = os.path.join(self.user_dir, settings_path)
        try:
            pickled = open(pickled_path, 'wb')
        except:
            u_print("Could not open file in configuration._save_settings().")
            return
        pickle.dump(saved, pickled, protocol=2)
        pickled.close()
        return

    def _select_language(self, choice):
        '''selects the appropriate file for language translation and attempts
        to set editarea_language to the same value'''
        translate['init_translation'](choice)
        u_print(_("language set to: ") , choice)
        self.editarea_language = choice

    def _page_security_level(self, url):
        '''determine the page security level based on the url'''
        info = urlsplit(url)
        # info.netloc == info[1] is not Python 2.4 compatible; we "fake it"
        info_netloc = info[1]
        if info_netloc == '':
            level = self.local_security
        else:
            level = self._get_site_security(info_netloc)
        self.current_page_security_level = level
        return level

    def _set_local_security(self, choice):
        '''sets the security level for pages viewed locally'''
        self.local_security = choice

    def _get_current_page_security_level(self):
        '''retrieves the security level of the current page'''
        return self.current_page_security_level

    def _get_site_security(self, site):
        '''determines the appropriate level of security to use for given site'''
        if site in self.site_security:
            u_print("in _get_site_security, site = ", site)
            return self.site_security[site]
        else:
            return 'display trusted'

    def _set_site_security(self, site, choice):
        '''sets the security level of a given site'''
        if choice in options['security']:
            self.site_security[site] = choice
            self._save_settings('site_security', choice)
            u_print(_("site security set to: ") , choice)
        else:
            u_print((_("Invalid choice for %s.site_security") %
                                                         self._preferences['_prefix']))
            u_print(_("The valid choices are: "), str(options['security']))

    def add_site(self):
        '''interactive function to facilitate adding new site to
           the secured list'''
        site = ask_user(_("Enter site url (for example, docs.python.org) "))
        level = ask_user(_("Enter security level (for example: normal) "))
        self._set_site_security(site, level)

    def add_rule(self):
        '''interactive function to enable rules to modify markup'''
        u_print(_("Enter a rule method to modify markup."))
        u_print(_("The allowed methods are: add_option, remove_option, replace"))
        method = ask_user(_("Enter method: ")).strip()
        if method == 'replace':
            to_replace = ask_user(_("Markup value to replace: "))
            replacement = ask_user(_("Replacement value: "))
            self._modification_rules.append([method, to_replace, replacement])
        elif method == 'add_option':
            add = ask_user(_("Enter option to add (e.g. linenumber): "))
            self._modification_rules.append([method, add])
        elif method == 'remove_option':
            remove = ask_user(_("Enter option to remove (e.g. linenumber)"))
            self._modification_rules.append([method, remove])
        else:
            u_print(_("Unknown method."))
            return
        self._save_settings()
        return

    def remove_rule(self, no):
        '''remove an existing rule'''
        try:
            del self._modification_rules[no]
            self._save_settings()
        except:
            u_print(_("Choose a valid rule number to remove."))
            self.list_rules()
        return

    def list_rules(self):
        '''list the rules used to modify markup'''
        u_print("#", _("\tmethod"), _("\targuments"))
        for i, rule in enumerate(self._modification_rules):
            u_print(i, "\t%s" % rule[0], "\t%s" % rule[1:])

    def _set_alternate_python_version(self, alt_py):
        '''sets the path to use for using an alternate Python version
           to run external scripts.'''
        self.alternate_python_version = alt_py
    #==============

def init():
    '''Called when we need to initialize the various instances - based on the
    number of different users defined.'''

    for prop in interface.additional_properties:
        setattr(UserPreferences, prop, interface.additional_properties[prop])

    skipped = []
    for key in additional_vlam:
        try:
            options[key].extend(additional_vlam[key])
        except:  # the key might not be registered yet
            options[key] = []
            skipped.append((key, additional_vlam[key]))

    # after the first pass, problematic keys should have been registered
    # by the plugin.
    for key, additional_option in skipped:
        try:
            options[key].extend(additional_option)
        except:
            u_print("Problem in config.init()")
            u_print("The following additional vlam option")
            u_print("key = %s, value= %s" %(key, additional_option))
            u_print("is raising an exception.")
            u_print("Please file a bug report")

    users = {}
    for name in accounts:
        config[name] = {}
        users[name] = UserPreferences(config[name], name)
        config[name]['log'] = users[name].log
        config[name]['log_filename'] = os.path.join(users[name].temp_dir, 'crunchy.html')
        config[name]['logging_uids'] = users[name].logging_uids
        config[name]['symbols'] = {config[name]['_prefix']:users[name],
                                    'temp_dir': users[name].temp_dir}
        config[name]['temp_dir'] = users[name].temp_dir
        config[name]['_get_current_page_security_level'] = users[name]._get_current_page_security_level
        config[name]['_set_alternate_python_version'] = users[name]._set_alternate_python_version
        config[name]['_set_local_security'] = users[name]._set_local_security
        config[name]['_save_settings'] = users[name]._save_settings
        config[name]['initial_security_set'] = False
