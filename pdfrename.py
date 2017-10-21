#!/usr/bin/env python

import PyPDF2
import os
import sys
import re

if len(sys.argv) < 2:
    print "Usage python pdfrename.py folder"
    sys.exit(1)
    
path    = sys.argv[1]
#convert path to absolute path
path = os.path.abspath(path)

#function to check if a string is ascii
def is_ascii(s):
        return all(ord(c) < 128 for c in s)



numOfPDFsFound=0
filenameList = []
fullPathFileList = []
for filename in os.listdir(path):
    if filename.endswith(".pdf"):
        numOfPDFsFound += 1        
        #append just the filename to the list without the fullpath
        filenameList.append(filename)

        #create a fullpath filename
        filename = os.path.join(path, filename)
        fullPathFileList.append(filename)
        

filecount=1
foundFilesList=[]
for filename, fullpathFilename in zip(filenameList, fullPathFileList):

        oldFilename = filename
        newfilename =''
        
        try:
            pdfReader = PyPDF2.PdfFileReader(fullpathFilename, strict=False)
            if pdfReader.isEncrypted:
                # print "The file is encrypted. Skipping"
                continue
            newFilename = pdfReader.documentInfo['/Title'] 
        except:
            continue
  

        #A number of tests will be performed in order to secure that we have 
        #a human readable and OS acceptable filename
        
        #if the newFilename is not ascii
        if not is_ascii(newFilename):
            continue
        if newFilename =='' or newFilename ==' ' or 'Microsoft Word' in newFilename:
            continue
        #if the filename is untitled skip
        if newFilename =='untitled' or newFilename =='untitled.pdf':
            continue
        #skip renaming the file if the target contains parenthesis
        if newFilename.find('(') !=-1 or newFilename.find(')') !=-1:
            continue
        #skip renaming the file if the new filename is similar with the old
        if newFilename in oldFilename:
            continue
        #if the newfilename doesn't have the .pdf extension add it
        if re.match('.*.pdf$',newFilename): 
            pass
        else:
            newFilename = newFilename +'.pdf'
        #if the new filename is larger than 35 chars don't change it
        if len(newFilename) > 35:
            continue

        print("Renaming file:%s to %s" %(oldFilename, newFilename))
        filecount +=1

        #create the absolute path + the filename of the newFilename for the renaming
        fullpathNewFilename = os.path.dirname(fullpathFilename) + '/' + newFilename

        try:
            os.rename(fullpathFilename, fullpathNewFilename)
        except:
            continue
