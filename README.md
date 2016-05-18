scripts
=======

Collection of various shell scripts.

burncast
--------
Utility to burn audio files longer than 80 minutes on an AudioCD. There
is no magic involved with squeezing overlong files on a CD, the script
just cuts off after 79 minutes (configurable).

__Requirements:__ `ffmpeg`, `ffprobe` (ffmpeg), `wodim`
(cdrkit/cdrtools), `mktemp`

chkblayout
----------
Switch keyboard layout. For use in window managers/desktop environments.

__Requirements:__ `bash`, `awk/grep`, `setxkbmap`

chvol
-----
Change the volume of the pulseaudio defaukt sink. Optionally, it can
display a notification showing the volume as progress.

__Requirements:__ `egrep`, pulseaudio`, `ponymix`, `notify-send` (libnotify)

dict.cc.py
----------
Query the [dict.cc](http://www.dict.cc) online-dictionary. Adapted from
[raaapha/dict.cc.py](https://github.com/raaapha/dict.cc.py) and
reworked/extended.

The script's output is tab-delimited, meaning each line begins with the
searched phrase, then a tab character and then the translation. This
normally does not look very pleasing, so I recommend piping the output
to `column`:
```bash
$ ./dict.cc.py "spam" | column -t -s $'\t'
```

__Requirements:__ `python>=3.3`

dir.py
------
Generate an HTML directory listing. The listing can be embbeded into a template file. this file can contain three variables: `${LISTING}` is replaced by the listing table itself, `${PWD}` yields the path and `${TEXT}` stands for a text file. The funtionality is inspired by the index module of lighttpd.

__Requirements:__ `python>=3.2` (http.escape)

twwatch.py
----------
Script to browse [twitch.tv](http://www.twitch.tv/) more conveniently
using `dmenu`. The actual streams are then played via `livestreamer`.

__Requirements:__ `python3`, `dmenu`, `livestreamer`

- - -
All scripts are released under a MIT license. See `LICENSE` for more
details.
