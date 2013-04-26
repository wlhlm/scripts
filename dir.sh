#!/bin/sh
# Generate custom directory listings

usage() {
	echo "Usage: $0  [-mh] [-w WEBROOT] [-t TEMPLATE] [-f FILE] DIR"
	echo "	-a			Show hidden files"
	echo "	-m			Include mime-type"
	echo "	-h			Show file sizes  in human readable form"
	echo "	-w [FILE]	Specify webroot part of the directory path to strip from links"
	echo "	-t [FILE]	Specify template file"
	echo "	-f [FILE]	Specify txt file to be put in the footer"
}

# process arguments
ARGS="`getopt amhw:t:f: "$@"`"
[ "$?" -ne "0" ] && usage && exit 1
set -- $ARGS

[ "$#" -eq "0" ] && usage && exit 1
[ "$1" = "--" ] && usage && exit 1

while [ "$#" -gt 0 ]; do
	case "$1" in
		-a)	hidden=1;;
		-m)	mime=1;;
		-h)	human=1;;
		-w)	web_dir="$2"; shift;;
		-t)	template="$2"; shift;;
		-f)	text_file="$2"; shift;;
		--) shift; break;;
		-*)	usage; exit 1;;
	esac
	shift
done

# escape HTML characters < and &
escape_html_chars() {
	sed -e 's/\&/\&amp;/g' -e 's/</\&lt;/g' <<<"$1"
}

generate_dir_table() {
	# get specified directory
	PWD="`readlink -nf "$1"`"

	# get file listing
	ls_args="-gc --no-group --time-style=long-iso --group-directories-first"
	[ -n "$human" ] && ls_args="$ls_args --human-readable"
	[ -n "$hidden" ] && ls_args="$ls_args --all"
	files="`ls $ls_args "$PWD" | sed 1d`"

	echo "<div id=\"list\"><table id=\"table\">"
	echo -n "<tr class=\"table_header\"><th>Name</th><th>Last Modified</th><th>Size</th>"
	[ -n "$mime" ] && echo -n "<th>Type</th>"
	echo "</tr>"
	# generate listing table
	while read f; do
		file_name_link=
		#file_name="`awk '{ print $6 }' <<<"$f"`"
		file_name="`awk '{ for(i=6;i<NF;i++) printf("%s ", $i); print $i; }' <<<"$f"`"
		file_date="`awk '{ print $4 " " $5 }' <<<"$f"`"
		file_size="`awk '{ print $3 }' <<<"$f"`"
		file_type="`awk '{ print substr($1, 1, 1) }' <<<"$f"`"
		file_path="$PWD"
		grep -q "^\.$\|^index\." <<<"$file_name" && continue

		# strip webroot part
		[ -n "$web_dir" ] && file_path="`sed "s;$web_dir;;" <<<"$file_path"`"

		file_name_dir=""
		[ -z "$file_name_link" ] && file_name_link=`escape_html_chars "$file_name"`
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

		echo -n "<tr class=\"listing\"><td class=\"n\"><a href=\"`escape_html_chars "$file_path/$file_name"`\">$file_name_link</a>$file_name_dir</td>"
		echo -n "<td class=\"d\">$file_date</td>"
		echo -n "<td class=\"s\">$file_size</td>"
		[ -n "$mime" ] && echo -n "<td class=\"t\">`file --mime-type -b "$PWD/$file_name"`</td>"
		echo "</tr>"
	done <<<"$files"
	echo "</table></div>"
}

output_listing() {
	template="$1"
	web_dir="$2"
	[ -n "$3" ] && text_file="`cat "$3"`"
	listing="`generate_dir_table "$4" | sed -e 's/\&/\\\\\\\&/g'`"

	if [ -z "$template" ]; then
		echo "$listing"
	else
		# process template, it currently supports the following tokens:
		# {{PWD}}		The current working directory
		# {{LISTING}}	The Listing itself
		# {{TEXT}}		This token will be replaced by the text file
		# 				specified with -f
		cat "$template" | sed "s;{{PWD}};$path;g" | \
			awk '{ gsub(A, B); print; }' A="{{LISTING}}" B="$listing" | \
			awk '{ gsub(A, B); print; }' A="{{TEXT}}" B="<pre class=\"readme\">$text_file</pre>"
	fi
}

# Generate listing
output_listing "$template" "$web_dir" "$text_file" "$1"
