
import sys
import os
import argparse
import subprocess as sp
import shlex 
import csv
import re

############### PYTHON3 ###############
#This allows for the command to output to console while running but with certain commands it causes issues (awk)
def run_shell_cmd(cmd_str,out_flag):
    cmd_lst = shlex.split(cmd_str)
    cmd_out = sp.Popen(cmd_lst, stdin=sp.PIPE, stdout=sp.PIPE, stderr=sp.PIPE,env=cur_env)
    cmd_stdout = ""
    for line in iter(cmd_out.stdout.readline, ""):
        if(cmd_out.poll() is None):
            cmd_stdout += line.decode("utf-8")
            if(out_flag == 1):
                sys.stdout.buffer.write(line)
            elif(out_flag == 2):
                sys.stderr.buffer.write(line)
        else:
            break
    _, cmd_stderr = cmd_out.communicate()
    cmd_stderr = cmd_stderr.decode("utf-8")
    print("cmd: %s returned with: %d" % (cmd_str,cmd_out.returncode))
    return cmd_stdout, cmd_stderr

#safe mode for running shell commands
def safe_run_shell_cmd(cmd_str):
    cmd_lst = shlex.split(cmd_str)
    cmd_out = sp.run(cmd_lst, stdin=sp.PIPE, stdout=sp.PIPE, stderr=sp.PIPE,env=cur_env)
    cmd_stdout = cmd_out.stdout.decode("utf-8")
    cmd_stderr = cmd_out.stderr.decode("utf-8")
    # print("cmd: %s returned with: %d" % (cmd_str,cmd_out.returncode))
    if(cmd_out.returncode != 0):
        print(cmd_stderr)
    return cmd_stdout, cmd_stderr
############### PYTHON3 ###############

#return the relative path of top level repo (COFFE in this case)
def find_top_repo(repo_str):
  cwd_pwd_list = os.getcwd().split("/")
  cwd_pwd_list.reverse()
  repo_idx = cwd_pwd_list.index(repo_str)
  return "../"*(repo_idx)

def make_dir(dir_rel_path):
  if(not os.path.isdir(dir_rel_path)):
      os.mkdir(dir_rel_path)
      # print("made directory in the path\n%s" % ( os.getcwd()))


#outputs csv to the report_csv_out dir
def reports_to_csv(report_path):
  os.chdir(report_path)
  decimal_re = re.compile(r'\d+\.{0,1}\d*')
  report_dict = {
      'mode': [],
      'top_level_mod' : [],
      'period': [],
      'wire_model': [],
      'metal_layers' : [],
      'utilization' : [],
      'area': [],
      'delay': [],
      'power': []
  }
  for rep in os.listdir(report_path):
    report_csv_out_dir = "report_csv_out"
    if("report_" in rep):
        #parse asic params from rep name
        rep_params = rep.split("_")
        if(len(rep_params) < 7):
          continue
        #check to see if its the mode or average of modes reports
        #be careful the mode param is only gonna work for dsp block (or other verilog that has mode_0,mode_1 ports to muxes), will have to be generalized in future TODO
        if("mode" in rep_params[1]):
            report_dict["mode"].append(rep_params[1])
            param_idx = 1
        else:
            report_dict["mode"].append("none")
            param_idx = 0

        report_dict["top_level_mod"].append(rep_params[1+param_idx])
        report_dict["period"].append(rep_params[2+param_idx])
        #skip one index for "wire" keyword
        report_dict["wire_model"].append(rep_params[3+param_idx])
        report_dict["metal_layers"].append(rep_params[5+param_idx])
        #remove the .txt from the last param in filename
        report_dict["utilization"].append(os.path.splitext(rep_params[6+param_idx])[0])
        fd = open(rep,"r")
        delay = ""
        power = ""
        area = ""
        for line in fd:
            if("area" in line):
                area = decimal_re.search(line).group(0)
            elif("delay" in line):
                delay = decimal_re.search(line).group(0)
            elif("power" in line):
                power = decimal_re.search(line).group(0)
        report_dict['area'].append(area)
        report_dict['delay'].append(delay)
        report_dict['power'].append(power)
        fd.close()
  os.chdir(script_path)
  make_dir(report_csv_out_dir)
  for row_idx in range(len(report_dict["delay"])):
    dict_row = [report_dict[key][row_idx] for key in report_dict.keys()]
  fd = open(report_csv_out_dir + "/condensed_report.csv","w")
  writer = csv.writer(fd)
  writer.writerow(report_dict.keys())
  for row_idx in range(len(report_dict["delay"])):
    dict_row = [report_dict[key][row_idx] for key in report_dict.keys()]
    writer.writerow(dict_row)
  fd.close()
  return report_dict

def main():
    global cur_env
    cur_env = os.environ.copy()
    global script_path
    script_path = os.getcwd()
    parser = argparse.ArgumentParser()
    parser.add_argument('-r','--report_path',type=str,help="path to directory containing coffe report outputs")
    args = parser.parse_args()
    arg_dict = vars(args)
    #create condensed reports
    report_pwd = os.path.join(os.getcwd(),arg_dict["report_path"])
    report_dict = reports_to_csv(report_pwd)



if __name__ == "__main__":
    main()

