cat data/Select_PacBio_contigs//*.fa > all-contigs.fa
blastz contig6_TRF_consensus_inregister.fa all-contigs.fa > all-contigs.blastz
python extract-matches.py all-contigs.fa all-contigs.blastz -l 165 > all.fa
