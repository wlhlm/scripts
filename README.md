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
Change the volume of the ALSA Master device. It also can optionally
display a notification showing the volume as progress.

__Requirements:__ `egrep`, `amixer`, `notify-send` (libnotify)

dir.sh
------
Generate a custom directory listing. Most usable for web servers. I've
written it because I needed more features than the default listing of
the `nginx` http server (I didn't want to compile-in an extra module).
It is inspired by the dirlisting module of `lighttpd`.

__Requirements:__ `coreutils: ls`, `getopt`, `awk`, `sed`, `file` for
mime-type information, `readlink`

dict.cc.py
----------
Query the [dict.cc](http://www.dict.cc) online-dictionary. Adapted from
[raaapha/dict.cc.py](https://github.com/raaapha/dict.cc.py) and
reworked/extended.

The script's output is tab-delimited, meaning each line begins with
searched phrase, than a tab character and the the translation. This
normally does not look very pleasing, so I recommend piping the output
to `column`:
```bash
$ ./dict.cc.py "spam" | column -t -s $'\t'
```

__Requirements:__ `python>=3.3`

lock
----
Trivial script for changing the power state of the computer but enabling
a screenlocker beforehand.

__Requirements:__ `systemctl` (systemd), a screenlocker (for example
slock or i3lock)

- - -
All scripts are released under a MIT license. See `LICENSE` for more
details.
