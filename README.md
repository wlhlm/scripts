scripts
=======

Collection of various shell scripts.

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

- - -
All scripts are released under a MIT license. See `LICENSE` for more
details.
