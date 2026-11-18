#!/usr/bin/perl

###########################################
#   seWhosOnNow v1.3 by Allen C. Huffman  #
#           with enhancements by          #
#             Chris Overstreet            #
# Copyright (C) 2001 by Sub-Etha Software #
#                FREEWARE!                #
#            subetha@pobox.com            #
#        http://os9al.com/subetha         #
###########################################
#
# You may do whatever you want with this code, provided you put a comment in that
# says "Based on" (or similar) and my original copyright notice above.
#
# Revision History:
#
# 2001/08/05 1.0 Initial (working) version.
#
# 2001/08/07 Christmas mods by Chris Overstreet (chris@lettersfromsanta.com)
#            to show number of "elves" online (http://www.lettersfromsanta.com)
#
# 2001/08/08 1.1 Updated to incorporate changes submitted by Chris Overstreet
#                (chris@lettersfromsanta.com) which allowed a better output
#                text.  He also modified the script to display "elf/elves"
#                instead of "visitor/visitors" for his Christmas site, so I
#                made that part customizable.  You can find a version of this
#                script in use on his site: (http://www.lettersfromsanta.com)
#                File locking is also now supported which will prevent a
#                potential problem if two instances of the script run at the
#                same time.  Also, a bug was fixed to make it properly round
#                minutes rather than printing out a bunch of decimal places.
#                Oops!
#
# 2004/02/07 1.2 Added support for hours, as in visitors within the last
#		"3 hours and 15 minutes" or "24 hours" or whatever.
#
# 2016/05/26 1.3 Adding concept of "on now" so it can say how many have been
#                on in the last X minutes/hours AND say how many are on
#                "right now" now (last 60 minutes, etc.).
#
# 2026/11/18 1.3 Renamed $nowspan to $onnowspan and made it truly optional:
#                when set, the output adds the "on now" count in parens
#                inside the main sentence, using one wording for both
#                cases: "(and X of them are here right now...)." That
#                phrasing reads fine whether the main sentence says
#                "currently online" or "within the past 24 hours", and
#                it never just repeats "online now". Added $showtimespan
#                = 2, a verbose "both windows" mode that spells out both
#                spans as clauses instead of using parens: "...in the past
#                24 hours, and X of them here in the past 15 minutes."
#                When $onnowspan is not set (0), the extra text is omitted.
#                Site config moved to sewhosonnow.conf (same directory) so
#                one script serves every site; the .conf holds the per-site
#                nouns, timespan, welcome-back message, and the optional
#                $onnowspan. If the .conf is missing, built-in defaults
#                are used. (Muse, 2026-11-18.)
#
# Site config. Defaults below; override them in sewhosonnow.conf (same
# directory as this script). The .conf only needs to set what differs
# from these defaults.
#
# Specify how many SECONDS has to pass before a visitor is considered no longer
# on the site.  For instance, setting the value to 60 will show the count of
# how many times the page has been loaded within the past 60 seconds.
#
our $timespan = 60*60*24;	# 24 hours
#$timespan = 60;	# 1 minute
#$timespan = 3600;	# 1 hour
#$timespan = 3600+1800; # 1 hour, 30 minutes
#$timespan = 7200;	# 2 hours

#
# If you want the display to show the timespan, set this value to 1.
# Set it to 2 for the verbose "both windows" mode, which spells out
# both spans ("...in the past 24 hours, and 3 of them here in the
# past 15 minutes."). Set it to 0 and the output reads "currently
# on the site" with no timespan shown.
#
our $showtimespan = 0;

#
# Optional: if you want to also add the "on now" count, specify how many
# SECONDS "right now" should be (e.g. 900 = 15 minutes, 1800 = 30 minutes,
# 3600 = 1 hour). Set it to 0 (or leave it out of the .conf) to omit it
# entirely. With $showtimespan on it reads "(and X are online now)" inside
# the sentence; with $showtimespan off it reads "(And X are online now.)"
# as its own sentence.
#
our $onnowspan = 0;

#
# Define the path and file name for the data file.
#
our $whosonnow_file = "sewhosonnow.dat";

#
# Define the singular and plural tense for the output ("visitor/visitors",
# "elf/elves", "rennie/rennies", "page load/page loads", etc.)
#
our $visitor_singular = "visitor";
our $visitor_plural = "visitors";

#
# To prevent multiple instances of the script running at the same time from
# corrupting the data file, a lock method should be used. 0=no locking, 1=use
# flock() method (which only works for Unix servers).
#
our $flock = 1;

#
# If you want to say something special for folks who keep reloading the page, you
# can set the following variable.
#
our $welcomeback = "";

#
# If you want to count multiple loads during the $timespan as a new visit (such
# as a hit count), set this variable to 1.
#
our $allow_recount = 0;

# Load site config (sewhosonnow.conf, same directory as this script). It sets
# $timespan, $showtimespan, $onnowspan, $whosonnow_file, $visitor_singular,
# $visitor_plural, $flock, $welcomeback and $allow_recount. If the file is
# missing, the defaults above are used. If it exists but has an error, die
# loudly rather than silently counting with the wrong nouns.
(my $conffile = $0) =~ s/\.cgi$/.conf/;
# do() needs a path with a directory in it ('.' is no longer in @INC).
$conffile = "./$conffile" unless $conffile =~ m{/};
if (-e $conffile) {
    do $conffile or die "sewhosonnow.conf: $@";
}

####################################################################################
#
# Begin processing... Nothing below this line needs to be modified.
#
print "Content-type: text/html\n\n";

# get the IP address of the current page visitor.
$currentip = $ENV{REMOTE_ADDR};

# if no IP, use a bogus one just for testing
if ( !$currentip ) {
	$currentip = "127.0.0.1";
}

# open (or create) the visitor log file.
unless ( open(FILE, "+<$whosonnow_file") ) {
	open( FILE,"+>$whosonnow_file") || die ("Unable to create file.\n" );
}

# lock file.
if ( $flock) {
	flock(FILE,2) || die("flock() error - unsupported on this server?");
}

# read the entire contents into an array.
@file = <FILE>;

# get the current system time (in seconds)
$currenttime = time;

# back up to start of file and erase it
seek(FILE,0,0);
truncate(FILE,0);

# scan through previous visitors until we find one that has
# visited within the specified amount of time
$visitors = 1;
$nowcount = 1; # 1.3

# check each entry of the log file.
foreach $line (@file)
{
	# split the line into ipaddress and timestamp.
	( $ipaddr, $timestamp ) = split(" ",$line);
	
	# weren't you just here?
	if ( $ipaddr eq $currentip ) {
		$helloagain = 1;
	}

	# is this an old entry or a repeat visitor within the timespan?
	unless ( ($timestamp < $currenttime-$timespan) || (!$allow_recount && ($ipaddr eq $currentip)) )
	{
		# this is within the specified period, so count it...
		$visitors++;

		# 1.3 if using an $onnowspan, count those too.
		# "on now" only counts unique IPs.
		if ( ($onnowspan) && (($timestamp > $currenttime-$onnowspan) && ($ipaddr ne $currentip)) ) {
			$nowcount++;
		}
		# then save it back to the file.
		print FILE "$ipaddr $timestamp\n";
	}
}

# write the current IP and timestamp to the end of the file.
print FILE "$currentip $currenttime\n";

# unlock file
if ( $flock ) {
	flock(FILE,8);
}

# done with file, so lets close it here.
close(FILE);

# change tense variables if number of visitors is greater than 1
if ( $visitors!=1 ) {
	$isare = "are";				# There are 2...
	$havehas = "have";			# There have been 2...
	$tense = $visitor_plural;	# 	... visitors ...
} else {
	$isare = "is";				# There is 1...
	$havehas = "has";			# There has been 1...
	$tense = $visitor_singular;	# 	... visitor ...
}

# 1.3: tense for the "on now" count as well.
if ( $nowcount!=1 ) {
	$onnow_isare = "are";
} else {
	$onnow_isare = "is";
}

# 1.3: format a span in seconds as "24 hours", "1 hour", "15 minutes",
# "1 hour and 30 minutes", "45 seconds", etc. Used for $timespan and
# for the verbose $showtimespan=2 second window.
sub format_span {
	my ($secs) = @_;
	my $out = "";
	my $h = int($secs/3600);
	if ($h > 0) {
		$out .= "$h hour";
		$out .= "s" if ($h != 1);
	}
	my $m = int($secs/60) - ($h*60);
	if ($m > 0) {
		$out .= " and " if ($h > 0);
		$out .= "$m minute";
		$out .= "s" if ($m != 1);
	}
	if ($secs < 60) {
		$out .= "$secs seconds";
	}
	return $out;
}

print "There ";

if ( $showtimespan ) {
	print "$havehas been";
} else {
		print "$isare";
}

print " $visitors $tense";

# 1.3: $showtimespan = 2 is the verbose "both windows" mode: spell out
# both spans as clauses, no parens. Only meaningful when $onnowspan is
# set; without it, it just reads as the plain timespan sentence.
if ( $showtimespan == 2 ) {
	print " online in the past " . format_span($timespan);
	if ( $onnowspan ) {
		print ", and $nowcount of them here in the past " . format_span($onnowspan);
	}
	print ".";
} else {
	# and, if selected, the timespan.
	if ( $showtimespan ) {
		print " online within the past " . format_span($timespan);
	} else {
		print " currently online";
	}

	# 1.3: the "on now" parenthetical, built once. Empty unless $onnowspan
	# is set. One wording for both cases: "here right now" reads fine
	# whether the main sentence says "currently online" or "within the
	# past 24 hours", and it never just repeats "online now".
	my $onnow = "";
	if ( $onnowspan ) {
		$onnow = " (and $nowcount of them $onnow_isare here right now...)";
	}
	print $onnow;

	# end the sentence.
	print ".";
}

# welcome back someone who won't leave the site...
if ($helloagain && $welcomeback) {
	print " $welcomeback";

}

# just to make output easier to read when testing offline.
print "\n";

exit(0);
