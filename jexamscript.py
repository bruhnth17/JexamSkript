#!/usr/bin/python
#
# JexamLogin/GradeCheck
#
import email
import time
import requests
import smtplib
import poplib
from lxml import html

######################################
#			   Data					 #
######################################

payload = {
	'j_username' : 'sXXXXXX', 	#Dein S-Nummer
	'j_password' : 'PSWD'		#Dein Passwort
	}
EMAIL_ME = 'deine@email.de'		#Deine Emailadresse
	
EMAIL_JX = 'jexam-news@outlook.com'
URL = 'https://jexam.inf.tu-dresden.de/de.jexam.web.v4.5/spring/welcome'
URL_LOGIN = 'https://jexam.inf.tu-dresden.de/de.jexam.web.v4.5/spring/j_acegi_security_check'
URL_LOGOUT = 'https://jexam.inf.tu-dresden.de/de.jexam.web.v4.5/spring/logout'
URL_EXAM = 'https://jexam.inf.tu-dresden.de/de.jexam.web.v4.5/spring/exams/results'

grades = []
exams = []

######################################
#			 Helper					 #
######################################

def updateLists(newGrades, newExams):
	global exams
	exams = newExams
	global grades
	grades = newGrades

def sendEmail(newExam, newGrade):
	message = ""
	for exam in newExam:
		message += "Neue Klausur: " + exam.strip() + '\n'
	for grade in newGrade: 
		message += "Neue Note: " + grade.strip() + '\n'	
	try:
		msg = email.message_from_string(message.encode('utf-8'))
		msg['From'] = EMAIL_JX
		msg['To'] = EMAIL_ME
		msg['Subject'] = "jExam Noten sind raus"

		s = smtplib.SMTP("smtp.live.com",587)
		s.ehlo() 		#Hostname to send for this command defaults to the fully qualified domain name of the local host.
		s.starttls() 	#Puts connection to SMTP server in TLS mode
		s.ehlo()		#No idea what this does
		s.login(EMAIL_JX, 'jexambot17')
		s.sendmail(EMAIL_ME, EMAIL_ME, msg.as_string())

		s.quit()
	except:
		print "sendMessage did not work"

def parseHTML(result):
	try:
		tree = html.fromstring(result)

		#lists with a lot of twin elements
		_EXAMS = tree.xpath('//*[@id="tab1"]/tbody/tr/td[position() = 3]/span[position() = 1]/text()')
		_GRADES = tree.xpath('//*[@id="tab1"]/tbody/tr/td[position() = 6]/span[position() = 1]/text()') 

		#new lists without twin elements
		newExams = set(_EXAMS)
		newGrades = set(_GRADES)
	
		#new list without \n or \t..
		newExams = map(lambda s: s.strip(), newExams)
		newGrades = map(lambda s: s.strip(), newGrades)

		#if something changed send me a message
		if(newExams != exams):
			differenceExam = set(newExams) - set(exams)
			differenceGrade = set(newGrades) - set(grades)
		
			sendEmail(differenceExam, differenceGrade)
			updateLists(newGrades, newExams)
	except:
		print "parseHTML did not work"


######################################
#			   Main					 #
######################################

while True:
	with requests.Session() as session:
		session.get(URL) 						#go on mainpage to get sessioncookie
		session.post(URL_LOGIN, data=payload)   #login
		result = session.post(URL_EXAM)			#go to results, get HTML-Page
		session.get(URL_LOGOUT)					#logout
	
		parseHTML(result.text)
	time.sleep(5*60)							#repeat every 5 minutes
	#print "here we go again"
