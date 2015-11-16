# a quick and dirty parser for Shamoni's CenH3 project / repeat recovery.
import argparse
import sys

def _collect_record(fp):
    record = []
    for line in fp:
        if line[0] == ' ':
            record.append(line.strip())
        elif line[0] == '}':
            record.append(line.strip())
            return record
        else:
            print 'ERROR: unknown line format', (line,)
            assert 0

def _parse_records(fp):
    records = []

    for line in fp:
        if line[0] == '#':
            pass
        elif line[0] in 'dhsaxm':
            record = [ line.strip() ]
            record += _collect_record(fp)
            records.append(record)
        else:
            print 'ERROR: unknown line format', (line,)
            assert 0

    return records


def remove_crud(records):
    keep_records = []
    for r in records:
        if r[0][0] in 'ha':
            keep_records.append(r)
    return keep_records

def extract_h_a_record_blocks(records):
    assert records[0][0][0] == 'h', records[0]

    parsed_records = []
    for record in records:
        if record[0][0] == 'h':
            query_name = record[1].strip().strip('"')[1:]
            subject_name = record[2].strip().strip('"')[1:]
        if record[0][0] == 'a':
            subject_start = int(record[2].split()[2])
            subject_end = int(record[3].split()[2])
            parsed_records.append( (query_name, subject_name, subject_start, subject_end) )
    return parsed_records


def filter_parsed_record_on_length(records, min_len):
    keep_records = []
    for (query_name, subject_name, subject_start, subject_end) in records:
        if subject_end - subject_start >= min_len:
            keep_records.append( (query_name, subject_name, subject_start, subject_end) )

    return keep_records


def parse_blastz(fp, min_length):
    records = _parse_records(fp)
    print >>sys.stderr, 'recovered %d records' % len(records)
    
    records = remove_crud(records)
    print >>sys.stderr, 'kept %d records' % len(records)
    
    records = extract_h_a_record_blocks(records)
    print >>sys.stderr, 'parsed %d "a" records' % len(records)

    records = filter_parsed_record_on_length(records, min_length)
    print >>sys.stderr, 'kept %d records with length filter' % len(records)

    return records

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('blastz_alignment')
    parser.add_argument('-l', '--min-length', type=int, default=100)
    args = parser.parse_args()

    fp = open(args.blastz_alignment)
    records = parse_blastz(fp, args.min_length)

    for (query_name, subject_name, s_start, s_end) in records:
        print query_name, subject_name[:20], s_start, s_end

if __name__ == '__main__':
    main()
