"""rob_vhost

Usage:
  rob_vhost create
  rob_vhost disable
  rob_vhost destroy
  rob_vhost -h | --help
  rob_vhost --version

Options:
  create        Build virtual hosting.
  disable       Delete virtual hosting (data preserved).
  destroy       Delete virtual hosting.
  -h --help     Show this screen.
  --version     Show version.
"""

from docopt import docopt
from rob_vhost_proc import Create
from rob_vhost_proc import Disable
from rob_vhost_proc import Destroy
#import rob_vhost_proc
import os.path
import sys
import json

version = '2.0.0.7'
conf_path = "/etc/rob_vhost/config.json"
local_conf_path = "/local/config.json"
local_base_path = os.getcwd()

if __name__ == "__main__":
    print(version)
    print(sys.version)
    local_conf_path = "{}{}".format(local_base_path, local_conf_path)
    print(local_conf_path)
    if os.path.exists(local_conf_path) == True:
        print("Local configuration")
        conf_path = local_conf_path
    elif os.path.exists(conf_path) == False:
        print("{} not found [ver {}]".format(conf_path, version))
        sys.exit(1)
    file_conf = open(conf_path)
    data_conf = json.load(file_conf)
    print(data_conf['apache_user_id'])
    arguments = docopt(__doc__, version=version)
    #print(arguments)
    if arguments['create']:
        obj = Create(data_conf, local_base_path)
        obj.run()
    elif arguments['disable']:
        obj = Disable(data_conf, local_base_path)
        obj.run()
    elif arguments['destroy']:
        obj = Destroy(data_conf, local_base_path)
        obj.run()
