#!/usr/bin/env python

import urllib.request, urllib.error, urllib.parse
from re import findall
from sys import exit
from optparse import OptionParser

class Dict:
	def getResponse(self, dictionary, query):
		query = urllib.parse.quote(query)
		# Trick to avoid dict.cc from denying the request: change User-agent to firefox's
		request = urllib.request.Request("http://" + dictionary + ".dict.cc/?s=" + query, data=None, headers={'User-agent': 'Mozilla/5.0'})
		f = urllib.request.urlopen(request)
		self.Response = f.read()

	# Find 'var c1Arr' and 'var c2Arr'
	def parseResponse(self, results):

		# Split lines
		lines = self.Response.decode("utf-8").split("\n")

		words1 = words2 = ""
		for l in lines:
			if l.find("var c1Arr") >= 0:
				words1 = l
			elif l.find("var c2Arr") >= 0:
				 words2 = l

		if not words1 or not words2:
			return False

		# Regex
		# pattern = "\"[A-Za-z \.()\-\?ßäöüÄÖÜéáíçÇâêî\']*\""
		pattern = "\"[^,]+\""

		# Return list of matching strings
		self.word_list = [findall(pattern, words1), findall(pattern, words2)]

		if len(self.word_list[0]) > results:
			self.word_list[0] = self.word_list[0][:results]
			self.word_list[1] = self.word_list[1][:results]

		# Strip double quotes
		for row in self.word_list:
			for i in range(0, len(row)):
				row[i] = row[i].strip("\"")

	def printResults(self, quote=False):
		if not self.word_list[0] or not self.word_list[1]:
			exit(1)

		# Find biggest word in first col
		length = 0
		for w in self.word_list[0]:
			length = len(w) if len(w) > length else length

		# Nice output
		for i in range(0, len(self.word_list[0])):
			if quote:
				print("{0:{width}}  {1}".format("'" + self.word_list[0][i] + "'", "'" + self.word_list[1][i] + "'", width=(length+2)))
			else:
				print("{0:{width}}  {1}".format(self.word_list[0][i], self.word_list[1][i], width=length))


if __name__ == "__main__":
	# Commandline parsing
	arg_parser = OptionParser(usage="Usage: %prog [options] [search]")
	arg_parser.add_option("-q", "--quote",
						  action="store_true", default=False,
						  help="quote results for better shell scripting")
	arg_parser.add_option("-r", "--results",
						  type="int", default=15, metavar="NUMBER",
						  help="only show NUMBER of results, default=15")
	arg_parser.add_option("-d", "--dictionary",
						  type="str", default="ende",
						  help="choose dictionary (e.g. 'enfr' for English/French dictionary), default=ende")
	(options, arguments) = arg_parser.parse_args()

	if len(arguments) < 1:
		arg_parser.error("missing search query")
	else:
		query = " ".join(arguments)

		myDict = Dict()
		myDict.getResponse(dictionary=options.dictionary, query=query)
		if myDict.parseResponse(options.results) == False:
			exit(1)
		myDict.printResults(quote=options.quote)
