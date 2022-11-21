
import sys
import os
import argparse
import subprocess as sp
import shlex 
import csv
import re

import pandas as pd
import numpy as np

import matplotlib.pyplot as plt

def truncate(f, n):
    '''Truncates/pads a float f to n decimal places without rounding'''
    s = '{}'.format(f)
    if 'e' in s or 'E' in s:
        return '{0:.{1}f}'.format(f, n)
    i, p, d = s.partition('.')
    return '.'.join([i, (d+'0'*n)[:n]])

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

#creates output directories and move to arch out folder to prepare for scripts to run
def create_out_dirs(hard_params,arch_params):
    gen_out_dir_name = "output_files"
    os.chdir(arch_params["coffe_repo_path"])
    make_dir(gen_out_dir_name)
    os.chdir(gen_out_dir_name)
    #make directory for this specific coffe run
    make_dir(arch_params["coffe_design_name"])
    os.chdir(arch_params["coffe_design_name"])
    make_dir(hard_params["arch_dir"])
    os.chdir(hard_params["arch_dir"])
    arch_dir = os.getcwd()
    os.chdir(arch_params["coffe_repo_path"])
    #return abs path to run ASIC flow from
    return arch_dir

def modify_hb_params(hard_params,arch_params):
    # GET DIR NAMES FROM PATHS
    for hb_key,hb_val in hard_params.items():
        if "folder" in hb_key:
          #takes the abs path and gets dir name
          out_dir_name = hb_val.split("/")[-1]
          if("synth_" in hb_key):
              hard_params["synth_dir"] = out_dir_name
          elif("pr_" in hb_key):
              hard_params["pnr_dir"] = out_dir_name
          elif("primetime_"in hb_key):
              hard_params["pt_dir"] = out_dir_name
    arch_out_path = arch_params["arch_out_folder"].split("/")[-1]
    out_dir_name = arch_out_path.split("/")[-1]
    hard_params["arch_dir"] = out_dir_name




def parse_report_str_to_dict(report_dir_str):
    fields = report_dir_str.split("_")
    print(fields)

def get_synth_vs_pnr_results(design_output_path):
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
        'power': [],
        'flow_stage': []
    }
    
    os.chdir(design_output_path)
    des_abs_path = os.getcwd()
    for f in os.listdir(des_abs_path):
        
        if(os.path.isdir(f)):
            if(f == "synth"):
                os.chdir(f)
                #process synth reports
                for rep_dir in os.listdir(os.getcwd()):
                    if ("reports" in rep_dir and os.path.isdir(os.getcwd())):
                        parse_report_str_to_dict(rep_dir)
                        print(os.getcwd())
                        os.chdir(rep_dir)
                        for rep in os.listdir(os.getcwd()):
                            if("area" in rep):
                                print(rep)
                                fd = open(rep,"r")
                                for line in fd:
                                    if 'library setup time' in line:
                                        print(line)
                                        #library_setup_time = decimal_re.search(line).group(0)
                                    if 'data arrival time' in line:
                                        print(line)
                                        #data_arrival_time = decimal_re.search(line).group(0)
                                #print(library_setup_time,data_arrival_time)
                                fd.close()
                        os.chdir("../")
            
            



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


def decode_report_str(report_file):
    tmp = report_file.split("_")
    period = ""
    # metal_layers = ""
    # util = ""
    # d
    for idx,string in enumerate(tmp):
        if(string == "period"):
            period = tmp[idx+1]
        break
    return period


def parse_parallel_outputs(parallel_results_path):
    """
    This function parses the ASIC results directory created after running scripts generated from option of coffe flow
    """
    #Directory structure of the parallel results is as follows:
    #results_dir: 
    #--->synth
    #-------->parameterized_folder
    #------------>outputs
    #------------>reports
    #------------>work
    #------------>scripts
    #--->pnr
    #............
    #--->sta
    #............
    
    # os.getcwd()
    out_dict = {
        "pnr": {},
        "synth": {},
        "sta": {}
    }
    decimal_re = re.compile(r"\d+\.{0,1}\d*")
    timing_str = "setup_timing"
    area_str = "area"
    power_str = "power"
    violator_str = "violators"
    os.chdir(parallel_results_path)
    results_path = os.getcwd()
    for top_level_mod in os.listdir(os.getcwd()):
        os.chdir(os.path.join(results_path,top_level_mod))
        top_level_mod_path = os.getcwd()
        for flow_dir in os.listdir(os.getcwd()):
            os.chdir(os.path.join(top_level_mod_path,flow_dir))
            flow_path = os.getcwd()
            for parameterized_dir in os.listdir(os.getcwd()):
                os.chdir(os.path.join(flow_path,parameterized_dir))
                parameterized_path = os.getcwd()
                for dir in os.listdir(os.getcwd()):
                    os.chdir(os.path.join(parameterized_path,dir))
                    dir_path = os.getcwd()
                    if(os.path.basename(dir_path) == "reports" and len(os.listdir()) > 0 and flow_dir == "pnr"):
                        for report_file in os.listdir(os.getcwd()):
                            # gen_dict_entry_key = ""
                            dict_entry = ""
                            if("area" in report_file):
                                #Area report
                                fd = open(report_file,"r")
                                for line in fd:
                                    if("router_wrap" in line):
                                        area = re.split(r"\s+",line)[-2]
                                dict_entry = parameterized_dir + "_" + re.sub(string=os.path.basename(os.path.splitext(report_file)[0]),pattern=area_str,repl="") #(area_str,os.path.basename(os.path.splitext(report_file)[0]))
                                period = decode_report_str(dict_entry)
                                if(dict_entry not in out_dict[flow_dir]):
                                    out_dict[flow_dir][dict_entry] = {}
                                out_dict[flow_dir][dict_entry]["area"] = float(area)
                                fd.close()
                            elif("setup_timing" in report_file and ".rpt" in report_file):
                                timing_met_re = re.compile(r"VIOLATED")
                                #timing report
                                fd = open(report_file,"r")
                                text = fd.read()
                                for line in text.split("\n"):
                                    if("- Arrival Time" in line):
                                        arrival_time = float(decimal_re.search(line).group(0))
                                    elif("Setup" in line):
                                        lib_setup_time = float(decimal_re.search(line).group(0))
                                #timing_met = any(("MET" in line) for line in text) 
                                #timing_met = False if(timing_met_re.search(text)) else True
                                total_del = arrival_time + lib_setup_time
                                dict_entry = parameterized_dir + "_" + re.sub(string=os.path.basename(os.path.splitext(report_file)[0]),pattern=timing_str,repl="")
                                if(dict_entry not in out_dict[flow_dir]):
                                    out_dict[flow_dir][dict_entry] = {}
                                out_dict[flow_dir][dict_entry]["delay"] = total_del
                                if(timing_met_re.search(text)):
                                    timing_met = False
                                else:
                                    timing_met = True
                                out_dict[flow_dir][dict_entry]["timing_met_setup"] = timing_met
                                fd.close()
                            elif("violators"in report_file and ".rpt" in report_file):
                                timing_met_re = re.compile(r"VIOLATED")
                                fd = open(report_file,"r")
                                text = fd.read()
                                if(timing_met_re.search(text)):
                                    #print(os.path.join(os.getcwd(),report_file))
                                    #print(timing_met_re.search(text).group(0))
                                    timing_met = False
                                else:
                                    timing_met = True
                                dict_entry = parameterized_dir + "_" + re.sub(string=os.path.basename(os.path.splitext(report_file)[0]),pattern=violator_str,repl="")
                                if(dict_entry not in out_dict[flow_dir]):
                                    out_dict[flow_dir][dict_entry] = {}
                                out_dict[flow_dir][dict_entry]["timing_met_hold"] = timing_met

                            elif("power" in report_file and ".rpt" in report_file):
                                #power report
                                fd = open(report_file,"r")
                                for line in fd:
                                    if("Total Power:" in line):
                                        total_power = float(decimal_re.search(line).group(0))
                                dict_entry = parameterized_dir + "_" + re.sub(string=os.path.basename(os.path.splitext(report_file)[0]),pattern=power_str,repl="")
                                if(dict_entry not in out_dict[flow_dir]):
                                    out_dict[flow_dir][dict_entry] = {}
                                out_dict[flow_dir][dict_entry]["power"] = float(truncate(total_power,3))
                                fd.close()
                            
                            if(dict_entry != ""):
                                #grabbing link dimensions from the fname
                                dict_ent_params = dict_entry.split("_")
                                dim_len = 0
                                period = 0
                                for idx,e in enumerate(dict_ent_params):
                                    if("len" in e):
                                        dim_len = float(dict_ent_params[idx+1])
                                    elif("period" in e):
                                        period = float(dict_ent_params[idx+1])
                                out_dict[flow_dir][dict_entry]["dim_len"] = float(dim_len)  
                                out_dict[flow_dir][dict_entry]["period"] = float(period)                      
    return out_dict

def main():
    global cur_env
    cur_env = os.environ.copy()
    global script_path
    script_path = os.getcwd()
    parser = argparse.ArgumentParser()
    parser.add_argument('-d','--design_path',type=str,help="path to coffe design output directory",default="")
    parser.add_argument('-r','--report_path',type=str,help="path to directory containing coffe report outputs",default="")
    parser.add_argument('-c ','--compare_results',nargs="+",action="append",help="condensed csv reports to compare",default=[])
    parser.add_argument('-p',"--parallel_path",type=str,help="path to directory containing coffe report outputs",default="")
    args = parser.parse_args()
    arg_dict = vars(args)
    #create condensed reports
    if(arg_dict["report_path"] != ""):
        report_pwd = os.path.join(os.getcwd(),arg_dict["report_path"])
        report_dict = reports_to_csv(report_pwd)
    elif(arg_dict["parallel_path"] != ""):
        parallel_results_path = os.path.abspath(arg_dict["parallel_path"])
        report_dict = parse_parallel_outputs(parallel_results_path)
        df = pd.DataFrame.from_dict({(i,j): report_dict[i][j] 
            for i in report_dict.keys() 
            for j in report_dict[i].keys()},
            orient='index')
        df = df.sort_values("dim_len")
        print(df[["timing_met_hold","area","power","dim_len","period"]])

        #print(df.columns.values )
        

        dropped_df = df.droplevel(level=0)
        #Adjust dimension length according to
        dropped_df["dim_len"] = dropped_df["dim_len"].apply(lambda x: x - 350)
        for period in dropped_df.period.unique():
            fig_df = dropped_df[dropped_df["period"] == float(period)]
            print(fig_df)
            fig,(ax1,ax2,ax3 ) = plt.subplots(nrows=1,ncols=3,figsize=(20,6))
            axes = [ax1,ax2,ax3]
            #dropped_df["color"] = dropped_df.loc[dropped_df["period"] == 0.5,"red"]
            # dropped_df["color"] = np.where(dropped_df["period"] == 0.5,"red","black")
            # dropped_df["color"] = np.where(dropped_df["period"]== 0.75,"blue",dropped_df["color"])
            # dropped_df["color"] = np.where(dropped_df["period"]== 1,"green",dropped_df["color"])
            # dropped_df["color"] = np.where(dropped_df["period"]== 1.33,"brown",dropped_df["color"])
            # dropped_df["color"] = np.where(dropped_df["period"]== 2,"cyan",dropped_df["color"])
            fig_df["color"] = np.where(fig_df["timing_met_hold"] == False,"red","blue")
            fig_df["color"] = np.where(fig_df["timing_met_setup"] == False,"red",fig_df["color"])


        # ax = dropped_df.set_index('dim_len').plot(y=['delay'],style='x')
            fig_df.plot.scatter(ax=ax1,x=['dim_len'],y=['delay'],style='x',c='color')
            fig_df.plot.scatter(ax=ax2,x=['dim_len'],y=['area'],style='x',c='color')
            fig_df.plot.scatter(ax=ax3,x=['dim_len'],y=['power'],style='x',c='color')
            for ax in axes:
                ax.set_xlabel("Length of router links (um)")
            ax1.set_ylabel("Delay (ps)")
            ax2.set_ylabel("Area (um^2)")
            ax3.set_ylabel("Power (uW)")

        # dropped_df.set_index('dim_len').plot(ax=ax,y=['area'],style='o',secondary_y=True,color=dropped_df["color"])
        
        #ax = df.unstack(level=0)#.plot(x='dim_len',y='delay',style='o')#.plot(kind='bar', subplots=True, rot=0)
        #print(ax)
        #fig = ax.get_figure()
            fig_name = os.path.join("/fs1/eecg/vaughn/morestep/COFFE/analyze_results",str(period)+"_area_delay_fig.png")
            fig.savefig(fig_name)



    sys.exit(0)
    # print(arg_dict)
    if(arg_dict["design_path"] != ""):
        get_synth_vs_pnr_results(arg_dict["design_path"])
    sys.exit(1)
    flattened_comp_list = [val for sublist in arg_dict["compare_results"] for val in sublist]
    print(flattened_comp_list)
    if(len(flattened_comp_list) > 1 ):
        
        # df_list = []
        # for in_csv in flattened_comp_list:
            # df_list.append(pd.read_csv(in_csv))
        df1 = pd.read_csv(flattened_comp_list[0])
        df2 = pd.read_csv(flattened_comp_list[1])
        # df1["matching"] = df2.eq(df1.iloc[:,0],axis=1).all(1)
        # df1["matching"] = df2.apply(lambda x: x.period)
        df1["area_diff"] = np.nan
        df2["area_diff"] = np.nan
        for index, row in df1.iterrows():
            row["area_diff"]
        print(df1.head())
        print(df2.head())
        #df_list[0]["report_diff"] = df_list[0].apply(lambda x: x.mode == x.period == x.metal_layers == x.wire_model == x.utilization == x.top_level_mod)
        # print(df_list[0]["report_diff"])
        


if __name__ == "__main__":
    main()

