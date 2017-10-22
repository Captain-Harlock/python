#!/usr/bin/env python

import PyPDF2
import os
import sys


if len(sys.argv) < 3:
    print "Usage python pdfgrep.py folder keyword"
    sys.exit(1)
    
path    = sys.argv[1]
keyword = sys.argv[2] 


#convert path to absolute path
path = os.path.abspath(path)


numOfPDFsFound=0
fileList = []
for filename in os.listdir(path):
    if filename.endswith(".pdf"):
        numOfPDFsFound += 1
        filename = os.path.join(path, filename)
        fileList.append(filename)

filecount=1
foundFilesList=[]
for filename in fileList:
        sys.stdout.flush()
        sys.stdout.write("\rChecking file:%s out of Total %s PDFs" %(filecount, numOfPDFsFound))
        sys.stdout.flush()
        pdfFileObj = open(filename,'rb')
        pdfReader = PyPDF2.PdfFileReader(pdfFileObj, strict=False)
        if pdfReader.isEncrypted:
           # print "The file is encrypted. Skipping"
            continue

        text =""
        count=0


        try:
            num_pages = pdfReader.numPages
            #The while loop will read each page
            while count < num_pages:
                pageObj = pdfReader.getPage(count)
                count +=1
                text += pageObj.extractText()
        except:
            continue

        #This if statement exists to check if the above library returned #words. 
        #It's done because PyPDF2 cannot read scanned files.
        if text != "":
            text = text
            if keyword.lower() in text.lower():
                foundFilesList.append(filename)
        filecount +=1


sys.stdout.write("\n")
print "Text \'%s\' found in the following files:" %keyword
for filename in foundFilesList:
    print filename
