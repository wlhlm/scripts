#!/usr/bin/env python3
import signal
import urllib.request, urllib.error, urllib.parse
from re import findall
from sys import exit
from argparse import ArgumentParser

class Dict:
	# Query dict.cc for the translations.  'dictionary' switches to a specific
	# dictionary, for example en.  'query' is the search query.
	def getResponse(self, dictionary, query):
		# urlencode the search query.
		query = urllib.parse.quote(query)
		# Trick to avoid dict.cc from denying the request: change User-agent to
		# firefox's.
		request = urllib.request.Request("http://" + dictionary + ".dict.cc/?s=" + query, data=None, headers={"User-agent": "Mozilla/5.0 (X11; Linux x86_64; rv:31.0) Gecko/20100101 Firefox/31.0"})
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
		pattern = r'"(?:[^"\\]|\\.)*"'

		# Return list of matching strings; remove first element since it's
		# empty.
		self.word_list = [findall(pattern, words1)[1:], findall(pattern, words2)[1:]]

		# Restrict the wordlists to a maximum of 'results'.
		if len(self.word_list[0]) > results:
			self.word_list[0] = self.word_list[0][:results]
			self.word_list[1] = self.word_list[1][:results]

		# Strip double quotes.
		for row in self.word_list:
			for i in range(0, len(row)):
				row[i] = row[i].strip("\"")

	# Print the search results (tab separated)
	def printResults(self):
		for i in range(0, len(self.word_list[0])):
			print("{0}\t{1}".format(self.word_list[0][i], self.word_list[1][i]))

def handleSIGINT(signal, frame):
    print("")
    exit(1)

if __name__ == "__main__":
	# Setup signal handler to avoid stacktrace
	signal.signal(signal.SIGINT, handleSIGINT)

	# Parse commandline
	arg_parser = ArgumentParser(usage="Usage: %(prog)s [options] SEARCH")
	arg_parser.add_argument("search", nargs="+", help="search term")
	arg_parser.add_argument("-r", "--results", type=int, default=15, metavar="NUMBER", help="only show NUMBER of results, default=15")
	arg_parser.add_argument("-d", "--dictionary", default="ende", metavar="DICT", help="choose dictionary (for example 'enfr' for English/French dictionary)")
	arguments = arg_parser.parse_args()

	query = " ".join(arguments.search)

	myDict = Dict()
	# Retrieve translation from dict.cc.
	myDict.getResponse(dictionary=arguments.dictionary, query=query)
	# Parse the response, exit on failure.
	if myDict.parseResponse(arguments.results) == False:
		exit(1)

	# Print out a list of the results.
	myDict.printResults()
