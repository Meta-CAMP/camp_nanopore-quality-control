import gzip
import argparse
import math
from itertools import islice

ap = argparse.ArgumentParser()
ap.add_argument("-i", "--input",type = str ,required=True,help="input fastq")
ap.add_argument("-o", "--output",type = str ,required=True,help="output filename and destination")
args = vars(ap.parse_args())

reads = {}
file = gzip.open(args["input"], 'rt') if args["input"].endswith('.gz') else open(args["input"], 'r')
data = file.readlines()

qual_lines = 0
prev_seq = 0
header = ""
for line in data:
    line = line.strip()
    if line.startswith("@"):
        header = line
        reads[header] = {"seq":"", "qual":""}
        qual_lines = 0
    elif line == "+" and prev_seq:
        qual_lines = 1
        qual_dict = {}
    else:
        if qual_lines:
            reads[header]["qual"] += line
            prev_seq = 0
        else:
            reads[header]["seq"] += line
            prev_seq = 1

f = open(args["output"],"w")
f.write(("read\tlength\tmean_qscores\tmean_errors\tqscore_mean_errors\n"))

max_iterations = 100000
for header, tdict in islice(reads.items(), max_iterations):
    qual = reads[header]["qual"]

    qs_list = []
    err_list = []

    for q in qual:
        q_num = ord(q)-33
        qs_list.append(q_num)
        err = 10**(q_num/-10)
        err_list.append(err)

    mean_qs = sum(qs_list)/len(qs_list)
    mean_err = sum(err_list)/len(err_list)
    eq_score = -10*math.log10(mean_err)

    f.write((header+"\t"+str(len(qs_list))+"\t"+str(mean_qs)+"\t"+str(mean_err)+"\t"+str(eq_score)+"\n"))

f.close()