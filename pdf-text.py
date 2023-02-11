# importing required modules
import PyPDF2
# enter name of input and output file
filename = input("enter name of input pdf file: ")
outputfilen = input("enter output file with extension: ")
# opening pdf file
pdfFileObj = open(filename, 'rb')
# creating a pdf reader object
pdfReader = PyPDF2.PdfFileReader(pdfFileObj)
# printing number of pages in pdf file
n = pdfReader.numPages
#print(n)

for i in range(n):
    page = pdfReader.getPage(i)
    text = page.extractText()
    file1 = open(outputfilen, 'a', errors = 'ignore')
    print(text)
    file1.writelines(text)
    file1.close()
pdfFileObj.close()
