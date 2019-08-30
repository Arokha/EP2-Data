#!/usr/bin/env python
# -*- coding: utf-8 -*-
import logging
import os
import json
import codecs
import collections
import re
import argparse

parser = argparse.ArgumentParser()
parser.add_argument("-v", "--verbose", help="increase output verbosity", action='count', default=0)
parser.add_argument("--no-html", help="remove html formating from strings", action='store_true', default=False)
args = parser.parse_args()

log = logging.getLogger('sanitizer' if __name__ == '__main__' else __name__)

def sanitize_strings(obj, parent=None, counter=[]):
	if isinstance(obj, collections.Mapping):
		for k,v in obj.iteritems(): obj[k] = sanitize_strings(v, k, counter)
	if isinstance(obj, collections.MutableSequence):
		for i, v in enumerate(obj): obj[i] = sanitize_strings(v, None, counter)
	if isinstance(obj, basestring) and parent:
		# https://github.com/Arokha/EP2-Data/issues/4
		if re.search(u'\u2013(\\d+)', obj): log.debug("Found wrong minus encoding")
		obj = re.sub(u'\u2013(\\d+)', u'-\\1', obj)
		# remove html formating from data. mutliple <p> will yield an json array of strings
		if args.no_html and '<p>' in obj:
			obj = obj.replace('</p>', '')
			obj = filter(bool, obj.split('<p>'))
			if len(obj) == 1: obj = obj[0]
			log.debug("%s field has html <p> formating, removing..." % parent)
			counter[0] += 1
	return obj

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

def sanitize():
	files = []
	# get the json files in the current directory and subdirs
	for root, dirs, _files in os.walk('.'):
		files.extend((os.path.join(root, f) for f in _files if f.endswith('.json')))
	# sanitize the files
	for file_path in files:
		log.debug("sanitizing %s" % file_path)
		# checks for illegal BOM, see https://tools.ietf.org/html/rfc7159#section-8.1
		remove_bom(file_path)
		# Bom have been dealt with, reopen the file as utf8
		with codecs.open(file_path, 'r', encoding='utf-8') as _file:
			content = json.loads(_file.read(), object_pairs_hook=collections.OrderedDict)
		# Walk the json objects, and sanitize the strings
		counter = [0]
		content = sanitize_strings(content, None, counter)
		if counter[0]: log.info('%s: performed %s html <p> removal' % (file_path, counter[0]))
		# Finally write back the json file
		with codecs.open(file_path, 'w', encoding='utf-8') as _file:
			json.dump(content, _file, sort_keys=False, indent=2, separators=(',', ': '), ensure_ascii=False)
	log.info("Done sanitizing %s json files." % len(files))

if __name__ == '__main__':
	logging.basicConfig(level=logging.WARNING-args.verbose*10)
	log.info(args)
	sanitize()
