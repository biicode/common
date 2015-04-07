from bisect import bisect
from biicode.common.utils.bii_logging import logger
import difflib
from biicode.common.exception import BiiException


def _lcs_unique(a, b):
    # set index[line in a] = position of line in a unless
    # a is a duplicate, in which case it's set to None
    index = {}
    for i in xrange(len(a)):
        line = a[i]
        if line in index:
            index[line] = None
        else:
            index[line] = i
    # make btoa[i] = position of line i in a, unless
    # that line doesn't occur exactly once in both,
    # in which case it's set to None
    btoa = [None] * len(b)
    index2 = {}
    for pos, line in enumerate(b):
        next_ = index.get(line)
        if next_ is not None:
            if line in index2:
                # unset the previous mapping, which we now know to
                # be invalid because the line isn't unique
                btoa[index2[line]] = None
                del index[line]
            else:
                index2[line] = pos
                btoa[pos] = next_
    # this is the Patience sorting algorithm
    # see http://en.wikipedia.org/wiki/Patience_sorting
    backpointers = [None] * len(b)
    stacks = []
    lasts = []
    k = 0
    for bpos, apos in enumerate(btoa):
        if apos is None:
            continue
        # as an optimization, check if the next line comes at the end,
        # because it usually does
        if stacks and stacks[-1] < apos:
            k = len(stacks)
        # as an optimization, check if the next line comes right after
        # the previous line, because usually it does
        elif stacks and stacks[k] < apos and (k == len(stacks) - 1 or stacks[k + 1] > apos):
            k += 1
        else:
            k = bisect(stacks, apos)
        if k > 0:
            backpointers[bpos] = lasts[k - 1]
        if k < len(stacks):
            stacks[k] = apos
            lasts[k] = bpos
        else:
            stacks.append(apos)
            lasts.append(bpos)
    if len(lasts) == 0:
        return []
    result = []
    k = lasts[-1]
    while k is not None:
        result.append((btoa[k], k))
        k = backpointers[k]
    result.reverse()
    return result


def _match_find(a, b, alo, blo, ahi, bhi, answer, maxrecursion):
    if maxrecursion < 0:
        logger.error('Internal merge error')
        # this will never happen normally, this check is to prevent DOS attacks
        return
    oldlength = len(answer)
    if alo == ahi or blo == bhi:
        return
    last_a_pos = alo - 1
    last_b_pos = blo - 1
    for apos, bpos in _lcs_unique(a[alo:ahi], b[blo:bhi]):
        # recurse between lines which are unique in each file and match
        apos += alo
        bpos += blo
        # Most of the time, you will have a sequence of similar entries
        if last_a_pos + 1 != apos or last_b_pos + 1 != bpos:
            _match_find(a, b, last_a_pos + 1, last_b_pos + 1, apos, bpos, answer, maxrecursion - 1)
        last_a_pos = apos
        last_b_pos = bpos
        answer.append((apos, bpos))
    if len(answer) > oldlength:
        # find matches between the last match and the end
        _match_find(a, b, last_a_pos + 1, last_b_pos + 1, ahi, bhi, answer, maxrecursion - 1)
    elif a[alo] == b[blo]:
        # find matching lines at the very beginning
        while alo < ahi and blo < bhi and a[alo] == b[blo]:
            answer.append((alo, blo))
            alo += 1
            blo += 1
        _match_find(a, b, alo, blo, ahi, bhi, answer, maxrecursion - 1)
    elif a[ahi - 1] == b[bhi - 1]:
        # find matching lines at the very end
        nahi = ahi - 1
        nbhi = bhi - 1
        while nahi > alo and nbhi > blo and a[nahi - 1] == b[nbhi - 1]:
            nahi -= 1
            nbhi -= 1
        _match_find(a, b, last_a_pos + 1, last_b_pos + 1, nahi, nbhi, answer, maxrecursion - 1)
        for i in xrange(ahi - nahi):
            answer.append((nahi + i, nbhi + i))


def _collapse_sequences(matches):
    answer = []
    start_a = start_b = None
    length = 0
    for i_a, i_b in matches:
        if start_a is not None and (i_a == start_a + length) and (i_b == start_b + length):
            length += 1
        else:
            if start_a is not None:
                answer.append((start_a, start_b, length))
            start_a = i_a
            start_b = i_b
            length = 1

    if length != 0:
        answer.append((start_a, start_b, length))

    return answer


def _compute_matchs(a, b):
    matches = []
    _match_find(a, b, 0, 0, len(a), len(b), matches, 10)
    # Matches now has individual line pairs of
    # line A matches line B, at the given offsets
    matching_blocks = _collapse_sequences(matches)
    matching_blocks.append((len(a), len(b), 0))

    return matching_blocks


def _range_intersection(ra, rb):
    sa = max(ra[0], rb[0])
    sb = min(ra[1], rb[1])
    if sa < sb:
        return sa, sb


def _range_compare(a, astart, aend, b, bstart, bend):
    if (aend - astart) != (bend - bstart):
        return False
    for ia, ib in zip(xrange(astart, aend), xrange(bstart, bend)):
        if a[ia] != b[ib]:
            return False
    else:
        return True


def remove_diff_lines(diff):
    return [line for line in diff if not line.startswith('?')]


def build_common_ancestor(source_lines, target_lines):
    '''source is the origin of data
    target is the place where the merge is being done, thus it is the most
    important version and should take precedence in case of doubt'''
    diff = difflib.Differ()
    ds = diff.compare(source_lines, target_lines)
    c = remove_diff_lines(ds)
    common = []
    for d in c:
        if d[0] not in '-+':
            common.append(d[2:])
    return common


def three_way_merge_text(common, base, other, basename='base', othername='other'):
    base = base.splitlines(1)
    other = other.splitlines(1)
    if not common:
        common = build_common_ancestor(base, other)
    else:
        common = common.splitlines(1)

    merger = TextMerger(None, basename, othername)
    result = merger.merge(common, base, other)

    return "".join(result), merger.collision


class TextMerger(object):

    START_MARKER = '<<<<<<<<<<<<<<<<<<<<<<<<<'
    MID_MARKER = '\n========================='
    END_MARKER = '\n>>>>>>>>>>>>>>>>>>>>>>>>>'

    def __init__(self, name_common=None, name_base=None, name_other=None):

        self.name_common = name_common
        self.name_base = name_base
        self.name_other = name_other

        self.collision = False

        self.start_marker = TextMerger.START_MARKER
        self.end_marker = TextMerger.END_MARKER
        self.mid_marker = TextMerger.MID_MARKER
        self.common_marker = None

        if self.name_base:
            self.start_marker += ' ' + str(self.name_base)
        if self.name_other:
            self.end_marker += ' ' + str(self.name_other)

    def merge(self, common, base, other):
        '''base, a, b are iterables of lines'''
        newline = '\n'
        if len(common) > 0:
            if common[0].endswith('\r\n'):
                newline = '\r\n'
            elif common[0].endswith('\r'):
                newline = '\r'
        #if base_marker and reprocess:
        #    raise BiiException('Merge error')

        mergeregions = _merge_regions(common, base, other)
        for t in mergeregions:
            what = t[0]
            if what == 'eq':
                for i in range(t[1], t[2]):
                    yield common[i]
            elif what == 'base' or what == 'same':
                for i in range(t[1], t[2]):
                    yield base[i]
            elif what == 'other':
                for i in range(t[1], t[2]):
                    yield other[i]
            elif what == 'collide':
                self.collision = True
                yield self.start_marker + newline
                for i in range(t[3], t[4]):
                    yield base[i]
                if self.common_marker is not None:
                    yield self.common_marker + newline
                    for i in range(t[1], t[2]):
                        yield common[i]
                yield self.mid_marker + newline
                for i in range(t[5], t[6]):
                    yield other[i]
                yield self.end_marker + newline
            else:
                raise BiiException('Internal merge error')


def _merge_regions(base, a, b):
    # section a[0:ia] has been disposed of, etc
    iz = ia = ib = 0

    for zmatch, zend, amatch, aend, bmatch, bend in _find_regions(base, a, b):
        matchlen = zend - zmatch
        # invariants:
        #   matchlen >= 0
        #   matchlen == (aend - amatch)
        #   matchlen == (bend - bmatch)
        len_a = amatch - ia
        len_b = bmatch - ib
        len_base = zmatch - iz
        # invariants:
        # assert len_a >= 0
        # assert len_b >= 0
        # assert len_base >= 0

        # print 'unmatched a=%d, b=%d' % (len_a, len_b)

        if len_a or len_b:
            # try to avoid actually slicing the lists
            same = _range_compare(a, ia, amatch, b, ib, bmatch)

            if same:
                yield 'same', ia, amatch
            else:
                equal_a = _range_compare(a, ia, amatch, base, iz, zmatch)
                equal_b = _range_compare(b, ib, bmatch, base, iz, zmatch)
                if equal_a and not equal_b:
                    yield 'other', ib, bmatch
                elif equal_b and not equal_a:
                    yield 'base', ia, amatch
                elif not equal_a and not equal_b:
                    yield 'collide', iz, zmatch, ia, amatch, ib, bmatch
                else:
                    raise BiiException('Internal merge error')

            ia = amatch
            ib = bmatch
        iz = zmatch

        # if the same part of the base was deleted on both sides
        # that's OK, we can just skip it.

        if matchlen > 0:
            # invariants:
            # assert ia == amatch
            # assert ib == bmatch
            # assert iz == zmatch

            yield 'eq', zmatch, zend
            iz = zend
            ia = aend
            ib = bend


def _find_regions(base, a, b):
    ia = ib = 0
    amatches = _compute_matchs(base, a)
    bmatches = _compute_matchs(base, b)
    len_a = len(amatches)
    len_b = len(bmatches)

    sl = []

    while ia < len_a and ib < len_b:
        abase, amatch, alen = amatches[ia]
        bbase, bmatch, blen = bmatches[ib]

        # there is an unconflicted block at i; how long does it
        # extend?  until whichever one ends earlier.
        i = _range_intersection((abase, abase + alen), (bbase, bbase + blen))
        if i:
            intbase = i[0]
            intend = i[1]
            intlen = intend - intbase

            # found a match of base[i[0], i[1]]; this may be less than
            # the region that matches in either one
            # assert intlen <= alen
            # assert intlen <= blen
            # assert abase <= intbase
            # assert bbase <= intbase

            asub = amatch + (intbase - abase)
            bsub = bmatch + (intbase - bbase)
            aend = asub + intlen
            bend = bsub + intlen

            # assert base[intbase:intend] == a[asub:aend], \
            #       (base[intbase:intend], a[asub:aend])
            # assert base[intbase:intend] == b[bsub:bend]

            sl.append((intbase, intend,
                       asub, aend,
                       bsub, bend))
        # advance whichever one ends first in the base text
        if (abase + alen) < (bbase + blen):
            ia += 1
        else:
            ib += 1

    intbase = len(base)
    abase = len(a)
    bbase = len(b)
    sl.append((intbase, intbase, abase, abase, bbase, bbase))

    return sl
