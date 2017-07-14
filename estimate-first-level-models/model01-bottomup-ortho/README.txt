
cp ../../create-regressors/outputs/dmtx_*.csv .  # copy the design matrices
python orthonormalize.py  # orthogonolize the regressors
python lpp-analysis.py    # generate the models and contrasts


Note: you can customize the input and output directories by setting the environement variables:

    DATA_DIR   # where the invidual subjects directory are
    OUTPUT_DIR   # where the results will be  
    DESIGNMAT_DIR   # where the design matrices are (. by default)

Christophe@pallier.org
