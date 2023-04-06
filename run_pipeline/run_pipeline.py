import argparse
import os
import shutil
from pathlib import Path
import multiprocessing
from utils import getSessionID, getSubjectID, MoveandCheck, split_list
from samseg_stats import generate_samseg_stats
import nibabel as nib

def process_samseg(dirs, derivatives_dir, freesurfer_path, fsl_path, convert_voxelsize=False, remove_temp=False, verbose=False):

    for dir in dirs:

        ### assemble T1w and FLAIR file lists
        t1w = sorted(list(Path(dir).rglob('*T1w*')))
        flair = sorted(list(Path(dir).rglob('*FLAIR*')))

        t1w = [str(x) for x in t1w]
        flair = [str(x) for x in flair]

        if verbose:
            print(t1w)
            print(flair)

        try:

            if (len(t1w) != len(flair)) or (len(t1w) <= 1) or (len(flair) <= 1):
                # instead of using assert we use this mechanism due to parallel processing
                # assert len(t1w) == len(flair), 'Mismatch T1w/FLAIR number'
                # we do not check for file corresondance as lists are sorted anyway
                print(f"Fatal Error for {dir}")
                break


            # create template folder
            temp_dir = os.path.join(derivatives_dir, f'sub-{getSubjectID(t1w[0])}', 'temp')
            print(temp_dir)
            temp_dir_output = os.path.join(temp_dir, "output")
            print(temp_dir_output)
            Path(temp_dir_output).mkdir(parents=True, exist_ok=True)

            # convert all to the same spacing
            # use baseline spacing as default
            if convert_voxelsize:
                t1w_spacing = nib.load(t1w[0]).header.get_zooms()
                flair_spacing = nib.load(flair[0]).header.get_zooms()

                t1w_conv = []
                flair_conv = []

                t1wbs_path = os.path.join(temp_dir,f'sub-{getSubjectID(t1w[0])}_ses-{getSessionID(t1w[0])}_T2w_res{t1w_spacing[0]}x{t1w_spacing[1]}x{t1w_spacing[2]}.nii.gz')
                flairbs_path = os.path.join(temp_dir, f'sub-{getSubjectID(flair[0])}_ses-{getSessionID(flair[0])}_FLAIR_res{flair_spacing[0]}x{flair_spacing[1]}x{flair_spacing[2]}.nii.gz')

                # copy the T1w / Flair images to the directory

                shutil.copy(t1w[0], t1wbs_path)
                shutil.copy(flair[0], flairbs_path)

                t1w_conv.append(t1wbs_path)
                flair_conv.append(flairbs_path)

                # convert remaining files, otherwise copy
                for i in range(1, len(t1w)):
                    t1wbs_path = os.path.join(temp_dir,f'sub-{getSubjectID(t1w[i])}_ses-{getSessionID(t1w[i])}_T2w_res{t1w_spacing[0]}x{t1w_spacing[1]}x{t1w_spacing[2]}.nii.gz')
                    flairbs_path = os.path.join(temp_dir, f'sub-{getSubjectID(flair[i])}_ses-{getSessionID(flair[i])}_FLAIR_res{flair_spacing[0]}x{flair_spacing[1]}x{flair_spacing[2]}.nii.gz')

                    if t1w_spacing != nib.load(t1w[i]).header.get_zooms():

                        ### run SAMSEG longitudinal segmentation 
                        os.system(f'export FREESURFER_HOME={freesurfer_path} ; \
                                    mri_convert {t1w[i]} -voxsize {t1w_spacing[0]} {t1w_spacing[1]} {t1w_spacing[2]} {t1wbs_path}; \
                                    ')
                    else:
                        # copy the file with that resolution!
                        shutil.copy(t1w[i], t1wbs_path)

                    t1w_conv.append(t1wbs_path)
 
                    if flair_spacing != nib.load(flair[i]).header.get_zooms():

                        ### run SAMSEG longitudinal segmentation 
                        os.system(f'export FREESURFER_HOME={freesurfer_path} ; \
                                    mri_convert {flair[i]} -voxsize {flair_spacing[0]} {flair_spacing[1]} {flair_spacing[2]} {flairbs_path}; \
                                    ')
                    else:
                        # copy the file with that resolution!
                        shutil.copy(flair[i], flairbs_path)    
                    
                    flair_conv.append(flairbs_path)     

                # use paths of the converted scans instead of the original ones!
                t1w = t1w_conv
                flair = flair_conv  


            # pre-define paths of registered images 
            t1w_reg = [str(Path(x).name).replace("T1w.nii.gz", "space-common_T1w.mgz") for x in t1w]
            flair_reg_field = [str(Path(x).name).replace("FLAIR.nii.gz", "space-common_FLAIR.lta") for x in flair]
            flair_reg = [str(Path(x).name).replace("FLAIR.nii.gz", "space-common_FLAIR.mgz") for x in flair]
            # call SAMSEG 
            print(getSubjectID(t1w[0]))
            os.system(f'export FREESURFER_HOME={freesurfer_path} ; \
                        cd {temp_dir}; \
                        mri_robust_template --mov {" ".join(map(str, t1w))} --template mean.mgz --satit --mapmov {" ".join(map(str, t1w_reg))};\
                        ')        
            

            ### co-register flairs to their corresponding registered T1w images
            # initialize an empty list fo timepoint argument for samseg that will be used later
            cmd_arg = []
            # iterate over all timepoints and call SAMSEG
            for i in range(len(flair)):
                # get transformation
                os.system(f'export FREESURFER_HOME={freesurfer_path} ; \
                            cd {temp_dir}; \
                            mri_coreg --mov {flair[i]} --ref {t1w_reg[i]} --reg {flair_reg_field[i]};\
                            ')

                # apply transformation
                os.system(f'export FREESURFER_HOME={freesurfer_path} ; \
                            cd {temp_dir}; \
                            mri_vol2vol --mov {flair[i]} --reg {flair_reg_field[i]} --o {flair_reg[i]} --targ {t1w_reg[i]};\
                            ')

                # generate timepoint argument for samseg
                cmd_arg.append(f'--timepoint {t1w_reg[i]} {flair_reg[i]}') 

                # generate a derivative folder for each session (BIDS)
                deriv_ses = os.path.join(derivatives_dir, f'sub-{getSubjectID(t1w[i])}', f'ses-{getSessionID(t1w[i])}', 'anat')
                Path(deriv_ses).mkdir(parents=True, exist_ok=True)

            ### run SAMSEG longitudinal segmentation 
            os.system(f'export FREESURFER_HOME={freesurfer_path} ; \
                        cd {temp_dir}; \
                        run_samseg_long {" ".join(map(str, cmd_arg))} --threads 4 --pallidum-separate --lesion --lesion-mask-pattern 0 1 -o output/\
                        ')
            
            ### run FSL-SIENA to calculate PBVC

            for i in range(len(t1w)-1):
                # create new temp file
                tempdir_sienna = os.path.join(temp_dir, f'_{i}')
                Path(tempdir_sienna).mkdir(parents=True, exist_ok=True)                    

                os.system(f'FSLDIR={fsl_path};\
                            . ${{FSLDIR}}/etc/fslconf/fsl.sh;\
                            PATH=${{FSLDIR}}/bin:${{PATH}};\
                            export FSLDIR PATH;\
                            {fsl_path}/bin/siena {Path(t1w[i])} {Path(t1w[i+1])} -o {tempdir_sienna} -B "-f 0.2 -B"')

            ### copy output files from temp folder to their session folders
            # write paths of output folders of the timepoint (tp) in a list
            tp_folder = sorted(list(str(x) for x in os.listdir(temp_dir_output) if "tp" in str(x)))

            # copy the mean image file and pbvc files
            mean_temp_location = os.path.join(temp_dir, "mean.mgz")
            mean_target_location = os.path.join(derivatives_dir, f'sub-{getSubjectID(t1w_reg[0])}', f'sub-{getSubjectID(t1w_reg[0])}' + '_mean.mgz')
            MoveandCheck(mean_temp_location, mean_target_location)
            
            for i in range(len(t1w)-1):
                # create new temp file
                tempdir_sienna = os.path.join(temp_dir, f'_{i}')
                # copy the SIENA PBVC html report
                pbvc_temp_location = os.path.join(tempdir_sienna, "report.html")
                pbvc_target_location = os.path.join(derivatives_dir, f'sub-{getSubjectID(t1w_reg[0])}', f'sub-{getSubjectID(t1w_reg[0])}' + '_PBVC-report_{i}.html')
                MoveandCheck(pbvc_temp_location, pbvc_target_location)

            # only continue if more than one timepoint was segmented
            # aggregate the samseg output files and move to appropriate directories
            if len(tp_folder) > 1:

                # iterate through all the timepoints 
                for i in range(len(tp_folder)):
                    # initialize empty lists
                    tp_files_temp_path = []
                    tp_files_ses_path = []

                    # define target path in derivatives (BIDS-conform)
                    deriv_ses = os.path.join(derivatives_dir, f'sub-{getSubjectID(t1w_reg[i])}', f'ses-{getSessionID(t1w_reg[i])}', 'anat') 
                    
                    # write template paths and target paths of files of timepoint i into a list (and prepend subject & session IDs (BIDS convention))
                    tp_folder_path = os.path.join(temp_dir_output, tp_folder[i])
                    tp_files = os.listdir(tp_folder_path)
                    for filename in tp_files:
                        # rename to BIDS
                        tp_files_bids = f'sub-{getSubjectID(t1w_reg[i])}' + '_' + f'ses-{getSessionID(t1w_reg[i])}' + '_' + filename
                        # list template and target paths
                        tp_files_temp_path.append(os.path.join(tp_folder_path, filename))
                        tp_files_ses_path.append(os.path.join(deriv_ses, tp_files_bids))

                    # define location of files in template folder
                    t1w_reg_temp_location = os.path.join(temp_dir, t1w_reg[i])
                    flair_reg_temp_location = os.path.join(temp_dir, flair_reg[i])
                    flair_reg_field_temp_location = os.path.join(temp_dir, flair_reg_field[i])

                    # define location of files in target folder
                    t1w_reg_ses_location = os.path.join(deriv_ses, t1w_reg[i])
                    flair_reg_ses_location = os.path.join(deriv_ses, flair_reg[i])
                    flair_reg_field_ses_location = os.path.join(deriv_ses, flair_reg_field[i])
                    
                    # copy files from template output folder to target output folder (one output folder per session)
                    # each time there is a check if the file in the temp folder exists and if it  was copied successfully
                    # T1w
                    MoveandCheck(t1w_reg_temp_location, t1w_reg_ses_location)
                    # FLAIR
                    MoveandCheck(flair_reg_temp_location, flair_reg_ses_location)
                    # FLAIR transformation file
                    MoveandCheck(flair_reg_field_temp_location, flair_reg_field_ses_location)
                    # copy output files to target folder
                    for i in range(len(tp_files_temp_path)):
                        MoveandCheck(tp_files_temp_path[i], tp_files_ses_path[i])
            else:
                print(f'Skipping longitudinal data copies.')

            if remove_temp:
                # delete the temp folder
                shutil.rmtree(temp_dir)
                if os.path.exists(temp_dir):
                    raise ValueError(f'failed to delete the template folder: {temp_dir}')
                else:
                    print(f'successfully deleted the template folder: {temp_dir}')
    
            # generate the actual samseg volumetric stats

            filename = f'sub-{getSubjectID(t1w[0])}_ses-{getSessionID(t1w[0])}_seg.mgz'
            bl_path = os.path.join(derivatives_dir, f'sub-{getSubjectID(t1w[0])}', f'ses-{getSessionID(t1w[0])}', 'anat', filename)
            filename = f'sub-{getSubjectID(t1w[1])}_ses-{getSessionID(t1w[1])}_seg.mgz'
            fu_path = os.path.join(derivatives_dir, f'sub-{getSubjectID(t1w[1])}', f'ses-{getSessionID(t1w[1])}', 'anat', filename)
            output_path = os.path.join(derivatives_dir, f'sub-{getSubjectID(t1w[0])}')
            generate_samseg_stats(bl_path=bl_path, fu_path=fu_path, output_path=output_path)
        except:
            print("Error occured during processing, proceeding with next subject.")
            
if __name__ == "__main__":

    parser = argparse.ArgumentParser(description='Run SAMSEG Longitudinal Pipeline on cohort.')
    parser.add_argument('-i', '--input_directory', help='Folder of derivatives in BIDS database.', required=True)
    parser.add_argument('-n', '--number_of_workers', help='Number of parallel processing cores.', type=int, default=os.cpu_count()-1)
    parser.add_argument('-f', '--freesurfer_path', help='Path to freesurfer binaries.', default='/home/jmcginnis/freesurfer')
    parser.add_argument('-fsl', '--fsl_path', help='Path to FSL binaries.', default='/home/jmcginnis/fsl')
    parser.add_argument('--convert_voxelsize', help="Converts resolution to baseline scan resolution.", action='store_true')
    parser.add_argument('--remove_temp', action='store_true')

    # read the arguments
    args = parser.parse_args()

    if args.remove_temp:
        remove_temp = True
    else:
        remove_temp = False

    if args.convert_voxelsize:
        convert_voxelsize = True
    else:
        convert_voxelsize = False

    # generate derivatives/labels/
    derivatives_dir = os.path.join(args.input_directory, "derivatives/samseg-longitudinal-7.3.2")
    Path(derivatives_dir).mkdir(parents=True, exist_ok=True)
    data_root = Path(os.path.join(args.input_directory))

    dirs = sorted(list(data_root.glob('*')))
    dirs = [str(x) for x in dirs]
    dirs = [x for x in dirs if "sub-" in x]
    files = split_list(dirs, args.number_of_workers)

    # initialize multithreading
    pool = multiprocessing.Pool(processes=args.number_of_workers)
    # creation, initialisation and launch of the different processes
    for x in range(0, args.number_of_workers):
        pool.apply_async(process_samseg, args=(files[x], derivatives_dir, args.freesurfer_path, args.fsl_path, convert_voxelsize, remove_temp))

    pool.close()
    pool.join()

