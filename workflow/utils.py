'''Utilities.'''


# --- Workflow setup --- #


import gzip
import os
from os import makedirs, symlink
from os.path import abspath, basename, exists, join
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
    df = pd.read_csv(samples, header = 0, index_col = 0)
    s = list(df.index)
    lst = df.values.tolist()
    for i,l in enumerate(lst):
        if not exists(join(tmp, s[i] + '.fastq.gz')):
            symlink(abspath(l[0]), join(tmp, s[i] + '.fastq.gz'))
    return s


def check_make(d):
    if not exists(d):
        makedirs(d)
        
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

        check_make(self.OUT)
        out_dirs = ['final_reports', '0_trimmed', '1_quality_filtered', '2_host_reads_removed', '3_summary', 'final_reports']
        for d in out_dirs: 
            check_make(join(self.OUT, d))
        # Add a subdirectory for symlinked-in input files
        check_make(self.TMP)
        # Add custom subdirectories to organize rule logs
        check_make(self.LOG)
        log_dirs = []
        for d in log_dirs: 
            check_make(join(self.LOG, d))

def cleanup_files(work_dir, df):
    pass
    smps = list(df.index)
    for d in []: # Add directories to clean up
        for s in smps:
            os.remove(join(work_dir, 'nanopore_preprocessing', d, 'file_to_remove')) # TODO remove fastq.gz files
            os.remove(join(work_dir, 'nanopore_preprocessing', d, 'file_to_remove'))

def print_cmds(f):
    # fo = basename(log).split('.')[0] + '.cmds'
    # lines = open(log, 'r').read().split('\n')
    fi = [l for l in f.split('\n') if l != '']
    write = False
    with open('commands.sh', 'w') as f_out:
        for l in fi:
            if 'rule' in l:
                f_out.write('# ' + l.strip().replace('rule ', '').replace(':', '') + '\n')
            if 'wildcards' in l: 
                f_out.write('# ' + l.strip().replace('wildcards: ', '') + '\n')
            if 'resources' in l:
                write = True 
                l = ''
            if '[' in l: 
                write = False 
            if write:
                f_out.write(l.strip() + '\n')
            if 'rule make_config' in l:
                break

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
