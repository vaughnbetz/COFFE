import matplotlib.pyplot as plt
import csv
import sys
import argparse

import pandas as pd
import numpy as np
import os, sys


def plot_key_vs_freq(data_dict,key=None,cost=False):
    #use delay to get
    target_freqs = [(1/float(i))*1000 if float(i) != 0 else None for i in data_dict["period"]]
    achieved_freqs = [(1/float(i))*1000 if float(i) != 0 else None for i in data_dict["delay"]]
    unique_tfreqs = list(set(target_freqs))
    freq_idxs = [None]*len(target_freqs)
    #The freq_idxs array stores indexes for each report according to the target frequency
    for i,u_tfreq in enumerate(unique_tfreqs):
        for j,t_freq in enumerate(target_freqs):
            if(t_freq == u_tfreq):
                freq_idxs[j] = i
    #now we have map from target freq to achived freq, use this to get to lists for each target_freq
    tfreq_unique_data = []
    afreq_unique_data = []
    tfreq_unique_data_2 = []
    for i in range(len(unique_tfreqs)):
        tfreq_unique_data.append([])
        afreq_unique_data.append([])
        tfreq_unique_data_2.append([])
    for idx,i in enumerate(freq_idxs):
        if(cost == False):
            tfreq_unique_data[i].append(float(data_dict[key][idx]))
        else:
            tfreq_unique_data[i].append(float(data_dict["area"][idx]))
            tfreq_unique_data_2[i].append(float(data_dict["delay"][idx]))
        afreq_unique_data[i].append(achieved_freqs[idx])
    avg_key_val = [None]*len(unique_tfreqs)
    avg_achieved_freq = [None]*len(unique_tfreqs)
    for i in range(len(unique_tfreqs)):
        if(cost == False):
            avg_key_val[i] = float(sum(tfreq_unique_data[i]))/float(len(tfreq_unique_data[i]))
        else:
            avg_key_val[i] = float(sum([area*delay for area,delay in zip(tfreq_unique_data[i],tfreq_unique_data_2[i])])/float(len(tfreq_unique_data[i])))            
        avg_achieved_freq[i] = float(sum(afreq_unique_data[i]))/float(len(afreq_unique_data[i]))
    fig, ax = plt.subplots(1,2,figsize=(12,5))
    fig.tight_layout(pad=5.0)
    ax0_ylabel_str = ""
    if(cost == False):
        ys = [float(i) for i in data_dict[key]] 
        fig_name = f"{key}_fig.png"
        if(key == "area"):
            ax0_ylabel_str = "Area (um2)"
        elif(key == "power"):
            ax0_ylabel_str = "Power (mW)"
            ys = [i*1000 for i in ys]
            avg_key_val = [i*1000 for i in avg_key_val]
        elif(key == "delay"):
            ax0_ylabel_str = "Delay (ns)"
    else:
        fig_name = "cost_fig.png"
        ax0_ylabel_str = "Area (um2) x Delay (ns)"
        ys = [float(i)*float(j) for i,j in zip(data_dict["area"],data_dict["delay"])]

    xmin,xmax = (min(achieved_freqs),max(achieved_freqs))
    ymin,ymax = (min(ys), max(ys))
    yrange = ymax - ymin
    xrange = xmax - xmin
    #data plot for key selected
    ax[0].set_xlim(xmin-(xrange/10),xmax+(xrange/10))
    ax[0].set_ylim(ymin-(yrange/10),ymax+(yrange/10))
    ax[0].set_xlabel("Achieved Freq (MHz)")
    ax[0].set_ylabel(ax0_ylabel_str)
    ax[0].scatter(achieved_freqs,ys,marker='x',c='b')
    # average plot
    ax[1].set_xlim(xmin-(xrange/10),xmax+(xrange/10))
    ax[1].set_ylim(ymin-(yrange/10),ymax+(yrange/10))
    ax[1].scatter(avg_achieved_freq,avg_key_val,marker='x',c='r')
    ax[1].set_xlabel("Achieved Freq (MHz)")
    ax[1].set_ylabel("Avg " + ax0_ylabel_str)
    plt.savefig(fig_name)

def read_csv(csv_path):
    data_dict = {}
    with open(csv_path,'r') as infile:
        reader = csv.reader(infile)
        header = next(reader)
        next(reader)
        out_list = [list(i) for i in zip(*reader)]
    for idx,key in enumerate(header):
        data_dict[key] = out_list[idx]
    return data_dict


def decode_dict_dtypes(param_dtype_dict,param_key,val):
  dtype_conv = param_dtype_dict[param_key]
  ret_val = np.NaN
  if(val != "NA"):
    if(dtype_conv == "str"):
        ret_val = str(val)
    elif(dtype_conv == "float"):
        ret_val = float(val)
    elif(dtype_conv == "int"):
        ret_val = int(val)
    elif(dtype_conv == "bool"):
        ret_val = (val == "True")

  return ret_val

def gen_plots_from_csv(report_dict,partition_flag,plot_out_dir):
    #TODO Make this better, we need to have the same dict here as in coffe hardblock functions
    param_dtype_dict = {
        #input params
        "top_level" : "str",
        "period" : "float",
        "wiremdl" : "str",
        "mlayer" : "int",
        "util" : "float",
        "dimlen" : "float",
        "mode" : "int",
        "pnr" : "bool",
        "synth" : "bool",
        "sta" : "bool",
        #output vals
        "delay" : "float",
        "area" : "float",
        "power" : "float",
        "timing_met_setup" : "bool",
        "timing_met_hold" : "bool",
    }

    df = pd.DataFrame.from_dict(report_dict)

    for col in df:
        df[col] = df[col].apply(lambda x: decode_dict_dtypes(param_dtype_dict,col,x))

    synth_df = df[df["synth"] == True]
    pnr_df = df[df["pnr"] == True]
    sta_df = df[df["sta"] == True]
    y_axis_vars = ["delay","area","power"]
    if(partition_flag):
        for period in pnr_df.period.unique():
            fig_df = pnr_df[pnr_df["period"] == float(period)]
            #averages values across metal layers
            # for var in y_axis_vars:
            #     fig_df[var] = fig_df.groupby("mlayer")[var].transform('mean')
            fig,(ax1,ax2,ax3) = plt.subplots(nrows=1,ncols=3,figsize=(20,6))
            fig.suptitle("Innovus PNR PPA estimates varying router link length for Target Freq: %s (MHz)" % str(round(float(1000/period),3)))
            axes = [ax1,ax2,ax3]
            fig_df["color"] = np.where(fig_df["timing_met_setup"] == False,"red","blue")
            fig_df.plot.scatter(ax=ax1,x='dimlen',y='delay',style='x',c='color')
            fig_df.plot.scatter(ax=ax2,x='dimlen',y='area',style='x',c='color')
            fig_df.plot.scatter(ax=ax3,x='dimlen',y='power',style='x',c='color')
            ax1.set_ylabel("Delay (ns)")
            ax2.set_ylabel("Area (um^2)")
            ax3.set_ylabel("Power (W)")
            for ax in axes:
                ax.set_xlabel("Length of router links (um)")
            fig_name = os.path.join(plot_out_dir,"period" + "_" + str(period) + "_ppa_ptn_fig.png")
            fig.savefig(fig_name)
    else:
        for top_level in df.top_level.unique():
            # for mlayer in df.mlayer.unique():
            #     fig_df = pnr_df[pnr_df["mlayer"] == float(mlayer)]
            fig_df = pnr_df
            fig,(ax1,ax2,ax3) = plt.subplots(nrows=1,ncols=3,figsize=(20,6))
            fig.suptitle("Innovus PNR PPA estimates varying target frequency")
            axes = [ax1,ax2,ax3]
            fig_df["color"] = np.where(fig_df["timing_met_setup"] == False,"red","blue")
            fig_df.plot.scatter(ax=ax1,x='period',y='delay',style='x',c='color')
            fig_df.plot.scatter(ax=ax2,x='period',y='area',style='x',c='color')
            fig_df.plot.scatter(ax=ax3,x='period',y='power',style='x',c='color')
            ax1.set_ylabel("Delay (ns)")
            ax2.set_ylabel("Area (um^2)")
            ax3.set_ylabel("Power (uW)")
            for ax in axes:
                ax.set_xlabel("Period (ns)")
                #"_" + "mlayer" + "_" + str(mlayer) +
            fig_name = os.path.join(plot_out_dir,"toplvl" + "_" + top_level +  "_ppa_fig.png")
            fig.savefig(fig_name)

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('-p','--csv_pll_path',type=str,help="path to condensed pll csv results file",default="")
    parser.add_argument('-c','--csv_path',type=str,help="path to condensed csv file",default="")
    parser.add_argument('-ptn',"--partitioned_results",action="store_true",default=False)
    args = parser.parse_args()
    arg_dict = vars(args)
    if(arg_dict["csv_pll_path"] != ""):
        pll_data_dict = read_csv(arg_dict['csv_pll_path'])
        gen_plots_from_csv(pll_data_dict,arg_dict["partitioned_results"],os.path.dirname(arg_dict['csv_pll_path']))
    if(arg_dict["csv_path"] != ""):
        data_dict = read_csv(arg_dict['csv_path'])
        plot_key_vs_freq(data_dict,"area")
        plot_key_vs_freq(data_dict,"delay")
        plot_key_vs_freq(data_dict,"power")
        plot_key_vs_freq(data_dict,cost=True)

if __name__ == "__main__":
    main()