#sample basic code reading fasta file 
#chopping sequences
#Biopython has better code

import re

'''
def parse(fasta, outfile):
    header = None
    with open(fasta, 'r') as fin, open(outfile, 'w') as fout:
            for line in fin:
                if line.startswith('>'):
                    header = line
                else:
                    fout.write(line)
if __name__ == '__main__':
    parse("1.faa", "1.txt")'''
'''


'''def parse(fasta, outfile):
    header = None
    with open(fasta, 'r') as fin, open(outfile, 'w') as fout:
        i=0
        for a in fin:
            b=a[i:i+3]+ ' '
            i+=1
            fout.write(b)
if __name__ == '__main__':
    parse("1.txt", "4.txt")

'''





