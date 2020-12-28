from typing import Dict, List

# Path component is a node in a tree.
# It's the equivalent of a short file/directory name in a file system.
# In our abstraction, it's represented as arbitrary bag of attributes
TestPathComponent = Dict[str, str]

# TestPath is a full path to a node in a tree from the root
# It's the equivalent of an absolute file name in a file system
TestPath = List[TestPathComponent]
