from os import listdir
from os.path import basename, isfile, join as pjoin

# Should be /var/spool
spoolDir='/tmp/kpos'

# FIXME: this would be called from the template.
@app.route('/ordersOnServer')
def ordersOnServer():
    processedOreders = []
    onlyfiles = [ f for f in listdir(spoolDir) if isfile(pjoin(spoolDir, f))]
    for filePath in onlyFiles:
        # Strip out the filename to the key
        key = basename(filePath)
        if 'printAtBar' in key and 'processed' in key and 'order' in key: 
            # Get the order content
            with open(filePath, 'r') ad fp:
                # Put into an array
                processedOrders[key]=fp.read()

