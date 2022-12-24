#!/usr/bin/perl

###########################################
#   Boderlines v1.1 by Allen C. Huffman   #
# Copyright (C) 2001 by Sub-Etha Software #
#                FREEWARE!                #
#            subetha@pobox.com            #
#      http://disneyfans.com/subetha      #
###########################################
$version = "v1.1";
#
# You may do whatever you want with this code, provided you put a comment in that
# says "Baseed on" (or similar) and my original copyright notice above.
#
# Revision History:
#
# 2001/08/04 1.0 Initial (working) version.
# 2001/08/08 1.1 Added "delete" to SysOp menu, and also added file locking.
#                Also fixed a bug with the random output routine, but only those
#                who downloaded v1.0 on the first day would have encountered
#                it. The file format has also changed with the addition of a
#                timestamp to each borderline and some other fields for future
#                use. This version has backwards compatibility code in it.
#
# New 1.1 format:
#
# 	$ip|$timestamp|$rsvd1|$rsvd2|$message
#
# User messages are not allowed to contain the "|" character, or <HTML> tags.
#

#
# Max number of borderlines to store.
#
$max = 10;

#
# Where do we send the user when they are done?  This can also be passed in
# from a form using a hidden field with a name of "returnURL" and the
# value set to the page such as "value=http://yourdomain.com/yourpage.htm".
#
#$return_URL = "http://disneyfans.com/subetha/borderlines.shtml";

#
# Specify the path/name to where the borderline data file will be stored.
#
$datafile_path = "seborderlines.dat";

#
# Location/name of this script... Hopefully you won't have to change
# this, but if you do it should be something like "/cgi-bin/seborderlines.cgi"
# or wherever your script is and whatever it is called...
#
$this_script = "$ENV{'SCRIPT_NAME'}";

#
# To prevent multiple instances of the script running at the same time from
# corrupting the data file, a lock method should be used. 0=no locking, 1=use
# flock() method (which only works for Unix servers).
#
$flock = 1;

####################################################################################
#
# Begin processing... Nothing below this line needs to be modified.
#

# parse any items passed in by a form or as parameters or something
&ReadParse;

# see if we have a special mode to work with
$mode = $in{'mode'};

# If they pass one in from a form, we'll use it instead
$returnURL = $in{'returnURL'};
if ( $returnURL ) {
	$return_URL = $returnURL;
}

#
# If no parameters then just show a random borderline.
#
if (!$in)
{
	print "Content-Type: text/html\n\n";

	# open the data file
	unless ( open(FILE, $datafile_path) ) {
		print "There are no borderlines, yet.";
		exit(0);
	}

	# read borderlines into an array
	@borderlines = <FILE>;

	# get number of borderlines
	$entries = scalar(@borderlines);
	
	# print a random borderline
	$random = int(rand($entries));	# 1.1 removed +1 since arrays are base 0
	$line = @borderlines[$random];

	# get rid of IP address in front of borderline
	($ipaddr,$timestamp,$rsvd1,$rsvd2,$message) = split( /\|/, $line, 5);
	# backwards compatibility check for 1.0. if no rsvd1 field, must be old.
	if (!$rsvd2) {
		$message = $timestamp;
		$timestamp = "";			
	}
	
	# print the borderline
	print $message;

	# close the file
	close(FILE);

	# then we exit
	exit(0);
}

####################################################################################
# mode=sysop
#
# SysOp "view all" mode.  This generates a full HTML page.
# In the future this will have the ability to edit or delete entries.
#
if ($mode eq "sysop")
{
	&do_top;

	# 1==sysop mode	
	&do_showborderlines(1);
	
	&do_end;
	
	exit(0);
}

####################################################################################
# mode=view
# Thise mode is for showing the borderline listing inline.
#
if ($mode eq "view")
{
	print "Content-Type: text/html\n\n";
	
	&do_showborderlines;

	exit(0);
}

####################################################################################
# mode=add
# List borderlines and allow adding a new one. This generates a full HTML page.
#
if ($mode eq "add")
{
	&do_top;
	
	print "<p align=\"center\">Welcome to Sub-Etha Software's BORDERLINES $version</p>\n";

	&do_showborderlines;
	
	&do_form;
	
	$ip = $ENV{REMOTE_ADDR};
	print "<p align=\"center\"><b>NOTE:</b> Your IP address of $ip will be logged.</a>\n";

	&do_end;

	exit(0);
}

####################################################################################
# mode=delete
# id=ID	
#
if ($mode eq "delete" )
{
	$id = $in{'id'};
	
	if (!$id) {
		&do_top;
		print "<p>No ID tag was passed in.  Sorry.</p>\n";
		&do_end;
		exit(0);
	}
	# try to find and delete the specified borderline.
	
	# open data file for read/write
	if ( open(FILE, "+<$datafile_path") ) {

		# lock file.
		if ( $flock) {
			flock(FILE,2) || die("flock() error - unsupported on this server?");
		}

		@borderlines = <FILE>;

		# seek back to start of file
		seek (FILE,0,0);

		# erase the old junk in the file
		truncate(FILE,0);

	} else {
		# create a new empty file if we have to
		open( FILE,"+>$datafile_path") || die ("Unable to create file.\n" );

		# lock file.
		if ( $flock) {
			flock(FILE,2) || die("flock() error - unsupported on this server?");
		}
	}

	foreach $line ( @borderlines )
	{
		chomp( $line );
		($ipaddr,$timestamp,$rsvd1,$rsvd2,$message) = split( /\|/, $line, 5);
		
		# backwards compatibility check for 1.0. if no rsvd1 field, must be old.
		if (!$rsvd1) {
			$message = $timestamp;
			$timestamp = "";			
		}

		# write back all lines not containing the msg id.
		if ( $id ne $timestamp ) {
			print FILE "$line\n";
		}
	}
	
	# unlock file
	if ( $flock ) {
		flock(FILE,8);
	}

	close(FILE);

	print "Location: $this_script?mode=sysop\n\n";
	
	exit(0);
}

####################################################################################
# If we have a message passed in, place it in the borderline file.
#

# get the user's borderline message
$message = $in{'message'};

#
# see if we have something to put in the file...
#
if ($message) {
	# get rid of trailing carraige return
	chomp $message;
	
	# filter out HTML tags
	$message =~ s/<[^>]*>//g;

	# filter out the "|" character
	$message =~ s/\|/!/g;


	# open data file for read/write
	if ( open(FILE, "+<$datafile_path") ) {

		# lock file.
		if ( $flock) {
			flock(FILE,2) || die("flock() error - unsupported on this server?");
		}

		@borderlines = <FILE>;

		# seek back to start of file
		seek (FILE,0,0);

		# erase the old junk in the file
		truncate(FILE,0);

	} else {
		# create a new empty file if we have to
		open( FILE,"+>$datafile_path") || die ("Unable to create file.\n" );

		# lock file.
		if ( $flock) {
			flock(FILE,2) || die("flock() error - unsupported on this server?");
		}
	}

	# add IP and timestamp to message
	$ip = $ENV{REMOTE_ADDR};
	$timestamp=time;
	$temp = "$ip|$timestamp|rsvd1|rsvd2|$message";
	$message = $temp;

	# add new message to the top
	unshift (@borderlines, $message);
	
	# get rid of any excess messages (over our storage limit).
	while ( @borderlines>$max ) {
		pop @borderlines;
	}

	foreach $line ( @borderlines )
	{
		chomp( $line );
		print FILE "$line\n";
	}
	
	# unlock file
	if ( $flock ) {
		flock(FILE,8);
	}

	close(FILE);
}

####################################################################################
# If here, we don't know why were were called, so just redirect...
#

# send browser to return page, if one was specified.
if ($return_URL) {
	print "Location: $return_URL\n\n";
} else {
	&do_top;
	print "<p>Your borderline has been added.</p>\n";
	&do_end;	
}
	
exit(0);

####################################################################################
# subroutines...
#
sub do_showborderlines
{
	# get number of arguments passed in
	my $argc = @_;
	my $sysop = shift @_;

	unless ( open(FILE, $datafile_path) ) {
		print "<p>There are no borderlines yet.</p>\n";
		return;
	}

	# read borderlines into an array
	@borderlines = <FILE>;

	$entries = scalar(@borderlines);
	
	print "<p>There are $entries borderlines right now:</p>\n";

	$count=0;
	foreach $line ( @borderlines ) {
		$count++;

		# get rid of IP address in front of borderline
		($ipaddr,$timestamp,$rsvd1,$rsvd2,$message) = split( /\|/, $line, 5);

		# backwards compatibility check for 1.0. if no rsvd1 field, must be old.
		if (!$rsvd2) {
			$message = $timestamp;
			$timestamp = "";			
		}

		print "<div>$count. ";
		if ($sysop) {
			# backwards compatibility with 1.0
			if ($timestamp) {
				print "<a href=\"$this_script?mode=delete&id=$timestamp\">(delete)</a> ";
			}

			print "[$ipaddr] ";
		}
		print "$message</div>\n";
	}
	close(FILE);
}

sub do_top
{
	print "Content-Type: text/html\n\n";

	print "<html><head><title>Sub-Etha's BORDERLINES $version</title><head><body>\n";
}

sub do_end
{
	print "</body></html>\n";
}

sub do_form
{
print <<EOF;
<form action="$this_script" method="post">
<p align="center">Enter your own borderline:</p>
<div align="center">Message:
<input type="text" name="message" size="80" maxlength="80">
<input type="submit" name="mode" value="Submit">
<input type="submit" name="mode" value="Cancel"></div>
</form>
EOF
}

####################################################################################
###
### Adapted from cgi-lib.pl by S.E.Brenner@bioc.cam.ac.uk
### Copyright 1994 Steven E. Brenner
sub ReadParse {
local (*in) = @_ if @_;
local ($i, $key, $val);

### replaced his MethGet function
if ( $ENV{'REQUEST_METHOD'} eq "GET" ) {
	$in = $ENV{'QUERY_STRING'};
} elsif ($ENV{'REQUEST_METHOD'} eq "POST") {
	read(STDIN,$in,$ENV{'CONTENT_LENGTH'});
} else {
	# Added for command line debugging
	# Supply name/value form data as a command line argument
	# Format: name1=value1\&name2=value2\&...
	# (need to escape & for shell)
	# Find the first argument that's not a switch (-)
	$in = ( grep( !/^-/, @ARGV )) [0];
	$in =~ s/\\&/&/g;
}

@in = split(/&/,$in);

foreach $i (0 .. $#in) {
	# Convert plus's to spaces
	$in[$i] =~ s/\+/ /g;

	# Split into key and value.
	($key, $val) = split(/=/,$in[$i],2); # splits on the first =.

	# Convert %XX from hex numbers to alphanumeric
	$key =~ s/%(..)/pack("c",hex($1))/ge;
	$val =~ s/%(..)/pack("c",hex($1))/ge;

	# Associate key and value. \0 is the multiple separator
	$in{$key} .= "\0" if (defined($in{$key}));
	$in{$key} .= $val;
	}
	return length($in);
}
