#!/usr/bin/env python
# coding: utf-8

import glob
import h3
import pandas as pd
import os
import h5py
import matplotlib.pyplot as plt
import numpy as np
from datetime import datetime, timedelta
import time
import io
import re
import sys

def plot_wave(f_final_l1b, f_final_l2a, beam_id, shot_number, output):
    # give the shotbumber and l1b file, plot the waveform 
    ################################################# get l1b data
    #print(shot_number)
    f = h5py.File(f_final_l1b, 'r')
    df = pd.DataFrame()
    df['shot_number'] = f[beam_id + '/shot_number'][()]
    # get all shot number 
    idx = df[df['shot_number'] == shot_number].index[0]
    # lat
    lat = f[beam_id + '/geolocation/latitude_bin0'][idx]
    lon = f[beam_id + '/geolocation/longitude_bin0'][idx]
    # delta time 
    delta_time = f[beam_id + '/delta_time'][idx]
    # Define the base date (2018-01-01)
    base_date = datetime(2018, 1, 1)
    # Calculate the new date
    new_date = base_date  + timedelta(seconds=delta_time)
    #start
    rx_start = f[beam_id + '/rx_sample_start_index'][idx]
    rx_count = f[beam_id + '/rx_sample_count'][idx]
    noise_mean = f[beam_id + '/noise_mean_corrected'][idx]
    elev_bin0  = f[beam_id + '/geolocation/elevation_bin0'][idx]
    elev_lastbin = f[beam_id + '/geolocation/elevation_lastbin'][idx]
    elev_tdx = f[beam_id + '/geolocation/digital_elevation_model'][idx]
    v = (elev_bin0 - elev_lastbin) / (rx_count - 1) # steps 
    n = rx_count
    elev_start = elev_bin0 
    rx_elev = [elev_start - i * v for i in range(n)][:-10] # drop last 100 elements.
    rx = f[beam_id + '/rxwaveform'][rx_start:rx_start+rx_count][:-10]
    #print('rx_elev', rx_elev)
    #print('rx', rx_elev)
    #After you are done
    f.close()
    ################################################# get l2a data
    f = h5py.File( f_final_l2a, 'r')
    df = pd.DataFrame()
    df['shot_number'] = f[beam_id + '/shot_number'][()]
    # get all shot number 
    idx = df[df['shot_number'] == shot_number].index[0]
    quality = f[beam_id + '/rx_assess/quality_flag'][idx]
    select_alg = f[beam_id + '/selected_algorithm'][idx]
    zg = f[beam_id + '/geolocation/elev_lowestmode_a' + str(select_alg)][idx]
    botloc =  f[beam_id + '/rx_processing_a'+ str(select_alg)+'/botloc'][idx]
    #print('botloc', botloc)
    toploc = f[beam_id + '/rx_processing_a' + str(select_alg)+ '/toploc'][idx]
    #print('toploc', toploc)
    # get rh 
    rh98 = f[beam_id + '/rh'][idx][98]
    #print(rh98)
    f.close()
    # Calculate 'rx_max'
    rx_max = max(rx)
    rx_max = 500 if rx_max < 500 else rx_max
    # Slice 'rx' and subtract 'noise_mean'
    tmp = rx[int(toploc):int(botloc) + 1] - noise_mean
    # Calculate 'pc' using cumulative sum
    pc = np.cumsum(tmp[::-1]) / np.sum(tmp) * (rx_max - noise_mean) + noise_mean
    
    # Slice 'rx_elev' in reverse
    pc_elev = rx_elev[int(toploc):int(botloc) + 1][::-1]
    ########################plot 
    # Create the plot
    # Create subplots with two figures side by side
    plt.figure(figsize=(7, 7))  # Adjust the figure size as needed
    # Set font size for all elements
    plt.rcParams.update({'font.size': 12})
    # First subplot on the left
    #plt.subplot(1, 2, 1)  # 1 row, 2 columns, first subplot
    plt.plot(rx, rx_elev)
    # Add text on top of the figure
    #plt.text(0.2, 0.8, 'Text at (0.2, 0.8)', transform=plt.gca().transAxes)
    plt.text(min(rx), max(rx_elev)+20, 'Shotnumber: ' + str(shot_number), fontsize=8, ha='left')
    plt.text(0.1, 0.95, 'Shotnumber: ' + str(shot_number) + ', Alg:' + str(select_alg), 
             fontsize=8, ha='left', transform=plt.gca().transAxes)
    plt.text(0.1, 0.9, 'RH98: '+ str(rh98) + 'm, BEAM: ' + str(beam_id) + ', Quality: ' + str(quality), 
            fontsize=8, ha='left', transform=plt.gca().transAxes)
    plt.text(0.1, 0.85, 'Date: ' + str(new_date), 
             fontsize=8, ha='left', transform=plt.gca().transAxes)
    plt.text(0.1, 0.80, 'Lat: ' + str(round(lat,4)) + ', Lon: ' + str(round(lon,4)), 
             fontsize=8, ha='left', transform=plt.gca().transAxes)
    # Create the main scatter plot
    #plt.scatter(pc, pc_elev, s=2, color="darkgreen", label="RH")
    plt.plot(pc, pc_elev, color="darkgreen", label="RH")
    #plt.axhline(y=elev_tdx, color='r', linestyle='--', label='TDX')
    plt.axhline(y=zg, color="brown", linestyle="-", linewidth=0.8, label="zg")
    ymin =  min(rx_elev)
    ymax =  max(rx_elev)
    # # for amazon forest.
    ymin =  -40
    ymax =   10
    plt.ylim(ymin,  ymax)
    
    # Add labels and a title
    plt.xlabel('DN')
    plt.ylabel('Elevation (m)')
    # Show the legend
    plt.legend(loc='best')
    # # Add horizontal lines for 'zg', 'rx_elev[toploc]', and 'rx_elev[botloc]'
    plt.axhline(y=rx_elev[int(toploc)], color="darkgrey", linestyle="--", linewidth=0.8, label="rx_elev[toploc]")
    plt.axhline(y=rx_elev[int(botloc)], color="darkgrey", linestyle="--", linewidth=0.8, label="rx_elev[botloc]")
    # Add text labels for "Ground" and "Canopy"
    plt.text(rx_max, zg + 1, "Ground", color="brown", horizontalalignment="right", verticalalignment="bottom")
    plt.text(rx_max, rx_elev[int(toploc)] + 1, "Canopy", color="black", horizontalalignment="right", verticalalignment="bottom")
    plt.twinx()
    #plt.gca().invert_yaxis()
    plt.ylim(ymin - zg,  ymax- zg)
    plt.ylabel("Height (m)")
    #plt.xlim(220,  400)
    #plt.savefig('../results/' + str(shot_number) + '.jpg') 
    print('## save plot in jpg...')
    plt.savefig(output + '/' + str(shot_number) + '.jpg') 
    #plt.show()
    plt.close ()


if __name__ == "__main__":
        if len(sys.argv) != 3:
                print("Usage: python shotnumber2wave.py <shot_number> <output_dir>")
                sys.exit(1)
        shot_number = int(sys.argv[1])
        output = sys.argv[2]
        os.makedirs(output, exist_ok=True)
        # test give shot number --> find l1b files 
        print('## read l1b and l2a files list...')
        datapath = '/gpfs/data1/vclgp/data/iss_gedi/soc/*/*/'
        l1b_list = glob.glob(datapath + "GEDI01_B*.h5")
        l2a_list = glob.glob(datapath + "GEDI02_A*.h5")
        # OOOOOBBFFFNNNNNNNN
        # 5499_00_003_00227330
        #shot_number = 20080800200051202
        # 2008_08_002_00051202
        NN = str(shot_number)[-8:]
        FFF = str(shot_number)[-11:-8]
        BB = str(shot_number)[-13:-11]
        OO = str(shot_number)[:-13]
        String = 'O' + '0' * (5 - len(OO)) + OO
        # Iterate through the list and check if the search string is in any of the file names
        found_files = [file for file in l1b_list if String in file]
        number = int(BB)
        binary_format = ''.join(bin(number)[2:])
        binary_format = '0' * (4 - len(binary_format)) +binary_format
        beam_id = 'BEAM' + binary_format
        print('## beam number: ', beam_id)
        # find out which file has the shout number 
        flag = 0
        for f_path in found_files:
            f = h5py.File(f_path, 'r')
            keys = list(f.keys())
            #print(keys)
            if beam_id not in keys: continue # if that beam not exist. 
            df = pd.DataFrame()
            df['shot_number'] = f[beam_id + '/shot_number'][()]
            f.close()
            if ((df['shot_number'] == shot_number).any()): # if there is a shotnumber there. 
                flag = 1
                f_final_l1b = f_path
                break
        if (flag == 0):
            print('no shotnumber is found...')
            sys.exit(1)
        print('## find l1b file: ', f_final_l1b )
        f_final_l2a = f_final_l1b.replace('GEDI01_B', 'GEDI02_A')
        l2a_s = re.sub(r'T\d{5}.*h5', '', f_final_l2a)
        f_final_l2a = [file for file in l2a_list if l2a_s in file][0]
        print('## find l2a file: ', f_final_l2a )
        print('## plotting...')
        plot_wave(f_final_l1b, f_final_l2a, beam_id, shot_number, output)