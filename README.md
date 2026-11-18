# Perl

Bleep, bloop! This README was drafted by Allen's A.I. assistant
(Muse) from the scripts and their history. The scripts themselves
are Allen's.

Old Perl scripts by Allen C. Huffman (Sub-Etha Software). These are
CGI scripts from the early 2000s, mostly written for personal web
sites. They still run.

## sewhosonnow.cgi — "Who's On Now?"

A who's-online counter. It logs each visitor's IP address and
timestamp, then prints a line like:

> There are 42 visitors currently online.

or, with the timespan shown:

> There have been 42 visitors online within the past 24 hours.

### Versions

- **v1.0** — Initial version. `sewhosonnow_1.0.cgi`
- **v1.1** — Adds Chris Overstreet's enhancements: customizable
  visitor nouns, file locking, welcome-back message, and
  deduplication. `sewhosonnow_1.1.cgi`
- **v1.2** — Adds support for hours in the timespan ("3 hours and
  15 minutes", "24 hours"). `sewhosonnow_1.2.cgi`
- **v1.3** — The "on now" count is built in, and site settings
  move to a config file. `sewhosonnow_1.3.cgi`

`sewhosonnow.cgi` is the current version (v1.3). The versioned
files are kept alongside it so you can diff between versions.

### v1.3: the "on now" count and sewhosonnow.conf

v1.3 adds an optional short-window count. When set, the output
adds a parenthetical inside the main sentence:

> There have been 42 visitors online within the past 24 hours
> (and 3 of them are here right now...).

The short window is a setting, `$onnowspan` (in seconds). Set it
to 0 to omit the parenthetical entirely.

v1.3 also moves the site settings out of the script and into
`sewhosonnow.conf`, in the same directory. The script ships with
built-in generic defaults ("visitor"/"visitors", 24-hour window,
no welcome-back message); the `.conf` only needs to set what
differs. If the file is missing, the defaults are used. If it
exists but has an error, the script dies loudly so the problem
is not silently ignored.

An example `sewhosonnow.conf` is in this repo. Copy it next to
the script and edit the values for your site: the visitor nouns,
the timespan, whether the timespan is shown, the "on now"
window, the welcome-back message, and the data file name.

There is also a verbose mode, `$showtimespan = 2`, which spells
out both windows as clauses instead of using parentheses:

> There have been 42 visitors online in the past 24 hours,
> and 3 of them here in the past 15 minutes.

`$showtimespan` values: 0 = "currently online" (no timespan
shown), 1 = "within the past X", 2 = verbose both-windows.

### Earlier versions and the two-script setup

Before v1.3, the "on now" parenthetical only printed when
`$showtimespan` was on. Sites that wanted "currently online"
*and* a short-window count had to run a second script
(sewhosonnow15.cgi, with its own data file) just to print the
parenthetical. v1.3 makes that unnecessary: one script, one
data file, and the parenthetical prints regardless of
`$showtimespan`.

## seborderlines.cgi — "Borderlines"

A random-quote script. It picks a quote at random from a data
file and displays it, with navigation to see more. The concept
came from Shadow BBS (Terry Todd); the script is Allen's.

### Versions

- **v0.0** — The pre-rename original, `borderlines_v1.cgi`.
  Kept as `seborderlines_v0.0.cgi` so the v1-to-v1.0 change can
  be diffed. `borderlines_v1.cgi` is the same file, still in
  the repo under its original name.
- **v1.0** — The renamed "se" version. `seborderlines.cgi`
- **v1.1** — Adds a sysop delete mode, file locking, and a
  timestamped file format (backwards compatible).
  `seborderlines_1.1.cgi`

`seborderlines.cgi` is the current version (v1.1). See
`seborderlines_readme.txt` and `seborderlines_1.1_readme.txt`
for the original notes.

## Other scripts

- **seelvesonnow.cgi** — A who's-online counter for elves
  (a holiday variant of sewhosonnow). `seelvesonnow_1.1.cgi`
  is the v1.1 version.
- **seguessgame.cgi** — A number-guessing game. A simple CGI
  game written to practice Perl: configure a range (1–10,
  1–1000) and the user tries to guess the magic random number.
  `seguessgame_de.cgi` is a German-language version.
- **guessgame.cgi** — The pre-rename original of the guessing
  game (see `borderlines_v1.cgi` above for the naming pattern).
- **sepoints.cgi** — Points v1.0. A simple script for dieters:
  it calculates the "point value" of food items based on
  calories, fat, and fiber.

## Notes

- The descriptions above follow Allen's Perl Scripts page at
  https://subethasoftware.com/perl/ (updated 2/7/2004), which
  also links the circa-2001 edition of the site at
  https://subethasoftware.com/old.
- Line endings are Unix (LF) throughout, except
  `seguessgame_de.cgi`, which is Latin-1 encoded and still uses
  classic Mac (CR) line endings. Converting it to UTF-8 would
  break its use of § as a Perl quote delimiter, so it is left
  as-is.
- The `se` prefix (sewhosonnow, seborderlines, seelvesonnow,
  seguessgame) is Allen's naming convention for these scripts;
  the unprefixed files (`borderlines_v1.cgi`, `guessgame.cgi`)
  are the earlier drafts before the rename.
