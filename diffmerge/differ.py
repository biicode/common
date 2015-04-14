import difflib
from biicode.common.diffmerge.compare import Changes


def similarity(text1, text2):
    """ more coarse estimation of similarity, but fast, not as slow as a full
    diff
    """
    text1 = text1.splitlines()
    text2 = text2.splitlines()
    changed = 0.0
    for t1 in text1:
        if t1 not in text2:
            changed += 1.0

    for t2 in text2:
        if t2 not in text1:
            changed += 1.0

    return 1.0 - changed / (len(text1) + len(text2))


def text_unified_diff(base, other, baseName='base', otherName='other'):
    if not base:
        base = ""
    if not other:
        other = ""
    return '\n'.join(difflib.unified_diff(base.splitlines(), other.splitlines(),
                                          baseName, otherName))

    ''' ALTERNATIVE IMPLEMENATION: diff = diff_match_patch()
    margin = 10
    diff.Patch_Margin = margin

    diffs=diff.diff_lineMode(base, other, -1, False)
    #TODO: Find here a fixed number of sourunding lines, instead of characters
    left = diff.patch_make(base, diffs)

    return diff.patch_toText(left) #.replace("%0A",'')'''


def compute_diff(changes, diff_function):
    diff = Changes()
    diff.renames = changes.renames
    for name, item in changes.created.iteritems():
        if name not in changes.renames.values():
            diff.created[name] = diff_function(None, item)

    for name, item in changes.deleted.iteritems():
        if name not in changes.renames:
            diff.deleted[name] = diff_function(item, None)
        else:
            new_name = changes.renames[name]
            new_item = changes.created[new_name]
            diff.modified[name] = diff_function(item, new_item)

    for name, item in changes.modified.iteritems():
        mod = changes.modified[name]
        diff.modified[name] = diff_function(mod[0], mod[1])

    return diff
