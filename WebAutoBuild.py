import glob
import re
import os
import hashlib
from selenium import webdriver
from selenium.webdriver.common.by import By
from os.path import dirname, isdir, isfile, join, basename
from time import sleep
from shutil import copyfile
from pathlib import Path
from css_html_js_minify import process_single_html_file, process_single_js_file, process_single_css_file

ROOT = dirname(__file__)
FILTERS_FILES = 'html|js|css|php'
FILTERS_MINIFY_FILES = 'js|css'
TIMEOUT_RELOAD = .5

print('''  Please start your local server and place this file in your site folder.
This script automatically checks if the html, php, css, js files have been modified and if found, then refreshes the page and compiles the files. ''')

URL = input("Your local website url: ");
driver = webdriver.Firefox()
driver.get(URL)


def get_suffix(path):
	return Path(path).suffix


def get_files_website(filters=FILTERS_FILES):
	catalog = []
	filters = filters.split('|')
	for file in glob.iglob(join(ROOT, '**', '*'), recursive=True):
		for ex in filters:
			s = re.search(r"\.(\w+)$", file)
			if s and s.group(1) == ex:
				catalog.append(file);
	return catalog


def md5sum(filename):
	md5 = hashlib.md5()
	with open(filename, 'rb') as f:
		for chunk in iter(lambda: f.read(128 * md5.block_size), b''):
			md5.update(chunk)
	return md5.hexdigest()


def get_signature():
	return [ (f, md5sum(f)) for f in get_files_website()]


def signature_compare(sign_1, sign_2):
	if len(sign_1) != len(sign_2):
		raise ValueError("Incorect scan filesystem")
	for k, v in enumerate(sign_1):
		if v[0] == sign_2[k][0]:
			if v[1] != sign_2[k][1]:
				return False
			continue
	return True


def minify_build(file, rt=ROOT):
	minf = join(ROOT, 'min')
	if not isdir(minf):
		os.mkdir(minf)
	if not(isfile(file)):
		return False
	s = get_suffix(file)
	if s == '.css':
		copyfile(file, join(minf, basename(file)))
		process_single_css_file(join(minf, basename(file), overwrite=True))



SIGNATURE =	get_signature()

while True:
	sign = get_signature()
	if not signature_compare(SIGNATURE, sign):
		driver.refresh()
		print("UPDATED!  ")
		SIGNATURE = get_signature()
		continue
	sleep(TIMEOUT_RELOAD)

	pass




