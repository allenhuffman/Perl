#!/usr/bin/perl############################################   Boderlines v1.0 by Allen C. Huffman   ## Copyright (C) 2001 by Sub-Etha Software ##                FREEWARE!                ##            subetha@pobox.com            ##      http://disneyfans.com/subetha      ############################################## You may do whatever you want with this code, provided you put a comment in that# says "Baseed on" (or similar) and my original copyright notice above.## Revision History:## 2001/08/04 1.0 Initial (working) version.### Max number of borderlines to store.#$max = 10;## Where do we send the user when they are done?  This can also be passed in# from a form using a hidden field with a name of "returnURL" and the# value set to the page such as "value=http://yourdomain.com/yourpage.htm".#$return_URL = "http://yourdomain.com/yourpage.htm";## Specify the path/name to where the borderline data file will be stored.#$datafile_path = "seborderlines.dat";## Location/name of this script... Hopefully you won't have to change# this, but if you do it should be something like "/cgi-bin/seborderlines.cgi"# or wherever your script is and whatever it is called...#$this_script = "$ENV{'SCRIPT_NAME'}";###################################################################################### Begin processing... Nothing below this line needs to be modified.## parse any items passed in by a form or as parameters or something&ReadParse;# see if we have a special mode to work with$mode = $in{'mode'};# If they pass one in from a form, we'll use it instead$returnURL = $in{'returnURL'};if ( $returnURL ) {	$return_URL = $returnURL;}## If no parameters then just show a random borderline.#if (!$in){	print "Content-Type: text/html\n\n";	# open the data file	unless ( open(FILE, $datafile_path) ) {		print "There are no borderlines, yet.";		exit(0);	}	# read borderlines into an array	@borderlines = <FILE>;	# get number of borderlines	$entries = scalar(@borderlines);		# print a random borderline	$random = int(rand($entries));	# 1.1 removed +1 since arrays are base 0	$line = @borderlines[$random];	# get rid of IP address in front of borderline	($ipaddr, $message) = split( /\|/, $line, 2);		# print the borderline	print $message;	# close the file	close(FILE);	# then we exit	exit(0);}## mode=sysop## SysOp "view all" mode.  This generates a full HTML page.# In the future this will have the ability to edit or delete entries.#if ($mode eq "sysop"){	&do_top;	# 1==sysop mode		&do_showborderlines(1);		&do_end;		exit(0);}## mode=view# Thise mode is for showing the borderline listing inline.#if ($mode eq "view"){	print "Content-Type: text/html\n\n";		&do_showborderlines;	exit(0);}## mode=add# List borderlines and allow adding a new one. This generates a full HTML page.#if ($mode eq "add"){	&do_top;		print "<p align=\"center\">Welcome to Sub-Etha Software's BORDERLINES!</p>\n";	&do_showborderlines;		&do_form;		$ip = $ENV{REMOTE_ADDR};	print "<p align=\"center\"><b>NOTE:</b> Your IP address of $ip will be logged.</a>\n";	&do_end;	exit(0);}## If we have a message passed in, place it in the borderline file.## get the user's borderline message$message = $in{'message'};# the format will be something like this:## message=This+is+the+message...## get rid of invalid stuff from the messageif ($message) {	# get rid of trailing carraige return	chomp $message;		# filter out HTML tags	$message =~ s/<[^>]*>//g;}## (continued)# okay, NOW see if we have something to put in the file...#if ($message) {	# open data file for read/write	if ( open(FILE, "+<$datafile_path") ) {		@borderlines = <FILE>;		# seek back to start of file		seek (FILE,0,0);		# erase the old junk in the file		truncate(FILE,0);	} else {		# create a new empty file if we have to		open( FILE,"+>$datafile_path") || die ("Unable to create file.\n" );	}		# add IP to message	$ip = $ENV{REMOTE_ADDR};	$temp = "$ip|$message";	$message = $temp;	# add new message to the top	unshift (@borderlines, $message);		# get rid of any excess messages (over our storage limit).	while ( @borderlines>$max ) {		pop @borderlines;	}	foreach $line ( @borderlines )	{		chomp( $line );		print FILE "$line\n";	}	close(FILE);}## If here, we don't know why were were called, so just redirect...## send browser to return page.print "Location: $return_URL\n\n";	exit(0);##################################################################################### subroutines...#sub do_showborderlines{	# get number of arguments passed in	my $argc = @_;	my $sysop = shift @_;	unless ( open(FILE, $datafile_path) ) {		print "<p>There are no borderlines yet.</p>\n";		return;	}	# read borderlines into an array	@borderlines = <FILE>;	$entries = scalar(@borderlines);		print "<p>There are $entries borderlines right now:</p>\n";		$count=0;	foreach $line ( @borderlines ) {		$count++;		($ipaddr,$message) = split( /\|/, $line, 2);		print "<div>$count. ";		if ( $sysop ) {			print "[$ipaddr] ";		}		print "$message</div>\n";	}	close(FILE);}sub do_top{	print "Content-Type: text/html\n\n";	print "<html><head><title>Sub-Etha's BORDERLINES...</title><head><body>\n";}sub do_end{	print "</body></html>\n";}sub do_form{print <<EOF;<form action="$this_script" method="post"><p align="center">Enter your own borderline:</p><div align="center">Message:<input type="text" name="message" size="80" maxlength="80"><input type="submit" name="mode" value="Submit"><input type="submit" name="mode" value="Cancel"></div></form>EOF}########################################################################################## Adapted from cgi-lib.pl by S.E.Brenner@bioc.cam.ac.uk### Copyright 1994 Steven E. Brennersub ReadParse {local (*in) = @_ if @_;local ($i, $key, $val);### replaced his MethGet functionif ( $ENV{'REQUEST_METHOD'} eq "GET" ) {	$in = $ENV{'QUERY_STRING'};} elsif ($ENV{'REQUEST_METHOD'} eq "POST") {	read(STDIN,$in,$ENV{'CONTENT_LENGTH'});} else {	# Added for command line debugging	# Supply name/value form data as a command line argument	# Format: name1=value1\&name2=value2\&...	# (need to escape & for shell)	# Find the first argument that's not a switch (-)	$in = ( grep( !/^-/, @ARGV )) [0];	$in =~ s/\\&/&/g;}@in = split(/&/,$in);foreach $i (0 .. $#in) {	# Convert plus's to spaces	$in[$i] =~ s/\+/ /g;	# Split into key and value.	($key, $val) = split(/=/,$in[$i],2); # splits on the first =.	# Convert %XX from hex numbers to alphanumeric	$key =~ s/%(..)/pack("c",hex($1))/ge;	$val =~ s/%(..)/pack("c",hex($1))/ge;	# Associate key and value. \0 is the multiple separator	$in{$key} .= "\0" if (defined($in{$key}));	$in{$key} .= $val;	}	return length($in);}