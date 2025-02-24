from os.path import basename

processedOreders = []
# Should be /var/spool
directory='/tmp/kpos/'
# FIXME: Rewrite to dir handling.
output = shell_exec('find /tmp/kpos | grep printAtBar | grep processed | grep order')
output = output.split("\n")

for filePath in output:
    # Strip out the filename to the key
    key = basename(filePath)
    # Get the order content
    with open(filePath, 'r') ad file:
        # Put into an array
        processedOrders[key]=file.read()

