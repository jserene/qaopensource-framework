
class JSElementLocator(object):

    def js_xpath_click(self, path):
        xpath_loc = """document.evaluate("{0}", document, null,
                        XPathResult.FIRST_ORDERED_NODE_TYPE, null).singleNodeValue.click();""".format(path)
        return xpath_loc

    def js_class_click(self, class_name):
        c_loc = """document.getElementsByClassName('{0}').click();""".format(class_name)
        return c_loc

    def js_id_click(self, elem_id):
        id_loc = """document.getElementsById('{0}').click();""".format(elem_id)
        return id_loc

    def js_name_click(self, name):
        name_loc = """document.getElementsByName('{0}').click();""".format(name)
        return name_loc

    def js_tag_name_click(self, tag_name):
        tag_name = """document.getElementsByTagName('{0}').click();""".format(tag_name)
        return tag_name


# To use the above
# js = JSElementLocator()
# driver.execute_script(js.js_class_click('foo_class_name'))
