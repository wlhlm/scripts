#!/bin/sh
# Generate custom directory listings.
# Requirements:
#	find
# 	getopt(1)
# 	readlink
# 	sed
# 	awk
# 	file (for mime-type information)

# Set shell options.
set -ef

# Initialize various variables
text_file=
hidden=
find_args=
template=

usage() {
	cat <<END
Usage: $0 [-amh] [-w WEBROOT] [-t TEMPLATE] [-f FILE] DIR
    -a          Show hidden files
    -m          Include mime-type
    -h          Show file sizes  in human readable form (default, in KByte
    -t [FILE]   Specify template file
    -f [FILE]   Specify txt file to be put in the footer (requires template file
                to be given, otherwise useless)
END
}

# Process arguments
ARGS="$(getopt af:hmt: "$@")"
[ "$?" -ne "0" ] && usage && exit 1
set -- $ARGS

[ "$#" -eq "1" ] && usage && exit 1

while [ "$#" -gt "0" ]; do
	case "$1" in
		-a)	hidden=1;;
		-m)	mime=1;;
		-h)	human=1;;
		-t)	template="$2"; shift;;
		-f)	text_file="$2"; shift;;
		--)	shift; break;;
		-*)	usage; exit 1;;
	esac
	shift
done

[ -z "$1" ] && usage && exit 1

# Escape HTML characters <, >, " and &.
escape_html_chars() {
	printf "%s" "$1" | sed -e 's/\&/\&amp;/g' -e 's/</\&lt;/g' -e 's/>/\&gt;/g' -e 's/"/\&quot;/g'
}

# Simple function to make file sizes human readable, since we can't rely on
# non-POSIX -h
human_readable() {
	if [ "$1" -lt 1024 ]; then
		printf "%d%s" "$1" "K"
	elif [ "$1" -ge 1024 -a "$1" -lt "$((1024**2))" ]; then
		printf "%d%s" "$(($1 / 1024))" "M"
	else
		printf "%d%s" "$(($1 / (1024**2)))" "G"
	fi
}

# Generate a HTML-table with the directory listing.
generate_dir_table() {
	cd "$(readlink -nf "$1")"

	# Get listing seperate for directories and files.
	[ -z "$hidden" ] && find_args="$find_args -a ( ! -name .* )"
	files="$(find . \( ! -name . -prune \) -type f $find_args)"
	dir="$(find . \( ! -name . -prune \) -type d $find_args)"

	# Print table header.
	printf "%s\n" "<div id=\"list\"><table id=\"table\">"
	printf "%s" "<tr class=\"table_header\"><th>Name</th><th>Size</th>"
	[ -n "$mime" ] && printf "%s" "<th>Type</th>"
	printf "%s\n" "</tr>"

	# Generate directory entries.
	printf "%s" "$dir" | while read -r d; do
		# Get directory properties.
		dir_name="${d##*/}"
		dir_path="${d%/*}"
		dir_name_link="$(escape_html_chars "$dir_name")"

		printf "%s" "<tr class=\"listing\"><td class=\"n\"><a href=\"$(escape_html_chars "$dir_path/$dir_name")\">$dir_name_link</a>/</td>"
		printf "%s" "<td class=\"s\">-</td>"
		[ -n "$mime" ] && printf "%s" "<td class=\"t\">Directory</td>"
		printf "%s\n" "</tr>"
	done

	# Generate directory entries.
	printf "%s" "$files" | while read -r f; do
		# Get file properties.
		file_name="${f##*/}"
		file_path="${f%/*}"
		file_size="$(du -sk "$f" | cut -f 1)"
		file_name_link="$(escape_html_chars "$file_name")"
		[ -n "$human" ] && file_size="$(human_readable "$file_size")"
		# Hide index.html since it's probably going to be the listing itself.
		printf "%s" "$file_name" | grep -q '^index\.' && continue

		printf "%s" "<tr class=\"listing\"><td class=\"n\"><a href=\"$(escape_html_chars "$file_path/$file_name")\">$file_name_link</a></td>"
		printf "%s" "<td class=\"s\">$file_size</td>"
		[ -n "$mime" ] && printf "%s" "<td class=\"t\">$(file --mime-type -b "$file_path/$file_name")</td>"
		printf "%s\n" "</tr>"
	done
	printf "%s\n" "</table></div>"
}

# Print the directory listing embedded into a template file.
output_listing() {
	listing="$(generate_dir_table "$1")"
	template="$2"
	text_file="$3"

	if [ -z "$template" ]; then
		cat <<END
$listing
END
	else
		# Escaping ampersand and slash for awk.
		[ -n "$text_file" ] && text_file="$(sed -e 's/\\/\\\\/g' -e 's/\&/\\\\\&/g' <"$text_file")"
		listing="$(sed -e 's/\\/\\\\/g' -e 's/\&/\\\\\&/g' <<END
$listing
END
)"

		# Process template, it currently supports the following tokens:
		# {{PWD}}       The current working directory
		# {{LISTING}}   The Listing itself
		# {{TEXT}}      This token will be replaced by the content of a text file
		#               specified with -f
		< "$template" sed "s;{{PWD}};$PWD;g" | \
			awk '{ gsub(A, B); print; }' A="{{LISTING}}" B="$listing" | \
			awk '{ gsub(A, B); print; }' A="{{TEXT}}" B="<pre class=\"readme\">$text_file</pre>"
	fi
}

# Generate listing
output_listing "$1" "$template" "$text_file"

