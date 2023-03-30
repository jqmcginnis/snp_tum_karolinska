## Repository for using SAMSEG longitudinal lesion segmentation on a large cohort, to sync settings with collaborators

### Requirements

We expect you to install the following dependencies:

- Freesurfer v. 7.3.2, c.f.: https://surfer.nmr.mgh.harvard.edu/fswiki/DownloadAndInstall
- FSL v.6.0, c.f.: https://fsl.fmrib.ox.ac.uk/fsl/fslwiki/FslInstallation/Linux


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

Output Data Structure (not 100% BIDS, we are working on it!). Important files highlighted!:

```
Database_SNP_test_bids/
├── dataset_description.json
├── derivatives
│   └── samseg-longitudinal-7.3.2
│       ├── sub-m000782
│       │   ├── ses-20090814
│       │   │   └── anat
│       │   │       ├── sub-m000782_ses-20090814_mode01_bias_corrected.mgz
│       │   │       ├── sub-m000782_ses-20090814_mode01_bias_field.mgz
│       │   │       ├── sub-m000782_ses-20090814_mode01_scaling.txt
│       │   │       ├── sub-m000782_ses-20090814_mode02_bias_corrected.mgz
│       │   │       ├── sub-m000782_ses-20090814_mode02_bias_field.mgz
│       │   │       ├── sub-m000782_ses-20090814_mode02_scaling.txt
│       │   │       ├── sub-m000782_ses-20090814_samseg.stats
│       │   │       ├── sub-m000782_ses-20090814_sbtiv.stats
│       │   │       ├── sub-m000782_ses-20090814_seg.mgz
│       │   │       ├── sub-m000782_ses-20090814_space-common_FLAIR.lta
│       │   │       ├── sub-m000782_ses-20090814_space-common_FLAIR.mgz
│       │   │       └── sub-m000782_ses-20090814_space-common_T1w.mgz
│       │   ├── ses-20130227
│       │   │   └── anat
│       │   │       ├── sub-m000782_ses-20130227_mode01_bias_corrected.mgz
│       │   │       ├── sub-m000782_ses-20130227_mode01_bias_field.mgz
│       │   │       ├── sub-m000782_ses-20130227_mode01_scaling.txt
│       │   │       ├── sub-m000782_ses-20130227_mode02_bias_corrected.mgz
│       │   │       ├── sub-m000782_ses-20130227_mode02_bias_field.mgz
│       │   │       ├── sub-m000782_ses-20130227_mode02_scaling.txt
│       │   │       ├── sub-m000782_ses-20130227_samseg.stats
│       │   │       ├── sub-m000782_ses-20130227_sbtiv.stats
│       │   │       ├── sub-m000782_ses-20130227_seg.mgz
│       │   │       ├── sub-m000782_ses-20130227_space-common_FLAIR.lta
│       │   │       ├── sub-m000782_ses-20130227_space-common_FLAIR.mgz
│       │   │       └── sub-m000782_ses-20130227_space-common_T1w.mgz
│       │   ├── `sub-m000782_bl_lesions.nii.gz`
│       │   ├── sub-m000782_bl-min-fu_lesions.nii.gz
│       │   ├── sub-m000782_fu_lesions.nii.gz
│       │   ├── sub-m000782_fu-min-bl_lesions.nii.gz
│       │   ├── sub-m000782_longi_lesions.csv
│       │   ├── sub-m000782_longi_lesions.npz
│       │   ├── sub-m000782_mean.mgz
│       │   ├── sub-m000782_PBVC-report.html
│       │   └── temp
│       │       ├── A_and_B.gif
│       │       ├── A_bet.png
│       │       ├── A_halfwayto_B_brain_mixeltype.nii.gz
│       │       ├── A_halfwayto_B_brain_pve_0.nii.gz
│       │       ├── A_halfwayto_B_brain_pve_1.nii.gz
│       │       ├── A_halfwayto_B_brain_pve_2.nii.gz
│       │       ├── A_halfwayto_B_brain_pveseg.nii.gz
│       │       ├── A_halfwayto_B_brain_seg.png
│       │       ├── A_halfwayto_B.mat
│       │       ├── A_halfwayto_B_render.nii.gz
│       │       ├── A_halfwayto_B_render.png
│       │       ├── A_halfwayto_scA_brain_mixeltype.nii.gz
│       │       ├── A_halfwayto_scA_brain.nii.gz
│       │       ├── A_halfwayto_scA_brain_pve_0.nii.gz
│       │       ├── A_halfwayto_scA_brain_pve_1.nii.gz
│       │       ├── A_halfwayto_scA_brain_pve_2.nii.gz
│       │       ├── A_halfwayto_scA_brain_pveseg.nii.gz
│       │       ├── A_halfwayto_scA.nii.gz
│       │       ├── A.nii.gz
│       │       ├── A_to_B_edgepoints.nii.gz
│       │       ├── A_to_B_flow.nii.gz
│       │       ├── A_to_B.mat
│       │       ├── A_to_scA_edgepoints.nii.gz
│       │       ├── A_to_scA_flow.nii.gz
│       │       ├── A_valid_mask_with_B.png
│       │       ├── B_bet.png
│       │       ├── B_halfwayto_A_brain_mixeltype.nii.gz
│       │       ├── B_halfwayto_A_brain_pve_0.nii.gz
│       │       ├── B_halfwayto_A_brain_pve_1.nii.gz
│       │       ├── B_halfwayto_A_brain_pve_2.nii.gz
│       │       ├── B_halfwayto_A_brain_pveseg.nii.gz
│       │       ├── B_halfwayto_A_brain_seg.png
│       │       ├── B_halfwayto_A.mat
│       │       ├── B_halfwayto_scB_brain_mixeltype.nii.gz
│       │       ├── B_halfwayto_scB_brain.nii.gz
│       │       ├── B_halfwayto_scB_brain_pve_0.nii.gz
│       │       ├── B_halfwayto_scB_brain_pve_1.nii.gz
│       │       ├── B_halfwayto_scB_brain_pve_2.nii.gz
│       │       ├── B_halfwayto_scB_brain_pveseg.nii.gz
│       │       ├── B_halfwayto_scB.nii.gz
│       │       ├── B.nii.gz
│       │       ├── B_to_A_edgepoints.nii.gz
│       │       ├── B_to_A_flow.nii.gz
│       │       ├── B_to_A.mat
│       │       ├── B_to_scB_edgepoints.nii.gz
│       │       ├── B_to_scB_flow.nii.gz
│       │       ├── B_valid_mask_with_A.png
│       │       ├── output
│       │       │   ├── base
│       │       │   │   ├── gaussians.rescaled.txt
│       │       │   │   ├── history.p
│       │       │   │   ├── mode01_average.mgz
│       │       │   │   ├── mode01_bias_corrected.mgz
│       │       │   │   ├── mode01_bias_field.mgz
│       │       │   │   ├── mode01_scaling.txt
│       │       │   │   ├── mode02_average.mgz
│       │       │   │   ├── mode02_bias_corrected.mgz
│       │       │   │   ├── mode02_bias_field.mgz
│       │       │   │   ├── mode02_scaling.txt
│       │       │   │   ├── samseg.stats
│       │       │   │   ├── samseg.talairach.lta
│       │       │   │   ├── sbtiv.stats
│       │       │   │   ├── seg.mgz
│       │       │   │   ├── template_coregistered.mgz
│       │       │   │   ├── template.lta
│       │       │   │   └── template_transforms.mat
│       │       │   ├── latentAtlases
│       │       │   │   ├── latentAtlas_iteration_01.mgz.gz
│       │       │   │   ├── latentAtlas_iteration_02.mgz.gz
│       │       │   │   ├── latentAtlas_iteration_03.mgz.gz
│       │       │   │   ├── latentAtlas_iteration_04.mgz.gz
│       │       │   │   └── latentAtlas_iteration_05.mgz.gz
│       │       │   ├── tp001
│       │       │   └── tp002
│       │       ├── report.html
│       │       └── report.siena
│       ├── sub-m002126
│       │   ├── ses-20100715
│       │   │   └── anat
│       │   │       ├── sub-m002126_ses-20100715_mode01_bias_corrected.mgz
│       │   │       ├── sub-m002126_ses-20100715_mode01_bias_field.mgz
│       │   │       ├── sub-m002126_ses-20100715_mode01_scaling.txt
│       │   │       ├── sub-m002126_ses-20100715_mode02_bias_corrected.mgz
│       │   │       ├── sub-m002126_ses-20100715_mode02_bias_field.mgz
│       │   │       ├── sub-m002126_ses-20100715_mode02_scaling.txt
│       │   │       ├── sub-m002126_ses-20100715_samseg.stats
│       │   │       ├── sub-m002126_ses-20100715_sbtiv.stats
│       │   │       ├── sub-m002126_ses-20100715_seg.mgz
│       │   │       ├── sub-m002126_ses-20100715_space-common_FLAIR.lta
│       │   │       ├── sub-m002126_ses-20100715_space-common_FLAIR.mgz
│       │   │       └── sub-m002126_ses-20100715_space-common_T1w.mgz
│       │   ├── ses-20121114
│       │   │   └── anat
│       │   │       ├── sub-m002126_ses-20121114_mode01_bias_corrected.mgz
│       │   │       ├── sub-m002126_ses-20121114_mode01_bias_field.mgz
│       │   │       ├── sub-m002126_ses-20121114_mode01_scaling.txt
│       │   │       ├── sub-m002126_ses-20121114_mode02_bias_corrected.mgz
│       │   │       ├── sub-m002126_ses-20121114_mode02_bias_field.mgz
│       │   │       ├── sub-m002126_ses-20121114_mode02_scaling.txt
│       │   │       ├── sub-m002126_ses-20121114_samseg.stats
│       │   │       ├── sub-m002126_ses-20121114_sbtiv.stats
│       │   │       ├── sub-m002126_ses-20121114_seg.mgz
│       │   │       ├── sub-m002126_ses-20121114_space-common_FLAIR.lta
│       │   │       ├── sub-m002126_ses-20121114_space-common_FLAIR.mgz
│       │   │       └── sub-m002126_ses-20121114_space-common_T1w.mgz
│       │   ├── sub-m002126_bl_lesions.nii.gz
│       │   ├── sub-m002126_bl-min-fu_lesions.nii.gz
│       │   ├── sub-m002126_fu_lesions.nii.gz
│       │   ├── sub-m002126_fu-min-bl_lesions.nii.gz
│       │   ├── sub-m002126_longi_lesions.csv
│       │   ├── sub-m002126_longi_lesions.npz
│       │   ├── sub-m002126_mean.mgz
│       │   ├── sub-m002126_PBVC-report.html
│       │   └── temp
│       │       ├── A_and_B.gif
│       │       ├── A_bet.png
│       │       ├── A_halfwayto_B_brain_mixeltype.nii.gz
│       │       ├── A_halfwayto_B_brain_pve_0.nii.gz
│       │       ├── A_halfwayto_B_brain_pve_1.nii.gz
│       │       ├── A_halfwayto_B_brain_pve_2.nii.gz
│       │       ├── A_halfwayto_B_brain_pveseg.nii.gz
│       │       ├── A_halfwayto_B_brain_seg.png
│       │       ├── A_halfwayto_B.mat
│       │       ├── A_halfwayto_B_render.nii.gz
│       │       ├── A_halfwayto_B_render.png
│       │       ├── A_halfwayto_scA_brain_mixeltype.nii.gz
│       │       ├── A_halfwayto_scA_brain.nii.gz
│       │       ├── A_halfwayto_scA_brain_pve_0.nii.gz
│       │       ├── A_halfwayto_scA_brain_pve_1.nii.gz
│       │       ├── A_halfwayto_scA_brain_pve_2.nii.gz
│       │       ├── A_halfwayto_scA_brain_pveseg.nii.gz
│       │       ├── A_halfwayto_scA.nii.gz
│       │       ├── A.nii.gz
│       │       ├── A_to_B_edgepoints.nii.gz
│       │       ├── A_to_B_flow.nii.gz
│       │       ├── A_to_B.mat
│       │       ├── A_to_scA_edgepoints.nii.gz
│       │       ├── A_to_scA_flow.nii.gz
│       │       ├── A_valid_mask_with_B.png
│       │       ├── B_bet.png
│       │       ├── B_halfwayto_A_brain_mixeltype.nii.gz
│       │       ├── B_halfwayto_A_brain_pve_0.nii.gz
│       │       ├── B_halfwayto_A_brain_pve_1.nii.gz
│       │       ├── B_halfwayto_A_brain_pve_2.nii.gz
│       │       ├── B_halfwayto_A_brain_pveseg.nii.gz
│       │       ├── B_halfwayto_A_brain_seg.png
│       │       ├── B_halfwayto_A.mat
│       │       ├── B_halfwayto_scB_brain_mixeltype.nii.gz
│       │       ├── B_halfwayto_scB_brain.nii.gz
│       │       ├── B_halfwayto_scB_brain_pve_0.nii.gz
│       │       ├── B_halfwayto_scB_brain_pve_1.nii.gz
│       │       ├── B_halfwayto_scB_brain_pve_2.nii.gz
│       │       ├── B_halfwayto_scB_brain_pveseg.nii.gz
│       │       ├── B_halfwayto_scB.nii.gz
│       │       ├── B.nii.gz
│       │       ├── B_to_A_edgepoints.nii.gz
│       │       ├── B_to_A_flow.nii.gz
│       │       ├── B_to_A.mat
│       │       ├── B_to_scB_edgepoints.nii.gz
│       │       ├── B_to_scB_flow.nii.gz
│       │       ├── B_valid_mask_with_A.png
│       │       ├── output
│       │       │   ├── base
│       │       │   │   ├── gaussians.rescaled.txt
│       │       │   │   ├── history.p
│       │       │   │   ├── mode01_average.mgz
│       │       │   │   ├── mode01_bias_corrected.mgz
│       │       │   │   ├── mode01_bias_field.mgz
│       │       │   │   ├── mode01_scaling.txt
│       │       │   │   ├── mode02_average.mgz
│       │       │   │   ├── mode02_bias_corrected.mgz
│       │       │   │   ├── mode02_bias_field.mgz
│       │       │   │   ├── mode02_scaling.txt
│       │       │   │   ├── samseg.stats
│       │       │   │   ├── samseg.talairach.lta
│       │       │   │   ├── sbtiv.stats
│       │       │   │   ├── seg.mgz
│       │       │   │   ├── template_coregistered.mgz
│       │       │   │   ├── template.lta
│       │       │   │   └── template_transforms.mat
│       │       │   ├── latentAtlases
│       │       │   │   ├── latentAtlas_iteration_01.mgz.gz
│       │       │   │   ├── latentAtlas_iteration_02.mgz.gz
│       │       │   │   ├── latentAtlas_iteration_03.mgz.gz
│       │       │   │   ├── latentAtlas_iteration_04.mgz.gz
│       │       │   │   └── latentAtlas_iteration_05.mgz.gz
│       │       │   ├── tp001
│       │       │   └── tp002
│       │       ├── report.html
│       │       └── report.siena


```

### Processing

1. To generate the BIDS-compliant database strucure, please run:

```
python3 bidsify_dataset/bidsify_dataset.py --input_directory /path/to/non-bids-compliant-db --output_directory /path/where/you/want/to/store/bids/db
```

2. To run the samseg longitudinal pipeline + fsl-based pbvc calculation, please install freesurfer/fsl respectively and run the following command:

```
python3 run_pipeline/run_pipeline.py --input_directory /path/to/bids --number_of_workers 32 --freesurfer_path /path/to/fs/installation --fsl_path /path/to/fsl
```

3. To aggregate all results into a single csv tabel for analysis please run the following command:

```
python3 run_pipeline/run_analysis.py --input_directory /path/to/processed/cohort --output_directory /path/to/output
```

### Any questions?

Please open an issue :)
