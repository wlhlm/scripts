#!/usr/bin/env python3
import urllib.request, urllib.error, urllib.parse
from re import findall
from sys import exit
from optparse import OptionParser

class Dict:
	# Query dict.cc for the translations.  'dictionary' switches to a specific
	# dictionary, for example en.  'query' is the search query.
	def getResponse(self, dictionary, query):
		# urlencode the search query.
		query = urllib.parse.quote(query)
		# Trick to avoid dict.cc from denying the request: change User-agent to
		# firefox's.
		request = urllib.request.Request("http://" + dictionary + ".dict.cc/?s=" + query, data=None, headers={"User-agent": "Mozilla/5.0"})
		f = urllib.request.urlopen(request)
		self.Response = f.read()

	# Parse the HTML-document we got from dict.cc. Search for 'var c1Arr' and
	# 'var c2Arr'.  Restrict the returned word lists to 'results'.
	def parseResponse(self, results):

		# Split lines
		lines = self.Response.decode("utf-8").split("\n")

		# Search for 'var c1Arr' and 'var c2Arr'.
		words1 = words2 = ""
		for l in lines:
			if l.find("var c1Arr") >= 0:
				words1 = l
			elif l.find("var c2Arr") >= 0:
				words2 = l

		# Stop when we cannot find anything -> it could be a server error.
		if not words1 or not words2:
			return False

		# Regex to extract the word list.
		# pattern = "\"[A-Za-z \.()\-\?ßäöüÄÖÜéáíçÇâêî\']*\""
		pattern = "\"[^,]+\""

		# Return list of matching strings.
		self.word_list = [findall(pattern, words1), findall(pattern, words2)]

		# Restrict the wordlists to a maximum of 'results'.
		if len(self.word_list[0]) > results:
			self.word_list[0] = self.word_list[0][:results]
			self.word_list[1] = self.word_list[1][:results]

		# Strip double quotes.
		for row in self.word_list:
			for i in range(0, len(row)):
				row[i] = row[i].strip("\"")

	# Print the search results. When 'quote' is set, wrap words in singlequotes
	# for better shell script handling.
	def printResults(self, quote=False):
		# Look for the biggest word in the first column to set the spacing
		# between the two columns.
		length = 0
		for w in self.word_list[0]:
			length = len(w) if len(w) > length else length

		# Print the results in two space-separated columns and quote if
		# neccessary.
		for i in range(0, len(self.word_list[0])):
			if quote:
				print("{0:{width}}  {1}".format("'" + self.word_list[0][i] + "'", "'" + self.word_list[1][i] + "'", width=(length+2)))
			else:
				print("{0:{width}}  {1}".format(self.word_list[0][i], self.word_list[1][i], width=length))

if __name__ == "__main__":
	# Parse commandline
	arg_parser = OptionParser(usage="Usage: %prog [options] [search]")
	arg_parser.add_option("-q", "--quote",
						  action="store_true", default=False,
						  help="quote results for better shell scripting")
	arg_parser.add_option("-r", "--results",
						  type="int", default=15, metavar="NUMBER",
						  help="only show NUMBER of results, default=15")
	arg_parser.add_option("-d", "--dictionary",
						  type="str", default="ende",
						  help="choose dictionary (for example 'enfr' for English/French dictionary), default=ende")
	(options, arguments) = arg_parser.parse_args()

	# Check whether a search query is missing.
	if len(arguments) < 1:
		arg_parser.error("missing search query")
	else:
		query = " ".join(arguments)

		myDict = Dict()
		# Retrieve translation from dict.cc.
		myDict.getResponse(dictionary=options.dictionary, query=query)
		# Parse the response, exit on failure.
		if myDict.parseResponse(options.results) == False:
			exit(1)

		# Print out a list of the results.
		myDict.printResults(quote=options.quote)
