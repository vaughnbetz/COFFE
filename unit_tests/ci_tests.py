import argparse
import os,sys
import subprocess as sp
import shlex 

import yaml

#This allows for the command to output to console while running but with certain commands it causes issues (awk)
def run_shell_cmd(cmd_str):
    cmd_lst = shlex.split(cmd_str)
    process = sp.Popen(cmd_lst, stdin=sp.PIPE, stdout=sp.PIPE, stderr=sp.PIPE,env=cur_env)
    cmd_stdout = ""
    for c in iter(lambda: process.stdout.read(1), b""):
        sys.stdout.buffer.write(c)
        cmd_stdout += c.decode("utf-8")
    _, cmd_stderr = process.communicate()
    cmd_stderr = cmd_stderr.decode("utf-8")
    return cmd_stdout, cmd_stderr

### CUSTOM FLOW TESTS ###
def run_custom_flow(in_config_fpath, mode="quick"):
    ## init run options ##
    run_opts = {}
    if mode == "quick":
        run_opts["iters"] = 1
    else:
        run_opts["iters"] = 4
    ## run custom flow ##
    print(f"Running custom flow with input config: {in_config_fpath}...")
    iters = run_opts["iters"]
    coffe_cmd = f"python3 {coffe_home}/coffe.py -i {iters} {in_config_fpath}"
    stdout, stderr = run_shell_cmd(coffe_cmd)
    return stdout, stderr


### STDCELL FLOW TESTS ###
def run_stdcell_flow(in_config_fpath):
    ## init run options ##
    run_opts = {}
    ## run custom flow ##
    print(f"Running stdcell flow with input config: {in_config_fpath}...")
    # Default mode is to run in parallel
    coffe_cmd = f"python3 {coffe_home}/coffe.py {in_config_fpath} -ho -p"
    stdout, stderr = run_shell_cmd(coffe_cmd)
    return stdout, stderr

def main():

    global cur_env
    global coffe_home

    cur_env = os.environ.copy()
    # Parse command line arguments
    parser = argparse.ArgumentParser()  
    parser.add_argument("-c",
                    "--coffe_top_level",
                    action='store',
                    default='~/COFFE',
                    help='Top level of your COFFE installation')
    parser.add_argument('-o', '--test_opts', type=str, choices=["custom", "stdcell", "all"], default="custom", help="choose test type")
    args = parser.parse_args()

    coffe_home = os.path.expanduser((args.coffe_top_level))

    input_test_dir = "input_files"
    custom_flow_dir = "custom_flow"
    stdcell_flow_dir = "stdcell_flow"
    # List of Custom Flow tests
    # Custom flow is automatic transistor sizing of FPGA circuits
    custom_flow_input_fpaths = [f for f in os.listdir(os.path.join(input_test_dir,custom_flow_dir)) if f.endswith(".yaml")]
    # List of Standard Cell flow tests
    stdcell_flow_input_fpaths = [f for f in os.listdir(os.path.join(input_test_dir,stdcell_flow_dir)) if f.endswith(".yaml")]

    if args.test_opts == "custom":
        for custom_flow_input_fpath in custom_flow_input_fpaths:
            coffe_out, _ = run_custom_flow(custom_flow_input_fpath)
            break
    elif args.test_opts == "stdcell":
        for stdcell_flow_input_fpath in stdcell_flow_input_fpaths:
            coffe_out, _ = run_stdcell_flow(stdcell_flow_input_fpath)
    elif args.test_opts == "all":
        for custom_flow_input_fpath in custom_flow_input_fpaths:
            coffe_out, _ = run_custom_flow(custom_flow_input_fpath)
        for stdcell_flow_input_fpath in stdcell_flow_input_fpaths:
            coffe_out, _ = run_stdcell_flow(stdcell_flow_input_fpath)
    # TODO compare with archived results


if __name__ == "__main__":
    main()