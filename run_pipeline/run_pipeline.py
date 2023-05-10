import argparse
import os
import shutil
from pathlib import Path
import multiprocessing
from utils import getSessionID, getSubjectID, MoveandCheck, split_list
from samseg_stats import generate_samseg_stats
import nibabel as nib

def process_samseg(dirs, derivatives_dir, freesurfer_path, fsl_path, convert_resolution=False, remove_temp=False):

    for dir in dirs:

        ### assemble T1w and FLAIR file lists
        t1w = sorted(list(Path(dir).rglob('*T1w*')))
        flair = sorted(list(Path(dir).rglob('*FLAIR*')))

        t1w = [str(x) for x in t1w]
        flair = [str(x) for x in flair]

        try:
            
            # check if more than 1 scans are available
            if (len(t1w) <= 1) or (len(flair) <= 1):
                # instead of using assert we use this mechanism due to parallel processing
                # assert len(t1w) == len(flair), 'Mismatch T1w/FLAIR number'
                # we do not check for file corresondance as lists are sorted anyway
                print(f"Fatal Error for {dir}: only one T1w or FLAIR scan.")
                break
            
            ### resample scans of tp1 and tp2 to the same spacing if necessary
            if convert_resolution:
                # get the spacing of the scans
                tp1_t1w_spacing = nib.load(t1w[0]).header.get_zooms()
                tp2_t1w_spacing = nib.load(t1w[1]).header.get_zooms()
                tp1_flair_spacing = nib.load(flair[0]).header.get_zooms()
                tp2_flair_spacing = nib.load(flair[1]).header.get_zooms()

                # check T1w image spacing
                if max(tp1_t1w_spacing)>1.1 or max(tp2_t1w_spacing)>1.1: 
                    # if spacing in one of the T1w images is larger than 1.1mm, we consider the resolution as being too low
                    print(f'T1W image low resolution ERROR for {dir}')
                    break

                # check FLAIR image spacing
                if max(tp1_flair_spacing)>1.6 or min(tp1_flair_spacing)>1.0 or max(tp2_flair_spacing)>1.6 or min(tp2_flair_spacing)>1.0:
                    # if spacing in one of the FALIR images is larger than 1.6mm or the lowest spacing is larger than 1.0, 
                    # then we consider the resolution as being too low 
                    # (since FLAIR is not isotropic in our MRI sequence acquisition parameters, we need to check min and max)
                    print(f'FLAIR image low resolution ERROR for {dir}')
                    break

                # check if one image has higher resolution (at least 0.1mm higher resolution) and 
                # downsample to 1x1x1 for T1w and to 0.8984x0.8984x1.5 for FLAIR
                # (these resolutions are defined by the sequence parameters applied in our institution)

                ## T1w
                if (min(tp1_t1w_spacing)<0.9) or (min(tp2_t1w_spacing)<0.9):
                    # transform tp1
                    tp1_t1w_res = t1w[0].replace('T1w.nii.gz', 'res-conform_T1w.nii.gz')
                    # call FREESURFER mri_convert with --conform flag to transform image to 1x1x1 spacing
                    os.system(f'export FREESURFER_HOME={freesurfer_path} ; \
                                mri_convert {t1w[0]} {tp1_t1w_res} --conform;\
                                ')
                    t1w.append(str(tp1_t1w_res))
                    # transform tp2
                    tp2_t1w_res = t1w[1].replace('T1w.nii.gz', 'res-conform_T1w.nii.gz')
                    # call FREESURFER mri_convert with --conform flag to transform image to 1x1x1 spacing
                    os.system(f'export FREESURFER_HOME={freesurfer_path} ; \
                                mri_convert {t1w[1]} {tp2_t1w_res} --conform;\
                                ')
                    t1w.append(str(tp2_t1w_res))
                # sort the list because later steps (while-loop removing duplicates) rely on a sorted list
                t1w.sort()

                ## FLAIR (cannot use --conform flag since FLAIR voxel spacing is not isotropic)
                # tp1
                if max(tp1_flair_spacing)<1.4:
                    tp1_flair_res = flair[0].replace('FLAIR.nii.gz', 'res-common_FLAIR.nii.gz')
                    # call FREESURFER mri_convert with -vs flag to transform image to specified spacing
                    os.system(f'export FREESURFER_HOME={freesurfer_path} ; \
                                mri_convert -vs 0.8984 0.8984 1.5 -it nii -ot nii {flair[0]} {tp1_flair_res};\
                                ')
                    flair.append(str(tp1_flair_res))
                # tp2
                if max(tp2_flair_spacing)<1.4:
                    tp2_flair_res = flair[1].replace('FLAIR.nii.gz', 'res-common_FLAIR.nii.gz')
                    # call FREESURFER mri_convert with -vs flag to transform image to specified spacing
                    os.system(f'export FREESURFER_HOME={freesurfer_path} ; \
                                mri_convert -vs 0.8984 0.8984 1.5 -it nii -ot nii {flair[1]} {tp2_flair_res};\
                                ')
                    flair.append(str(tp2_flair_res))
                # sort the list because later steps (while-loop removing duplicates) rely on a sorted list
                flair.sort()
            
            #### check for which files 'T1w.nii.gz' AND 'res-conform_T1w.nii.gz' exists in t1w an replace T1w file path with res-common_T1w file path
            # (same for FLAIR check 'FLAIR.nii.gz' and 'res-common.nii.gz')
            ## T1w
            i=0
            while i <= len(t1w)-1:
                t1w_path = os.path.join(dir, f'ses-{getSessionID(t1w[i])}', 'anat', f'sub-{getSubjectID(t1w[i])}_ses-{getSessionID(t1w[i])}_T1w.nii.gz')
                t1w_res_path = os.path.join(dir, f'ses-{getSessionID(t1w[i])}', 'anat', f'sub-{getSubjectID(t1w[i])}_ses-{getSessionID(t1w[i])}_res-conform_T1w.nii.gz')
                print('t1w_res_path:')
                print(t1w_res_path)
                # if both file paths are in the list, remove the original file path and keep the resampled file path
                if (t1w_path in t1w) and (t1w_res_path in t1w):
                    t1w.remove(t1w_path)
                # update index
                i += 1
                ## FlAIR
            i=0
            while i <= len(flair)-1:
                flair_path = os.path.join(dir, f'ses-{getSessionID(flair[i])}', 'anat', f'sub-{getSubjectID(flair[i])}_ses-{getSessionID(flair[i])}_FLAIR.nii.gz')
                flair_res_path = os.path.join(dir, f'ses-{getSessionID(flair[i])}', 'anat', f'sub-{getSubjectID(flair[i])}_ses-{getSessionID(flair[i])}_res-common_FLAIR.nii.gz')
                # if both file paths are in the list, remove the original file path and keep the resampled file path
                if (flair_path in flair) and (flair_res_path in flair):
                    flair.remove(flair_path)
                # update index
                i += 1
            
            # remove duplicates from list
            t1w = list(dict.fromkeys(t1w))
            flair = list(dict.fromkeys(flair))
            # print('t1w: ')
            # print(t1w)
            # print('flair: ')
            # print(flair)

            ### check if there are as many t1 as flair images
            if (len(t1w) != len(flair)):
                # instead of using assert we use this mechanism due to parallel processing
                # assert len(t1w) == len(flair), 'Mismatch T1w/FLAIR number'
                # we do not check for file corresondance as lists are sorted anyway
                print(f"Fatal Error for {dir}: unequal number of T1w and FLAIR scans.")
                break

            ### perform registartion with both T1w images
            # do the registration in a template folder and distribute its results to BIDS conform output directories later
            # create template folder
            #print(t1w)
            temp_dir = os.path.join(derivatives_dir, f'sub-{getSubjectID(t1w[0])}', 'temp')
            # print(temp_dir)
            temp_dir_output = os.path.join(temp_dir, "output")
            # print(temp_dir_output)
            Path(temp_dir_output).mkdir(parents=True, exist_ok=True)
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
            os.system(f'FSLDIR={fsl_path};\
                        . ${{FSLDIR}}/etc/fslconf/fsl.sh;\
                        PATH=${{FSLDIR}}/bin:${{PATH}};\
                        export FSLDIR PATH;\
                        {fsl_path}/bin/siena {Path(t1w[0])} {Path(t1w[1])} -o {temp_dir} -B "-f 0.2 -B"')

            ### copy output files from temp folder to their session folders
            # write paths of output folders of the timepoint (tp) in a list
            tp_folder = sorted(list(str(x) for x in os.listdir(temp_dir_output) if "tp" in str(x)))
            # print('tp_folder: ')
            # print(tp_folder)
            # copy the mean image file and pbvc files
            mean_temp_location = os.path.join(temp_dir, "mean.mgz")
            mean_target_location = os.path.join(derivatives_dir, f'sub-{getSubjectID(t1w_reg[0])}', f'sub-{getSubjectID(t1w_reg[0])}' + '_mean.mgz')
            MoveandCheck(mean_temp_location, mean_target_location)
            # copy the SIENA PBVC html report
            pbvc_temp_location = os.path.join(temp_dir, "report.html")
            pbvc_target_location = os.path.join(derivatives_dir, f'sub-{getSubjectID(t1w_reg[0])}', f'sub-{getSubjectID(t1w_reg[0])}' + '_PBVC-report.html')
            MoveandCheck(pbvc_temp_location, pbvc_target_location)

            ### re-organize file locations
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
    
            ### generate the actual samseg volumetric stats
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
    parser.add_argument('--convert_resolution', help='Converts resolution to 1mm^3 (T1w) and to 0.8984x0.8984x1.5mm^3 (FLAIR).', action='store_true')
    parser.add_argument('--remove_temp', action='store_true')

    # read the arguments
    args = parser.parse_args()

    if args.remove_temp:
        remove_temp = True
    else:
        remove_temp = False

    if args.convert_resolution:
        convert_resolution = True
    else:
        convert_resolution = False

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
        pool.apply_async(process_samseg, args=(files[x], derivatives_dir, args.freesurfer_path, args.fsl_path, convert_resolution, remove_temp))

    pool.close()
    pool.join()

