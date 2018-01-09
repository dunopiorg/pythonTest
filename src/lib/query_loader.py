import xml.etree.ElementTree as Et
import os


class QueryLoader(object):
    __instance = None

    def __init__(self):
        self.query_files_dict = {}
        self.load()

    def __new__(cls):
        if QueryLoader.__instance is None:
            QueryLoader.__instance = object.__new__(cls)
        return QueryLoader.__instance

    def load(self):
        file_names = os.listdir('../query_xml')
        for filename in file_names:
            src = '../query_xml/%s' % filename
            tree = Et.parse(src)
            name = filename.split('.')[0]
            self.query_files_dict[name] = tree.getroot()

    def get_query(self, category, query_id):
        if category in self.query_files_dict:
            query_node = self.query_files_dict[category].find(".//query[@id='" + query_id + "']")

        return query_node.text
