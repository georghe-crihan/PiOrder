from os import umask, mkdir, remove, chmod, replace as os_replace
from os.path import exists
from time import strftime
from re import sub as re_sub
from tempfile import NamedTemporaryFile
from xml.dom.minidom import parseString as SimpleXMLElement

spoolDir = '/tmp/kpos'
logFile = spoolDir + '/kpos_print.log' 
cntFile = spoolDir + '/kpos_counter.txt'

a = request.form.get('order')
order = a.join() # Convert to string
count = 0

# Implement a counter file, use the counter to track the file name
# FIXME: Somewhat atomic locking (via os.replace).
tempdir = None
tmpname = None
try:
    with NamedTemporaryFile(dir=tempdir, delete=False, mode="w", encoding="utf8") as tmpfile:
        with open(cntFile, 'r') as fp:
            count = int(fp.read())
        tmpname = tmpfile.name
        with open(tmpname, 'w') as fp:
            fp.write(count + 1)
        os_replace(tmpname, cntFile)
finally:
     try:
         remove(tmpname)
     except (TypeError, OSError):
         pass

# Logging
log_fp = open(logFile, 'a')

# Get the name of the customer and order time; to put into the filename too
orderXML = SimpleXMLElement(order)

orderRef = ''

# FIXME: port XML keys handling: .getElementsByTagName()->getAttribute().
# Get order type: takeout or inhouse
takeoutOrInhouse = orderXML.takeoutOrInhouse
if takeoutOrInhouse == 'TAKEOUT':
    orderRef = re_sub(r'/\s+/', '', orderXML.customer)
else:
    orderRef = 'Table' + orderXML.tableNumber + '_' + orderXML.numbOfCust + 'people'

# Four-digit year, month, day digits, underscore, 24-hour, two-digit min, sec.
orderTime = strftime('%Y%m%d_%H%M%S') 

# Create spoolDir folder
if not exists(spoolDir + '/'):
    old_umask = umask(0)
    mkdir(spoolDir + '/', 0o777)
    umask(old_umask)

# FIXME: port XML keys handling.
for printer in orderXML.printTerminal:
    printerPath = ''
    if printer == 'BAR':
        printerPath = 'printAtBar'
    if printer == 'KITCHEN':
        printerPath = 'sendToKitchen'
	
    outputFile=spoolDir + printerPath + '/order_' + count + '_' + takeoutOrInhouse + '_' + orderRef + '_' + orderTime
    with open(outputFile, 'a') as of:
        of.write(order)
        chmod(outputFile, 0o777)
        log_fp.write("\nOutput file created: %s", (outputFile,))

# Daemon service kpos will print and move the file

# Close the log file
log_fp.close()
