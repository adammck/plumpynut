#!/usr/bin/env python
# vim: noet

SUPPORT = "666"
SORRY = "Sorry, I did not understand your message. "

ENGLISH = {
	"unknown_alias":  "I don't know anyone called %s",
	"unknown":        "The %s %s does not exist",
	"suggest":        "No such %s as %s. Did you mean %s (%s)?",
	"error":          SORRY + "For help, please reply: HELP",
	
	"ident":          "Hello, %s",
	"ident_again":    "Hello again, %s",
	"ident_help":     SORRY + "Please tell me who you are by replying: I AM <USERNAME>",	
	"whoami":         "You are %s",
	"whoami_unknown": "I don't know who you are. Please tell me by replying: I AM <USERNAME>",
	"whoami_help":    SORRY + "To find out who you are identified as, please reply: WHO AM I",
	"whois":          "%s is %s",
	"whois_help":     SORRY + "Please tell me who you are searching for, by replying: WHO IS <USERNAME>",
	"alert_ok":       "Thank you. Your alert was received and sent to UNICEF",
	"alert_help":     SORRY + "Please tell me what you are alerting, by replying: ALERT <NOTICE>",
	"cancel_ok":      "Your last report has been deleted",	
	"cancel_none":    "You have not submitted any reports today. If you wish to change an older entry, please call " + SUPPORT,
	"cancel_help":    SORRY + "You may delete your last report by replying: CANCEL",
	"supplies_help":  SORRY + "To list all supply codes, please reply: SUPPLIES",
	"locations_help": SORRY + "To list all location codes, please reply: LOCATIONS",
	
	"help_main":   "Help options: IDENTIFY, REPORT or ALERT",
	"help_help":   SORRY + "Please reply: HELP IDENTIFY, HELP REPORT or HELP ALERT",
	"help_report": "To make a report, please reply: <SUPPLY-CODE> <LOCATION-CODE> <BENEFICIERIES> <QUANTITY> <CONSUMPTION> <BALANCE>"
}

