#!/bin/sh
# Generate custom directory listings
# Requirements:
# 	coreutils: ls
# 	readlink
# 	sed
# 	awk
# 	file (for mime-type information)

# shell options
set -e

# various variables
text_file=
hidden=
path=
web_dir=
template=

usage() {
	echo "Usage: $0 [-amh] [-w WEBROOT] [-t TEMPLATE] [-f FILE] DIR"
	echo "	-a          Show hidden files"
	echo "	-m          Include mime-type"
	echo "	-h          Show file sizes  in human readable form"
	echo "	-w [FILE]   Specify webroot part of the directory path to strip from links"
	echo "	-t [FILE]   Specify template file"
	echo "	-f [FILE]   Specify txt file to be put in the footer"
}

# process arguments
ARGS="$(getopt amhw:t:f: "$@")"
[ "$?" -ne "0" ] && usage && exit 1
set -- $ARGS

[ "$#" -eq "0" ] && usage && exit 1

while [ "$#" -gt 0 ]; do
	case "$1" in
		-a)	hidden=1;;
		-m)	mime=1;;
		-h)	human=1;;
		-w)	web_dir="$2"; shift;;
		-t)	template="$2"; shift;;
		-f)	text_file="$2"; shift;;
		--)	shift; break;;
		-*)	usage; exit 1;;
	esac
	shift
done

# escape HTML characters < and &
escape_html_chars() {
	echo "$1" | sed -e 's/\&/\&amp;/g' -e 's/</\&lt;/g' -e 's/"/\&quot;/g'
}

generate_dir_table() {
	# get specified directory
	PWD="$(readlink -nf "$1")"

	# get file listing
	ls_args="-gc --no-group --time-style=long-iso --group-directories-first"
	[ -n "$human" ] && ls_args="$ls_args --human-readable"
	[ -n "$hidden" ] && ls_args="$ls_args --all"
	files="$(ls $ls_args "$PWD" | sed 1d)"

	echo "<div id=\"list\"><table id=\"table\">"
	printf "%s" "<tr class=\"table_header\"><th>Name</th><th>Last Modified</th><th>Size</th>"
	[ -n "$mime" ] && printf "%s" "<th>Type</th>"
	echo "</tr>"
	# generate listing table
	echo "$files" | while read -r f; do
		file_name_link=
		file_name="$(echo "$f" | awk '{ for(i=6;i<NF;i++) printf("%s ", $i); print $i; }')"
		file_date="$(echo "$f" | awk '{ print $4 " " $5 }')"
		file_size="$(echo "$f" | awk '{ print $3 }')"
		file_type="$(echo "$f" | awk '{ print substr($1, 1, 1) }')"
		file_path="$PWD"
		echo "$file_name" | grep -q '^\.$\|^index\.' && continue

		# strip webroot part
		[ -n "$web_dir" ] && file_path="$(echo "$file_path" | sed "s;$web_dir;;")"

		file_name_dir=""
		[ -z "$file_name_link" ] && file_name_link="$(escape_html_chars "$file_name")"
		if [ "$file_type" = "d" ]; then
			file_name_dir="/"
			file_size="-"
		else
			if [ "$file_type" = "l" ]; then
				file_name_link="<span class=\"link\">$file_name_link</span>"
				file_size="-"
			fi
		fi

		# special handling for parent directory
		[ "$file_name" = ".." ] && file_name="" && file_name_link="Parent Direcotry" && file_path=".."

		printf "%s" "<tr class=\"listing\"><td class=\"n\"><a href=\"$(escape_html_chars "$file_path/$file_name")\">$file_name_link</a>$file_name_dir</td>"
		printf "%s" "<td class=\"d\">$file_date</td>"
		printf "%s" "<td class=\"s\">$file_size</td>"
		[ -n "$mime" ] && printf "%s" "<td class=\"t\">$(file --mime-type -b "$PWD/$file_name")</td>"
		echo "</tr>"
	done
	echo "</table></div>"
}

output_listing() {
	template="$1"
	web_dir="$2"
	[ -n "$3" ] && text_file="$(cat "$3")"
	# escaping ampersand for awk
	listing="$(generate_dir_table "$4" | sed -e 's/\&/\\\\\\\&/g')"

	if [ -z "$template" ]; then
		printf "%s" "$listing"
	else
		# process template, it currently supports the following tokens:
		# {{PWD}}       The current working directory
		# {{LISTING}}   The Listing itself
		# {{TEXT}}      This token will be replaced by the content of a text file
		#               specified with -f
		<"$template" sed "s;{{PWD}};$PWD;g" | \
			awk '{ gsub(A, B); print; }' A="{{LISTING}}" B="$listing" | \
			awk '{ gsub(A, B); print; }' A="{{TEXT}}" B="<pre class=\"readme\">$text_file</pre>"
	fi
}

# Generate listing
output_listing "$template" "$web_dir" "$text_file" "$1"
