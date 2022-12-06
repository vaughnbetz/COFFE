#!/bin/bash


RUN_OPTS=$1
CSV_PATH=$2
PLOT_PYTHON_PATH=$3
PLOT_OPTS=${4:-"foo"}

python3_path=$(which python3)
# check to see if coffe conda env is active
if [[ $python3_path == *"coffe-env"* ]]; then
    if [[ ${PLOT_OPTS} != "foo" ]]; then
        python3 "${PLOT_PYTHON_PATH}/plot_coffe_results.py" "${RUN_OPTS}" "${CSV_PATH}" "${PLOT_OPTS}"
    else
        python3 "${PLOT_PYTHON_PATH}/plot_coffe_results.py" "${RUN_OPTS}" "${CSV_PATH}"
    fi
else
    echo "plotting option cannot be run without python3 and related environment, please run the command \"source activate coffe-env\""
    exit 1
fi
# conda activate coffe_env
