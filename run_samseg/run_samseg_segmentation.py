import argparse
import os
from pathlib import Path
import multiprocessing
import re

def split_list(alist, splits=1):
    length = len(alist)
    return [alist[i * length // splits: (i + 1) * length // splits]
            for i in range(splits)]

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

def process_samseg(dirs, derivatives_dir, freesurfer_path):

    for dir in dirs:

        # assemble T1w and FLAIR file lists
        t1w = sorted(list(Path(dir).rglob('*T1w*')))
        flair = sorted(list(Path(dir).rglob('*FLAIR*')))

        t1w = [str(x) for x in t1w]
        flair = [str(x) for x in flair]

        if len(t1w) != len(flair):
            # instead of using assert we use this mechanism due to parallel processing
            # assert len(t1w) == len(flair), 'Mismatch T1w/FLAIR number'
            # we do not check for file corresondance as lists are sorted anyway
            print(f"Fatal Error for {dir}")
            break

        # print(t1w)
        

        # 3) perform registartion with both T1w images
        # mri_robust_template --mov tp0_t1.nii tp1_t1.nii tp2_t1.nii --template mean.mgz --satit --mapmov tp0_t1_reg.mgz tp1_t1_reg.mgz tp2_t1_reg.mgz
        # create derivatives subfolder


        # do the registration in a template folder and distribute its results to BIDS conform output directories later
        temp_dir = os.path.join(derivatives_dir, f'sub-m{getSubjectID(t1w[0])}', 'temp')
        Path(temp_dir).mkdir(parents=True, exist_ok=True)

        t1w_reg = [str(Path(x).name).replace("T1w.nii.gz", "space-common_T1w.mgz") for x in t1w]
        flair_reg_field = [str(Path(x).name).replace("FLAIR.nii.gz", "space-common_FLAIR.lta") for x in flair]
        flair_reg = [str(Path(x).name).replace("FLAIR.nii.gz", "space-common_FLAIR.mgz") for x in flair]

        '''
        os.system(f'export FREESURFER_HOME={freesurfer_path} ; \
                    cd {temp_dir}; \
                    mri_robust_template --mov {" ".join(map(str, t1w))} --template mean.mgz --satit --mapmov {" ".join(map(str, t1w_reg))};\
                    ')


        
        # co-register flairs


        for i in range(len(flair)):
            os.system(f'export FREESURFER_HOME={freesurfer_path} ; \
                        cd {temp_dir}; \
                        mri_coreg --mov {flair[i]} --ref {t1w_reg[i]} --reg {flair_reg_field[i]};\
                        ')

            os.system(f'export FREESURFER_HOME={freesurfer_path} ; \
                        cd {temp_dir}; \
                        mri_vol2vol --mov {flair[i]} --reg {flair_reg_field[i]} --o {flair_reg[i]} --targ {t1w_reg[i]};\
                        ')
        '''

        cmd_arg = []

        for i in range(len(flair)):
            cmd_arg.append(f'--timepoint {t1w_reg[i]} {flair_reg[i]}')     


        os.system(f'export FREESURFER_HOME={freesurfer_path} ; \
                    cd {temp_dir}; \
                    run_samseg_long {" ".join(map(str, cmd_arg))} --threads 1 --pallidum-separate --lesion --lesion-mask-pattern 0 1 -o output/\
                    ')

        

        



parser = argparse.ArgumentParser(description='Run SAMSEG Longitudinal Pipeline on cohort.')
parser.add_argument('-i', '--input_directory', help='Folder of derivatives in BIDS database.', required=True)
parser.add_argument('-n', '--number_of_workers', help='Number of parallel processing cores.', type=int, default=os.cpu_count()-1)
parser.add_argument('-f', '--freesurfer_path', help='Path to freesurfer binaries.', default='/home/twiltgen/Tun_software/Freesurfer/FS_7.3.2/freesurfer')

# read the arguments
args = parser.parse_args()

# generate derivatives/labels/
derivatives_dir = os.path.join(args.input_directory, "derivatives/samseg-longitudinal-7.3.2")
Path(derivatives_dir).mkdir(parents=True, exist_ok=True)
data_root = Path(os.path.join(args.input_directory))

dirs = sorted(list(data_root.glob('*')))

# filter directories to only include sub-m folders
dirs = [str(x) for x in dirs]
dirs = [x for x in dirs if "sub-m" in x]

files = split_list(dirs, args.number_of_workers)

# initialize multithreading
pool = multiprocessing.Pool(processes=args.number_of_workers)
# creation, initialisation and launch of the different processes
for x in range(0, args.number_of_workers):
    pool.apply_async(process_samseg, args=(files[x],derivatives_dir, args.freesurfer_path))

pool.close()
pool.join()