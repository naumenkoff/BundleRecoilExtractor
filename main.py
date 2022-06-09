from bundle_dumper import *
from dump_parser import *
import json

#
# Written by Kiwan#0617
#

# Log what we are doing
print("[>] Searching for required MonoScript entries.")

# Get time before dump began
start = time.time()

# Log that we need user input.
print("[>] Enter the root path of the Rust game directory below. ex: C:\Program Files (x86)\Steam\steamapps\common\Rust")

# Get the root path
path = input("[<] Input: ")

# Begin dumping the bundle.
bdumper = BundleDumper(r'%s\Bundles\shared\content.bundle' % (path))

# Check that MonoScript entries have been found.
if bdumper.monoscripts_found() == False:

    # Log the error and exit
    print("[!] Could not find required MonoScript entries.")

    # Quit
    exit()

# Log that we found MonoScripts successfully
print("[>] Successfully found required MonoScript entries. Time: %s seconds." % round(time.time() - start, 2))

# Find weapons, attachments, and combine them.
dump = bdumper.dump_assets()

# Create a parser object
bparser = DumpParser(dump)

# Get a list of weapons
weapons = bparser.parse_weapons()

# Get a list of attachments
attachments = bparser.parse_attachments()

# Construct the dump file.
parsed_dump = {
    "weapons"       : weapons,
    "attachments"   : attachments
}

# Log how many weapons and attachments were found.
print("[>] Found %s weapons and %s attachments. Time: %s seconds." % (len(parsed_dump['weapons']), len(parsed_dump['attachments']), round(time.time() - start, 2)))

# Open the file for writing
with open("dump.json", "w") as f_write:

    # Write to file
    f_write.write(json.dumps(parsed_dump, indent=4, sort_keys=True))

# Log that we wrote data to 'dump.json'
print("[>] Wrote dump to 'dump.json'.")