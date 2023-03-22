## Repository for using SAMSEG longitudinal lesion segmentation on a large cohort, to sync settings with collaborators

### Requirements

We expect you to install the following dependencies:

- Freesurfer v. 7.3.2, c.f.: https://surfer.nmr.mgh.harvard.edu/fswiki/DownloadAndInstall

Please create a conda environment using [environment.yml](environment.yml).

### Introduction

Our cohort database is NOT BIDS-compliant by default - to have better control of it, we use a script to BIDSify our database structure.

### Dataset structure

Incoming datastrure:

```
├── m_000782
│   ├── 2009-09-25
│   │   ├── f2.nii
│   │   └── t1.nii
│   └── 2011-12-20
│       ├── f2.nii
│       └── t1.nii
├── m_002126
│   ├── 2010-07-15
│   │   ├── f2.nii
│   │   └── t1.nii
│   └── 2012-11-14
│       ├── f2.nii
│       └── t1.nii
├── m_002275
│   ├── 2010-11-11
│   │   ├── f2.nii
│   │   └── t1.nii
│   └── 2016-10-10
│       ├── f2.nii
│       └── t1.nii
├── m_002348
│   ├── 2011-01-18
│   │   ├── f2.nii
│   │   └── t1.nii
│   └── 2018-11-30
│       ├── f2.nii
│       └── t1.nii
```

BIDS-compliant datastructure:

```
.
├── dataset_description.json
├── derivatives
├── participants.csv
├── sub-m000782
│   ├── ses-20090925
│   │   └── anat
│   │       ├── sub-m_000782_ses-20090925_FLAIR.nii.gz
│   │       └── sub-m_000782_ses-20090925_T1w.nii.gz
│   └── ses-20111220
│       └── anat
│           ├── sub-m_000782_ses-20111220_FLAIR.nii.gz
│           └── sub-m_000782_ses-20111220_T1w.nii.gz
├── sub-m002126
│   ├── ses-20100715
│   │   └── anat
│   │       ├── sub-m_002126_ses-20100715_FLAIR.nii.gz
│   │       └── sub-m_002126_ses-20100715_T1w.nii.gz
│   └── ses-20121114
│       └── anat
│           ├── sub-m_002126_ses-20121114_FLAIR.nii.gz
│           └── sub-m_002126_ses-20121114_T1w.nii.gz
├── sub-m002275
│   ├── ses-20101111
│   │   └── anat
│   │       ├── sub-m_002275_ses-20101111_FLAIR.nii.gz
│   │       └── sub-m_002275_ses-20101111_T1w.nii.gz
│   └── ses-20161010
│       └── anat
│           ├── sub-m_002275_ses-20161010_FLAIR.nii.gz
│           └── sub-m_002275_ses-20161010_T1w.nii.gz
└── sub-m002348
    ├── ses-20110118
    │   └── anat
    │       ├── sub-m_002348_ses-20110118_FLAIR.nii.gz
    │       └── sub-m_002348_ses-20110118_T1w.nii.gz
    └── ses-20181130
        └── anat
            ├── sub-m_002348_ses-20181130_FLAIR.nii.gz
            └── sub-m_002348_ses-20181130_T1w.nii.gz
```

### Processing

1. To generate the BIDS-compliant database strucure, please run:

```
python3 bidsify_dataset/bidsify_dataset.py --input_directory /path/to/non-bids-compliant-db --output_directory /path/where/you/want/to/store/bids/db
```

2. To run the samseg longitudinal pipeline, please install freesurfer and run the fllowing command:

```
python3 run_pipeline/run_pipeline.py --input_directory /path/to/bids --number_of_workers 32 --freesurfer_path /path/to/fs/installation
```

### Analysis / Evaluation

After running SAMSEG, you should have obtained your results in the following dataset structure:


### Any questions?

Please open an issue :)
