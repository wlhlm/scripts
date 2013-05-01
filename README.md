scripts
=======

Collection of shell scripts I've written to control my computer

chkblayout
----------
Switch keyboard layout. For use in window managers/desktop environments.

dir.sh
------
Generate a custom directory listing. Most usable for web servers. I've written
it because I needed more features than the default listing of the i`nginx` http server
(I didn't wanted to compile-in an extra module). It is inspired by the dirlisting
module of `lighttpd`.

__Requirements:__ `coreutils: ls`, `awk`, `sed`

- - -
All scripts are released under a MIT license. See `LICENSE` for more details.
