import sys
import os

common_path = os.path.dirname(__file__)
common_path = os.path.split(common_path)[0]
common_path = os.path.join(common_path, "Common")

sys.path.insert(0, common_path)

import util
