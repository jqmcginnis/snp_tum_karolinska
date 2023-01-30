import argparse
import os
import json
import gzip

parser = argparse.ArgumentParser(description='Segment t1/f2 of brains in given database.')
parser.add_argument('-i', '--input_directory', help='Folder of database.', required=True)
parser.add_argument('-o','--output_directory', help='Folder of bids database', required=True)

args = parser.parse_args()
mode = 0o777

# create a new folder in the top directory
raw_database_dir = os.path.dirname(args.input_directory)
raw_database_name = os.path.basename(args.input_directory)
bids_database_name = raw_database_name + "_bids"
bids_database_path = os.path.join(os.path.abspath(args.output_directory),bids_database_name)

# BIDS file-format structure
t1w_label = 't1w'
t2w_label = 't2w'
flair_label = 'f2'

# define LICENSE
license = "MIT"

try:
    # create BIDS top directory structure
    os.mkdir(bids_database_path, mode)

except OSError as exc:
    pass

# @TODO: create extensive dataset description
#  https://bids-specification.readthedocs.io/en/stable/03-modality-agnostic-files.html

dictionary ={
  "Name": "TUMNIC-MS_Brain_Dataset",
  "BIDSVersion": "1.7.0",
  "DatasetType": "raw",
  "License": "CC0",
  "Authors": [
    "Mark Muehlau",
    "Tun Wiltgen",
    "Julian McGinnis",
  ],
  "Acknowledgements": "",
  "HowToAcknowledge": "",
  "Funding": [
    "",
    ""
  ],
  "EthicsApprovals": [
    ""
  ],
  "ReferencesAndLinks": [
    "",
    ""
  ],
  "DatasetDOI": "",
  "HEDVersion": "",
  "GeneratedBy": [
    {
      "Name": "jqmcginnis",
      "Version": "0.0.1",
    }
  ],
  "SourceDatasets": [
    {
      "URL": "",
      "Version": "January 31 2023"
    }
  ]
}

# only subdirectories, files excluded
dirs = [name for name in os.listdir(args.input_directory) if os.path.isdir(os.path.join(args.input_directory, name))]
dirs = sorted(dirs)
print(dirs)

for id in dirs:
    patient_id = id
    patient_path = os.path.join(args.input_directory, id)
    print('Patient ID:', patient_id)
    bids_subdir = "sub-"+patient_id
    bids_subdir_path = os.path.join(bids_database_path,bids_subdir)
    try:
        os.mkdir(bids_subdir_path)
    except:
        pass

    session_dirs = [name for name in os.listdir(patient_path) if os.path.isdir(os.path.join(patient_path, name))]

    for session in session_dirs:
        session_id = 'ses-'+session.replace("-", "")
        # assert proper date format
        session_path = os.path.join(patient_path, session)
        bids_session_path = os.path.join(bids_subdir_path, session_id)
        bids_session_path_anat = os.path.join(bids_session_path,'anat')
        print(bids_session_path)
        print(session_path)
        try:
            os.mkdir(bids_session_path)
            os.mkdir(bids_session_path_anat)

        except:
            raise ValueError('Error making new directories. Abort.')
            
        t1w_raw = os.path.join(session_path, "t1.nii")
        t1w_bids = os.path.join(bids_session_path_anat, f"sub-{patient_id}_{session_id}_{t1w_label}.nii.gz")
        t2w_raw = os.path.join(session_path, "t2.nii")
        t2w_bids = os.path.join(bids_session_path_anat, f"sub-{patient_id}_{session_id}_{t2w_label}.nii.gz")
        f2w_raw = os.path.join(session_path, "f2.nii")
        f2w_bids = os.path.join(bids_session_path_anat, f"sub-{patient_id}_{session_id}_{flair_label}.nii.gz")

        raw_dirs = [t1w_raw, t2w_raw, f2w_raw]
        bids_dirs = [t1w_bids, t2w_bids,f2w_bids]

        for raw,bids in zip(raw_dirs,bids_dirs):
          try:
              with open(raw, 'rb') as src, gzip.open(bids, 'wb') as dst:
                    dst.writelines(src)
          except:
              pass


# Serializing json
json_object = json.dumps(dictionary, indent=4)
# write to dataset description
with open(os.path.join(bids_database_path,"dataset_description.json"), "w") as outfile:
    outfile.write(json_object)

# create README
with open(os.path.join(bids_database_path,"README"), "a") as outfile:
    outfile.write("")

# create LICENSE
# choose from a variety of licenses
with open(os.path.join(bids_database_path,"LICENSE"), "w") as outfile:
    outfile.write("")

# create participants.tsv and participants.json
with open(os.path.join(bids_database_path,"participants.tsv"), "a") as outfile:
    outfile.write("")

with open(os.path.join(bids_database_path,"participants.json"), "a") as outfile:
    outfile.write("")

