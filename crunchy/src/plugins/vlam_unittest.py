"""  Crunchy unittest plugin.

From a subclass of unittest.TestCase in a <pre> element, create an editor for
a user to enter some code which should satisfy the unittest.
"""

# All plugins should import the crunchy plugin API via interface.py
from src.interface import config, plugin, Element, SubElement, tostring, python_version
from src.utilities import extract_log_id, wrap_in_div

# The set of other "widgets/services" required from other plugins
requires =  set(["editor_widget", "io_widget"])

# each unittest code sample will be kept track via a uid used as a key.
unittests = {}

def register():
    """The register() function is required for all plugins.
       In this case, we need to register two types of 'actions':
       1. a custom 'vlam handler' designed to tell Crunchy how to
          interpret the special Crunchy markup.
       2. a custom http handler to deal with "run unittest" commands,
          issued by clicking on a button incorporated in the
          'unittest widget';
       """
    # 'unittest' only appears inside <pre> elements, using the notation
    # <pre title='unittest ...'>
    plugin['register_tag_handler']("pre", "title", "unittest",
                                          unittest_widget_callback)
    # By convention, the custom handler for "name" will be called
    # via "/name"; for security, we add a random session id
    # to the custom handler's name to be executed.
    plugin['register_http_handler'](
                         "/unittest%s"%plugin['session_random_id'],
                                       unittest_runner_callback)


def unittest_runner_callback(request):
    """Handles all execution of unittests. The request object will contain
    all the data in the AJAX message sent from the browser."""
    # note how the code to be executed is not simply the code entered by
    # the user, and obtained as "request.data", but also includes a part
    # (doctest_pycode) defined below used to automatically call the
    # correct method in the doctest module.
    # TODO: update the comment
    if python_version >= 3:
        request.data = request.data.decode('utf-8')
    code = unittest_pycode % {
        'user_code': request.data,
        'unit_test': unittests[request.args["uid"]],
    }
    plugin['exec_code'](code, request.args["uid"], doctest=False) # TODO: doctests=True?
    request.send_response(200)
    request.end_headers()

def unittest_widget_callback(page, elem, uid):
    """Handles embedding suitable code into the page in order to display and
    run unittests"""
    vlam = elem.attrib["title"]
    log_id = extract_log_id(vlam)
    if log_id:
        t = 'unittest'
        config[page.username]['logging_uids'][uid] = (log_id, t)

    # When a security mode is set to "display ...", we only parse the
    # page, but no Python execution from is allowed from that page.
    # If that is the case, we won't include javascript either, to make
    # thus making the source easier to read.
    if 'display' not in config[page.username]['page_security_level'](page.url):
        if not page.includes("unittest_included") :
            page.add_include("unittest_included")
            page.add_js_code(unittest_jscode)

    elem.attrib['title'] = "python"
    unittestcode, show_vlam = plugin['services'].style(page, elem, None, vlam)
    elem.attrib['title'] = vlam

    if log_id:
        config['log'][log_id] = [tostring(markup)]
    # which we store
    unittests[uid] = unittestcode

    wrap_in_div(elem, uid, vlam, "doctest", show_vlam)
    if config[page.username]['popups']:
        # insert popup helper
        img = Element("img", src="/images/help.png", style="height:32px;",
                title = "cluetip Hello %s! "%page.username + "This is a unittest.; click for more.",
                rel = "/docs/popups/unittest.html")
        elem.append(img)
        plugin['services'].insert_cluetip(page, img, uid)

    #insert_markup(elem, uid, vlam, markup, "unittest")

    # call the insert_editor_subwidget service to insert an editor:
    plugin['services'].insert_editor_subwidget(page, elem, uid)
    #some spacing:
    SubElement(elem, "br")
    # the actual button used for code execution:
    btn = SubElement(elem, "button")
    btn.text = "Run Unittest"
    btn.attrib["onclick"] = "exec_unittest('%s')" % uid
    if "analyzer_score" in vlam:
        plugin['services'].add_scoring(page, btn, uid)
    if "analyzer_report" in vlam:
        plugin['services'].insert_analyzer_button(page, elem, uid)
    SubElement(elem, "br")
    # finally, an output subwidget:
    plugin['services'].insert_io_subwidget(page, elem, uid)

# we need some unique javascript in the page; note how the
# "/unittest" handler mentioned above appears here, together with the
# random session id.
unittest_jscode = """
function exec_unittest(uid){
    try{
    document.getElementById("kill_image_"+uid).style.display = "block";
    }
    catch(err){;}
    code=editAreaLoader.getValue("code_"+uid);
    var j = new XMLHttpRequest();
    j.open("POST", "/unittest%s?uid="+uid, false);
    j.send(code);
};
""" % plugin['session_random_id']
# Finally, the special Python code used to call the unittest module,
# mentioned previously
unittest_pycode = '''
import unittest

%(user_code)s

%(unit_test)s

def test_suite():
    """Make the list of test classes"""
    obj_list = (globals()[obj_name] for obj_name in globals())
    tests = []
    for obj in obj_list:
        try:
            if issubclass(obj, unittest.TestCase):
                tests.append(unittest.makeSuite(obj))
        except TypeError:
            # obj is not a class
            pass
    return unittest.TestSuite(tests)

#__test_runner = unittest.TextTestRunner(doctest_out)
__test_runner = unittest.TextTestRunner(descriptions=2, verbosity=2)
__test_runner.run(test_suite())
'''

#Note: information about doctest_out is found in interpreter.py
