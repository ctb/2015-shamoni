#! /usr/bin/env python
import sys

def parse_blastz(buf):
    assert buf[0:5] == '#:lav', "this doesn't look like a blastz output file..."

    # there are between two and three #:lav markers in the file.  After
    # the second one are the forward matches, and after the 3rd one (if
    # it's there) are the reverse matches.

    start_forward = buf.find('#:lav', 1)
    assert start_forward > 0

    end_forward = buf.find('#:lav', start_forward + 1)

    is_rc = 1
    if end_forward == -1:
        end_forward = len(buf)
        is_rc = 0

    forward_buf = buf[start_forward:end_forward]
    records = forward_buf.split('\n}\n')
    matches = parse_blastz_record_block(records, 1)

    if is_rc:
        start_reverse = end_forward
        end_reverse = len(buf)

        reverse_buf = buf[start_reverse:end_reverse]
        records = reverse_buf.split('\n}\n')
        matches.extend(parse_blastz_record_block(records, -1))
        
    return matches

def parse_blastz_record_block(records, orient):
    #
    # run through all of the records
    #
    matches = []
    for record in records:
        # convert by linebreaks
        lines = record.split('\n')

        # get rid of comments
        lines = [ i for i in lines if len(i) and i[0] != '#' ]

        # get rid of now-empty records (should only be last line of file)
        if not lines:
            continue

        # double check format!
        assert lines[0][2] == '{'

        # ok, now for expected records ('a' for now) process specially.
        record_type = lines[0][0]
        if record_type == 'a':
            lines = lines[1:]
            matches.extend(_parse_record(lines, orient))
        else:
            continue

    return matches

def _parse_record(record, orient):
    record = [ i.strip().split() for i in record ]

    # just get the 'l' records, for now
    matches = [ i[1:] for i in record if i[0] == 'l' ]
    matches = [ map(int, i) for i in matches ]

    l = []
    for (start_top, start_bot, end_top, end_bot, percent) in matches:
        assert start_top < end_top
        assert start_bot < end_bot
        l.append(((start_top, end_top), (start_bot, end_bot), percent, orient))

    return l

def translate_blastz_matches_to_iff(features, bot_seq_len):
    iffList = []

    for ((start_top, end_top), (start_bot, end_bot), percent, orient) in features:
        if orient < 0:
            start_bot = bot_seq_len - start_bot - 1
            end_bot = bot_seq_len - end_bot - 1
            
        iffList.append('''\
  <IFFFeature start="%d" end="%d" orientation="%d">
    <Score type="percent" value="%.1f"/>
    <PairMatch ref="" start="%d" end="%d"/>
  </IFFFeature>
''' % (start_top, end_top, orient, percent, start_bot, end_bot))

    return "\n".join(iffList)
        
if __name__ == '__main__':
    m = parse_blastz(open(sys.argv[1]).read())
    print translate_blastz_matches_to_iff(m, 101913)
