'''
This module implements a function for parsing tags in code comments:
#bii:implemented
#bii:entry_point
#bii:license

'''

import re

tags_finder = re.compile(r'bii:#(\w+)\s*\(\s*([^\)]*)\s*\)')  # regexp for finding biicode inline tags


def parse_tags(comments):
    """Parse all biicode tags from comments
    @param comments: list of comments found in files
    @return tags: dictionary containing types of tags and contents
    {
        "entry_point": "MAIN", "EXLUDE", or "DYNLIB",
        "dependencies": dependencies statement, as in dependencies.bii,
        "license": license string
    }
    """
    tags = {}
    for c in comments:
        match = tags_finder.findall(c)
        for m in match:
            tags.setdefault(m[0], []).append(m[1])
    return tags