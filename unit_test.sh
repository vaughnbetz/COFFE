#!/bin/bash

#This is a unit test, which just makes sure that all stages of the COFFE flow runs, then tests the reporting/plotting utilities
py2=$(which python2)
py3=$(which python3)
if [ $py2 != "" ] || [ $py3 != "" ] 
then
    #run the coffe flow, hardblock and full custom
    python2 coffe.py -i 1 input_files/strtx_III_dsp/dsp_coffe_params.txt
    cd ./analyze_results
    python3 condense_reports.py -r ../output_files/strtx_III_dsp/arch_out_dir
    python3 plot_coffe_results.py -c report_csv_out/condensed_report.csv
else
    echo "couldn't find python2 executable"
fi