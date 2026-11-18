#!/usr/bin/perl

###########################################
#   seWhosOnNow v1.2 by Allen C. Huffman  #
#           with enhancements by          #
#             Chris Overstreet            #
# Copyright (C) 2001 by Sub-Etha Software #
#                FREEWARE!                #
#            subetha@pobox.com            #
#        http://os9al.com/subetha         #
###########################################
#
# You may do whatever you want with this code, provided you put a comment in that
# says "Baseed on" (or similar) and my original copyright notice above.
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

#
# Specify how many SECONDS has to pass before a visitor is considered no longer
# on the site.  For instance, setting the value to 60 will show the count of
# how many times the page has been loaded within the past 60 seconds.
#
#$timespan = 60;	# 1 minute
#$timespan = 45;	# 45 seconds
#$timespan = 3600;	# 1 hour
#$timespan = 3600+1800; # 1 hour, 30 minutes
#$timespan = 7200;	# 2 hours
$timespan = 60*60*24;	# 24 hours

#
# If you want the display to show the timespan ("within the past X seconds/minutes")
# then set this value to 1.  If it is set to 0, the output will read "currently
# on the site".
#
$showtimespan = 1;

#
# Define the path and file name for the data file.
#
$whosonnow_file = "sewhosonnow.dat";

#
# Define the singular and plural tense for the output ("visitor/visitors",
# "elf/elves", "rennie/rennies", "page load/page loads", etc.)
#
$visitor_singular = "vistor";
$visitor_plural = "visitors";

#$visitor_singular = "elf";
#$visitor_plural = "elves";

#
# To prevent multiple instances of the script running at the same time from
# corrupting the data file, a lock method should be used. 0=no locking, 1=use
# flock() method (which only works for Unix servers).
#
$flock = 1;

#
# If you want to say something special for folks who keep reloading the page, you
# can set the following variable.
#
$welcomeback = "(Weren't you just here?)";

#
# If you want to count multiple loads during the $timespan as a new visit (such
# as a hit count), set this variable to 1.
#
$allow_recount = 0;

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

# check each entry of the log file.
foreach $line (@file)
{
	# split the line into ipaddress and timestamp.
	( $ipaddr, $timestamp ) = split(" ",$line);
	
	# weren't you just here?
	if ( $ipaddr eq $currentip ) {
		$helloagain = 1;
	}

	# is this an old entry or a repeate visitor within the timespan?
	unless ( ($timestamp < $currenttime-$timespan) || (!$allow_recount && ($ipaddr eq $currentip)) )
	{
		# this is within the specified period, so count it...
		$visitors++;
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

print "There ";

if ( $showtimespan ) {
	print "$havehas been";
} else {
		print "$isare";
}

print " $visitors $tense";

# and, if selected, the timespan.
if ( $showtimespan ) {
	print " online within the past ";
	$hours = int( $timespan/3600 );		# 1.2 hours(s)
	if ( $hours>0 ) {
		print "$hours hour";
		if ( $hours!=1 ) {
			print "s";
		}
	}
	$minutes = int( $timespan/60 )-($hours*60);
	if ( $minutes>0 ) {
		if ( $hours>0 ) {
			print " and ";
		}
		print "$minutes minute";
		if ( $minutes!=1 ) {
			print "s";
		}
	}
	if ( $timespan<60 ) {					# seconds
		print "$timespan seconds";
	}
	print "."
} else {
	print " currently online.";
}

# welcome back someone who won't leave the site...
if ($helloagain && $welcomeback) {
	print " $welcomeback";

}

# just to make output easier to read when testing offline.
print "\n";

exit(0);

