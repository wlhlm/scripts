#!/bin/sh
# Change pulseaudio volume and optionally show notification
#
# Requirements:
#   pulseaudio
# 	ponymix
# 	notify-send (libnotify) (optional)

# Set shell options
set -ef

# Settings:
# notification timeout
timeout=500
# programm names
NOTIFY="notify-send"

# display help screen
usage() {
	echo "Usage: $0 [-h | --help] [-n] [-s FILE] VOLUME_SETTING"
	echo "  -n          Display notifiction"
	echo "  -s          Play a sound when changing volume"
	echo "  -h, --help  Show this message"
}

# initialize variables
notification=
sound_file=
vol_setting=
curr_volume=
setting_mode=

# parse commandline parameters
[ "$#" -eq "0" ] && usage && exit 1
while [ "$#" -gt "0" ]; do
	case "$1" in
		-n) notification=1;;
		-s) sound_file="$2"; shift;;
		-h|--help) usage; exit 0;;
        +*) vol_setting="${1#+}"
            setting_mode="plus";;
		-*) vol_setting="${1#-}"
            setting_mode="minus";;
        mute|unmute|toggle)
            setting_mode="$1";;
		 *) vol_setting="$1"
            setting_mode="absolute";;
	 esac
	 shift
 done

case "$setting_mode" in
    mute|unmute|toggle)
        ponymix "$setting_mode" 2>&1 >/dev/null;;
    plus)
        ponymix increase "$vol_setting" 2>&1 >/dev/null;;
    minus)
        ponymix decrease "$vol_setting" 2>&1 >/dev/null;;
    absolute)
        ponymix set-volume "$vol_setting" 2>&1 >/dev/null;;
esac

# get volume
curr_volume="$(ponymix get-volume)"

[ -n "$sound_file" ] && paplay "$sound_file"

if [ -n "$notification" ]; then
	# Send notification; check whether the device is muted or not.
	if ponymix is-muted; then
		$NOTIFY -t $timeout -u low -h "int:value:$curr_volume" "Pulseaudio" "Volume [MUTE]"
	else
		$NOTIFY -t $timeout -u low -h "int:value:$curr_volume" "Pulseaudio" "Volume"
	fi
fi
