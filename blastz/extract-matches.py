#! /usr/bin/env python
import parse_blastz2
import argparse
import screed
import sys

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('contigfile')
    parser.add_argument('blastz_alignment')
    parser.add_argument('-l', '--min-length', type=int, default=100)
    parser.add_argument('-b', '--boundary', type=int, default=5)
    args = parser.parse_args()

    sequences = {}
    for record in screed.open(args.contigfile):
        sequences[record.name] = record.sequence
        rc_name = record.name + " (reverse complement)"
        sequences[rc_name] = screed.rc(str(record.sequence))
    print >>sys.stderr, 'loaded %d sequences from %s' % (len(sequences), args.contigfile)

    fp = open(args.blastz_alignment)
    records = parse_blastz2.parse_blastz(fp, args.min_length)
    print >>sys.stderr, 'loaded %d records with min length %d' % (len(records), args.min_length)

    for (query_name, s_name, s_start, s_end) in records:
        seq = sequences[s_name]
        
        b_start = max(s_start - 1 - args.boundary, 0)
        b_end = min(s_end - 1 + args.boundary, len(seq))
        
        interval = seq[b_start:b_end]
        s_short = s_name.split()[0]
        if 'reverse complement' in s_name:
            s_short += 'RC'
        print '>%s:%d-%d\n%s' % (s_short, b_start, b_end, interval)

if __name__ == '__main__':
    main()
