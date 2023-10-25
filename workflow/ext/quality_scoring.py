import gzip
import argparse
import math
from itertools import islice

ap = argparse.ArgumentParser()
ap.add_argument("-i", "--input",type = str ,required=True,help="input fastq")
ap.add_argument("-o", "--output",type = str ,required=True,help="output filename and destination")
args = vars(ap.parse_args())

reads = {}
file_path = args["input"]

with gzip.open(file_path, 'rt') if file_path.endswith('.gz') else open(file_path, 'r') as file:
    for i, line in enumerate(file):
        line = line.strip()
        if i % 4 == 0:  # Header
            header = line
            reads[header] = {"seq":"", "qual":""}
        elif i % 4 == 1:  # Sequence
            reads[header]["seq"] = line
        elif i % 4 == 3:  # Quality
            reads[header]["qual"] = line

f = open(args["output"],"w")
f.write(("read\tlength\tmean_qscores\tmean_errors\tqscore_mean_errors\n"))

max_iterations = 100000
for header, tdict in islice(reads.items(), max_iterations):
    qual = reads[header]["qual"]

    qs_list = []
    err_list = []

    try:
        for q in qual:
            q_num = ord(q) - 33
            qs_list.append(q_num)
            err = 10 ** (q_num / -10)
            err_list.append(err)

        mean_qs = sum(qs_list) / len(qs_list)
        mean_err = sum(err_list) / len(err_list)
        eq_score = -10 * math.log10(mean_err)

        f.write((header + "\t" + str(len(qs_list)) + "\t" + str(mean_qs) + "\t" + str(mean_err) + "\t" + str(
            eq_score) + "\n"))

    except ZeroDivisionError:
        print(f"ZeroDivisionError for header: {header}")

f.close()