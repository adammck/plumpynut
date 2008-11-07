#!/usr/bin/env python
# vim: noet

SUPPORT = "UNICEF"
SORRY = "Sorry, I did not understand your message. "

ENGLISH = {
	"unknown_alias":  "I don't know anyone called %s",
	"unknown":        "The %s %s does not exist",
	"suggest":        "No such %s as %s. Did you mean %s (%s)?",
	"error":          SORRY + "For help, please reply: HELP",
	
	"ident":          "Hello, %s",
	"ident_again":    "Hello again, %s",
	"ident_help":     SORRY + "Please tell me who you are by replying: I AM YOUR-USERNAME",	
	
	"whoami":         "You are %s",
	"whoami_unknown": "I don't know who you are. Please tell me by replying: I AM YOUR-USERNAME",
	"whoami_help":    SORRY + "To find out who you are registered as, please reply: WHO AM I",
	
	"whois":          "%s is %s",
	"whois_help":     SORRY + "Please tell me who you are searching for, by replying: WHO IS USERNAME",

	"alert_ok":       "Thanks %s, Your alert was received and sent to UNICEF",
	"alert_help":     SORRY + "Please tell me what you are alerting, by replying: ALERT YOUR-NOTICE",
	
	"cancel_ok":      "Thanks %s, your %s report has been cancelled",	
	"cancel_code_ok": "Your last report for %s has been deleted",	
	"cancel_none":    "You have not submitted any reports today, %s. If you wish to change an older entry, please call " + SUPPORT,
	"cancel_help":    SORRY + "You may delete your last report by replying: CANCEL",
	
	"supplies_help":  SORRY + "To list all supply codes, please reply: SUPPLIES",
	
	"help_main":   "uniSMS Help: reply with HELP REGISTER for registration, HELP REPORT for entry formatting, or HELP ALERT for help with alerting",
	"help_help":   SORRY + "Please reply: HELP REGISTER, HELP REPORT or HELP ALERT",
	"help_report": "To make a report reply with: SUPPLY-CODE LOCATION-CODE BENEFICIERIES QUANTITY CONSUMPTION BALANCE. Separate data with spaces and reports with commas.",
	"help_reg":  "If your mobile number is not registered, please reply: I AM YOUR-USERNAME",
	"help_alert":  "To alert UNICEF, reply with ALERT followed by your notice",

	"conv_welc": "You're welcome, %s!",
	"conv_greet": "Greetings, friend!",
	"conv_swear": "Would you text that to your mother, %s?"
}

