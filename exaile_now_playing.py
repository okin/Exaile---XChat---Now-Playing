#! /usr/bin/env python
# -*- coding: utf-8 -*-

import xchat, dbus, string

#XChat Plugin Information
__module_name__ = "Exaile 0.3 Now Playing"
__module_version__ = "0.2.1"
__module_description__ = "Show what song Exaile is playing."
hook = "exaile" #what is our hook? (the command used to call the script, i.e. /exaile)

exa = ""

#Show the user what was loaded
print __module_name__ + " version " + __module_version__ + " loaded"

def show_help():
	print __module_name__ + " v" + __module_version__ + " for XChat"
	print "You can use the following commands:"
	print "\2/" + hook + "\2 to show others what your Exaile is playing"
	print "\2/" + hook + " silent\2 to show only yourself what your Exaile is playing"
	print "Other Functions are:"
	print "\2/" + hook + " play\2 to toggle play/pause."
	print "\2/" + hook + " next\2 to jump to the next track."
	print "\2/" + hook + " prev\2 to jump to the previous track."
	print "\2/" + hook + " stop\2 to stop playing."
	print "\2/" + hook + " sac\2 to stop playing after the current track."
	print "\2/" + hook + " vol+\2 to increase the volume."
	print "\2/" + hook + " vol-\2 to decrease the volume."
	print "\2/" + hook + " version\2 to show plugin and player version."
	print "\2/" + hook + " help\2 to show this help."

def control_exaile(command):
	global exa_dbus
	command = string.lower(command)
	if command == "silent":
		print "Exaile: " + getTrackInfo()	
	elif command == "play":
		if exa_dbus.IsPlaying():
			exa_dbus.PlayPause()
		else:
			exa_dbus.Play() #Exaile is stopped, so start playing
	elif command == "stop":
		exa_dbus.Stop()
	elif command == "sac":
		exa_dbus.StopAfterCurrent()
		if exa_dbus.IsPlaying():
			print "Exaile will stop playing after this track." #let the User know the command was sent
	elif command == "next":
		exa_dbus.Next()
	elif command == "prev":
		exa_dbus.Prev()
	elif command == "vol-":
		exa_dbus.ChangeVolume(-5)
	elif command == "vol+":
		exa_dbus.ChangeVolume(+5)
	elif command == "version":
		print __module_name__ + " version " + __module_version__
		print "Plugin written by Niko Wenselowski (webmaster@nik0.de) with heavy inspiration from Sonics Now Playing Script for Exaile 0.2.x"
		print "Exaile Version: \2" + str(exa_dbus.GetVersion()) + "\2"
	elif command == "help":
		show_help()
	else:
		print "Unknow command!"
		print "Type \2/" + hook + " help\2 for some help."

def getTrackInfo():
	global exa_dbus
	if exa_dbus.IsPlaying():
		#basic information
		artist = exa_dbus.GetTrackAttr("artist")
		title = exa_dbus.GetTrackAttr("title")

		if not title and not artist: #no information about artist and title so we use the filename
			filename = exa_dbus.GetTrackAttr("__loc")
			filename = filename.rpartition("/")[2] #everything after the last / should be the filename
			filename.encode("utf-8") #make sure that its encoded with utf-8.
			output = filename;
		else:
			title = title.encode("utf-8")
			if not artist:				
				output = title
			else:
				artist = artist.encode("utf-8")
				output = artist + " - " + title

		length = exa_dbus.GetTrackAttr("__length") #length in seconds. must use __length because <SiDi> yeh, internal tags are named with __TAGNAME
		length = int(round(float(length)))
		length = str(length // 60) + ":" + str('%0*d' % (2, (length % 60)))

		progress = exa_dbus.CurrentProgress()
		output = output + " [" + length + " (" + str(progress) + "%)]" #not working until length is returned

		#more special information from here on
		album = exa_dbus.GetTrackAttr("album")
		if album:
			album = album.encode("utf-8")
			output = output + " from " + album
			#Information about disc, total number of discs could be added here		
		year = exa_dbus.GetTrackAttr("date")		
		if year:
			year.encode("utf-8")
			output = output + " ("+ year + ")"
	else:
		output = "Exaile is currently not playing!"
	return output

def show_song(call, word_eol, userdata):
	'''
	Main-method.
	Returns information about the song.
	If the hook gehts arguments it will pass the command to control_exaile
	'''
	global exa_dbus
	
	try:
		#Connect to DBus
		bus = dbus.SessionBus()
		dbus_object = bus.get_object("org.exaile.Exaile","/org/exaile/Exaile")
		exa_dbus = dbus.Interface(dbus_object,"org.exaile.Exaile")
	except:
		print "DBus can't connect to Exaile!"
		return xchat.EAT_ALL

	#Did we get more than just our hook?
	if len(call) > 1:
		control_exaile(call[1])
		return xchat.EAT_ALL

	if exa_dbus.IsPlaying():
		xchat.command ("me is listening to " + getTrackInfo())
	else:
		print getTrackInfo()
	return xchat.EAT_ALL

#Tell XChat the hooks
xchat.hook_command(hook, show_song, help=hook +" Tell which song are you currently playing in exaile, /"+ hook +" help for more infos") 	
