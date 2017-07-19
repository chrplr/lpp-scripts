# 
# Note: This Makefile is not clever, i.e. it  does not know about dependencies
# Time-stamp: <2017-07-19 14:56:08 cp983411>

ROOT_DIR=/volatile/Le_Petit_Prince/

SUBJECTS_FMRI_DATA=$(ROOT_DIR)/lpp

DESIGN_MATRICES_DIR=$(ROOT_DIR)/lpp-results/design-matrices-model01-ortho

FIRSTLEVEL_RESULTS=$(ROOT_DIR)/lpp-results/model01-ortho-19072017

GROUP_RESULTS=$(ROOT_DIR)/lpp-results/group-model1


# ROI_RESULTS=$(ROOT_DIR)/lpp-results


create-design-matrices:
	$(MAKE) -C create-first-level-design-matrices/model01-bottomup
	mkdir -p $(DESIGN_MATRICES_DIR) ; \
	cp create-first-level-design-matrices/model01-bottomup/dmtx*.csv $(DESIGN_MATRICES_DIR)



estimate-first-level:
	python estimate-first-level-models/model01-bottomup-ortho/orthonormalize.py \
				--design_matrices=$(DESIGN_MATRICES_DIR)  \
				--output_dir=$(DESIGN_MATRICES_DIR);
	# Remark: it would make more sense to move orthonormalize
	# to the previous goal 'create_design_matrices'
	python estimate-first-level-models/model01-bottomup-ortho/lpp-analysis.py \
				--subject_fmri_data=$(SUBJECTS_FMRI_DATA) \
				--design_matrices=$(DESIGN_MATRICES_DIR) \
				--output_dir=$(FIRSTLEVEL_RESULTS)

second-level:
	python second-level-analyses/model01-bottomup/group-analyses.py --data_dir=${FIRSTLEVEL_RESULTS} --output_dir=${GROUP_RESULTS} 

roi-analyses:
	python rois-analyses/lpp-rois.py --data_dir=${FIRSTLEVEL_RESULTS}
