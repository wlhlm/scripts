#!/bin/sh
# Generate custom directory listing

usage() {
	echo "Usage: $0  [-mh] [-w WEBROOT] [-t TEMPLATE] [-f FILE] DIR"
	echo "	-.	Show hidden files"
	echo "	-m	Include mime-type"
	echo "	-h	Show file sizes  in human readable form"
	echo "	-w	Specify webroot part of the directory path to strip from links"
	echo "	-t	Specify template file"
	echo "	-f	Specify txt file to be put in the footer"
}

# process arguments
ARGS=`getopt .mhw:t:f: "$@"`
[ "$?" -ne "0" ] && usage && exit 1
set -- $ARGS

[ "$#" -eq "0" ] && usage && exit 1
[ "$1" = "--" ] && usage && exit 1

while [ "$#" -gt 0 ]; do
	case "$1" in
		-.)	hidden=1;;
		-m)	mime=1;;
		-h)	human="h";;
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
	echo $1 | sed -e 's/\&/\&amp;/g' -e 's/</\&lt;/g'
}

generate_dir_table() {
	# get specified directory
	PWD="`readlink -nf $(echo $1 | tr -d "'")`"
	# get file listing
	files="`ls -gGca$human --time-style=long-iso "$PWD" | sed 1d`"

	echo "<div id=\"list\"><table id=\"table\">"
	echo -n "<tr class=\"table_header\"><th>Name</th><th>Last Modified</th><th>Size</th>"
	[ -n "$mime" ] && echo -n "<th>Type</th>"
	echo "</tr>"
	# generate file listing table
	echo "$files" | while read f; do
		file_name_link=
		file_name="`echo "$f" | awk '{ print $6 }'`"
		file_date="`echo "$f" | awk '{ print $4 " " $5 }'`"
		file_size="`echo "$f" | awk '{ print $3 }'`"
		file_type="`echo "$f" | awk '{ print substr($1, 1, 1) }'`"
		file_path="$PWD"
		echo "$file_name" | grep -q "^\.$\|^index\." && continue
		[ -z "$hidden" ] && echo "$file_name" | grep -q "^\.[^\.]*$" && continue

		# strip webroot path part
		if [ -n "$web_dir" ]; then
			web_dir="`echo $web_dir | tr -d "'"`"
			file_path="`echo "$PWD" | sed "s;$web_dir;;g"`"
		fi

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
	done
	echo "</table></div>"
}

output_listing() {
	template="$1"
	web_dir="`echo "$2" | tr -d "'"`"
	[ -n "$text_file" ] && text_file="`cat $(echo "$3" | tr -d "'")`"
	[ -z "$template" ] && template="dir.tmpl"
	path="`echo "$4" | tr -d "'" | sed "s;$web_dir;;g"`"
	listing="`generate_dir_table $4 | sed -e ':a;N;$!ba;s/\n/\\\\n/g' -e 's/[]"&\/()$*.^|[]/\\\\&/g'`"

	# process template
	echo "`cat "$template" | sed "s;{{PWD}};$path;g" | \
		sed ':a;N;$!ba;s/\n/\\\\n/g' | \
		sed "s/{{LISTING}}/$listing/g" | \
		sed "s/{{TEXT}}/<pre class=\"readme\">$text_file<\/pre>/g" | \
		sed 's/{{.*}}//g' | \
		sed 's/\\\\n/\n/g'`"
}

template="${template%\'}"
template="${template#\'}"
output_listing "$template" "$web_dir" "$text_file" "$1"
