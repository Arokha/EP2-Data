#!/usr/bin/env python
# -*- coding: utf-8 -*-
import logging
import os
import json
import codecs
import collections
import re
import argparse
import uuid

# script options, default values should comply with EP2-Data rules (see readme.md)
parser = argparse.ArgumentParser()
parser.add_argument("-v", "--verbose", help="increase output verbosity", action='count', default=0)
parser.add_argument("--no-html", help="remove html formating from strings", action='store_true', default=False)
parser.add_argument("--lower-keys", help="lowercase the keys of json objects", action='store_false', default=True)
parser.add_argument("--no-uuid", help="remove any uuid from the data, otherwise add it if it's missing", action='store_true', default=False)
parser.add_argument("--no-ref", help="do not add reference and resource info of an top level object", action='store_true', default=False)
args = parser.parse_args()

log = logging.getLogger('sanitizer' if __name__ == '__main__' else __name__)

class Sanitizer(object):

	def __init__(self):
		self._files = []

	@property
	def json_files(self):
		if not self._files:
			# get the json files in the current directory and subdirs
			for root, dirs, _files in os.walk('.'):
				self._files.extend((os.path.join(root, f) for f in _files if f.endswith('.json')))
		return self._files

	@staticmethod
	def remove_bom(file_path):
		remove_bom = False
		# open the file, detect a BOM
		with open(file_path, 'r') as _file:
			content = _file.read()
			for bom_name in ['BOM_UTF8']:
				bom = getattr(codecs, bom_name)
				if content[:len(bom)] == bom:
					log.warning('%s: illegal %s' % (file_path, bom_name))
					remove_bom = True
					break
		# if a BOM has been detected remove it
		if remove_bom:
			with open(file_path, 'r') as read_no_bom:
				content = read_no_bom.read().decode('utf-8-sig') # remove the bom
			with codecs.open(file_path, 'w', encoding='utf-8') as no_bom:
				no_bom.write(content)

	def sanitize(self, obj, top_level=False):
		# a json array, sanityze its elements
		if isinstance(obj, list):
			for item in obj: self.sanitize(item, top_level = top_level)
		# it's a json object, sanitize its key,value pairs
		if isinstance(obj, dict):
			log.debug("Sanitityzing object %s" % obj)
			for key, value in obj.items():
				# lowercase the key from "Key" to "key"
				if args.lower_keys:
					del obj[key]
					key = key.lower()
				obj[key] = self.sanitize(value)
			# top level objects may require a "id", "resource" and "reference" keys
			if top_level:
				# Add or Remove UUIDs
				if args.no_uuid and 'id' in obj: del obj['id']
				if not args.no_uuid and 'id' not in obj: obj[u'id'] = unicode(str(uuid.uuid4()))
				# Add resource and reference
				if not args.no_ref and 'reference' not in obj: obj['reference'] = u''
				# XXX defaulting to EP2 second edition will be a problem when other books release
				if not args.no_ref and 'resource' not in obj: obj['resource'] = u'Eclipse Phase Second Edition'
		# a json strings
		if isinstance(obj, basestring):
			# https://github.com/Arokha/EP2-Data/issues/4
			if re.search(u'\u2013(\\d+)', obj): log.debug("Found wrong minus encoding")
			obj = re.sub(u'\u2013(\\d+)', u'-\\1', obj)
			# remove html formating from data. mutliple <p> will yield an json array of strings
			if args.no_html and '<p>' in obj:
				obj = obj.replace('</p>', '')
				obj = filter(bool, obj.split('<p>'))
				if len(obj) == 1: obj = obj[0]
				log.debug("field has html <p> formating, removing...")
		return obj

	def run(self):
		# sanitize the files
		for file_path in self.json_files:
			# checks for illegal BOM, see https://tools.ietf.org/html/rfc7159#section-8.1
			self.remove_bom(file_path)
		# now sanityze the content if the files
		for file_path in self.json_files:
			log.debug("sanitizing %s" % file_path)
			with codecs.open(file_path, 'r', encoding='utf-8') as _file:
				content = json.loads(_file.read(), object_pairs_hook=collections.OrderedDict)
			# Walk the json objects, and sanitize the strings
			log.info("Sanitizing %s" % file_path)
			content = self.sanitize(content, top_level=True)
			# Finally write back the json file
			with codecs.open(file_path, 'w', encoding='utf-8') as _file:
				json.dump(content, _file, sort_keys=False, indent=2, separators=(',', ': '), ensure_ascii=False)
		log.info("Done sanitizing %s json files." % len(self.json_files))



if __name__ == '__main__':
	logging.basicConfig(level=logging.WARNING-args.verbose*10)
	log.info(args)
	Sanitizer().run()
