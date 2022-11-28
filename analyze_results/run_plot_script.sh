#!/bin/bash


RUN_OPTS=$1
CSV_PATH=$2
PLOT_PYTHON_PATH=$3
python3_path=$(which python3)
# check to see if coffe conda env is active
if [[ $python3_path == *"coffe-env"* ]]; then
    python3 "${PLOT_PYTHON_PATH}/plot_coffe_results.py" "${RUN_OPTS}" "${CSV_PATH}"
else
    echo "plotting option cannot be run without python3 and related environment, please activate coffe conda env"
    exit 1
fi


# conda activate coffe_env
