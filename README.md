scripts
=======

Collection of various shell scripts.

chkblayout
----------
Switch keyboard layout. For use in window managers/desktop environments.

__Requirements:__ `bash`, `awk/grep`, `setxkbmap`

dir.sh
------
Generate a custom directory listing. Most usable for web servers. I've written
it because I needed more features than the default listing of the `nginx` http
server (I didn't wanted to compile-in an extra module). It is inspired by the
dirlisting module of `lighttpd`.

__Requirements:__ `coreutils: ls`, `awk`, `sed`

dict.cc.py
----------
Query the [dict.cc](http://www.dict.cc) online-dictionary. Adapted from
[raaapha/dict.cc.py(https://github.com/raaapha/dict.cc.py) and
reworked/extended.

__Requirements:__ `python3.3`

- - -
All scripts are released under a MIT license. See `LICENSE` for more details.
