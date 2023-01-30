import argparse
import os
from tqdm import tqdm
from pathlib import Path
import multiprocessing
import re

def split_list(alist, splits=1):
    length = len(alist)
    return [alist[i * length // splits: (i + 1) * length // splits]
            for i in range(splits)]

parser = argparse.ArgumentParser(description='Segment T1w / FLAIR of brains in given database.')
parser.add_argument('-i', '--input_directory', help='Folder of derivatives in BIDS database.', required=True)
parser.add_argument('-n', '--number_of_workers', help='Number of parallel processing cores.', type=int, default=os.cpu_count())

# read the arguments
args = parser.parse_args()

# generate derivatives/labels/
derivatives_dir = os.path.join(args.input_directory, "derivatives")
Path(derivatives_dir).mkdir(parents=True, exist_ok=True)
data_root = Path(os.path.join(args.input_directory))

# segmentation labels
left_ch_plexus = 31
right_ch_plexus = 63

def getSubjectID(path):
    """
    :param path: path to data file
    :return: return the BIDS-compliant subject ID
    """
    stringList = str(path).split("/")
    indices = [i for i, s in enumerate(stringList) if 'sub-' in s]
    text = stringList[indices[0]]
    try:
        found = re.search(r'sub-m(\d{6})', text).group(1)
    except AttributeError:
        found = ''
    return found

def getSessionID(path):
    """
    :param path: path to data file
    :return: return the BIDS-compliant session ID
    """
    stringList = str(path).split("/")
    indices = [i for i, s in enumerate(stringList) if '_ses-' in s]
    text = stringList[indices[0]]
    try:
        found = re.search(r'ses-(\d{8})', text).group(1)
    except AttributeError:
        found = ''
    return found


def process_samseg(subdirs):
    print(subdirs)
    for subdir in subdirs:

        t1w_files = sorted(list(Path(subdir).rglob('*T1w.nii.gz')))  # within raw data dir
        flair_files = sorted(list(Path(subdir).rglob('*FLAIR.nii.gz')))

        print(t1w_files)
        print(flair_files)

        if len(t1w_files) == len(flair_files):
            for i in range(len(t1w_files)):
                co_reg_t1w_nifti = str(t1w_files[i])
                co_reg_flair_nifti = str(flair_files[i])

                print(t1w_files)

                ch_plexus = co_reg_t1w_nifti.replace("T1w.nii.gz", "dseg.mgz")
                ch_plexus_nifti = co_reg_t1w_nifti.replace("T1w.nii.gz", "dseg.nii.gz")

                print(ch_plexus_nifti)

                os.system(f'export FREESURFER_HOME=$HOME/freesurfer ; \
                        cd {subdir}/anat/ ; \
                        run_samseg --input {co_reg_t1w_nifti} {co_reg_flair_nifti} --pallidum-separate --output seg; \
                        mri_binarize --i seg/seg.mgz --match {left_ch_plexus} {right_ch_plexus} --o {ch_plexus}; \
                        mri_convert {ch_plexus} {ch_plexus_nifti} ; \
                        ')



if __name__ == '__main__':

    dirs = sorted(list(data_root.glob('*')))
    subdir_list = []
    for dir in dirs:  # iterate over subdirs
        # glob the session directories
        subdirs = sorted(list(dir.glob('*')))
        subdirs = [str(x) for x in subdirs]
        subdir_list.append(subdirs)

    files = [item for sublist in subdir_list for item in sublist] # flatten list
    files = split_list(files, args.number_of_workers)

    # initialize multithreading
    pool = multiprocessing.Pool(processes=args.number_of_workers)
    # creation, initialisation and launch of the different processes
    for x in range(0, args.number_of_workers):
        pool.apply_async(process_samseg, args=(files[x],))

    pool.close()
    pool.join()

