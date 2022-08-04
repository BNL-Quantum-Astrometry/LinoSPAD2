"""Script for plotting separate plots for specific pairs of pixels.

Works with a single data file.

This script utilizes an unpacking module used specifically for the LinoSPAD2
data output.

The output is saved in the `results/delta_t` directory, in the case there is
no such folder, it is created where the data are stored.

This file can also be imported as a module and contains the following
functions:

    * plot_delta_separate - plots delta t for each pair of pixels in
    the range of 251-255

"""

import os
import glob
from tqdm import tqdm
import numpy as np
from matplotlib import pyplot as plt
from functions import unpack as f_up


def plot_delta_separate(path, show_fig: bool = False):
    '''Plots delta t for each pair of pixels in the range of 251-255.

    Parameters
    ----------
    path : str
        Path to data file.
    show_fig : bool, optional
        Switch for showing the output plot. The default is False.

    Returns
    -------
    None.

    '''

    os.chdir(path)

    filename = glob.glob('*.dat*')[0]

    data = f_up.unpack_binary_512(filename)

    data_251 = data[251]  # 251st pixel
    data_252 = data[252]  # 253st pixel
    data_253 = data[253]  # 254st pixel
    data_254 = data[254]  # 254st pixel
    data_255 = data[255]  # 254st pixel

    pixel_numbers = np.arange(251, 256, 1)

    all_data = np.vstack((data_251, data_252, data_253, data_254, data_255))

    plt.rcParams.update({'font.size': 20})

    for q in range(5):
        for w in range(5):
            if w <= q:
                continue

            data_pair = np.vstack((all_data[q], all_data[w]))

            minuend = len(data_pair)-1  # i=255
            lines_of_data = len(data_pair[0])
            subtrahend = len(data_pair)  # k=254
            timestamps = 512  # lines of data in the acq cycle

            output = []

            for i in tqdm(range(minuend)):
                acq = 0  # number of acq cycle
                for j in range(lines_of_data):
                    if data_pair[i][j] == -1:
                        continue
                    if j % 512 == 0:
                        acq = acq + 1  # next acq cycle
                    for k in range(subtrahend):
                        if k <= i:
                            continue  # to avoid repetition: 2-1, 153-45 etc.
                        for p in range(timestamps):
                            n = 512*(acq-1) + p
                            if data_pair[k][n] == -1:
                                continue
                            elif data_pair[i][j] - data_pair[k][n] > 1e4:
                                continue
                            elif data_pair[i][j] - data_pair[k][n] < -1e4:
                                continue
                            else:
                                output.append(data_pair[i][j]
                                              - data_pair[k][n])

            bins = np.arange(np.min(output), np.max(output), 17.857*10)
            plt.figure(figsize=(16, 10))
            plt.xlabel('\u0394t [ps]')
            plt.ylabel('Timestamps [-]')
            plt.title('Pixels {p1}-{p2}'.format(p1=pixel_numbers[q],
                                                p2=pixel_numbers[w]))
            plt.hist(output, bins=bins)

            try:
                os.chdir("results/delta_t")
            except Exception:
                os.mkdir("results/delta_t")
                os.chdir("results/delta_t")
            plt.savefig("{name}_pixels {p1}-{p2}.png".format(name=filename,
                                                        p1=pixel_numbers[q],
                                                        p2=pixel_numbers[w]))
            plt.pause(0.1)
            plt.close()
            os.chdir("../..")