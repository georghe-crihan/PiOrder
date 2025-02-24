#!/usr/bin/env python27

def playSoundsForChefs():
   /usr/bin/omxplayer --no-osd /home/pi/kpos/Roland-R-8-Bell-Tree.wav > /dev/null
   /usr/bin/omxplayer --no-osd /home/pi/kpos/Crash-Cymbal-8.wav > /dev/null
   /usr/bin/omxplayer --no-osd /home/pi/kpos/Alesis-S4-Plus-BrassSect-C3.wav > /dev/null
   /usr/bin/omxplayer --no-osd /home/pi/kpos/Steel-Bell-C6.wav > /dev/null

def anyFiles(d):
    from os import listdir
    return [ f for f in listdir(d) if (isfile(pjoin(d, f) and 'order' in f)) ]

def parseAndPrintJobAtKitchen(jobToPrint, dirOnSuccess, dirOnFailure):
    from xml.dom import minidom
    from time import sleep 
    import kitchenPrint
    import shutil

    xmlToProcess = open(jobToPrint)
    xmlToProcess = xmlToProcess.read()
    xmldoc = minidom.parseString(xmlToProcess)

    orderString = '\n\n'
    takeoutOrInhouse = xmldoc.getElementsByTagName('takeoutOrInhouse')[0].firstChild.nodeValue
    if takeoutOrInhouse == 'TAKEOUT':
        customer = xmldoc.getElementsByTagName('customer')[0].firstChild.nodeValue
        orderTime = xmldoc.getElementsByTagName('orderTime')[0].firstChild.nodeValue
        collectionTime = xmldoc.getElementsByTagName('collectionTime')[0].firstChild.nodeValue
        orderString += "Customer: "+ customer +"\n"
        orderString += '    TAKEOUT\n'
else:
        tableNumber = xmldoc.getElementsByTagName('tableNumber')[0].firstChild.nodeValue
        numbOfCust = xmldoc.getElementsByTagName('numbOfCust')[0].firstChild.nodeValue
        printTime = xmldoc.getElementsByTagName('printTime')[0].firstChild.nodeValue
        inhouseReadyTime = xmldoc.getElementsByTagName('inhouseReadyTime')[0].firstChild.nodeValue
        orderString += "Table  "+ tableNumber +"\n"
        orderString += "Customers: "+ numbOfCust +"\n"
        orderString += "Ordered: "+ printTime +"\n"
        orderString += '****************\n'
        orderString += '    INHOUSE\n'
        orderString += '****************\n'

    if len(xmldoc.getElementsByTagName('standingOrder'))==1:
        orderString += '@STANDING ORDER@\n\n'
orderNote = ''
    if len(xmldoc.getElementsByTagName('orderNote'))==1:
        orderNote = xmldoc.getElementsByTagName('orderNote')[0].firstChild.nodeValue
        orderString += 'NOTE:' + orderNote + '\n'

    itemlist = xmldoc.getElementsByTagName('item')
#    orderString += "\n"
    prevCategory=''
    for s in itemlist:
        category = s.getElementsByTagName('category')[0].firstChild.nodeValue
        if takeoutOrInhouse == 'INHOUSE':
            if category=='Popadoms':
                continue
            if category=='Drinks':
                continue
        if category!='Starters' and prevCategory=='Starters':
            orderString += "----------------\n\n"
        # TODO: if only starters then there will be no line. Unlikely.
        if category!=prevCategory:
            orderString += "\n"
        prevCategory = category
        qty = s.getElementsByTagName('qty')[0].firstChild.nodeValue
        foodDesc= s.getElementsByTagName('outDescrip')[0].firstChild.nodeValue
        orderString += qty + " " + foodDesc.upper() + "\n"

    if debug:
        print strftime("%Y-%m-%d %H:%M:%S") + " Printing the following: \n" + orderString
        orderString += "\n\nCollection: " + collectionTime
    if takeoutOrInhouse == 'TAKEOUT':
        orderString += "\n     "+ collectionTime + "\n"
    else:
        orderString += "\n     "+ inhouseReadyTime + "\n"
        orderString += '\n'
        orderString += '****************\n'
        orderString += '    INHOUSE\n'
        orderString += '****************\n'

    # Printing to the printer goes here

    # For Testing: Print the string to file
    if debug:
        with open('/tmp/toPrint.o', 'w') as tmpFile
        tmpFile.write(orderString)

        # For testing: Print the output to stdout
        print orderString
        print "MAIN CHEF\n" + orderString + "\n"
        print "TANDOORI CHEF\n" + orderString + "\n"

    # Print to the printer
    try:
        orderString_main = "MAIN CHEF\n" + orderString + "\n"
        orderString_tandChef = "TANDOORI CHEF\n" + orderString + "\n"
        kitchenPrint.printToPrinter(orderString_main)
        sleep(5)
        kitchenPrint.printToPrinter(orderString_tandChef)
        sleep(5)
        shutil.move(jobToPrint, dirOnSuccess)
    except:
        shutil.move(jobToPrint, dirOnFailure)
        raise

def main():
    while True:
        for fname in anyFiles(printAtKitchenDir):
            # On success, move to processed directory, on error to failed
            parseAndPrintJobAtKitchen(fname, printAtKitchenProcessedDir, printAtKitchenFailedDir)
	playSoundsForChefs()

        # Retry failed printing of order at kitchen only
        for fname in anyFiles(printAtKitchenFailedDir):
            echo `date` >> pjoin(kpos, 'filesInError.txt')
            echo "File in error detected: fname" >> pjoin(kpos, 'filesInError.txt')
            # Print at the kitchen
            parseAndPrintJobAtKitchen(fname, printAtKitchenProcessedDir, printAtKitchenFailedDir)
        playSoundsForChefs()

    sleep(1) 


kpos='/tmp/kpos'
printAtKitchenDir=pjoin(kpos, "printAtKitchen")
printAtKitchenProcessedDir=pjoin(printAtKitchenDir, "processed")
printAtKitchenFailedDir=pjoin(printAtKitchenDir, "/failed")

# Create directories
for d in [ printAtKitchenDir printAtKitchenProcessedDir printAtKitchenFailedDir 
]:
    # Create dirs
    pass

main()
