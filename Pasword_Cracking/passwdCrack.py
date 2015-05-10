#!/usr/bin/python
#Linux password cracking with Dictionary file
#This tool uses as input two files a linux /etc/shadow file and a dictionary file with passwords.

import crypt
import sys 

def testPass(cryptPass):
	salt = cryptPass[0:12]
	#dictFile = open('dictionary2.txt','r', errors='ignore')

	for word in open('crackstation.txt','r'):
		#dictFile.readlines():
		word = word.strip('\n')
		cryptWord = crypt.crypt("%r"%word,salt)
		#print(cryptWord)

		sys.stdout.write("Now Testing:%s                              \r"%(word) )
		sys.stdout.flush()

		if cryptWord == cryptPass:
			print ('[+] Found Password: '+ word + '\n')
			return
	print ('[-] Password Not Found.')
	return

def main():
	passFile = open('passwords.txt')
	for line in passFile.readlines():
		if ':' in line:
			user = line.split(':')[0]
			cryptPass = line.split(':')[1].strip(' ')
			print ('[*] Cracking Password For: ' + user)
			testPass(cryptPass)
if __name__ == '__main__':
	main()
