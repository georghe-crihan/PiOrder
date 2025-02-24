#!/usr/bin/env python27

from os import makedirs, chmod, rename
from os.path import join as pjoin
from time import sleep
from paramiko import SSHClient
from scp import SCPClient, SCPException

def createSSHClient(server, port, user, password):
    client = SSHClient()
    client.load_system_host_keys()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    client.connect(server, port, user, password)
    return client

def anyFiles(d):
    from os import listdir
    return [ f for f in listdir(d) if (isfile(pjoin(d, f) and 'order' in f)) ]

def parseAndPrintJobAtBar(jobToPrint, dirOnSuccess, dirOnFailure):
    from xml.dom import minidom
    import barPrint
    import shutil
    import datetime


    xmlToProcess = open(jobToPrint)
    xmlToProcess = xmlToProcess.read()
    xmldoc = minidom.parseString(xmlToProcess)

    # Get footer text
    footerText=''
    with open("/home/pi/kpos/footer.txt", "r") as myfile:
        footerText=myfile.read()

    orderString = ''
    takeoutOrInhouse = xmldoc.getElementsByTagName('takeoutOrInhouse')[0].firstChild.nodeValue
    if takeoutOrInhouse == 'TAKEOUT':
        customer = xmldoc.getElementsByTagName('customer')[0].firstChild.nodeValue
        orderTime = xmldoc.getElementsByTagName('orderTime')[0].firstChild.nodeValue
        collectionTime = xmldoc.getElementsByTagName('collectionTime')[0].firstChild.nodeValue
        orderString += "Customer: "+ customer +"\n"
        orderString += "Time Ordered: "+ orderTime +"\n"
        orderString += "Collection Time: "+ collectionTime +"\n"
    else:
        tableNumber = xmldoc.getElementsByTagName('tableNumber')[0].firstChild.nodeValue
        numbOfCust = xmldoc.getElementsByTagName('numbOfCust')[0].firstChild.nodeValue	
        printTime = xmldoc.getElementsByTagName('printTime')[0].firstChild.nodeValue	
        orderString += "Table Number: " + tableNumber + "\n"
        orderString += "No. of Customers: " + numbOfCust + "\n"
        orderString += "Print Time: " + printTime + "\n"

    timestamp = xmldoc.getElementsByTagName('timestamp')[0].firstChild.nodeValue
    timestamp_date = datetime.datetime.fromtimestamp(int(timestamp[0:10])).strftime('%a %d %b %Y')
    orderString += "Date: " + timestamp_date + "\n"

    if len(xmldoc.getElementsByTagName('standingOrder'))==1:
        orderString += 'STANDING ORDER\n'
    orderNote = ''
    if len(xmldoc.getElementsByTagName('orderNote'))==1:
        orderNote = xmldoc.getElementsByTagName('orderNote')[0].firstChild.nodeValue
        orderString += 'Order Note:' + orderNote + '\n\n'

    itemlist = xmldoc.getElementsByTagName('item')
    prevCategory=''
    chutenyChargePrinted=False
    for s in itemlist:
        category = s.getElementsByTagName('category')[0].firstChild.nodeValue
        if category!=prevCategory:
            print prevCategory
            orderString += "\n" + category + "\n"
            prevCategory = category
        if takeoutOrInhouse == 'INHOUSE' and category=="Popadoms" and not chutenyChargePrinted:
            chutneysCharge = xmldoc.getElementsByTagName('chutneysCharge')[0].firstChild.nodeValue
            padding = 30 - len("Chutneys" + chutneysCharge)
            orderString += "Chutneys" + " "*padding + chutneysCharge+ "\n"
            chutenyChargePrinted = True
        qty = s.getElementsByTagName('qty')[0].firstChild.nodeValue
        foodDesc = s.getElementsByTagName('foodDesc')[0].firstChild.nodeValue
        subTotal = s.getElementsByTagName('subtotal')[0].firstChild.nodeValue
        textLength = len(qty + " " + foodDesc + " " + subTotal)
        if textLength > 30:
            orderString += qty + " " + foodDesc + "\n"
            padding = 30 - len(subTotal)
            orderString += " "*padding + subTotal + "\n"
        else:
            padding = 30 - len(qty + " " + foodDesc + " " + subTotal)
            orderString += qty + " " + foodDesc + " " + " "*padding + subTotal +"\n"

    totQty = xmldoc.getElementsByTagName('totalQty')[0].firstChild.nodeValue
    serviceCharge = xmldoc.getElementsByTagName('serviceCharge')[0].firstChild.nodeValue
    totalCost = xmldoc.getElementsByTagName('total')[0].firstChild.nodeValue

    padding = 30 - len("Total Qty: " + totQty)
    orderString += "\nTotal Qty: " + " "*padding + totQty + "\n"
    if takeoutOrInhouse == 'INHOUSE':
        padding = 30 - len("Service: " + serviceCharge)
        orderString += "Service: " + " "*padding + serviceCharge + "\n"
    padding = 30 - len("Total Cost: " + totalCost)
    orderString += "Total Cost: " + " "*padding + totalCost + "\n"
    orderString += "\n" + footerText

    # Output to the printer goes here

    # For Testing: Print the string to file
    if debug:
        with open('/tmp/toPrint.o','w') as tmpFile
            tmpFile.write(orderString)

        # For testing: Print the output to stdout
        print orderString

    # Print to the printer
    try:
        barPrint.printToPrinter(orderString)
        shutil.move(jobToPrint,dirOnSuccess)
    except:
        shutil.move(jobToPrint,dirOnFailure)
        raise

def main():
    while keepRunning:
        for fname in anyFiles(sendToKitchenDir):
            # Send to the kitchen
            # Needs finger print check via manually sudo scp-ing
            # i.e. sudo -s; scp -i /home/pi/kpos/id_rsa /tmp/test pi@kitchen-printer:/tmp/
            ssh = createSSHClient(server, port, user, password)
            with SCPClient(ssh.get_transport()) as scp:
                try:
                    scp.put(fname, remote_path='/tmp/kpos/printAtKitchen/')
                    rename(fname, pjoin(sendToKitchenSentDir, fname)
                except SCPException:
#            scp -i /home/pi/kpos/id_rsa -o ConnectTimeout=2 fname pi@kitchen-printer:/tmp/kpos/printAtKitchen/
                    # TODO: print at kitchen if not reachable
                    rename(fname, pjoin(sendToKitchenFailedDir, fname)

        for fname in anyFiles(printAtBarDir):
            # Print at the bar
            # One success, move to processed folder; otherwise failToProcessDir
            parseAndPrintJobAtBar(fname, printAtBarProcessedDir, printAtBarFailedDir)

        for fname in anyFiles(printAtBarForKitchenDir):
            # Print at the bar for kitchen, in event of failing to print at the ktichen
            parseAndPrintJobAtKitchen(fname, printAtBarForKitchenProcessedDir, printAtBarForKitchenFailedDir)

        for fname in anyFiles(printCustomerReceipt):
            # Print customer receipt, same as the job print but with VAT and logo
            parseAndPrintReceiptAtBar(fname, printCustomerReceiptProcessedDir, printCustomerReceiptFailedDir)

        # Retry sending a failed order
        for fname in anyFiles(sendToKitchenFailedDir):
            scp -i /home/pi/kpos/id_rsa -o ConnectTimeout=2 filename pi@kitchen-printer:/tmp/kpos/printAtKitchen/
            if [ $? -eq 0 ]:
                rename(fname, pjoin(sendToKitchenSentDir, fname))
            else:
                rename(filename, pjoin(sendToKitchenFailedDir, fname))

        sleep(1) 


kpos="/tmp/kpos"
printAtBarDir=pjoin(kpos, "printAtBar")
printAtBarProcessedDir=pjoin(printAtBarDir, "processed")
printAtBarFailedDir=pjoin(printAtBarDir, "failed")
sendToKitchenDir=pjoin(kpos, "sendToKitchen")
sendToKitchenSentDir=pjoin(sendToKitchenDir, "processed")
sendToKitchenFailedDir=pjoin(sendToKitchenDir, "failed")
printAtBarForKitchenDir=pjoin(kpos, "printAtBarForKitchen")
printAtBarForKitchenProcessedDir=pjoin(printAtBarForKitchenDir, "processed")
printAtBarForKitchenFailedDir=pjoin(printAtBarForKitchenDir, "failed")
printCustomerReceipt=pjoin(kpos, "printCustomerReceipt")
printCustomerReceiptProcessedDir=pjoin(printCustomerReceipt, "processed")
printCustomerReceiptFailedDir=pjoin(printCustomerReceipt, "failed")

# Create directories
for d in [ kpos printAtBarDir printAtBarProcessedDir printAtBarFailedDir \
           sendToKitchenDir sendToKitchenSentDir sendToKitchenFailedDir \
           printAtBarForKitchenDir printAtBarForKitchenProcessedDir printAtBarForKitchenFailedDir \
           printCustomerReceipt printCustomerReceiptProcessedDir printCustomerReceiptFailedDir ]:
    try:
        makedirs(d)
        chmod(d, 0o777)
    except:
        pass

keepRunning = True

main()
