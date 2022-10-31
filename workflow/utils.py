'''Utilities.'''


# --- Workflow setup --- #


import gzip
import os
from os import makedirs, symlink
from os.path import abspath, exists, join
import pandas as pd
import shutil


def extract_from_gzip(ap, out):
    """Summary

    Args:
        ap (TYPE): Description
        out (TYPE): Description
    """
    if open(ap, 'rb').read(2) == b'\x1f\x8b':  # If the input is gzipped

        with gzip.open(ap, 'rb') as f_in, open(out, 'wb') as f_out:
            shutil.copyfileobj(f_in, f_out)

    else:  # Otherwise, symlink
        symlink(ap, out)


def ingest_samples(samples, tmp):
    """Summary

    Args:
        samples (TYPE): Description
        tmp (TYPE): Description

    Returns:
        TYPE: Description
    """

    sample_df = pd.read_csv(samples, header=0, index_col=0)  # name, fastq

    # Remove existing fastq symlinks
    for fastq_file in os.listdir(tmp):
        os.remove(join(tmp, fastq_file))

    # Build symlinks to input fastq files and place them in input tmp dir
    for sample_name, row in sample_df.iterrows():
        symlink(abspath(row['fastq']), join(tmp, f"{sample_name}.fastq.gz"))

    return list(sample_df.index.values)  # return the sample names


class Workflow_Dirs:
    '''Management of the working directory tree.

    Attributes:
        LOG (str): Description
        OUT (str): Description
        TMP (str): Description
    '''

    OUT = ''
    TMP = ''
    LOG = ''

    def __init__(self, work_dir, module):
        """Summary

        Args:
            work_dir (TYPE): Description
            module (TYPE): Description
        """

        self.OUT = join(work_dir, module)
        self.TMP = join(work_dir, 'tmp')
        self.LOG = join(work_dir, 'logs')

        if not exists(self.OUT):

            makedirs(self.OUT)
            makedirs(join(self.OUT, '0_trimmed'))
            makedirs(join(self.OUT, '1_quality_filtered'))
            makedirs(join(self.OUT, '2_host_reads_removed'))
            makedirs(join(self.OUT, '3_summary'))
            makedirs(join(self.OUT, 'final_reports'))

        if not exists(self.TMP):
            makedirs(self.TMP)

        if not exists(self.LOG):
            makedirs(self.LOG)

# --- Workflow functions --- #


def write_step_seq_lens(sample_name,
                        step_name,
                        fastq_filepath,
                        stats_filepath):
    """
    Writes the number of reads, number of bases, and mean bases per read for
    the input fastq file.

    Args:
        sample_name (str): name of the current sample
        step_name (str): name of the current step
        fastq_filepath (str): path to the fastq file to be QC'd
        read_stats_filepath (str): path to the output read stats file for the
                                   current input fastq file
    """
    seq_lens = calc_read_lens(fastq_filepath)

    with open(stats_filepath, 'w') as stats_handle:

        num_reads = len(seq_lens)
        num_bases = sum(seq_lens)
        mean_bases_per_read = round(num_bases / num_reads, 2)

        stats_handle.write(f"{sample_name},{step_name},{num_reads},{num_bases},{mean_bases_per_read}\n")


def calc_read_lens(fastq_filepath):
    """
    Finds the length of each read in the input fastq file.

    Args:
        fastq_filepath (str): path to the fastq file to be QC'd

    Returns:
        list: list of the length of each sequence in the input fastq file
    """

    fastq_handle = gzip.open(fastq_filepath, 'rt') if fastq_filepath.endswith('.gz') else open(fastq_filepath, 'r')

    seq_lens = []

    for i, line in enumerate(fastq_handle):

        if i % 4 == 1:
            seq_lens.append(len(line.strip()))

    fastq_handle.close()

    return seq_lens


def sample_statistics(stats_filepaths, sample_stats_filepath):
    """
    Concatenates individual step reads statistics into a single DataFrame for
    the current sample and adds columns indicating proportion of initial reads
    remaining and proportion of initial bases remaining.

    Args:
        stats_filepaths (list): list of paths to individual sample step read
                                stats files
        sample_stats_filepath (str): path to file with concatenated sample step
                                     read stats
    """

    stats_df_list = []

    for stats_filepath in stats_filepaths:
        stats_df_list.append(pd.read_csv(stats_filepath, header=None))

    merged_df = pd.concat(stats_df_list)  # sample_name,step,num_reads,total_size,mean_read_len
    begin_row = merged_df.iloc[:, 1] == '0_begin'
    merged_df.loc[:, 5] = merged_df.iloc[:, 2] / int(merged_df.loc[begin_row, 2])  # prop_init_reads
    merged_df.loc[:, 6] = merged_df.iloc[:, 3] / int(merged_df.loc[begin_row, 3])  # prop_init_bases
    merged_df = merged_df.reindex(columns=[0, 1, 2, 5, 3, 6, 4])
    merged_df.to_csv(sample_stats_filepath, header=False, index=False)
