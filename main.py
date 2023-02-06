import bundle_dumper
import dump_parser
import json
import time

# enter rust path here
rust_root = 'C:\Program Files (x86)\Steam\steamapps\common\Rust'

start_time = time.time()

print("Dumping weapon recoil from the game.")

bdumper = bundle_dumper.BundleDumper(rust_root + r'\Bundles\shared\content.bundle')
bparser = dump_parser.DumpParser(bdumper.dump_assets())
dump = {
    'weapons': bparser.parse_weapons(),
    'attachments': bparser.parse_attachments()
    }

print("Found %s weapons, %s attachments." % (len(dump['weapons']), len(dump['attachments'])))

with open("dump.json", "w") as f_write: f_write.write(json.dumps(dump, indent=4))

print("Bundle has been dumped. Time taken: %s seconds." % round(time.time() - start_time, 2))
