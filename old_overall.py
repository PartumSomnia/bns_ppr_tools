
#
from __future__ import division
from sys import path

from dask.array.ma import masked_array

path.append('modules/')

from _curses import raw
from mpl_toolkits.axes_grid1 import make_axes_locatable
from matplotlib import ticker
import matplotlib.pyplot as plt
from matplotlib import rc
plt.rc('text', usetex=True)
plt.rc('font', family='serif')
# import units as ut # for tmerg
import statsmodels.formula.api as smf
from math import pi, log10, sqrt
import scipy.optimize as opt
import matplotlib as mpl
import pandas as pd
import numpy as np
import itertools
import os.path
import cPickle
import math
import time
import copy
import h5py
import csv
import os
import functools
from scipy import interpolate
from scidata.utils import locate
import scidata.carpet.hdf5 as h5
import scidata.xgraph as xg
from matplotlib.mlab import griddata

from matplotlib.ticker import AutoMinorLocator, FixedLocator, NullFormatter, \
    MultipleLocator
from matplotlib.colors import LogNorm, Normalize
from matplotlib.colors import Normalize, LogNorm
from matplotlib.collections import PatchCollection
from matplotlib.patches import Rectangle
from matplotlib import patches


from preanalysis import LOAD_INIT_DATA
from outflowed import EJECTA_PARS
from preanalysis import LOAD_ITTIME
from plotting_methods import PLOT_MANY_TASKS
from profile import LOAD_PROFILE_XYXZ, LOAD_RES_CORR, LOAD_DENSITY_MODES
from mkn_interface import COMPUTE_LIGHTCURVE, COMBINE_LIGHTCURVES
from combine import TEX_TABLES, COMPARISON_TABLE, TWO_SIMS, THREE_SIMS, ADD_METHODS_ALL_PAR
import units as ut # for tmerg
from utils import *


for letter in "kusi":
    print(letter),


''' lissts of all the simulations '''
simulations = {"BLh":
                 {
                      "q=1.8": ["BLh_M10201856_M0_LK_SR"], # Prompt collapse
                      "q=1.7": ["BLh_M10651772_M0_LK_SR"], # stable
                      "q=1.4": ["BLh_M16351146_M0_LK_LR"],
                      "q=1.3": ["BLh_M11841581_M0_LK_SR"],
                      "q=1":   ["BLh_M13641364_M0_LK_SR"]
                 },
              "DD2":
                  {
                      "q=1": ["DD2_M13641364_M0_HR_R04", "DD2_M13641364_M0_LK_HR_R04",
                              "DD2_M13641364_M0_LK_LR_R04", "DD2_M13641364_M0_LK_SR_R04",
                              "DD2_M13641364_M0_LR", "DD2_M13641364_M0_LR_R04",
                              "DD2_M13641364_M0_SR", "DD2_M13641364_M0_SR_R04"],
                      "q=1.1": ["DD2_M14321300_M0_LR", "DD2_M14351298_M0_LR"],
                      "q=1.2": ["DD2_M14861254_M0_HR", "DD2_M14861254_M0_LR",
                                "DD2_M14971245_M0_HR", "DD2_M14971245_M0_SR",
                                "DD2_M14971246_M0_LR", "DD2_M15091235_M0_LK_HR",
                                "DD2_M15091235_M0_LK_SR"],
                      "q=1.4": ["DD2_M16351146_M0_LK_LR"]
                  },
              "LS220":
                  {
                      "q=1": ["LS220_M13641364_M0_HR", #"LS220_M13641364_M0_LK_HR", # TOO short. 3ms
                              "LS220_M13641364_M0_LK_SR", "LS220_M13641364_M0_LK_SR_restart",
                              "LS220_M13641364_M0_LR", "LS220_M13641364_M0_SR"],
                      "q=1.1": ["LS220_M14001330_M0_HR", "LS220_M14001330_M0_SR",
                                "LS220_M14351298_M0_HR", "LS220_M14351298_M0_SR"],
                      "q=1.2": ["LS220_M14691268_M0_HR", "LS220_M14691268_M0_LK_HR",
                                "LS220_M14691268_M0_LK_SR", "LS220_M14691268_M0_LR",
                                "LS220_M14691268_M0_SR"],
                      "q=1.4": ["LS220_M16351146_M0_LK_LR", "LS220_M11461635_M0_LK_SR"],
                      "q=1.7": ["LS220_M10651772_M0_LK_LR"]
                  },
              "SFHo":
                  {
                      "q=1": ["SFHo_M13641364_M0_HR", "SFHo_M13641364_M0_LK_HR",
                              "SFHo_M13641364_M0_LK_SR", #"SFHo_M13641364_M0_LK_SR_2019pizza", # failed
                              "SFHo_M13641364_M0_SR"],
                      "q=1.1":["SFHo_M14521283_M0_HR", "SFHo_M14521283_M0_LK_HR",
                               "SFHo_M14521283_M0_LK_SR", "SFHo_M14521283_M0_LK_SR_2019pizza",
                               "SFHo_M14521283_M0_SR"],
                      "q=1.4":["SFHo_M16351146_M0_LK_LR"]
                  },
              "SLy4":
                  {
                      "q=1": [#"SLy4_M13641364_M0_HR", # precollapse
                              # "SLy4_M13641364_M0_LK_HR", # crap, absent tarball data
                              "SLy4_M13641364_M0_LK_LR", "SLy4_M13641364_M0_LK_SR",
                              # "SLy4_M13641364_M0_LR",
                              "SLy4_M13641364_M0_SR"],
                      "q=1.1":[#"SLy4_M14521283_M0_HR", unphysical and premerger
                               "SLy4_M14521283_M0_LR",
                               "SLy4_M14521283_M0_SR"]
                  }
              }

sims_err_lk_onoff = {

    "def": {"sims":["DD2_M13641364_M0_LK_SR_R04", "DD2_M15091235_M0_LK_SR", "LS220_M14691268_M0_LK_SR", "SFHo_M14521283_M0_LK_SR"],
            "lbls": ["DD2 136 136 LK", "DD2 151 123 LK", "LS220 147 127 LK", "SFHo 145 128 LK"],
            "colors":["black", 'gray', 'red', "green"],
            "lss":["-", '-', '-', '-'],
            "lws":[1.,1.,1.,1.]},
    "comp":{"sims":["DD2_M13641364_M0_SR_R04", "DD2_M14971245_M0_SR", "LS220_M14691268_M0_SR", "SFHo_M14521283_M0_SR"],
            "lbls": ["DD2 136 136", "DD2 150 125", "LS220 147 127", "SFHo 145 128"],
            "colors":["black", 'gray', 'red', "green"],
            "lss":["--", '--', '--', '--'],
            "lws":[1.,1.,1.,1.]},
}

"""=================================================================================================================="""

''' ejecta summory '''


def plot_last_disk_mass_with_lambda(v_n_x, v_n_y, v_n, det=None, mask=None):
    #
    simlist = [
                  "BLh_M10651772_M0_LK_SR",
                  "BLh_M11841581_M0_LK_SR",
                  "BLh_M13641364_M0_LK_SR",
                  "BLh_M16351146_M0_LK_LR",
                  "BLh_M10201856_M0_LK_SR"] + [
                  "DD2_M13641364_M0_HR",
                  "DD2_M13641364_M0_HR_R04",
                  "DD2_M13641364_M0_LK_HR_R04",
                  "DD2_M14861254_M0_HR",
                  "DD2_M14971245_M0_HR",
                  "DD2_M15091235_M0_LK_HR",
                  "DD2_M11461635_M0_LK_SR",
                  "DD2_M13641364_M0_LK_SR_R04",
                  "DD2_M13641364_M0_SR",
                  "DD2_M13641364_M0_SR_R04",
                  "DD2_M14971245_M0_SR",
                  "DD2_M15091235_M0_LK_SR",
                  "DD2_M14321300_M0_LR",
                  "DD2_M14351298_M0_LR",
                  "DD2_M14861254_M0_LR",
                  "DD2_M14971246_M0_LR",
                  "DD2_M13641364_M0_LR",
                  "DD2_M13641364_M0_LR_R04",
                  "DD2_M13641364_M0_LK_LR_R04",
                  "DD2_M16351146_M0_LK_LR"] + [
                  "LS220_M13641364_M0_HR",
                  "LS220_M14001330_M0_HR",
                  "LS220_M14351298_M0_HR",
                  "LS220_M14691268_M0_HR",
                  "LS220_M14691268_M0_LK_HR",
                  "LS220_M13641364_M0_LK_SR",
                  "LS220_M13641364_M0_LK_SR_restart",
                  "LS220_M14691268_M0_SR",
                  "LS220_M13641364_M0_SR",
                  "LS220_M14001330_M0_SR",
                  "LS220_M14351298_M0_SR",
                  "LS220_M11461635_M0_LK_SR",
                  "LS220_M14691268_M0_LK_SR",
                  "LS220_M14691268_M0_LR",
                  "LS220_M13641364_M0_LR",
                  "LS220_M10651772_M0_LK_LR",
                  "LS220_M16351146_M0_LK_LR"] + [
                  # "SFHo_M10651772_M0_LK_LR", # premerger
                  # "SFHo_M11461635_M0_LK_SR", # too short. No dyn. ej
                  "SFHo_M13641364_M0_HR",
                  "SFHo_M13641364_M0_LK_HR",
                  "SFHo_M14521283_M0_HR",
                  "SFHo_M14521283_M0_LK_HR",
                  "SFHo_M13641364_M0_LK_SR",
                  "SFHo_M13641364_M0_LK_SR_2019pizza",
                  "SFHo_M13641364_M0_SR",
                  "SFHo_M14521283_M0_LK_SR",
                  "SFHo_M14521283_M0_LK_SR_2019pizza",
                  "SFHo_M14521283_M0_SR",
                  "SFHo_M16351146_M0_LK_LR"] + [
                  # "SLy4_M10651772_M0_LK_LR", # premerger
                  # "SLy4_M11461635_M0_LK_SR", # premerger
                  "SLy4_M13641364_M0_LK_SR",
                  # "SLy4_M13641364_M0_LR", # removed. Wrong
                  "SLy4_M13641364_M0_SR",
                  # "SLy4_M14521283_M0_HR",
                  # "SLy4_M14521283_M0_LR", # missing output-0012 Wring GW data (but good simulation)
                  "SLy4_M14521283_M0_SR",
                  "SLy4_M13641364_M0_LK_LR",
              ]
    #
    # v_n = "Mdisk3Dmax"
    # v_n_x = "Lambda"
    # v_n_y = "q"
    # det = None
    # mask = None
    #
    # --------------------------

    if det != None and mask != None:
        figname = "{}_{}_{}_{}_{}.png".format(v_n_x, v_n_y, v_n, det, mask)
    else:
        figname = "{}_{}_{}.png".format(v_n_x, v_n_y, v_n)

    # --------------------------
    eos_lambda = {}

    data = {"LS220": {},
            "DD2": {},
            "BLh": {},
            "SFHo": {},
            "SLy4": {}}

    for sim in simlist:
        o_par = ADD_METHODS_ALL_PAR(sim)
        o_init = LOAD_INIT_DATA(sim)
        lam = o_init.get_par(v_n_x)
        eos = o_init.get_par("EOS")
        q = o_init.get_par(v_n_y)
        if det != None and mask != None:
            mdisk = o_par.get_outflow_par(det, mask, v_n)
        else:
            mdisk = o_par.get_par(v_n)
            # tdisk = o_par.get_par("tdisk3D")
        #
        if sim.__contains__("_HR"):
            lam = lam + 25.
        elif sim.__contains__("_SR"):
            lam = lam + 0.
        elif sim.__contains__("_LR"):
            lam = lam - 25.
        else:
            raise NameError("res:{} is not recognized".format(eos))

        #
        for eos_ in data.keys():
            if eos_ == eos:
                if not np.isnan(mdisk):
                    if not eos in eos_lambda.keys():
                        eos_lambda[eos] = lam
                    data[eos][sim] = {}
                    Printcolor.green("sim: {}. v_n:{} is not nan".format(sim, v_n))
                    data[eos][sim][v_n_x] = float(lam)
                    data[eos][sim][v_n_y] = float(q)
                    data[eos][sim][v_n] = float(mdisk)
                    data[eos][sim]['eos'] = eos
                else:
                    Printcolor.red("sim: {}, v_n:{} is nan".format(sim, v_n))
        #
        if det != None and mask != None and mask.__contains__("bern"):
            tcoll = o_par.get_par("tcoll_gw")
            for eos_ in data.keys():
                if eos_ == eos:
                    if not np.isinf(tcoll):
                        Printcolor.green("tcoll != np.inf sim: {}".format(sim))
                        data[eos][sim]["tcoll_gw"] = float(tcoll)
                    else:
                        data[eos][sim]["tcoll_gw"] = np.inf
                        Printcolor.yellow("\ttcoll = np.inf sim: {}".format(sim))

    #   #   #   #   #
    #   #   #   #   #
    for eos in data.keys():
        # print(data[eos][sim]["Lambda"])
        sims = data[eos].keys()
        data[eos][v_n_x + 's'] = np.array([float(data[eos][sim][v_n_x]) for sim in sims])
        data[eos][v_n_y + 's'] = np.array([float(data[eos][sim][v_n_y]) for sim in sims])
        data[eos][v_n] = np.array([float(data[eos][sim][v_n]) for sim in sims])
        if det != None and mask != None and mask.__contains__("bern"):
            data[eos]["tcoll_gw"] = np.array([float(data[eos][sim]["tcoll_gw"]) for sim in sims])

    # lams = [np.array([data[eos][sim]["Lambda"] for sim in data.keys()]) for eos in data.keys()]
    # qs = [np.array([data[eos][sim]["q"] for sim in data.keys()]) for eos in data.keys()]
    # dmasses = [np.array([data[eos][sim]["Mdisk3D"] for sim in data.keys()]) for eos in data.keys()]
    #
    #
    #
    o_plot = PLOT_MANY_TASKS()
    o_plot.gen_set["figdir"] = Paths.plots + "all2/"
    o_plot.gen_set["type"] = "cartesian"
    o_plot.gen_set["figsize"] = (4.2, 3.6)  # <->, |]
    o_plot.gen_set["figname"] = figname
    o_plot.gen_set["sharex"] = True
    o_plot.gen_set["sharey"] = False
    o_plot.gen_set["subplots_adjust_h"] = 0.0
    o_plot.gen_set["subplots_adjust_w"] = 0.0
    o_plot.set_plot_dics = []
    #
    # lams2d, qs2d = np.meshgrid(lams, qs)
    # dmasses2d = griddata(lams, qs, dmasses, lams2d, qs2d, interp='linear')
    # print(lams2d)
    # print(qs2d)
    # print(dmasses2d)
    # print(len(lams), len(qs), len(dmasses))
    # qs1, qs2 = qs.min(), qs.max()
    # lam1, lam2 = lams.min(), lams.max()
    # qstep = 0.1
    # lamstep = 100
    # grid_q = np.arange(start=qs1, stop=qs2, step=qstep)
    # grid_lam = np.arange(start=lam1, stop=lam2, step=lamstep)

    # for eos in eos_lambda.keys():
    #     eos_dic = {
    #         'task': 'text', 'ptype': 'cartesian',
    #         'position': (1, 1),
    #         'x': eos_lambda[eos], 'y': 1.5, 'text': eos,
    #         'horizontalalignment': 'center',
    #         'color': 'black', 'fs': 14
    #     }
    #     o_plot.set_plot_dics.append(eos_dic)

    #

    if det != None and mask != None and mask.__contains__("bern") and v_n.__contains__("Mej"):
        for eos in data.keys():
            for sim in simlist:
                if sim in data[eos].keys():
                    x = data[eos][sim][v_n_x]
                    y = data[eos][sim][v_n_y]
                    tcoll = data[eos][sim]["tcoll_gw"]
                    arror_dic = {
                        'task': 'line', 'position': (1, 1), 'ptype': 'cartesian',
                        'xarr': x, "yarr": y,
                        'v_n_x': v_n_x, 'v_n_y': v_n_y, 'v_n': v_n,
                        'xmin': None, 'xmax': None, 'ymin': None, 'ymax': None,
                        'xscale': None, 'yscale': None,
                        'marker': 'o', "color": "black", 'annotate': None, 'ms': 1, 'arrow': "up",
                        'alpha': 1.0,
                        'fontsize': 12,
                        'labelsize': 12,
                    }
                    # if sim.__contains__("_LR"):
                    #     arror_dic['marker'] = 'x'
                    # elif sim.__contains__("_SR"):
                    #     arror_dic['marker'] = 'o'
                    # elif sim.__contains__("_HR"):
                    #     arror_dic['marker'] = "d"

                    if not np.isinf(tcoll):
                        pass
                        # BH FORMED
                        # print("BH: {}".format(sim))
                        # arror_dic['arrow'] = None
                        # o_plot.set_plot_dics.append(arror_dic)
                    else:
                        # BH DOES NOT FORM
                        arror_dic['arrow'] = "up"
                        print("No BH: {}".format(sim))
                        o_plot.set_plot_dics.append(arror_dic)

    for eos, marker in zip(data.keys(), ['^', '<', '>', 'v', 'd']):

        lams_i = data[eos][v_n_x + 's']
        qs_i = data[eos][v_n_y + 's']
        dmasses_i = data[eos][v_n]
        mss = []  # np.zeros(len(data[eos].keys()))
        sr_x_arr = []
        sr_y_arr = []
        for i, sim in enumerate(data[eos].keys()):
            if sim.__contains__("_LR"):
                mss.append(40)
            elif sim.__contains__("_SR"):
                mss.append(55)
                sr_x_arr.append(data[eos][sim][v_n_x])
                sr_y_arr.append(data[eos][sim][v_n_y])
            elif sim.__contains__("_HR"):
                mss.append(70)

        # SR line
        sr_y_arr, sr_x_arr = UTILS.x_y_z_sort(sr_y_arr, sr_x_arr)
        sr_line_dic = {
            'task': 'line', 'position': (1, 1), 'ptype': 'cartesian',
            'xarr': sr_x_arr, "yarr": sr_y_arr,
            'v_n_x': v_n_x, 'v_n_y': v_n_y, 'v_n': v_n,
            'xmin': None, 'xmax': None, 'ymin': None, 'ymax': None,
            'xscale': None, 'yscale': None,
            # 'marker': 'x', "color": "white", 'alpha':1., 'ms':5,#
            'ls': ':', "color": "gray", 'alpha': 1., 'lw': 0.5, 'alpha': 1., 'ds': 'default',  #
            'alpha': 1.0,
            'fontsize': 12,
            'labelsize': 12,
        }
        o_plot.set_plot_dics.append(sr_line_dic)

        # lr
        lks = []
        for i, sim in enumerate(data[eos].keys()):
            if sim.__contains__("_LK_"):
                lks.append("green")
            else:
                lks.append('none')

        dic = {
            'task': 'scatter', 'ptype': 'cartesian',  # 'aspect': 1.,
            'xarr': lams_i, "yarr": qs_i, "zarr": dmasses_i,
            'position': (1, 1),  # 'title': '[{:.1f} ms]'.format(time_),
            'cbar': {'location': 'right .03 .0', 'label': Labels.labels(v_n),  # 'fmt': '%.1f',
                     'labelsize': 14, 'fontsize': 14},
            'v_n_x': v_n_x, 'v_n_y': v_n_y, 'v_n': v_n,
            'xlabel': v_n_x, "ylabel": v_n_y, 'label': eos,
            'xmin': 300, 'xmax': 900, 'ymin': 0.90, 'ymax': 2.1, 'vmin': 0.001, 'vmax': 0.40,
            'fill_vmin': False,  # fills the x < vmin with vmin
            'xscale': None, 'yscale': None,
            'cmap': 'inferno', 'norm': None, 'ms': mss, 'marker': marker, 'alpha': 0.7, "edgecolors": lks,
            'fancyticks': True,
            'minorticks': True,
            'title': {},
            'legend': {},
            'sharey': False,
            'sharex': True,  # removes angular citkscitks
            'fontsize': 14,
            'labelsize': 14
        }
        #
        if v_n.__contains__("Mdisk3D"):
            dic["vmin"], dic["vmax"] = 0.001, 0.40
        elif v_n.__contains__("Mej"):
            dic["vmin"], dic["vmax"] = 0.001, 0.02
            dic['norm'] = "log"
        elif v_n.__contains__("Ye"):
            dic['vmin'] = 0.1
            dic['vmax'] = 0.4
        elif v_n.__contains__("vel_inf"):
            dic['vmin'] = 0.10
            dic['vmax'] = 0.25
        #
        if eos == data.keys()[-1]:
            dic['legend'] = {'loc': 'upp'
                                    'er right', 'ncol': 3, 'fontsize': 10}
        o_plot.set_plot_dics.append(dic)

    # for sim in data.keys():
    #     eos_dic = {
    #         'task': 'text', 'ptype': 'cartesian',
    #         'position': (1, 1),
    #         'x': data[sim]['Lambda'], 'y': data[sim]['q'], 'text': data[sim]['eos'],
    #         'horizontalalignment': 'center',
    #         'color': 'black', 'fs': 11
    #     }
    #     o_plot.set_plot_dics.append(eos_dic)

    # disk_mass_dic = {
    #     'task': 'colormesh', 'ptype': 'cartesian', #'aspect': 1.,
    #     'xarr': lams2d, "yarr": qs2d, "zarr": dmasses2d,
    #     'position': (1, 1),  # 'title': '[{:.1f} ms]'.format(time_),
    #     'cbar': {'location': 'right .03 .0', 'label': Labels.labels("Mdisk3D"),  # 'fmt': '%.1f',
    #             'labelsize': 14, 'fontsize': 14},
    #     'v_n_x': 'x', 'v_n_y': 'z', 'v_n': "Mdisk3D",
    #     'xlabel': 'Lambda', "ylabel": "q",
    #     'xmin': 350, 'xmax': 860, 'ymin': 1.00, 'ymax': 1.6, 'vmin': 0.001, 'vmax': 0.40,
    #     'fill_vmin': False,  # fills the x < vmin with vmin
    #     'xscale': None, 'yscale': None,
    #     'mask': None, 'cmap': 'Greys', 'norm': "log",
    #     'fancyticks': True,
    #     'minorticks':True,
    #     'title': {},
    #     'sharey': False,
    #     'sharex': False,  # removes angular citkscitks
    #     'fontsize': 14,
    #     'labelsize': 14
    # }
    # o_plot.set_plot_dics.append(disk_mass_dic)
    o_plot.main()
    print("DONE")
    exit(1)


def plot_last_disk_mass_with_lambda2(v_n_x, v_n_y, v_n_col, mask_x=None, mask_y=None, mask_col=None, det=None,
                                     plot_legend=True):
    data = {"BLh": {}, "DD2": {}, "LS220": {}, "SFHo": {}, "SLy4": {}}
    for eos in simulations.keys():
        all_x_arr = []
        all_y_arr = []
        all_col_arr = []
        all_res_arr = []
        all_lk_arr = []
        all_bh_arr = []
        for q in simulations[eos].keys():
            data[eos][q] = {}
            #
            x_arr = []
            y_arr = []
            col_arr = []
            res_arr = []
            lk_arr = []
            bh_arr = []
            for sim in simulations[eos][q]:
                o_init = LOAD_INIT_DATA(sim)
                o_par = ADD_METHODS_ALL_PAR(sim)
                #
                if v_n_x in o_init.list_v_ns and mask_x == None:
                    x_arr.append(o_init.get_par(v_n_x))
                elif not v_n_x in o_init.list_v_ns and mask_x == None:
                    x_arr.append(o_par.get_par(v_n_x))
                elif not v_n_x in o_init.list_v_ns and mask_x != None:
                    x_arr.append(o_par.get_outflow_par(det, mask_x, v_n_x))
                else:
                    raise NameError("unrecognized: v_n_x:{} mask_x:{} det:{} combination"
                                    .format(v_n_x, mask_x, det))
                #
                if v_n_y in o_init.list_v_ns and mask_y == None:
                    y_arr.append(o_init.get_par(v_n_y))
                elif not v_n_y in o_init.list_v_ns and mask_y == None:
                    y_arr.append(o_par.get_par(v_n_y))
                elif not v_n_y in o_init.list_v_ns and mask_y != None:
                    y_arr.append(o_par.get_outflow_par(det, mask_y, v_n_y))
                else:
                    raise NameError("unrecognized: v_n_y:{} mask_x:{} det:{} combination"
                                    .format(v_n_y, mask_y, det))
                #
                if v_n_col in o_init.list_v_ns and mask_col == None:
                    col_arr.append(o_init.get_par(v_n_col))
                elif not v_n_col in o_init.list_v_ns and mask_col == None:
                    col_arr.append(o_par.get_par(v_n_col))
                elif not v_n_col in o_init.list_v_ns and mask_col != None:
                    col_arr.append(o_par.get_outflow_par(det, mask_col, v_n_col))
                else:
                    raise NameError("unrecognized: v_n_col:{} mask_x:{} det:{} combination"
                                    .format(v_n_col, mask_col, det))
                #
                res = o_init.get_par("res")
                if res == "HR": res_arr.append("v")
                if res == "SR": res_arr.append("d")
                if res == "LR": res_arr.append("^")
                #
                lk = o_init.get_par("vis")
                if lk == "LK":
                    lk_arr.append("gray")
                else:
                    lk_arr.append("none")
                tcoll = o_par.get_par("tcoll_gw")
                if not np.isinf(tcoll):
                    bh_arr.append("x")
                else:
                    bh_arr.append(None)

                #
            #
            data[eos][q][v_n_x] = x_arr
            data[eos][q][v_n_y] = y_arr
            data[eos][q][v_n_col] = col_arr
            data[eos][q]["res"] = res_arr
            data[eos][q]["vis"] = lk_arr
            data[eos][q]["tcoll"] = bh_arr
            #
            all_x_arr = all_x_arr + x_arr
            all_y_arr = all_y_arr + y_arr
            all_col_arr = all_col_arr + col_arr
            all_res_arr = all_res_arr + res_arr
            all_lk_arr = all_lk_arr + lk_arr
            all_bh_arr = all_bh_arr + bh_arr
        #
        data[eos][v_n_x + 's'] = all_x_arr
        data[eos][v_n_y + 's'] = all_y_arr
        data[eos][v_n_col + 's'] = all_col_arr
        data[eos]["res" + 's'] = all_res_arr
        data[eos]["vis" + 's'] = all_lk_arr
        data[eos]["tcoll" + 's'] = all_bh_arr
    #
    #
    figname = ''
    if mask_x == None:
        figname = figname + v_n_x + '_'
    else:
        figname = figname + v_n_x + '_' + mask_x + '_'
    if mask_y == None:
        figname = figname + v_n_y + '_'
    else:
        figname = figname + v_n_y + '_' + mask_y + '_'
    if mask_col == None:
        figname = figname + v_n_col + '_'
    else:
        figname = figname + v_n_col + '_' + mask_col + '_'
    if det == None:
        figname = figname + ''
    else:
        figname = figname + str(det)
    figname = figname + '.png'
    #
    o_plot = PLOT_MANY_TASKS()
    o_plot.gen_set["figdir"] = Paths.plots + "all2/"
    o_plot.gen_set["type"] = "cartesian"
    o_plot.gen_set["figsize"] = (4.2, 3.6)  # <->, |]
    o_plot.gen_set["figname"] = figname
    o_plot.gen_set["sharex"] = True
    o_plot.gen_set["sharey"] = False
    o_plot.gen_set["subplots_adjust_h"] = 0.0
    o_plot.gen_set["subplots_adjust_w"] = 0.0
    o_plot.set_plot_dics = []
    #

    #
    i_col = 1
    for eos in ["SLy4", "SFHo", "BLh", "LS220", "DD2"]:
        print(eos)

        # LEGEND

        if eos == "DD2" and plot_legend:
            for res in ["HR", "LR", "SR"]:
                marker_dic_lr = {
                    'task': 'line', 'ptype': 'cartesian',
                    'position': (1, i_col),
                    'xarr': [-1], "yarr": [-1],
                    'xlabel': None, "ylabel": None,
                    'label': res,
                    'marker': 'd', 'color': 'gray', 'ms': 8, 'alpha': 1.,
                    'sharey': False,
                    'sharex': False,  # removes angular citkscitks
                    'fontsize': 14,
                    'labelsize': 14
                }
                if res == "HR": marker_dic_lr['marker'] = "v"
                if res == "SR": marker_dic_lr['marker'] = "d"
                if res == "LR": marker_dic_lr['marker'] = "^"
                # if res == "BH": marker_dic_lr['marker'] = "x"
                if res == "SR":
                    marker_dic_lr['legend'] = {'loc': 'upper right', 'ncol': 1, 'fontsize': 12, 'shadow': False,
                                               'framealpha': 0.5, 'borderaxespad': 0.0}
                o_plot.set_plot_dics.append(marker_dic_lr)
        #
        xarr = np.array(data[eos][v_n_x + 's'])
        yarr = np.array(data[eos][v_n_y + 's'])
        colarr = data[eos][v_n_col + 's']
        marker = data[eos]["res" + 's']
        edgecolor = data[eos]["vis" + 's']
        bh_marker = data[eos]["tcoll" + 's']
        #
        if v_n_y == "Mej_tot":
            yarr = yarr * 1e2
        #
        #
        #
        dic_bh = {
            'task': 'scatter', 'ptype': 'cartesian',  # 'aspect': 1.,
            'xarr': xarr, "yarr": yarr, "zarr": colarr,
            'position': (1, i_col),  # 'title': '[{:.1f} ms]'.format(time_),
            'cbar': {},
            'v_n_x': v_n_x, 'v_n_y': v_n_y, 'v_n': v_n_col,
            'xlabel': None, "ylabel": None, 'label': eos,
            'xmin': 300, 'xmax': 900, 'ymin': 0.03, 'ymax': 0.3, 'vmin': 1.0, 'vmax': 1.5,
            'fill_vmin': False,  # fills the x < vmin with vmin
            'xscale': None, 'yscale': None,
            'cmap': 'viridis', 'norm': None, 'ms': 80, 'marker': bh_marker, 'alpha': 1.0, "edgecolors": edgecolor,
            'fancyticks': True,
            'minorticks': True,
            'title': {},
            'legend': {},
            'sharey': False,
            'sharex': False,  # removes angular citkscitks
            'fontsize': 14,
            'labelsize': 14
        }
        #
        if mask_y != None and mask_y.__contains__("bern"):
            o_plot.set_plot_dics.append(dic_bh)
        #

        #

        #
        print("marker: {}".format(marker))
        dic = {
            'task': 'scatter', 'ptype': 'cartesian',  # 'aspect': 1.,
            'xarr': xarr, "yarr": yarr, "zarr": colarr,
            'position': (1, i_col),  # 'title': '[{:.1f} ms]'.format(time_),
            'cbar': {},
            'v_n_x': v_n_x, 'v_n_y': v_n_y, 'v_n': v_n_col,
            'xlabel': None, "ylabel": Labels.labels(v_n_y),
            'xmin': 300, 'xmax': 900, 'ymin': 0.03, 'ymax': 0.3, 'vmin': 1.0, 'vmax': 1.8,
            'fill_vmin': False,  # fills the x < vmin with vmin
            'xscale': None, 'yscale': None,
            'cmap': 'viridis', 'norm': None, 'ms': 80, 'marker': marker, 'alpha': 0.8, "edgecolors": edgecolor,
            'tick_params': {"axis": 'both', "which": 'both', "labelleft": True,
                            "labelright": False,  # "tick1On":True, "tick2On":True,
                            "labelsize": 12,
                            "direction": 'in',
                            "bottom": True, "top": True, "left": True, "right": True},
            'yaxiscolor': {'bottom': 'black', 'top': 'black', 'right': 'black', 'left': 'black'},
            'minorticks': True,
            'title': {"text": eos, "fontsize": 12},
            'label': "xxx",
            'legend': {},
            'sharey': False,
            'sharex': False,  # removes angular citkscitks
            'fontsize': 14,
            'labelsize': 14
        }
        #
        if v_n_y == "Mdisk3Dmax":
            dic['ymin'], dic['ymax'] = 0.03, 0.30
        if v_n_y == "Mej_tot" and mask_y == "geo":
            dic['ymin'], dic['ymax'] = 0, 0.8
        if v_n_y == "Mej_tot" and mask_y == "bern_geoend":
            dic['ymin'], dic['ymax'] = 0, 3.2
        if v_n_y == "Ye_ave" and mask_y == "geo":
            dic['ymin'], dic['ymax'] = 0.1, 0.3
        if v_n_y == "Ye_ave" and mask_y == "bern_geoend":
            dic['ymin'], dic['ymax'] = 0.1, 0.4
        if v_n_y == "vel_inf_ave" and mask_y == "geo":
            dic['ymin'], dic['ymax'] = 0.1, 0.3
        if v_n_y == "vel_inf_ave" and mask_y == "bern_geoend":
            dic['ymin'], dic['ymax'] = 0.05, 0.25
        #
        if eos == "SLy4":
            dic['xmin'], dic['xmax'] = 380, 420
            dic['xticks'] = [400]
        if eos == "SFHo":
            dic['xmin'], dic['xmax'] = 400, 440
            dic['xticks'] = [420]
        if eos == "BLh":
            dic['xmin'], dic['xmax'] = 520, 550
            dic['xticks'] = [530]
        if eos == "LS220":
            dic['xmin'], dic['xmax'] = 690, 730
            dic['xticks'] = [710]
        if eos == "DD2":
            dic['xmin'], dic['xmax'] = 830, 855
            dic['xticks'] = [840]
        if eos == "SLy4":
            dic['tick_params']['right'] = False
            dic['yaxiscolor']["right"] = "lightgray"
        elif eos == "DD2":
            dic['tick_params']['left'] = False
            dic['yaxiscolor']["left"] = "lightgray"
        else:
            dic['tick_params']['left'] = False
            dic['tick_params']['right'] = False
            dic['yaxiscolor']["left"] = "lightgray"
            dic['yaxiscolor']["right"] = "lightgray"

        #
        # if eos != "SLy4" and eos != "DD2":
        #     dic['yaxiscolor'] = {'left':'lightgray','right':'lightgray', 'label': 'black'}
        #     dic['ytickcolor'] = {'left':'lightgray','right':'lightgray'}
        #     dic['yminortickcolor'] = {'left': 'lightgray', 'right': 'lightgray'}
        # elif eos == "DD2":
        #     dic['yaxiscolor'] = {'left': 'lightgray', 'right': 'black', 'label': 'black'}
        #     # dic['ytickcolor'] = {'left': 'lightgray'}
        #     # dic['yminortickcolor'] = {'left': 'lightgray'}
        # elif eos == "SLy4":
        #     dic['yaxiscolor'] = {'left': 'black', 'right': 'lightgray', 'label': 'black'}
        #     # dic['ytickcolor'] = {'right': 'lightgray'}
        #     # dic['yminortickcolor'] = {'right': 'lightgray'}

        #
        if eos != "SLy4":
            dic['sharey'] = True
        if eos == "BLh":
            dic['xlabel'] = Labels.labels(v_n_x)
        if eos == 'DD2':
            dic['cbar'] = {'location': 'right .03 .0', 'label': Labels.labels(v_n_col),  # 'fmt': '%.1f',
                           'labelsize': 14, 'fontsize': 14}
        #
        i_col = i_col + 1
        o_plot.set_plot_dics.append(dic)
        #

    #
    o_plot.main()
    # exit(0)


''' timecorr '''


def plot_ejecta_time_corr_properites():
    o_plot = PLOT_MANY_TASKS()
    o_plot.gen_set["figdir"] = Paths.plots + "all2/"
    o_plot.gen_set["type"] = "cartesian"
    o_plot.gen_set["figsize"] = (11.0, 3.6)  # <->, |]
    o_plot.gen_set["figname"] = "timecorrs_Ye_DD2_LS220_SLy_equalmass.png"
    o_plot.gen_set["sharex"] = False
    o_plot.gen_set["sharey"] = True
    o_plot.gen_set["dpi"] = 128
    o_plot.gen_set["subplots_adjust_h"] = 0.3
    o_plot.gen_set["subplots_adjust_w"] = 0.01
    o_plot.set_plot_dics = []

    det = 0

    sims = ["DD2_M13641364_M0_LK_SR_R04", "BLh_M13641364_M0_LK_SR", "LS220_M13641364_M0_LK_SR",
            "SLy4_M13641364_M0_LK_SR", "SFHo_M13641364_M0_LK_SR"]
    lbls = ["DD2_M13641364_M0_LK_SR_R04", "BLh_M13641364_M0_LK_SR", "LS220_M13641364_M0_LK_SR",
            "SLy4_M13641364_M0_LK_SR", "SFHo_M13641364_M0_LK_SR"]
    masks = ["bern_geoend", "bern_geoend", "bern_geoend", "bern_geoend", "bern_geoend"]
    # v_ns = ["vel_inf", "vel_inf", "vel_inf", "vel_inf", "vel_inf"]
    v_ns = ["Y_e", "Y_e", "Y_e", "Y_e", "Y_e"]

    i_x_plot = 1
    for sim, lbl, mask, v_n in zip(sims, lbls, masks, v_ns):

        fpath = Paths.ppr_sims + sim + "/" + "outflow_{}/".format(det) + mask + '/' + "timecorr_{}.h5".format(v_n)
        if not os.path.isfile(fpath):
            raise IOError("File does not exist: {}".format(fpath))

        dfile = h5py.File(fpath, "r")
        timearr = np.array(dfile["time"])
        v_n_arr = np.array(dfile[v_n])
        mass = np.array(dfile["mass"])

        corr_dic2 = {  # relies on the "get_res_corr(self, it, v_n): " method of data object
            'task': 'corr2d', 'dtype': 'corr', 'ptype': 'cartesian',
            'xarr': timearr, 'yarr': v_n_arr, 'zarr': mass,
            'position': (1, i_x_plot),
            'v_n_x': "time", 'v_n_y': v_n, 'v_n': 'mass', 'normalize': True,
            'cbar': {},
            'cmap': 'inferno',
            'xlabel': Labels.labels("time"), 'ylabel': Labels.labels(v_n),
            'xmin': timearr[0], 'xmax': timearr[-1], 'ymin': None, 'ymax': None, 'vmin': 1e-4, 'vmax': 1e-1,
            'xscale': "linear", 'yscale': "linear", 'norm': 'log',
            'mask_below': None, 'mask_above': None,
            'title': {},  # {"text": o_corr_data.sim.replace('_', '\_'), 'fontsize': 14},
            'text': {'text': lbl.replace('_', '\_'), 'coords': (0.05, 0.9), 'color': 'white', 'fs': 12},
            'fancyticks': True,
            'minorticks': True,
            'sharex': False,  # removes angular citkscitks
            'sharey': False,
            'fontsize': 14,
            'labelsize': 14
        }

        if i_x_plot > 1:
            corr_dic2['sharey'] = True
        # if i_x_plot == 1:
        #     corr_dic2['text'] = {'text': lbl.replace('_', '\_'), 'coords': (0.1, 0.9),  'color': 'white', 'fs': 14}
        if sim == sims[-1]:
            corr_dic2['cbar'] = {
                'location': 'right .03 .0', 'label': Labels.labels("mass"),  # 'fmt': '%.1f',
                'labelsize': 14, 'fontsize': 14}
        i_x_plot += 1
        corr_dic2 = Limits.in_dic(corr_dic2)
        o_plot.set_plot_dics.append(corr_dic2)

    o_plot.main()
    exit(1)


# plot_ejecta_time_corr_properites()

# def plot_total_fluxes_q1():
#
#     o_plot = PLOT_MANY_TASKS()
#     o_plot.gen_set["figdir"] = Paths.plots + "all2/"
#     o_plot.gen_set["type"] = "cartesian"
#     o_plot.gen_set["figsize"] = (9.0, 3.6)  # <->, |]
#     o_plot.gen_set["figname"] = "totfluxes_equalmasses.png"
#     o_plot.gen_set["sharex"] = False
#     o_plot.gen_set["sharey"] = True
#     o_plot.gen_set["dpi"] = 128
#     o_plot.gen_set["subplots_adjust_h"] = 0.3
#     o_plot.gen_set["subplots_adjust_w"] = 0.01
#     o_plot.set_plot_dics = []
#
#     det = 0
#
#     sims = ["DD2_M13641364_M0_LK_SR_R04", "BLh_M13641364_M0_LK_SR", "LS220_M13641364_M0_LK_SR", "SLy4_M13641364_M0_LK_SR", "SFHo_M13641364_M0_LK_SR"]
#     lbls = ["DD2", "BLh", "LS220", "SLy4", "SFHo"]
#     masks= ["bern_geoend", "bern_geoend", "bern_geoend", "bern_geoend", "bern_geoend"]
#     colors=["black", "gray", "red", "blue", "green"]
#     lss   =["-", "-", "-", "-", "-"]
#
#     i_x_plot = 1
#     for sim, lbl, mask, color, ls in zip(sims, lbls, masks, colors, lss):
#
#         fpath = Paths.ppr_sims + sim + "/" + "outflow_{}/".format(det) + mask + '/' + "total_flux.dat"
#         if not os.path.isfile(fpath):
#             raise IOError("File does not exist: {}".format(fpath))
#
#         timearr, massarr = np.loadtxt(fpath,usecols=(0,2),unpack=True)
#
#         plot_dic = {
#             'task': 'line', 'ptype': 'cartesian',
#             'position': (1, 1),
#             'xarr': timearr * 1e3, 'yarr': massarr * 1e2,
#             'v_n_x': "time", 'v_n_y': "mass",
#             'color': color, 'ls': ls, 'lw': 0.8, 'ds': 'default', 'alpha': 1.0,
#             'ymin': 0, 'ymax': 1.5, 'xmin': 15, 'xmax': 100,
#             'xlabel': Labels.labels("time"), 'ylabel': Labels.labels("ejmass"),
#             'label': lbl, 'yscale': 'linear',
#             'fancyticks': True, 'minorticks': True,
#             'fontsize': 14,
#             'labelsize': 14,
#             'legend': {}  # 'loc': 'best', 'ncol': 2, 'fontsize': 18
#         }
#         if sim == sims[-1]:
#             plot_dic['legend'] = {'loc': 'best', 'ncol': 1, 'fontsize': 14}
#
#         o_plot.set_plot_dics.append(plot_dic)
#
#         #
#         #
#
#
#         i_x_plot += 1
#     o_plot.main()
#     exit(1)
# plot_total_fluxes_q1()

# def plot_total_fluxes_qnot1():
#
#     o_plot = PLOT_MANY_TASKS()
#     o_plot.gen_set["figdir"] = Paths.plots + "all2/"
#     o_plot.gen_set["type"] = "cartesian"
#     o_plot.gen_set["figsize"] = (9.0, 3.6)  # <->, |]
#     o_plot.gen_set["figname"] = "totfluxes_unequalmasses.png"
#     o_plot.gen_set["sharex"] = False
#     o_plot.gen_set["sharey"] = True
#     o_plot.gen_set["dpi"] = 128
#     o_plot.gen_set["subplots_adjust_h"] = 0.3
#     o_plot.gen_set["subplots_adjust_w"] = 0.01
#     o_plot.set_plot_dics = []
#
#     det = 0
#
#     sims = ["DD2_M15091235_M0_LK_SR", "LS220_M14691268_M0_LK_SR", "SFHo_M14521283_M0_LK_SR"]
#     lbls = ["DD2 151 124", "LS220 150 127", "SFHo 145 128"]
#     masks= ["bern_geoend", "bern_geoend", "bern_geoend"]
#     colors=["black", "red", "green"]
#     lss   =["-", "-", "-"]
#
#     i_x_plot = 1
#     for sim, lbl, mask, color, ls in zip(sims, lbls, masks, colors, lss):
#
#         fpath = Paths.ppr_sims + sim + "/" + "outflow_{}/".format(det) + mask + '/' + "total_flux.dat"
#         if not os.path.isfile(fpath):
#             raise IOError("File does not exist: {}".format(fpath))
#
#         timearr, massarr = np.loadtxt(fpath,usecols=(0,2),unpack=True)
#
#         plot_dic = {
#             'task': 'line', 'ptype': 'cartesian',
#             'position': (1, 1),
#             'xarr': timearr * 1e3, 'yarr': massarr * 1e2,
#             'v_n_x': "time", 'v_n_y': "mass",
#             'color': color, 'ls': ls, 'lw': 0.8, 'ds': 'default', 'alpha': 1.0,
#             'ymin': 0, 'ymax': 3.0, 'xmin': 15, 'xmax': 100,
#             'xlabel': Labels.labels("time"), 'ylabel': Labels.labels("ejmass"),
#             'label': lbl, 'yscale': 'linear',
#             'fancyticks': True, 'minorticks': True,
#             'fontsize': 14,
#             'labelsize': 14,
#             'legend': {}  # 'loc': 'best', 'ncol': 2, 'fontsize': 18
#         }
#         if sim == sims[-1]:
#             plot_dic['legend'] = {'loc': 'best', 'ncol': 1, 'fontsize': 14}
#
#         o_plot.set_plot_dics.append(plot_dic)
#
#         #
#         #
#
#
#         i_x_plot += 1
#     o_plot.main()
#     exit(1)
# plot_total_fluxes_qnot1()

''' ejecta mass fluxes '''


def plot_total_fluxes_q1_and_qnot1(mask):
    o_plot = PLOT_MANY_TASKS()
    o_plot.gen_set["figdir"] = Paths.plots + "all2/"
    o_plot.gen_set["type"] = "cartesian"
    o_plot.gen_set["figsize"] = (4.2, 3.6)  # <->, |]
    o_plot.gen_set["figname"] = "totfluxes_{}.png".format(mask)
    o_plot.gen_set["sharex"] = False
    o_plot.gen_set["sharey"] = True
    o_plot.gen_set["dpi"] = 128
    o_plot.gen_set["subplots_adjust_h"] = 0.3
    o_plot.gen_set["subplots_adjust_w"] = 0.01
    o_plot.set_plot_dics = []

    det = 0

    # sims = ["DD2_M13641364_M0_LK_SR_R04", "BLh_M13641364_M0_LK_SR", "LS220_M13641364_M0_LK_SR", "SLy4_M13641364_M0_LK_SR", "SFHo_M13641364_M0_LK_SR"]
    # lbls = ["DD2", "BLh", "LS220", "SLy4", "SFHo"]
    # masks= [mask, mask, mask, mask, mask]
    # colors=["black", "gray", "red", "blue", "green"]
    # lss   =["-", "-", "-", "-", "-"]
    #
    # sims += ["DD2_M15091235_M0_LK_SR", "LS220_M14691268_M0_LK_SR", "SFHo_M14521283_M0_LK_SR"]
    # lbls += ["DD2 151 124", "LS220 150 127", "SFHo 145 128"]
    # masks+= [mask, mask, mask, mask, mask]
    # colors+=["black", "red", "green"]
    # lss   +=["--", "--", "--"]

    sims = ["DD2_M14971245_M0_SR", "DD2_M13641364_M0_SR", "DD2_M15091235_M0_LK_SR", "BLh_M13641364_M0_LK_SR",
            "LS220_M14691268_M0_LK_SR"]
    lbls = [r"DD2_M14971245_M0_SR".replace('_', '\_'), r"DD2_M13641364_M0_SR".replace('_', '\_'),
            r"DD2_M15091235_M0_LK_SR".replace('_', '\_'), r"BLh_M13641364_M0_LK_SR".replace('_', '\_'),
            r"LS220_M14691268_M0_LK_SR".replace('_', '\_')]
    masks = [mask, mask, mask, mask, mask]
    colors = ["blue", "green", "cyan", "black", "red"]
    lss = ["-", "-", "-", "-", '-']

    # sims += ["DD2_M15091235_M0_LK_SR", "LS220_M14691268_M0_LK_SR"]
    # lbls += ["DD2 151 124", "LS220 150 127"]
    # masks+= [mask, mask]
    # colors+=["blue", "red"]
    # lss   +=["--", "--"]

    i_x_plot = 1
    for sim, lbl, mask, color, ls in zip(sims, lbls, masks, colors, lss):

        fpath = Paths.ppr_sims + sim + "/" + "outflow_{}/".format(det) + mask + '/' + "total_flux.dat"
        if not os.path.isfile(fpath):
            raise IOError("File does not exist: {}".format(fpath))

        timearr, massarr = np.loadtxt(fpath, usecols=(0, 2), unpack=True)

        fpath = Paths.ppr_sims + sim + "/" + "waveforms/" + "tmerger.dat"
        if not os.path.isfile(fpath):
            raise IOError("File does not exist: {}".format(fpath))
        tmerg = np.float(np.loadtxt(fpath, unpack=True))
        timearr = timearr - (tmerg * Constants.time_constant * 1e-3)

        plot_dic = {
            'task': 'line', 'ptype': 'cartesian',
            'position': (1, 1),
            'xarr': timearr * 1e3, 'yarr': massarr * 1e4,
            'v_n_x': "time", 'v_n_y': "mass",
            'color': color, 'ls': ls, 'lw': 0.8, 'ds': 'default', 'alpha': 1.0,
            'xmin': 0, 'xmax': 110, 'ymin': 0, 'ymax': 2.5,
            'xlabel': Labels.labels("t-tmerg"), 'ylabel': Labels.labels("ejmass4"),
            'label': lbl, 'yscale': 'linear',
            'fancyticks': True, 'minorticks': True,
            'fontsize': 14,
            'labelsize': 14,
            'legend': {'loc': 'best', 'ncol': 1, 'fontsize': 11}  # 'loc': 'best', 'ncol': 2, 'fontsize': 18
        }
        if mask == "geo": plot_dic["ymax"] = 1.

        if sim >= sims[-1]:
            plot_dic['legend'] = {'loc': 'best', 'ncol': 1, 'fontsize': 12}

        o_plot.set_plot_dics.append(plot_dic)

        #
        #

        i_x_plot += 1
    o_plot.main()
    exit(1)


# plot_total_fluxes_q1_and_qnot1(mask="bern_geoend")
# plot_total_fluxes_q1_and_qnot1(mask="geo")

def plot_total_fluxes_lk_on_off(mask):
    o_plot = PLOT_MANY_TASKS()
    o_plot.gen_set["figdir"] = Paths.plots + "all2/"
    o_plot.gen_set["type"] = "cartesian"
    o_plot.gen_set["figsize"] = (9.0, 3.6)  # <->, |]
    o_plot.gen_set["figname"] = "totfluxes_lk_{}.png".format(mask)
    o_plot.gen_set["sharex"] = False
    o_plot.gen_set["sharey"] = True
    o_plot.gen_set["dpi"] = 128
    o_plot.gen_set["subplots_adjust_h"] = 0.3
    o_plot.gen_set["subplots_adjust_w"] = 0.01
    o_plot.set_plot_dics = []

    det = 0
    # plus LK
    sims = ["DD2_M13641364_M0_LK_SR_R04", "DD2_M15091235_M0_LK_SR", "LS220_M14691268_M0_LK_SR",
            "SFHo_M14521283_M0_LK_SR"]
    lbls = ["DD2 136 136 LK", "DD2 151 123 LK", "LS220 147 127 LK", "SFHo 145 128 LK"]
    masks = [mask, mask, mask, mask]
    colors = ["black", 'gray', 'red', "green"]
    lss = ["-", '-', '-', '-']
    # minus LK
    sims2 = ["DD2_M13641364_M0_SR_R04", "DD2_M14971245_M0_SR", "LS220_M14691268_M0_SR", "SFHo_M14521283_M0_SR"]
    lbls2 = ["DD2 136 136", "DD2 150 125", "LS220 147 127", "SFHo 145 128"]
    masks2 = [mask, mask, mask, mask]
    colors2 = ["black", 'gray', 'red', "green"]
    lss2 = ["--", '--', '--', '--']

    sims += sims2
    lbls += lbls2
    masks += masks2
    colors += colors2
    lss += lss2

    i_x_plot = 1
    for sim, lbl, mask, color, ls in zip(sims, lbls, masks, colors, lss):

        fpath = Paths.ppr_sims + sim + "/" + "outflow_{}/".format(det) + mask + '/' + "total_flux.dat"
        if not os.path.isfile(fpath):
            raise IOError("File does not exist: {}".format(fpath))

        timearr, massarr = np.loadtxt(fpath, usecols=(0, 2), unpack=True)

        fpath = Paths.ppr_sims + sim + "/" + "waveforms/" + "tmerger.dat"
        if not os.path.isfile(fpath):
            raise IOError("File does not exist: {}".format(fpath))
        tmerg = np.float(np.loadtxt(fpath, unpack=True))
        timearr = timearr - (tmerg * Constants.time_constant * 1e-3)

        plot_dic = {
            'task': 'line', 'ptype': 'cartesian',
            'position': (1, 1),
            'xarr': timearr * 1e3, 'yarr': massarr * 1e2,
            'v_n_x': "time", 'v_n_y': "mass",
            'color': color, 'ls': ls, 'lw': 0.8, 'ds': 'default', 'alpha': 1.0,
            'xmin': 0, 'xmax': 110, 'ymin': 0, 'ymax': 3.0,
            'xlabel': Labels.labels("t-tmerg"), 'ylabel': Labels.labels("ejmass"),
            'label': lbl, 'yscale': 'linear',
            'fancyticks': True, 'minorticks': True,
            'fontsize': 14,
            'labelsize': 14,
            'legend': {}  # 'loc': 'best', 'ncol': 2, 'fontsize': 18
        }
        if mask == "geo": plot_dic["ymax"] = 1.
        if sim == sims[-1]:
            plot_dic['legend'] = {'loc': 'best', 'ncol': 2, 'fontsize': 14}

        o_plot.set_plot_dics.append(plot_dic)

        #

        #

        i_x_plot += 1
    o_plot.main()

    errs = {}

    for sim1, mask1, sim2, mask2 in zip(sims, masks, sims2, masks2):

        errs[sim1] = {}

        print(" --------------| {} |---------------- ".format(sim1.split('_')[0]))

        # loading times
        fpath1 = Paths.ppr_sims + sim1 + "/" + "outflow_{}/".format(det) + mask1 + '/' + "total_flux.dat"
        if not os.path.isfile(fpath1):
            raise IOError("File does not exist: {}".format(fpath1))

        timearr1, massarr1 = np.loadtxt(fpath1, usecols=(0, 2), unpack=True)

        # loading tmerg
        fpath1 = Paths.ppr_sims + sim1 + "/" + "waveforms/" + "tmerger.dat"
        if not os.path.isfile(fpath1):
            raise IOError("File does not exist: {}".format(fpath1))
        tmerg1 = np.float(np.loadtxt(fpath1, unpack=True))
        timearr1 = timearr1 - (tmerg1 * Constants.time_constant * 1e-3)

        # loading times
        fpath2 = Paths.ppr_sims + sim2 + "/" + "outflow_{}/".format(det) + mask2 + '/' + "total_flux.dat"
        if not os.path.isfile(fpath2):
            raise IOError("File does not exist: {}".format(fpath2))

        timearr2, massarr2 = np.loadtxt(fpath2, usecols=(0, 2), unpack=True)

        # loading tmerg
        fpath2 = Paths.ppr_sims + sim2 + "/" + "waveforms/" + "tmerger.dat"
        if not os.path.isfile(fpath2):
            raise IOError("File does not exist: {}".format(fpath2))
        tmerg2 = np.float(np.loadtxt(fpath2, unpack=True))
        timearr2 = timearr2 - (tmerg2 * Constants.time_constant * 1e-3)

        # estimating tmax
        tmax = np.array([timearr1[-1], timearr2[-1]]).min()
        assert tmax <= timearr1.max()
        assert tmax <= timearr2.max()
        m1 = massarr1[UTILS.find_nearest_index(timearr1, tmax)]
        m2 = massarr2[UTILS.find_nearest_index(timearr2, tmax)]

        # print(" --------------| {} |---------------- ".format(sim1.split('_')[0]))
        print(" tmax:         {:.1f} [ms]".format(tmax * 1e3))
        # print(" \n")
        print(" sim1:         {} ".format(sim1))
        print(" timearr1[-1]: {:.1f} [ms]".format(timearr1[-1] * 1e3))
        print(" mass1[-1]     {:.2f} [1e-2Msun]".format(massarr1[-1] * 1e2))
        print(" m1[tmax]      {:.2f} [1e-2Msun]".format(m1 * 1e2))
        # print(" \n")
        print(" sim1:         {} ".format(sim2))
        print(" timearr1[-1]: {:.1f} [ms]".format(timearr2[-1] * 1e3))
        print(" mass1[-1]     {:.2f} [1e-2Msun]".format(massarr2[-1] * 1e2))
        print(" m2[tmax]      {:.2f} [1e-2Msun]".format(m2 * 1e2))
        # print(" \n")
        print(" abs(m1-m2)/m1 {:.1f} [%]".format(100 * np.abs(m1 - m2) / m1))
        print(" ---------------------------------------- ")

        errs[sim1]["sim1"] = sim1
        errs[sim1]["sim2"] = sim2
        errs[sim1]["tmax"] = tmax * 1e3
        errs[sim1]["m1"] = m1 * 1e2
        errs[sim1]["m2"] = m2 * 1e2
        errs[sim1]["err"] = 100 * np.abs(m1 - m2) / m1

    # table

    # sims = ['DD2_M13641364_M0_SR', 'LS220_M13641364_M0_SR', 'SLy4_M13641364_M0_SR']
    # v_ns = ["EOS", "M1", "M2", 'Mdisk3D', 'Mej', 'Yeej', 'vej', 'Mej_bern', 'Yeej_bern', 'vej_bern']
    # precs = ["str", "1.2", "1.2", ".4", ".4", ".4", ".4", ".4", ".4", ".4"]

    print('\n')

    cols = ["sim1", "sim2", "m1", "m2", "tmax", "err"]
    units_dic = {"sim1": "", "sim2": "", "m1": "$[10^{-2} M_{\odot}]$", "m2": "$[10^{-2} M_{\odot}]$", "tmax": "[ms]",
                 "err": r"[\%]"}
    lbl_dic = {"sim1": "Default Run", "sim2": "Comparison Run", "m1": r"$M_{\text{ej}}^a$", "m2": r"$M_{\text{ej}}^b$",
               "tmax": r"$t_{\text{max}}$", "err": r"$\Delta$"}
    precs = ["", "", ".2f", ".2f", ".1f", "d"]

    size = '{'
    head = ''
    for i, v_n in enumerate(cols):
        v_n = lbl_dic[v_n]
        size = size + 'c'
        head = head + '{}'.format(v_n)
        if v_n != cols[-1]: size = size + ' '
        if i != len(cols) - 1: head = head + ' & '
    size = size + '}'

    unit_bar = ''
    for v_n in cols:
        if v_n in units_dic.keys():
            unit = units_dic[v_n]
        else:
            unit = v_n
        unit_bar = unit_bar + '{}'.format(unit)
        if v_n != cols[-1]: unit_bar = unit_bar + ' & '

    head = head + ' \\\\'  # = \\
    unit_bar = unit_bar + ' \\\\ '

    print(errs[sims[0]])

    print('\n')

    print('\\begin{table*}[t]')
    print('\\begin{center}')
    print('\\begin{tabular}' + '{}'.format(size))
    print('\\hline')
    print(head)
    print(unit_bar)
    print('\\hline\\hline')

    for sim1, mask1, sim2, mask2 in zip(sims, masks, sims2, masks2):
        row = ''
        for v_n, prec in zip(cols, precs):

            if prec != "":
                val = "%{}".format(prec) % errs[sim1][v_n]
            else:
                val = errs[sim1][v_n].replace("_", "\_")
            row = row + val
            if v_n != cols[-1]: row = row + ' & '
        row = row + ' \\\\'  # = \\
        print(row)

    print(r'\hline')
    print(r'\end{tabular}')
    print(r'\end{center}')
    print(r'\caption{' + r'Viscosity effect on the ejected material total cumulative mass. Criterion {} '
          .format(mask.replace('_', '\_')) +
          r'$\Delta = |M_{\text{ej}}^a - M_{\text{ej}}^b| / M_{\text{ej}}^a |_{tmax} $ }')
    print(r'\label{tbl:1}')
    print(r'\end{table*}')

    exit(1)


# plot_total_fluxes_lk_on_off(mask="bern_geoend")
# plot_total_fluxes_lk_on_off("geo")

def plot_total_fluxes_lk_on_resolution(mask):
    o_plot = PLOT_MANY_TASKS()
    o_plot.gen_set["figdir"] = Paths.plots + "all2/"
    o_plot.gen_set["type"] = "cartesian"
    o_plot.gen_set["figsize"] = (9.0, 3.6)  # <->, |]
    o_plot.gen_set["figname"] = "totfluxes_lk_res_{}.png".format(mask)
    o_plot.gen_set["sharex"] = False
    o_plot.gen_set["sharey"] = True
    o_plot.gen_set["dpi"] = 128
    o_plot.gen_set["subplots_adjust_h"] = 0.3
    o_plot.gen_set["subplots_adjust_w"] = 0.01
    o_plot.set_plot_dics = []

    det = 0
    # HR # LS220_M13641364_M0_LK_HR
    sims_hr = ["DD2_M13641364_M0_LK_HR_R04", "DD2_M15091235_M0_LK_HR", "", "LS220_M14691268_M0_LK_HR",
               "SFHo_M13641364_M0_LK_HR", "SFHo_M14521283_M0_LK_HR"]
    lbl_hr = ["DD2 136 136 HR", "DD2 151 124 HR", "LS220 136 136 HR", "LS220 147 137 HR", "SFHo 136 136 HR",
              "SFHo 145 128 HR"]
    color_hr = ["black", "gray", "orange", "red", "green", "lightgreen"]
    masks_hr = [mask, mask, mask, mask, mask, mask]
    lss_hr = ['--', '--', '--', '--', "--", "--"]
    # SR
    sims_sr = ["DD2_M13641364_M0_LK_SR_R04", "DD2_M15091235_M0_LK_SR", "LS220_M13641364_M0_LK_SR",
               "LS220_M14691268_M0_LK_SR", "SFHo_M13641364_M0_LK_SR", "SFHo_M14521283_M0_LK_SR"]
    lbl_sr = ["DD2 136 136 SR", "DD2 151 124 HR", "LS220 136 136 SR", "LS220 147 137 SR", "SFHo 136 136 HR",
              "SFHo 145 128 HR"]
    color_sr = ["black", "gray", "orange", "red", "green", "lightgreen"]
    masks_sr = [mask, mask, mask, mask, mask, mask]
    lss_sr = ['-', '-', '-', '-', '-', '-']
    # LR
    sims_lr = ["DD2_M13641364_M0_LK_LR_R04", "", "", "", "", ""]
    lbl_lr = ["DD2 136 136 LR", "DD2 151 124 LR", "LS220 136 136 LR", "LS220 147 137 LR", "SFHo 136 136 LR",
              "SFHo 145 128 LR"]
    color_lr = ["black", "gray", "orange", "red", "green", "lightgreen"]
    masks_lr = [mask, mask, mask, mask, mask, mask]
    lss_lr = [':', ':', ":", ":", ":", ":"]

    # plus
    sims = sims_hr + sims_lr + sims_sr
    lsls = lbl_hr + lbl_lr + lbl_sr
    colors = color_hr + color_lr + color_sr
    masks = masks_hr + masks_lr + masks_sr
    lss = lss_hr + lss_lr + lss_sr

    i_x_plot = 1
    for sim, lbl, mask, color, ls in zip(sims, lsls, masks, colors, lss):

        if sim != "":
            fpath = Paths.ppr_sims + sim + "/" + "outflow_{}/".format(det) + mask + '/' + "total_flux.dat"
            if not os.path.isfile(fpath):
                raise IOError("File does not exist: {}".format(fpath))

            timearr, massarr = np.loadtxt(fpath, usecols=(0, 2), unpack=True)

            fpath = Paths.ppr_sims + sim + "/" + "waveforms/" + "tmerger.dat"
            if not os.path.isfile(fpath):
                raise IOError("File does not exist: {}".format(fpath))
            tmerg = np.float(np.loadtxt(fpath, unpack=True))
            timearr = timearr - (tmerg * Constants.time_constant * 1e-3)

            plot_dic = {
                'task': 'line', 'ptype': 'cartesian',
                'position': (1, 1),
                'xarr': timearr * 1e3, 'yarr': massarr * 1e2,
                'v_n_x': "time", 'v_n_y': "mass",
                'color': color, 'ls': ls, 'lw': 0.8, 'ds': 'default', 'alpha': 1.0,
                'xmin': 0, 'xmax': 110, 'ymin': 0, 'ymax': 3.0,
                'xlabel': Labels.labels("t-tmerg"), 'ylabel': Labels.labels("ejmass"),
                'label': lbl, 'yscale': 'linear',
                'fancyticks': True, 'minorticks': True,
                'fontsize': 14,
                'labelsize': 14,
                'legend': {}  # 'loc': 'best', 'ncol': 2, 'fontsize': 18
            }
            if mask == "geo": plot_dic["ymax"] = 1.
            # print(sim, sims[-1])
            if sim == sims[-1]:
                plot_dic['legend'] = {'loc': 'best', 'ncol': 2, 'fontsize': 12}

            o_plot.set_plot_dics.append(plot_dic)

            i_x_plot += 1
    o_plot.main()

    for sim_hr, sim_sr, sim_lr, mask_hr, mask_sr, mask_lr in \
            zip(sims_hr, sims_sr, sims_lr, masks_hr, masks_sr, masks_lr):

        def_sim = sim_sr
        def_mask = mask_sr
        def_res = "SR"

        if sims_hr != "":
            comp_res = "HR"
            comp_sim = sim_hr
            comp_mask = mask_hr
        elif sims_lr != "":
            comp_res = "LR"
            comp_sim = sim_lr
            comp_mask = mask_lr
        else:
            raise ValueError("neither HR nor LR is available")

        # loading times
        fpath1 = Paths.ppr_sims + def_sim + "/" + "outflow_{}/".format(det) + def_mask + '/' + "total_flux.dat"
        if not os.path.isfile(fpath1):
            raise IOError("File does not exist: {}".format(fpath1))

        timearr1, massarr1 = np.loadtxt(fpath1, usecols=(0, 2), unpack=True)

        # loading tmerg
        fpath1 = Paths.ppr_sims + def_sim + "/" + "waveforms/" + "tmerger.dat"
        if not os.path.isfile(fpath1):
            raise IOError("File does not exist: {}".format(fpath1))
        tmerg1 = np.float(np.loadtxt(fpath1, unpack=True))
        timearr1 = timearr1 - (tmerg1 * Constants.time_constant * 1e-3)

        # loading times
        fpath2 = Paths.ppr_sims + comp_sim + "/" + "outflow_{}/".format(det) + comp_mask + '/' + "total_flux.dat"
        if not os.path.isfile(fpath2):
            raise IOError("File does not exist: {}".format(fpath2))

        timearr2, massarr2 = np.loadtxt(fpath2, usecols=(0, 2), unpack=True)

        # loading tmerg
        fpath2 = Paths.ppr_sims + comp_sim + "/" + "waveforms/" + "tmerger.dat"
        if not os.path.isfile(fpath2):
            raise IOError("File does not exist: {}".format(fpath2))
        tmerg2 = np.float(np.loadtxt(fpath2, unpack=True))
        timearr2 = timearr2 - (tmerg2 * Constants.time_constant * 1e-3)

        # estimating tmax
        tmax = np.array([timearr1[-1], timearr2[-1]]).min()
        assert tmax <= timearr1.max()
        assert tmax <= timearr2.max()
        m1 = massarr1[UTILS.find_nearest_index(timearr1, tmax)]
        m2 = massarr2[UTILS.find_nearest_index(timearr2, tmax)]

        # print(" --------------| {} |---------------- ".format(sim1.split('_')[0]))
        print(" tmax:         {:.1f} [ms]".format(tmax * 1e3))
        # print(" \n")
        print(" Resolution:   {} ".format(def_res))
        print(" sim1:         {} ".format(def_sim))
        print(" timearr1[-1]: {:.1f} [ms]".format(timearr1[-1] * 1e3))
        print(" mass1[-1]     {:.2f} [1e-2Msun]".format(massarr1[-1] * 1e2))
        print(" m1[tmax]      {:.2f} [1e-2Msun]".format(m1 * 1e2))
        # print(" \n")
        print("\nResolution:   {} ".format(comp_res))
        print(" sim1:         {} ".format(comp_sim))
        print(" timearr1[-1]: {:.1f} [ms]".format(timearr2[-1] * 1e3))
        print(" mass1[-1]     {:.2f} [1e-2Msun]".format(massarr2[-1] * 1e2))
        print(" m2[tmax]      {:.2f} [1e-2Msun]".format(m2 * 1e2))
        # print(" \n")
        print(" abs(m1-m2)/m1 {:.1f} [%]".format(100 * np.abs(m1 - m2) / m1))
        print(" ---------------------------------------- ")

    #
    #     print(" --------------| {} |---------------- ".format(sim1.split('_')[0]))
    #
    #     # loading times
    #     fpath1 = Paths.ppr_sims + sim1 + "/" + "outflow_{}/".format(det) + mask1 + '/' + "total_flux.dat"
    #     if not os.path.isfile(fpath1):
    #         raise IOError("File does not exist: {}".format(fpath1))
    #
    #     timearr1, massarr1 = np.loadtxt(fpath1, usecols=(0, 2), unpack=True)
    #
    #     # loading tmerg
    #     fpath1 = Paths.ppr_sims + sim1 + "/" + "waveforms/" + "tmerger.dat"
    #     if not os.path.isfile(fpath1):
    #         raise IOError("File does not exist: {}".format(fpath1))
    #     tmerg1 = np.float(np.loadtxt(fpath1, unpack=True))
    #     timearr1 = timearr1 - (tmerg1 * Constants.time_constant * 1e-3)
    #
    #     # loading times
    #     fpath2 = Paths.ppr_sims + sim2 + "/" + "outflow_{}/".format(det) + mask2 + '/' + "total_flux.dat"
    #     if not os.path.isfile(fpath2):
    #         raise IOError("File does not exist: {}".format(fpath2))
    #
    #     timearr2, massarr2 = np.loadtxt(fpath2, usecols=(0, 2), unpack=True)
    #
    #     # loading tmerg
    #     fpath2 = Paths.ppr_sims + sim2 + "/" + "waveforms/" + "tmerger.dat"
    #     if not os.path.isfile(fpath2):
    #         raise IOError("File does not exist: {}".format(fpath2))
    #     tmerg2 = np.float(np.loadtxt(fpath2, unpack=True))
    #     timearr2 = timearr2 - (tmerg2 * Constants.time_constant * 1e-3)
    #
    #     # estimating tmax
    #     tmax = np.array([timearr1[-1], timearr2[-1]]).min()
    #     assert tmax <= timearr1.max()
    #     assert tmax <= timearr2.max()
    #     m1 = massarr1[UTILS.find_nearest_index(timearr1, tmax)]
    #     m2 = massarr2[UTILS.find_nearest_index(timearr2, tmax)]
    #
    #     # print(" --------------| {} |---------------- ".format(sim1.split('_')[0]))
    #     print(" tmax:         {:.1f} [ms]".format(tmax*1e3))
    #     # print(" \n")
    #     print(" sim1:         {} ".format(sim1))
    #     print(" timearr1[-1]: {:.1f} [ms]".format(timearr1[-1]*1e3))
    #     print(" mass1[-1]     {:.2f} [1e-2Msun]".format(massarr1[-1]*1e2))
    #     print(" m1[tmax]      {:.2f} [1e-2Msun]".format(m1 * 1e2))
    #     # print(" \n")
    #     print(" sim1:         {} ".format(sim2))
    #     print(" timearr1[-1]: {:.1f} [ms]".format(timearr2[-1]*1e3))
    #     print(" mass1[-1]     {:.2f} [1e-2Msun]".format(massarr2[-1]*1e2))
    #     print(" m2[tmax]      {:.2f} [1e-2Msun]".format(m2 * 1e2))
    #     # print(" \n")
    #     print(" abs(m1-m2)/m1 {:.1f} [%]".format(100 * np.abs(m1 - m2) / m1))
    #     print(" ---------------------------------------- ")

    exit(1)


# plot_total_fluxes_lk_on_resolution(mask="geo_geoend")
# plot_total_fluxes_lk_on_resolution(mask="geo")

def plot_total_fluxes_lk_off_resolution(mask):
    o_plot = PLOT_MANY_TASKS()
    o_plot.gen_set["figdir"] = Paths.plots + "all2/"
    o_plot.gen_set["type"] = "cartesian"
    o_plot.gen_set["figsize"] = (9.0, 3.6)  # <->, |]
    o_plot.gen_set["figname"] = "totfluxes_res_{}.png".format(mask)
    o_plot.gen_set["sharex"] = False
    o_plot.gen_set["sharey"] = True
    o_plot.gen_set["dpi"] = 128
    o_plot.gen_set["subplots_adjust_h"] = 0.3
    o_plot.gen_set["subplots_adjust_w"] = 0.01
    o_plot.set_plot_dics = []

    det = 0
    # HR    "DD2_M13641364_M0_HR_R04"
    sims_hr = ["", "DD2_M14971245_M0_HR", "LS220_M13641364_M0_HR", "LS220_M14691268_M0_HR", "SFHo_M13641364_M0_HR",
               "SFHo_M14521283_M0_HR"]
    lbl_hr = ["DD2 136 136 HR", "DD2 150 125 HR", "LS220 136 136 HR", "LS220 147 127 HR", "SFHo 136 136 HR",
              "SFHo 145 128 HR"]
    color_hr = ["black", "gray", "orange", "red", "lightgreen", "green"]
    masks_hr = [mask, mask, mask, mask, mask, mask]
    lss_hr = ['--', '--', '--', '--', '--', '--']
    # SR
    sims_sr = ["DD2_M13641364_M0_SR_R04", "DD2_M14971245_M0_SR", "LS220_M13641364_M0_SR", "LS220_M14691268_M0_SR",
               "SFHo_M13641364_M0_SR", "SFHo_M14521283_M0_SR"]
    lbl_sr = ["DD2 136 136 SR", "DD2 150 125 SR", "LS220 136 136 SR", "LS220 147 127 SR", "SFHo 136 136 SR",
              "SFHo 145 128 SR"]
    color_sr = ["black", "gray", "orange", "red", "lightgreen", "green"]
    masks_sr = [mask, mask, mask, mask, mask, mask]
    lss_sr = ['-', '-', '-', '-', '-', '-']
    # LR
    sims_lr = ["DD2_M13641364_M0_LR_R04", "DD2_M14971246_M0_LR", "LS220_M13641364_M0_LR", "LS220_M14691268_M0_LR", "",
               ""]
    lbl_lr = ["DD2 136 136 LR", "DD2 150 125 LR", "LS220 136 136 LR", "LS220 147 127 LR", "SFHo 136 136 LR",
              "SFHo 145 128 LR"]
    color_lr = ["black", "gray", "orange", "red", "lightgreen", "green"]
    masks_lr = [mask, mask, mask, mask, mask, mask]
    lss_lr = [':', ':', ':', ':', ':', ':']

    # plus
    sims = sims_hr + sims_lr + sims_sr
    lsls = lbl_hr + lbl_lr + lbl_sr
    colors = color_hr + color_lr + color_sr
    masks = masks_hr + masks_lr + masks_sr
    lss = lss_hr + lss_lr + lss_sr

    i_x_plot = 1
    for sim, lbl, mask, color, ls in zip(sims, lsls, masks, colors, lss):

        if sim != "":
            fpath = Paths.ppr_sims + sim + "/" + "outflow_{}/".format(det) + mask + '/' + "total_flux.dat"
            if not os.path.isfile(fpath):
                raise IOError("File does not exist: {}".format(fpath))

            timearr, massarr = np.loadtxt(fpath, usecols=(0, 2), unpack=True)

            fpath = Paths.ppr_sims + sim + "/" + "waveforms/" + "tmerger.dat"
            if not os.path.isfile(fpath):
                raise IOError("File does not exist: {}".format(fpath))
            tmerg = np.float(np.loadtxt(fpath, unpack=True))
            timearr = timearr - (tmerg * Constants.time_constant * 1e-3)

            plot_dic = {
                'task': 'line', 'ptype': 'cartesian',
                'position': (1, 1),
                'xarr': timearr * 1e3, 'yarr': massarr * 1e2,
                'v_n_x': "time", 'v_n_y': "mass",
                'color': color, 'ls': ls, 'lw': 0.8, 'ds': 'default', 'alpha': 1.0,
                'xmin': 0, 'xmax': 110, 'ymin': 0, 'ymax': 3.0,
                'xlabel': Labels.labels("t-tmerg"), 'ylabel': Labels.labels("ejmass"),
                'label': lbl, 'yscale': 'linear',
                'fancyticks': True, 'minorticks': True,
                'fontsize': 14,
                'labelsize': 14,
                'legend': {}  # 'loc': 'best', 'ncol': 2, 'fontsize': 18
            }
            # print(sim, sims[-1])
            if mask == "geo": plot_dic["ymax"] = 1.
            if sim == sims[-1]:
                plot_dic['legend'] = {'loc': 'best', 'ncol': 3, 'fontsize': 12}

            o_plot.set_plot_dics.append(plot_dic)

            i_x_plot += 1
    o_plot.main()

    for sim_hr, sim_sr, sim_lr, mask_hr, mask_sr, mask_lr in \
            zip(sims_hr, sims_sr, sims_lr, masks_hr, masks_sr, masks_lr):

        def_sim = sim_sr
        def_mask = mask_sr
        def_res = "SR"

        if sim_hr != "":
            comp_res = "HR"
            comp_sim = sim_hr
            comp_mask = mask_hr
        elif sim_lr != "":
            comp_res = "LR"
            comp_sim = sim_lr
            comp_mask = mask_lr
        else:
            raise ValueError("neither HR nor LR is available")

        assert comp_sim != ""

        # loading times
        fpath1 = Paths.ppr_sims + def_sim + "/" + "outflow_{}/".format(det) + def_mask + '/' + "total_flux.dat"
        if not os.path.isfile(fpath1):
            raise IOError("File does not exist: {}".format(fpath1))

        timearr1, massarr1 = np.loadtxt(fpath1, usecols=(0, 2), unpack=True)

        # loading tmerg
        fpath1 = Paths.ppr_sims + def_sim + "/" + "waveforms/" + "tmerger.dat"
        if not os.path.isfile(fpath1):
            raise IOError("File does not exist: {}".format(fpath1))
        tmerg1 = np.float(np.loadtxt(fpath1, unpack=True))
        timearr1 = timearr1 - (tmerg1 * Constants.time_constant * 1e-3)

        # loading times
        fpath2 = Paths.ppr_sims + comp_sim + "/" + "outflow_{}/".format(det) + comp_mask + '/' + "total_flux.dat"
        if not os.path.isfile(fpath2):
            raise IOError("File does not exist: {}".format(fpath2))

        timearr2, massarr2 = np.loadtxt(fpath2, usecols=(0, 2), unpack=True)

        # loading tmerg
        fpath2 = Paths.ppr_sims + comp_sim + "/" + "waveforms/" + "tmerger.dat"
        if not os.path.isfile(fpath2):
            raise IOError("File does not exist: {}".format(fpath2))
        tmerg2 = np.float(np.loadtxt(fpath2, unpack=True))
        timearr2 = timearr2 - (tmerg2 * Constants.time_constant * 1e-3)

        # estimating tmax
        tmax = np.array([timearr1[-1], timearr2[-1]]).min()
        assert tmax <= timearr1.max()
        assert tmax <= timearr2.max()
        m1 = massarr1[UTILS.find_nearest_index(timearr1, tmax)]
        m2 = massarr2[UTILS.find_nearest_index(timearr2, tmax)]

        # print(" --------------| {} |---------------- ".format(sim1.split('_')[0]))
        print(" tmax:         {:.1f} [ms]".format(tmax * 1e3))
        # print(" \n")
        print(" Resolution:   {} ".format(def_res))
        print(" sim1:         {} ".format(def_sim))
        print(" timearr1[-1]: {:.1f} [ms]".format(timearr1[-1] * 1e3))
        print(" mass1[-1]     {:.2f} [1e-2Msun]".format(massarr1[-1] * 1e2))
        print(" m1[tmax]      {:.2f} [1e-2Msun]".format(m1 * 1e2))
        # print(" \n")
        print("\nResolution: {} ".format(comp_res))
        print(" sim1:         {} ".format(comp_sim))
        print(" timearr1[-1]: {:.1f} [ms]".format(timearr2[-1] * 1e3))
        print(" mass1[-1]     {:.2f} [1e-2Msun]".format(massarr2[-1] * 1e2))
        print(" m2[tmax]      {:.2f} [1e-2Msun]".format(m2 * 1e2))
        # print(" \n")
        print(" abs(m1-m2)/m1 {:.1f} [%]".format(100 * np.abs(m1 - m2) / m1))
        print(" ---------------------------------------- ")

    #
    #     print(" --------------| {} |---------------- ".format(sim1.split('_')[0]))
    #
    #     # loading times
    #     fpath1 = Paths.ppr_sims + sim1 + "/" + "outflow_{}/".format(det) + mask1 + '/' + "total_flux.dat"
    #     if not os.path.isfile(fpath1):
    #         raise IOError("File does not exist: {}".format(fpath1))
    #
    #     timearr1, massarr1 = np.loadtxt(fpath1, usecols=(0, 2), unpack=True)
    #
    #     # loading tmerg
    #     fpath1 = Paths.ppr_sims + sim1 + "/" + "waveforms/" + "tmerger.dat"
    #     if not os.path.isfile(fpath1):
    #         raise IOError("File does not exist: {}".format(fpath1))
    #     tmerg1 = np.float(np.loadtxt(fpath1, unpack=True))
    #     timearr1 = timearr1 - (tmerg1 * Constants.time_constant * 1e-3)
    #
    #     # loading times
    #     fpath2 = Paths.ppr_sims + sim2 + "/" + "outflow_{}/".format(det) + mask2 + '/' + "total_flux.dat"
    #     if not os.path.isfile(fpath2):
    #         raise IOError("File does not exist: {}".format(fpath2))
    #
    #     timearr2, massarr2 = np.loadtxt(fpath2, usecols=(0, 2), unpack=True)
    #
    #     # loading tmerg
    #     fpath2 = Paths.ppr_sims + sim2 + "/" + "waveforms/" + "tmerger.dat"
    #     if not os.path.isfile(fpath2):
    #         raise IOError("File does not exist: {}".format(fpath2))
    #     tmerg2 = np.float(np.loadtxt(fpath2, unpack=True))
    #     timearr2 = timearr2 - (tmerg2 * Constants.time_constant * 1e-3)
    #
    #     # estimating tmax
    #     tmax = np.array([timearr1[-1], timearr2[-1]]).min()
    #     assert tmax <= timearr1.max()
    #     assert tmax <= timearr2.max()
    #     m1 = massarr1[UTILS.find_nearest_index(timearr1, tmax)]
    #     m2 = massarr2[UTILS.find_nearest_index(timearr2, tmax)]
    #
    #     # print(" --------------| {} |---------------- ".format(sim1.split('_')[0]))
    #     print(" tmax:         {:.1f} [ms]".format(tmax*1e3))
    #     # print(" \n")
    #     print(" sim1:         {} ".format(sim1))
    #     print(" timearr1[-1]: {:.1f} [ms]".format(timearr1[-1]*1e3))
    #     print(" mass1[-1]     {:.2f} [1e-2Msun]".format(massarr1[-1]*1e2))
    #     print(" m1[tmax]      {:.2f} [1e-2Msun]".format(m1 * 1e2))
    #     # print(" \n")
    #     print(" sim1:         {} ".format(sim2))
    #     print(" timearr1[-1]: {:.1f} [ms]".format(timearr2[-1]*1e3))
    #     print(" mass1[-1]     {:.2f} [1e-2Msun]".format(massarr2[-1]*1e2))
    #     print(" m2[tmax]      {:.2f} [1e-2Msun]".format(m2 * 1e2))
    #     # print(" \n")
    #     print(" abs(m1-m2)/m1 {:.1f} [%]".format(100 * np.abs(m1 - m2) / m1))
    #     print(" ---------------------------------------- ")

    exit(1)


# plot_total_fluxes_lk_off_resolution(mask="bern_geoend")
# plot_total_fluxes_lk_off_resolution(mask="geo")

''' ejecta 1D histograms '''


def plot_histograms_ejecta(mask, mask2):
    o_plot = PLOT_MANY_TASKS()
    o_plot.gen_set["figdir"] = Paths.plots + "all2/"
    o_plot.gen_set["type"] = "cartesian"
    o_plot.gen_set["figsize"] = (16.2, 3.6)  # <->, |]
    o_plot.gen_set["figname"] = "hists_for_all_nucleo_{}.png".format(mask)
    o_plot.gen_set["sharex"] = False
    o_plot.gen_set["sharey"] = True
    o_plot.gen_set["dpi"] = 128
    o_plot.gen_set["subplots_adjust_h"] = 0.3
    o_plot.gen_set["subplots_adjust_w"] = 0.0
    o_plot.set_plot_dics = []
    averages = {}

    det = 0

    sims = ["DD2_M14971245_M0_SR", "DD2_M13641364_M0_SR", "DD2_M15091235_M0_LK_SR", "BLh_M13641364_M0_LK_SR",
            "LS220_M14691268_M0_LK_SR"]
    lbls = [sim.replace('_', '\_') for sim in sims]
    masks = [mask, mask, mask, mask, mask]
    colors = ["blue", "cyan", "green", "black", "red"]
    lss = ["-", "-", "-", "-", "-"]
    lws = [1., 1., 1., 1., 1.]

    # sims = ["DD2_M13641364_M0_LK_SR_R04", "BLh_M13641364_M0_LK_SR", "LS220_M13641364_M0_LK_SR",
    #         "SLy4_M13641364_M0_LK_SR", "SFHo_M13641364_M0_LK_SR"]
    # lbls = ["DD2", "BLh", "LS220", "SLy4", "SFHo"]
    # masks = [mask, mask, mask, mask, mask]
    # colors = ["black", "gray", "red", "blue", "green"]
    # lss = ["-", "-", "-", "-", "-"]
    # lws = [1., 1., 1., 1., 1.]
    #
    # sims += ["DD2_M15091235_M0_LK_SR", "LS220_M14691268_M0_LK_SR", "SFHo_M14521283_M0_LK_SR"]
    # lbls += ["DD2 151 124", "LS220 150 127", "SFHo 145 128"]
    # masks += [mask, mask, mask]
    # colors += ["black", "red", "green"]
    # lss += ["--", "--", "--"]
    # lws += [1., 1., 1.]


    # v_ns = ["theta", "Y_e", "vel_inf", "entropy"]
    v_ns = ["Y_e"]
    i_x_plot = 1
    for v_n in v_ns:
        averages[v_n] = {}
        for sim, lbl, mask, color, ls, lw in zip(sims, lbls, masks, colors, lss, lws):

            # loading hist
            fpath = Paths.ppr_sims + sim + "/" + "outflow_{}/".format(det) + mask + '/' + "hist_{}.dat".format(v_n)
            if not os.path.isfile(fpath):
                raise IOError("File does not exist: {}".format(fpath))
            hist = np.loadtxt(fpath, usecols=(0, 1), unpack=False)

            # loading times
            fpath1 = Paths.ppr_sims + sim + "/" + "outflow_{}/".format(det) + mask + '/' + "total_flux.dat"
            if not os.path.isfile(fpath1):
                raise IOError("File does not exist: {}".format(fpath1))
            timearr1, massarr1 = np.loadtxt(fpath1, usecols=(0, 2), unpack=True)

            if v_n == "Y_e":
                ave = EJECTA_PARS.compute_ave_ye(massarr1[-1], hist)
                averages[v_n][sim] = ave
            elif v_n == "theta":
                ave = EJECTA_PARS.compute_ave_theta_rms(hist)
                averages[v_n][sim] = ave
            elif v_n == "vel_inf":
                ave = EJECTA_PARS.compute_ave_vel_inf(massarr1[-1], hist)
                averages[v_n][sim] = ave
            elif v_n == "entropy":
                ave = EJECTA_PARS.compute_ave_vel_inf(massarr1[-1], hist)
                averages[v_n][sim] = ave
            else:
                raise NameError("no averages set for v_n:{}".format(v_n))

            plot_dic = {
                'task': 'hist1d', 'ptype': 'cartesian',
                'position': (1, i_x_plot),
                'data': hist, 'normalize': True,
                'v_n_x': v_n, 'v_n_y': None,
                'color': color, 'ls': ls, 'lw': lw, 'ds': 'steps', 'alpha': 1.0,
                'xmin': None, 'xamx': None, 'ymin': 1e-3, 'ymax': 5e-1,
                'xlabel': Labels.labels(v_n), 'ylabel': Labels.labels("mass"),
                'label': lbl, 'yscale': 'log',
                'fancyticks': True, 'minorticks': True,
                'fontsize': 14,
                'labelsize': 14,
                'sharex': False,
                'sharey': False,
                'legend': {}  # 'loc': 'best', 'ncol': 2, 'fontsize': 18
            }
            plot_dic = Limits.in_dic(plot_dic)
            if v_n != v_ns[0]:
                plot_dic["sharey"] = True
            if v_n == v_ns[0] and sim == sims[-1]:
                plot_dic['legend'] = {'loc': 'lower center', 'ncol': 1, "fontsize": 9}  #
                # plot_dic['legend'] = {
                #     'bbox_to_anchor': (1.0, -0.1),
                #     # 'loc': 'lower left',
                #     'loc': 'lower left', 'ncol': 1, 'fontsize': 9, 'framealpha': 0., 'borderaxespad': 0.,
                #     'borderayespad': 0.}
            o_plot.set_plot_dics.append(plot_dic)

        i_x_plot += 1

    #
    masks = [mask2, mask2, mask2, mask2, mask2]
    v_ns = ["Y_e"]
    i_x_plot = 2
    for v_n in v_ns:
        averages[v_n] = {}
        for sim, lbl, mask, color, ls, lw in zip(sims, lbls, masks, colors, lss, lws):

            # loading hist
            fpath = Paths.ppr_sims + sim + "/" + "outflow_{}/".format(det) + mask + '/' + "hist_{}.dat".format(v_n)
            if not os.path.isfile(fpath):
                raise IOError("File does not exist: {}".format(fpath))
            hist = np.loadtxt(fpath, usecols=(0, 1), unpack=False)

            # loading times
            fpath1 = Paths.ppr_sims + sim + "/" + "outflow_{}/".format(det) + mask + '/' + "total_flux.dat"
            if not os.path.isfile(fpath1):
                raise IOError("File does not exist: {}".format(fpath1))
            timearr1, massarr1 = np.loadtxt(fpath1, usecols=(0, 2), unpack=True)

            if v_n == "Y_e":
                ave = EJECTA_PARS.compute_ave_ye(massarr1[-1], hist)
                averages[v_n][sim] = ave
            elif v_n == "theta":
                ave = EJECTA_PARS.compute_ave_theta_rms(hist)
                averages[v_n][sim] = ave
            elif v_n == "vel_inf":
                ave = EJECTA_PARS.compute_ave_vel_inf(massarr1[-1], hist)
                averages[v_n][sim] = ave
            elif v_n == "entropy":
                ave = EJECTA_PARS.compute_ave_vel_inf(massarr1[-1], hist)
                averages[v_n][sim] = ave
            else:
                raise NameError("no averages set for v_n:{}".format(v_n))

            plot_dic = {
                'task': 'hist1d', 'ptype': 'cartesian',
                'position': (1, i_x_plot),
                'data': hist, 'normalize': True,
                'v_n_x': v_n, 'v_n_y': None,
                'color': color, 'ls': ls, 'lw': lw, 'ds': 'steps', 'alpha': 1.0,
                'xmin': None, 'xamx': None, 'ymin': 1e-3, 'ymax': 5e-1,
                'xlabel': Labels.labels(v_n), 'ylabel': Labels.labels("mass"),
                'label': lbl, 'yscale': 'log',
                'fancyticks': True, 'minorticks': True,
                'fontsize': 14,
                'labelsize': 14,
                'sharex': False,
                'sharey': True,
                'legend': {}  # 'loc': 'best', 'ncol': 2, 'fontsize': 18
            }
            plot_dic = Limits.in_dic(plot_dic)
            if v_n != v_ns[0]:
                plot_dic["sharey"] = True
            # if v_n == v_ns[0] and sim == sims[-1]:
            #     plot_dic['legend'] = {'loc': 'lower left', 'ncol':1,"fontsize":9} #

            o_plot.set_plot_dics.append(plot_dic)

        i_x_plot += 1

    o_plot.main()

    for v_n in v_ns:
        print("\t{}".format(v_n))
        for sim in sims:
            print("\t\t{}".format(sim)),
            print("       {:.2f}".format(averages[v_n][sim]))

    exit(1)


def plot_histograms_ejecta_for_many_sims():
    o_plot = PLOT_MANY_TASKS()
    o_plot.gen_set["figdir"] = Paths.plots + "all2/"
    o_plot.gen_set["type"] = "cartesian"
    o_plot.gen_set["figsize"] = (4.2, 3.6)  # <->, |]
    o_plot.gen_set["figname"] = "hists_geo_for_all_nucleo.png"
    o_plot.gen_set["sharex"] = False
    o_plot.gen_set["sharey"] = True
    o_plot.gen_set["dpi"] = 128
    o_plot.gen_set["subplots_adjust_h"] = 0.3
    o_plot.gen_set["subplots_adjust_w"] = 0.0
    o_plot.set_plot_dics = []
    averages = {}

    det = 0

    sims = ["BLh_M11841581_M0_LK_SR",
            "DD2_M13641364_M0_LK_SR_R04", "DD2_M13641364_M0_SR_R04", "DD2_M15091235_M0_LK_SR", "DD2_M14971245_M0_SR",
            "LS220_M13641364_M0_LK_SR_restart", "LS220_M13641364_M0_SR", "LS220_M14691268_M0_LK_SR",
            "LS220_M14351298_M0_SR",  # "LS220_M14691268_M0_SR",
            "SFHo_M13641364_M0_LK_SR_2019pizza", "SFHo_M13641364_M0_SR", "SFHo_M14521283_M0_LK_SR_2019pizza",
            "SFHo_M14521283_M0_SR",
            "SLy4_M13641364_M0_LK_SR", "SLy4_M14521283_M0_SR"]

    lbls = [sim.replace('_', '\_') for sim in sims]
    masks = ["geo",
             "geo", "geo", "geo", "geo",
             "geo", "geo", "geo", "geo",
             "geo", "geo", "geo", "geo",
             "geo", "geo"]
    # masks = ["geo bern_geoend", "geo bern_geoend", "geo bern_geoend", "geo bern_geoend", "geo bern_geoend"]
    colors = ["black",
              "blue", "blue", "blue", "blue",
              "red", "red", "red", "red",
              "green", "green", "green", "green",
              "orange", "orange"]
    alphas = [1.,
              1., 1., 1., 1.,
              1., 1., 1., 1.,
              1., 1., 1., 1.,
              1., 1.]
    lss = ['-',
           '-', '--', '-.', ':',
           '-', '--', '-.', ':',
           '-', '--', '-.', ':',
           '-', '--']
    lws = [1.,
           1., 0.8, 0.5, 0.5,
           1., 0.8, 0.5, 0.5,
           1., 0.8, 0.5, 0.5,
           1., 0.8]


    # v_ns = ["theta", "Y_e", "vel_inf", "entropy"]
    v_ns = ["Y_e"]
    i_x_plot = 1
    for v_n in v_ns:
        averages[v_n] = {}
        for sim, lbl, mask, color, ls, lw in zip(sims, lbls, masks, colors, lss, lws):

            # loading hist
            fpath = Paths.ppr_sims + sim + "/" + "outflow_{}/".format(det) + mask + '/' + "hist_{}.dat".format(v_n)
            if not os.path.isfile(fpath):
                raise IOError("File does not exist: {}".format(fpath))
            hist = np.loadtxt(fpath, usecols=(0, 1), unpack=False)

            # loading times
            fpath1 = Paths.ppr_sims + sim + "/" + "outflow_{}/".format(det) + mask + '/' + "total_flux.dat"
            if not os.path.isfile(fpath1):
                raise IOError("File does not exist: {}".format(fpath1))
            timearr1, massarr1 = np.loadtxt(fpath1, usecols=(0, 2), unpack=True)

            if v_n == "Y_e":
                ave = EJECTA_PARS.compute_ave_ye(massarr1[-1], hist)
                averages[v_n][sim] = ave
            elif v_n == "theta":
                ave = EJECTA_PARS.compute_ave_theta_rms(hist)
                averages[v_n][sim] = ave
            elif v_n == "vel_inf":
                ave = EJECTA_PARS.compute_ave_vel_inf(massarr1[-1], hist)
                averages[v_n][sim] = ave
            elif v_n == "entropy":
                ave = EJECTA_PARS.compute_ave_vel_inf(massarr1[-1], hist)
                averages[v_n][sim] = ave
            else:
                raise NameError("no averages set for v_n:{}".format(v_n))

            plot_dic = {
                'task': 'hist1d', 'ptype': 'cartesian',
                'position': (1, i_x_plot),
                'data': hist, 'normalize': True,
                'v_n_x': v_n, 'v_n_y': None,
                'color': color, 'ls': ls, 'lw': lw, 'ds': 'steps', 'alpha': 1.0,
                'xmin': None, 'xamx': None, 'ymin': 1e-3, 'ymax': 5e-1,
                'xlabel': Labels.labels(v_n), 'ylabel': Labels.labels("mass"),
                'label': lbl, 'yscale': 'log',
                'fancyticks': True, 'minorticks': True,
                'fontsize': 14,
                'labelsize': 14,
                'sharex': False,
                'sharey': False,
                'legend': {}  # 'loc': 'best', 'ncol': 2, 'fontsize': 18
            }
            plot_dic = Limits.in_dic(plot_dic)
            if v_n != v_ns[0]:
                plot_dic["sharey"] = True
            if v_n == v_ns[0] and sim == sims[-1]:
                # plot_dic['legend'] = {'loc': 'lower center', 'ncol': 1, "fontsize": 9}  #
                plot_dic['legend'] = {
                    'bbox_to_anchor': (1.0, -0.1),
                    # 'loc': 'lower left',
                    'loc': 'lower left', 'ncol': 1, 'fontsize': 9, 'framealpha': 0., 'borderaxespad': 0.,
                    'borderayespad': 0.}
            o_plot.set_plot_dics.append(plot_dic)

        i_x_plot += 1

    o_plot.main()

    for v_n in v_ns:
        print("\t{}".format(v_n))
        for sim in sims:
            print("\t\t{}".format(sim)),
            print("       {:.2f}".format(averages[v_n][sim]))

    exit(1)


# plot_histograms_ejecta("geo")
# plot_histograms_ejecta("bern_geoend")

def plot_histograms_lk_on_off(mask):
    o_plot = PLOT_MANY_TASKS()
    o_plot.gen_set["figdir"] = Paths.plots + "all2/"
    o_plot.gen_set["type"] = "cartesian"
    o_plot.gen_set["figsize"] = (11.0, 3.6)  # <->, |]
    o_plot.gen_set["figname"] = "tothist_lk_{}.png".format(mask)
    o_plot.gen_set["sharex"] = False
    o_plot.gen_set["sharey"] = True
    o_plot.gen_set["dpi"] = 128
    o_plot.gen_set["subplots_adjust_h"] = 0.3
    o_plot.gen_set["subplots_adjust_w"] = 0.0
    o_plot.set_plot_dics = []
    averages = {}

    det = 0

    sims = ["DD2_M13641364_M0_LK_SR_R04", "DD2_M15091235_M0_LK_SR", "LS220_M14691268_M0_LK_SR",
            "SFHo_M14521283_M0_LK_SR"]
    lbls = ["DD2 136 136 LK", "DD2 151 123 LK", "LS220 147 127 LK", "SFHo 145 128 LK"]
    masks = [mask, mask, mask, mask]
    colors = ["black", 'gray', 'red', "green"]
    lss = ["-", '-', '-', '-']
    lws = [1., 1., 1., 1., ]
    # minus LK
    sims2 = ["DD2_M13641364_M0_SR_R04", "DD2_M14971245_M0_SR", "LS220_M14691268_M0_SR", "SFHo_M14521283_M0_SR"]
    lbls2 = ["DD2 136 136", "DD2 150 125", "LS220 147 127", "SFHo 145 128"]
    masks2 = [mask, mask, mask, mask]
    colors2 = ["black", 'gray', 'red', "green"]
    lss2 = ["--", '--', '--', '--']
    lws2 = [1., 1., 1., 1., ]

    sims += sims2
    lbls += lbls2
    masks += masks2
    colors += colors2
    lss += lss2
    lws += lws2

    v_ns = ["theta", "Y_e", "vel_inf", "entropy"]
    i_x_plot = 1
    for v_n in v_ns:
        averages[v_n] = {}
        for sim, lbl, mask, color, ls, lw in zip(sims, lbls, masks, colors, lss, lws):

            # loading hist
            fpath = Paths.ppr_sims + sim + "/" + "outflow_{}/".format(det) + mask + '/' + "hist_{}.dat".format(v_n)
            if not os.path.isfile(fpath):
                raise IOError("File does not exist: {}".format(fpath))
            hist = np.loadtxt(fpath, usecols=(0, 1), unpack=False)

            # loading times
            fpath1 = Paths.ppr_sims + sim + "/" + "outflow_{}/".format(det) + mask + '/' + "total_flux.dat"
            if not os.path.isfile(fpath1):
                raise IOError("File does not exist: {}".format(fpath1))
            timearr1, massarr1 = np.loadtxt(fpath1, usecols=(0, 2), unpack=True)

            if v_n == "Y_e":
                ave = EJECTA_PARS.compute_ave_ye(massarr1[-1], hist)
                averages[v_n][sim] = ave
            elif v_n == "theta":
                ave = EJECTA_PARS.compute_ave_theta_rms(hist)
                averages[v_n][sim] = ave
            elif v_n == "vel_inf":
                ave = EJECTA_PARS.compute_ave_vel_inf(massarr1[-1], hist)
                averages[v_n][sim] = ave
            elif v_n == "entropy":
                ave = EJECTA_PARS.compute_ave_vel_inf(massarr1[-1], hist)
                averages[v_n][sim] = ave
            else:
                raise NameError("no averages set for v_n:{}".format(v_n))

            plot_dic = {
                'task': 'hist1d', 'ptype': 'cartesian',
                'position': (1, i_x_plot),
                'data': hist, 'normalize': True,
                'v_n_x': v_n, 'v_n_y': None,
                'color': color, 'ls': ls, 'lw': lw, 'ds': 'steps', 'alpha': 1.0,
                'xmin': None, 'xamx': None, 'ymin': 1e-3, 'ymax': 1e0,
                'xlabel': Labels.labels(v_n), 'ylabel': Labels.labels("mass"),
                'label': lbl, 'yscale': 'log',
                'fancyticks': True, 'minorticks': True,
                'fontsize': 14,
                'labelsize': 14,
                'sharex': False,
                'sharey': False,
                'legend': {}  # 'loc': 'best', 'ncol': 2, 'fontsize': 18
            }
            plot_dic = Limits.in_dic(plot_dic)
            if v_n != v_ns[0]:
                plot_dic["sharey"] = True
            if v_n == v_ns[-1] and sim == sims[-1]:
                plot_dic['legend'] = {'bbox_to_anchor': (-3.00, 1.0), 'loc': 'upper left', 'ncol': 4, "fontsize": 12}

            o_plot.set_plot_dics.append(plot_dic)

        i_x_plot += 1
    o_plot.main()

    for v_n in v_ns:
        print(" --- v_n: {} --- ".format(v_n))
        for sim1, sim2 in zip(sims, sims2):
            val1 = averages[v_n][sim1]
            val2 = averages[v_n][sim2]
            err = 100 * (val1 - val2) / val1
            print("\t{}  :  {:.2f}".format(sim1, val1))
            print("\t{}  :  {:.2f}".format(sim2, val2))
            print("\t\tErr:\t\t{:.1f}".format(err))
        print(" -------------------- ".format(v_n))

    exit(1)


# plot_histograms_lk_on_off("geo")
# plot_histograms_lk_on_off("bern_geoend")


def plot_histograms_lk_on_resolution(mask):
    o_plot = PLOT_MANY_TASKS()
    o_plot.gen_set["figdir"] = Paths.plots + "all2/"
    o_plot.gen_set["type"] = "cartesian"
    o_plot.gen_set["figsize"] = (11.0, 3.6)  # <->, |]
    o_plot.gen_set["figname"] = "tothist_lk_res_{}.png".format(mask)
    o_plot.gen_set["sharex"] = False
    o_plot.gen_set["sharey"] = True
    o_plot.gen_set["dpi"] = 128
    o_plot.gen_set["subplots_adjust_h"] = 0.3
    o_plot.gen_set["subplots_adjust_w"] = 0.0
    o_plot.set_plot_dics = []
    averages = {}

    det = 0
    # HR  "LS220_M13641364_M0_LK_HR"  -- too short
    sims_hr = ["DD2_M13641364_M0_LK_HR_R04", "DD2_M15091235_M0_LK_HR", "", "LS220_M14691268_M0_LK_HR",
               "SFHo_M13641364_M0_LK_HR", "SFHo_M14521283_M0_LK_HR"]
    lbl_hr = ["DD2 136 136 HR", "DD2 151 124 HR", "LS220 136 136 HR", "LS220 147 137 HR", "SFHo 136 136 HR",
              "SFHo 145 128 HR"]
    color_hr = ["black", "gray", "orange", "red", "green", "lightgreen"]
    masks_hr = [mask, mask, mask, mask, mask, mask]
    lss_hr = ['--', '--', '--', '--', "--", "--"]
    lws_hr = [1., 1., 1., 1., 1., 1.]
    # SR  "LS220_M13641364_M0_LK_SR"
    sims_sr = ["DD2_M13641364_M0_LK_SR_R04", "DD2_M15091235_M0_LK_SR", "", "LS220_M14691268_M0_LK_SR",
               "SFHo_M13641364_M0_LK_SR", "SFHo_M14521283_M0_LK_SR"]
    lbl_sr = ["DD2 136 136 SR", "DD2 151 124 HR", "LS220 136 136 SR", "LS220 147 137 SR", "SFHo 136 136 HR",
              "SFHo 145 128 HR"]
    color_sr = ["black", "gray", "orange", "red", "green", "lightgreen"]
    masks_sr = [mask, mask, mask, mask, mask, mask]
    lss_sr = ['-', '-', '-', '-', '-', '-']
    lws_sr = [1., 1., 1., 1., 1., 1.]
    # LR
    sims_lr = ["DD2_M13641364_M0_LK_LR_R04", "", "", "", "", ""]
    lbl_lr = ["DD2 136 136 LR", "DD2 151 124 LR", "LS220 136 136 LR", "LS220 147 137 LR", "SFHo 136 136 LR",
              "SFHo 145 128 LR"]
    color_lr = ["black", "gray", "orange", "red", "green", "lightgreen"]
    masks_lr = [mask, mask, mask, mask, mask, mask]
    lss_lr = [':', ':', ":", ":", ":", ":"]
    lws_lr = [1., 1., 1., 1., 1., 1.]

    # plus
    sims = sims_hr + sims_lr + sims_sr
    lbls = lbl_hr + lbl_lr + lbl_sr
    colors = color_hr + color_lr + color_sr
    masks = masks_hr + masks_lr + masks_sr
    lss = lss_hr + lss_lr + lss_sr
    lws = lws_hr + lws_lr + lws_sr

    v_ns = ["theta", "Y_e", "vel_inf", "entropy"]
    i_x_plot = 1
    for v_n in v_ns:
        averages[v_n] = {}
        for sim, lbl, mask, color, ls, lw in zip(sims, lbls, masks, colors, lss, lws):
            if sim != "":
                # loading hist
                fpath = Paths.ppr_sims + sim + "/" + "outflow_{}/".format(det) + mask + '/' + "hist_{}.dat".format(v_n)
                if not os.path.isfile(fpath):
                    raise IOError("File does not exist: {}".format(fpath))
                hist = np.loadtxt(fpath, usecols=(0, 1), unpack=False)

                # loading times
                fpath1 = Paths.ppr_sims + sim + "/" + "outflow_{}/".format(det) + mask + '/' + "total_flux.dat"
                if not os.path.isfile(fpath1):
                    raise IOError("File does not exist: {}".format(fpath1))
                timearr1, massarr1 = np.loadtxt(fpath1, usecols=(0, 2), unpack=True)

                if v_n == "Y_e":
                    ave = EJECTA_PARS.compute_ave_ye(massarr1[-1], hist)
                    averages[v_n][sim] = ave
                elif v_n == "theta":
                    ave = EJECTA_PARS.compute_ave_theta_rms(hist)
                    averages[v_n][sim] = ave
                elif v_n == "vel_inf":
                    ave = EJECTA_PARS.compute_ave_vel_inf(massarr1[-1], hist)
                    averages[v_n][sim] = ave
                elif v_n == "entropy":
                    ave = EJECTA_PARS.compute_ave_vel_inf(massarr1[-1], hist)
                    averages[v_n][sim] = ave
                else:
                    raise NameError("no averages set for v_n:{}".format(v_n))

                plot_dic = {
                    'task': 'hist1d', 'ptype': 'cartesian',
                    'position': (1, i_x_plot),
                    'data': hist, 'normalize': True,
                    'v_n_x': v_n, 'v_n_y': None,
                    'color': color, 'ls': ls, 'lw': lw, 'ds': 'steps', 'alpha': 1.0,
                    'xmin': None, 'xamx': None, 'ymin': 1e-3, 'ymax': 1e0,
                    'xlabel': Labels.labels(v_n), 'ylabel': Labels.labels("mass"),
                    'label': lbl, 'yscale': 'log',
                    'fancyticks': True, 'minorticks': True,
                    'fontsize': 14,
                    'labelsize': 14,
                    'sharex': False,
                    'sharey': False,
                    'legend': {}  # 'loc': 'best', 'ncol': 2, 'fontsize': 18
                }
                plot_dic = Limits.in_dic(plot_dic)
                if v_n != v_ns[0]:
                    plot_dic["sharey"] = True
                if v_n == v_ns[-1] and sim == sims[-1]:
                    plot_dic['legend'] = {'bbox_to_anchor': (-3.00, 1.0), 'loc': 'upper left', 'ncol': 4,
                                          "fontsize": 12}

                o_plot.set_plot_dics.append(plot_dic)

        i_x_plot += 1
    o_plot.main()

    for v_n in v_ns:
        print(" --- v_n: {} --- ".format(v_n))
        for sim_hr, sim_sr, sim_lr in zip(sims_hr, sims_sr, sims_lr):
            # print(sim_hr, sim_sr, sim_lr)
            if not sim_sr == "":
                assert sim_sr != ""
                def_sim = sim_sr
                def_res = "SR"

                if sim_hr != '':
                    comp_res = "HR"
                    comp_sim = sim_hr
                elif sim_hr == '' and sim_lr != '':
                    comp_res = "LR"
                    comp_sim = sim_lr
                else:
                    raise ValueError("neither HR nor LR is available")

                # print(def_sim, comp_sim)

                assert comp_sim != ""

                val1 = averages[v_n][def_sim]
                val2 = averages[v_n][comp_sim]
                err = 100 * (val1 - val2) / val1
                print("\t{}  :  {:.2f}".format(def_sim, val1))
                print("\t{}  :  {:.2f}".format(comp_sim, val2))
                print("\t\tErr:\t\t{:.1f}".format(err))
        print(" -------------------- ".format(v_n))

    exit(1)


# plot_histograms_lk_on_resolution("geo")
# plot_histograms_lk_on_resolution("bern_geoend")

def plot_histograms_lk_off_resolution(mask):
    o_plot = PLOT_MANY_TASKS()
    o_plot.gen_set["figdir"] = Paths.plots + "all2/"
    o_plot.gen_set["type"] = "cartesian"
    o_plot.gen_set["figsize"] = (11.0, 3.6)  # <->, |]
    o_plot.gen_set["figname"] = "tothist_res_{}.png".format(mask)
    o_plot.gen_set["sharex"] = False
    o_plot.gen_set["sharey"] = True
    o_plot.gen_set["dpi"] = 128
    o_plot.gen_set["subplots_adjust_h"] = 0.3
    o_plot.gen_set["subplots_adjust_w"] = 0.0
    o_plot.set_plot_dics = []
    averages = {}

    det = 0
    # HR  "LS220_M13641364_M0_LK_HR"  -- too short
    sims_hr = ["", "DD2_M14971245_M0_HR", "LS220_M13641364_M0_HR", "LS220_M14691268_M0_HR", "SFHo_M13641364_M0_HR",
               "SFHo_M14521283_M0_HR"]
    lbl_hr = ["DD2 136 136 HR", "DD2 150 125 HR", "LS220 136 136 HR", "LS220 147 127 HR", "SFHo 136 136 HR",
              "SFHo 145 128 HR"]
    color_hr = ["black", "gray", "orange", "red", "lightgreen", "green"]
    masks_hr = [mask, mask, mask, mask, mask, mask]
    lss_hr = ['--', '--', '--', '--', '--', '--']
    lws_hr = [1., 1., 1., 1., 1., 1.]
    # SR  "LS220_M13641364_M0_LK_SR"
    sims_sr = ["DD2_M13641364_M0_SR_R04", "DD2_M14971245_M0_SR", "LS220_M13641364_M0_SR", "LS220_M14691268_M0_SR",
               "SFHo_M13641364_M0_SR", "SFHo_M14521283_M0_SR"]
    lbl_sr = ["DD2 136 136 SR", "DD2 150 125 SR", "LS220 136 136 SR", "LS220 147 127 SR", "SFHo 136 136 SR",
              "SFHo 145 128 SR"]
    color_sr = ["black", "gray", "orange", "red", "lightgreen", "green"]
    masks_sr = [mask, mask, mask, mask, mask, mask]
    lss_sr = ['-', '-', '-', '-', '-', '-']
    lws_sr = [1., 1., 1., 1., 1., 1.]
    # LR
    sims_lr = ["DD2_M13641364_M0_LR_R04", "DD2_M14971246_M0_LR", "LS220_M13641364_M0_LR", "LS220_M14691268_M0_LR", "",
               ""]
    lbl_lr = ["DD2 136 136 LR", "DD2 150 125 LR", "LS220 136 136 LR", "LS220 147 127 LR", "SFHo 136 136 LR",
              "SFHo 145 128 LR"]
    color_lr = ["black", "gray", "orange", "red", "lightgreen", "green"]
    masks_lr = [mask, mask, mask, mask, mask, mask]
    lss_lr = [':', ':', ':', ':', ':', ':']
    lws_lr = [1., 1., 1., 1., 1., 1.]

    # plus
    sims = sims_hr + sims_lr + sims_sr
    lbls = lbl_hr + lbl_lr + lbl_sr
    colors = color_hr + color_lr + color_sr
    masks = masks_hr + masks_lr + masks_sr
    lss = lss_hr + lss_lr + lss_sr
    lws = lws_hr + lws_lr + lws_sr

    v_ns = ["theta", "Y_e", "vel_inf", "entropy"]
    i_x_plot = 1
    for v_n in v_ns:
        averages[v_n] = {}
        for sim, lbl, mask, color, ls, lw in zip(sims, lbls, masks, colors, lss, lws):
            if sim != "":
                # loading hist
                fpath = Paths.ppr_sims + sim + "/" + "outflow_{}/".format(det) + mask + '/' + "hist_{}.dat".format(v_n)
                if not os.path.isfile(fpath):
                    raise IOError("File does not exist: {}".format(fpath))
                hist = np.loadtxt(fpath, usecols=(0, 1), unpack=False)

                # loading times
                fpath1 = Paths.ppr_sims + sim + "/" + "outflow_{}/".format(det) + mask + '/' + "total_flux.dat"
                if not os.path.isfile(fpath1):
                    raise IOError("File does not exist: {}".format(fpath1))
                timearr1, massarr1 = np.loadtxt(fpath1, usecols=(0, 2), unpack=True)

                if v_n == "Y_e":
                    ave = EJECTA_PARS.compute_ave_ye(massarr1[-1], hist)
                    averages[v_n][sim] = ave
                elif v_n == "theta":
                    ave = EJECTA_PARS.compute_ave_theta_rms(hist)
                    averages[v_n][sim] = ave
                elif v_n == "vel_inf":
                    ave = EJECTA_PARS.compute_ave_vel_inf(massarr1[-1], hist)
                    averages[v_n][sim] = ave
                elif v_n == "entropy":
                    ave = EJECTA_PARS.compute_ave_vel_inf(massarr1[-1], hist)
                    averages[v_n][sim] = ave
                else:
                    raise NameError("no averages set for v_n:{}".format(v_n))

                plot_dic = {
                    'task': 'hist1d', 'ptype': 'cartesian',
                    'position': (1, i_x_plot),
                    'data': hist, 'normalize': True,
                    'v_n_x': v_n, 'v_n_y': None,
                    'color': color, 'ls': ls, 'lw': lw, 'ds': 'steps', 'alpha': 1.0,
                    'xmin': None, 'xamx': None, 'ymin': 1e-3, 'ymax': 1e0,
                    'xlabel': Labels.labels(v_n), 'ylabel': Labels.labels("mass"),
                    'label': lbl, 'yscale': 'log',
                    'fancyticks': True, 'minorticks': True,
                    'fontsize': 14,
                    'labelsize': 14,
                    'sharex': False,
                    'sharey': False,
                    'legend': {}  # 'loc': 'best', 'ncol': 2, 'fontsize': 18
                }
                plot_dic = Limits.in_dic(plot_dic)
                if v_n != v_ns[0]:
                    plot_dic["sharey"] = True
                if v_n == v_ns[-1] and sim == sims[-1]:
                    plot_dic['legend'] = {'bbox_to_anchor': (-3.00, 1.0), 'loc': 'upper left', 'ncol': 4,
                                          "fontsize": 12}

                o_plot.set_plot_dics.append(plot_dic)

        i_x_plot += 1
    o_plot.main()

    for v_n in v_ns:
        print(" --- v_n: {} --- ".format(v_n))
        for sim_hr, sim_sr, sim_lr in zip(sims_hr, sims_sr, sims_lr):
            # print(sim_hr, sim_sr, sim_lr)
            if not sim_sr == "":
                assert sim_sr != ""
                def_sim = sim_sr
                def_res = "SR"

                if sim_hr != '':
                    comp_res = "HR"
                    comp_sim = sim_hr
                elif sim_hr == '' and sim_lr != '':
                    comp_res = "LR"
                    comp_sim = sim_lr
                else:
                    raise ValueError("neither HR nor LR is available")

                # print(def_sim, comp_sim)

                assert comp_sim != ""

                val1 = averages[v_n][def_sim]
                val2 = averages[v_n][comp_sim]
                err = 100 * (val1 - val2) / val1
                print("\t{}  :  {:.2f}".format(def_sim, val1))
                print("\t{}  :  {:.2f}".format(comp_sim, val2))
                print("\t\tErr:\t\t{:.1f}".format(err))
        print(" -------------------- ".format(v_n))

    exit(1)


# plot_histograms_lk_off_resolution("geo")
# plot_histograms_lk_off_resolution("bern_geoend")

''' neutrino driven wind '''


def plot_several_q_eff(v_n, sims, iterations, figname):
    o_plot = PLOT_MANY_TASKS()
    o_plot.gen_set["figdir"] = Paths.plots + "all2/"
    o_plot.gen_set["type"] = "cartesian"
    o_plot.gen_set["figsize"] = (12., 3.2)  # <->, |] # to match hists with (8.5, 2.7)
    o_plot.gen_set["figname"] = figname
    o_plot.gen_set["sharex"] = False
    o_plot.gen_set["sharey"] = False
    o_plot.gen_set["subplots_adjust_h"] = 0.2
    o_plot.gen_set["subplots_adjust_w"] = 0.0
    o_plot.set_plot_dics = []

    rl = 3
    # v_n = "Q_eff_nua"

    # sims = ["LS220_M14691268_M0_LK_SR"]
    # iterations = [1302528, 1515520, 1843200]

    i_x_plot = 1
    i_y_plot = 1
    for sim in sims:

        d3class = LOAD_PROFILE_XYXZ(sim)
        d1class = ADD_METHODS_ALL_PAR(sim)

        for it in iterations:

            tmerg = d1class.get_par("tmerg")
            time_ = d3class.get_time_for_it(it, "prof")

            dens_arr = d3class.get_data(it, rl, "xz", "density")
            data_arr = d3class.get_data(it, rl, "xz", v_n)
            data_arr = data_arr / dens_arr
            x_arr = d3class.get_data(it, rl, "xz", "x")
            z_arr = d3class.get_data(it, rl, "xz", "z")

            def_dic_xz = {'task': 'colormesh', 'ptype': 'cartesian', 'aspect': 1.,
                          'xarr': x_arr, "yarr": z_arr, "zarr": data_arr,
                          'position': (i_y_plot, i_x_plot),  # 'title': '[{:.1f} ms]'.format(time_),
                          'cbar': {},
                          'v_n_x': 'x', 'v_n_y': 'z', 'v_n': v_n,
                          'xmin': None, 'xmax': None, 'ymin': None, 'ymax': None, 'vmin': 1e-10, 'vmax': 1e-4,
                          'fill_vmin': False,  # fills the x < vmin with vmin
                          'xscale': None, 'yscale': None,
                          'mask': None, 'cmap': 'inferno_r', 'norm': "log",
                          'fancyticks': True,
                          'minorticks': True,
                          'title': {"text": r'$t-t_{merg}:$' + r'${:.1f}$'.format((time_ - tmerg) * 1e3),
                                    'fontsize': 14},
                          # 'sharex': True,  # removes angular citkscitks
                          'fontsize': 14,
                          'labelsize': 14,
                          'sharex': False,
                          'sharey': True,
                          }

            def_dic_xz["xmin"], def_dic_xz["xmax"], _, _, def_dic_xz["ymin"], def_dic_xz["ymax"] \
                = UTILS.get_xmin_xmax_ymin_ymax_zmin_zmax(rl)

            if v_n == 'Q_eff_nua':

                def_dic_xz['v_n'] = 'Q_eff_nua/D'
                def_dic_xz['vmin'] = 1e-7
                def_dic_xz['vmax'] = 1e-3
                # def_dic_xz['norm'] = None
            elif v_n == 'Q_eff_nue':

                def_dic_xz['v_n'] = 'Q_eff_nue/D'
                def_dic_xz['vmin'] = 1e-7
                def_dic_xz['vmax'] = 1e-3
                # def_dic_xz['norm'] = None
            elif v_n == 'Q_eff_nux':

                def_dic_xz['v_n'] = 'Q_eff_nux/D'
                def_dic_xz['vmin'] = 1e-10
                def_dic_xz['vmax'] = 1e-4
                # def_dic_xz['norm'] = None
                # print("v_n: {} [{}->{}]".format(v_n, def_dic_xz['zarr'].min(), def_dic_xz['zarr'].max()))
            elif v_n == "R_eff_nua":

                def_dic_xz['v_n'] = 'R_eff_nua/D'
                def_dic_xz['vmin'] = 1e2
                def_dic_xz['vmax'] = 1e6
                # def_dic_xz['norm'] = None

                print("v_n: {} [{}->{}]".format(v_n, def_dic_xz['zarr'].min(), def_dic_xz['zarr'].max()))
                # exit(1)

            if it == iterations[0]:
                def_dic_xz["sharey"] = False

            if it == iterations[-1]:
                def_dic_xz['cbar'] = {'location': 'right .02 0.', 'label': Labels.labels(v_n) + "/D",
                                      # 'right .02 0.' 'fmt': '%.1e',
                                      'labelsize': 14, 'aspect': 6.,
                                      'fontsize': 14}

            o_plot.set_plot_dics.append(def_dic_xz)

            i_x_plot = i_x_plot + 1
        i_y_plot = i_y_plot + 1
    o_plot.main()
    exit(0)


''' disk histogram evolution & disk mass '''


def plot_disk_hist_evol_one_v_n(v_n, sim, figname):
    # sim = "LS220_M13641364_M0_LK_SR_restart"
    # v_n = "Ye"
    # figname = "ls220_ye_disk_hist.png"
    print(v_n)

    d3_corr = LOAD_RES_CORR(sim)
    iterations = d3_corr.list_iterations
    times = []
    bins = []
    values = []
    for it in iterations:
        fpath = Paths.ppr_sims + sim + "/" + "profiles/" + str(it) + "/" + "hist_{}.dat".format(v_n)
        if os.path.isfile(fpath):
            times.append(d3_corr.get_time_for_it(it, "prof"))
            print("\tLoading it:{} t:{}".format(it, times[-1]))
            data = np.loadtxt(fpath, unpack=False)
            bins = data[:, 0]
            values.append(data[:, 1])
        else:
            print("\tFile not found it:{}".format(fpath))
    assert len(times) > 0
    times = np.array(times) * 1e3
    bins = np.array(bins)
    values = np.reshape(np.array(values), newshape=(len(iterations), len(bins))).T
    #
    d1class = ADD_METHODS_ALL_PAR(sim)
    tmerg = d1class.get_par("tmerg") * 1e3
    times = times - tmerg
    #
    values = values / np.sum(values)
    values = np.maximum(values, 1e-10)
    #
    if v_n in ["theta"]:
        bins = bins / np.pi * 180.
    #
    def_dic = {'task': 'colormesh', 'ptype': 'cartesian',  # 'aspect': 1.,
               'xarr': times, "yarr": bins, "zarr": values,
               'position': (1, 1),  # 'title': '[{:.1f} ms]'.format(time_),
               'cbar': {'location': 'right .02 0.', 'label': Labels.labels("mass"),  # 'right .02 0.' 'fmt': '%.1e',
                        'labelsize': 14,  # 'aspect': 6.,
                        'fontsize': 14},
               'v_n_x': 'x', 'v_n_y': 'z', 'v_n': v_n,
               'xlabel': Labels.labels("t-tmerg"), 'ylabel': Labels.labels(v_n),
               'xmin': times.min(), 'xmax': times.max(), 'ymin': bins.min(), 'ymax': bins.max(), 'vmin': 1e-6,
               'vmax': 1e-2,
               'fill_vmin': False,  # fills the x < vmin with vmin
               'xscale': None, 'yscale': None,
               'mask': None, 'cmap': 'Greys', 'norm': "log",
               'fancyticks': True,
               'minorticks': True,
               'title': {},  # "text": r'$t-t_{merg}:$' + r'${:.1f}$'.format((time_ - tmerg) * 1e3), 'fontsize': 14
               # 'sharex': True,  # removes angular citkscitks
               'fontsize': 14,
               'labelsize': 14,
               'sharex': False,
               'sharey': False,
               }
    #
    tcoll = d1class.get_par("tcoll_gw")
    if not np.isnan(tcoll):
        tcoll = (tcoll * 1e3) - tmerg
        tcoll_dic = {'task': 'line', 'ptype': 'cartesian',
                     'position': (1, 1),
                     'xarr': [tcoll, tcoll], 'yarr': [bins.min(), bins.max()],
                     'color': 'black', 'ls': '-', 'lw': 0.6, 'ds': 'default', 'alpha': 1.0,
                     }
        print(tcoll)
    else:
        print("No tcoll")

    o_plot = PLOT_MANY_TASKS()
    o_plot.gen_set["figdir"] = Paths.plots + "all2/"
    o_plot.gen_set["type"] = "cartesian"
    o_plot.gen_set["figsize"] = (4.2, 3.6)  # <->, |] # to match hists with (8.5, 2.7)
    o_plot.gen_set["figname"] = figname
    o_plot.gen_set["sharex"] = False
    o_plot.gen_set["sharey"] = False
    o_plot.gen_set["subplots_adjust_h"] = 0.2
    o_plot.gen_set["subplots_adjust_w"] = 0.0
    o_plot.set_plot_dics = []
    #
    if not np.isnan(tcoll):
        o_plot.set_plot_dics.append(tcoll_dic)
    o_plot.set_plot_dics.append(def_dic)
    #
    if v_n in ["temp", "dens_unb_bern", "rho"]:
        def_dic["yscale"] = "log"
    #
    o_plot.main()

    exit(1)


def plot_disk_hist_evol(sim, figname):
    v_ns = ["r", "theta", "Ye", "velz", "temp", "rho", "dens_unb_bern"]

    # v_ns = ["velz", "temp", "rho", "dens_unb_bern"]

    d3_corr = LOAD_RES_CORR(sim)
    iterations = d3_corr.list_iterations

    o_plot = PLOT_MANY_TASKS()
    o_plot.gen_set["figdir"] = Paths.plots + "all2/"
    o_plot.gen_set["type"] = "cartesian"
    o_plot.gen_set["figsize"] = (len(v_ns) * 3., 2.7)  # <->, |] # to match hists with (8.5, 2.7)
    o_plot.gen_set["figname"] = figname
    o_plot.gen_set["sharex"] = False
    o_plot.gen_set["sharey"] = False
    o_plot.gen_set["subplots_adjust_h"] = 0.2
    o_plot.gen_set["subplots_adjust_w"] = 0.4
    o_plot.set_plot_dics = []

    i_plot = 1
    for v_n in v_ns:
        print("v_n:{}".format(v_n))
        times = []
        bins = []
        values = []
        for it in iterations:
            fpath = Paths.ppr_sims + sim + "/" + "profiles/" + str(it) + "/" + "hist_{}.dat".format(v_n)
            if os.path.isfile(fpath):
                times.append(d3_corr.get_time_for_it(it, "prof"))
                print("\tLoading it:{} t:{}".format(it, times[-1]))
                data = np.loadtxt(fpath, unpack=False)
                bins = data[:, 0]
                values.append(data[:, 1])
            else:
                print("\tFile not found it:{}".format(fpath))

        assert len(times) > 0
        times = np.array(times) * 1e3
        bins = np.array(bins)
        values = np.reshape(np.array(values), newshape=(len(times), len(bins))).T
        #
        d1class = ADD_METHODS_ALL_PAR(sim)
        tmerg = d1class.get_par("tmerg") * 1e3
        times = times - tmerg
        #
        values = values / np.sum(values)
        values = np.maximum(values, 1e-10)
        #
        if v_n in ["theta"]:
            bins = 90 - (bins / np.pi * 180.)
        #
        def_dic = {'task': 'colormesh', 'ptype': 'cartesian',  # 'aspect': 1.,
                   'xarr': times, "yarr": bins, "zarr": values,
                   'position': (1, i_plot),  # 'title': '[{:.1f} ms]'.format(time_),
                   'cbar': {},
                   'v_n_x': 'x', 'v_n_y': 'z', 'v_n': v_n,
                   'xlabel': Labels.labels("t-tmerg"), 'ylabel': Labels.labels(v_n),
                   'xmin': times.min(), 'xmax': times.max(), 'ymin': bins.min(), 'ymax': bins.max(), 'vmin': 1e-6,
                   'vmax': 1e-2,
                   'fill_vmin': False,  # fills the x < vmin with vmin
                   'xscale': None, 'yscale': None,
                   'mask': None, 'cmap': 'Greys', 'norm': "log",
                   'fancyticks': True,
                   'minorticks': True,
                   'title': {},  # "text": r'$t-t_{merg}:$' + r'${:.1f}$'.format((time_ - tmerg) * 1e3), 'fontsize': 14
                   # 'sharex': True,  # removes angular citkscitks
                   'text': {},
                   'fontsize': 14,
                   'labelsize': 14,
                   'sharex': False,
                   'sharey': False,
                   }
        if v_n == v_ns[-1]:
            def_dic['cbar'] = {'location': 'right .02 0.', 'label': Labels.labels("mass"),
                               # 'right .02 0.' 'fmt': '%.1e',
                               'labelsize': 14,  # 'aspect': 6.,
                               'fontsize': 14}
        if v_n == v_ns[0]:
            def_dic['text'] = {'coords': (1.0, 1.05), 'text': sim.replace("_", "\_"), 'color': 'black', 'fs': 16}
        if v_n == "velz":
            def_dic['ymin'] = -.3
            def_dic['ymax'] = .3
        elif v_n == "temp":
            def_dic['ymin'] = 1e-1
            def_dic['ymax'] = 1e2

        tcoll = d1class.get_par("tcoll_gw")
        if not np.isnan(tcoll):
            tcoll = (tcoll * 1e3) - tmerg
            tcoll_dic = {'task': 'line', 'ptype': 'cartesian',
                         'position': (1, i_plot),
                         'xarr': [tcoll, tcoll], 'yarr': [bins.min(), bins.max()],
                         'color': 'black', 'ls': '-', 'lw': 0.6, 'ds': 'default', 'alpha': 1.0,
                         }
            print(tcoll)
        else:
            print("No tcoll")

        #
        if not np.isnan(tcoll):
            o_plot.set_plot_dics.append(tcoll_dic)
        o_plot.set_plot_dics.append(def_dic)
        #
        if v_n in ["temp", "dens_unb_bern", "rho"]:
            def_dic["yscale"] = "log"
        #
        i_plot = i_plot + 1
    o_plot.main()

    exit(1)


def plot_disk_mass_evol_SR():
    # 11
    sims = ["DD2_M13641364_M0_LK_SR_R04", "BLh_M13641364_M0_LK_SR"] + \
           ["DD2_M15091235_M0_LK_SR", "LS220_M14691268_M0_LK_SR"] + \
           ["DD2_M13641364_M0_SR", "LS220_M13641364_M0_SR", "SFHo_M13641364_M0_SR", "SLy4_M13641364_M0_SR"] + \
           ["DD2_M14971245_M0_SR", "SFHo_M14521283_M0_SR", "SLy4_M14521283_M0_SR"]
    #
    colors = ["blue", "black"] + \
             ["blue", "red"] + \
             ["blue", "red", "green", "orange"] + \
             ["blue", "green", "orange"]
    #
    lss = ["-", "-"] + \
          ["--", "--"] + \
          [":", ":", ":", ":"] + \
          ["-.", "-."]
    #
    lws = [1., 1.] + \
          [1., 1.] + \
          [1., 1., 1., 1.] + \
          [1., 1.]
    alphas = [1., 1.] + \
             [1., 1.] + \
             [1., 1., 1., 1.] + \
             [1., 1.]
    #
    # ----

    o_plot = PLOT_MANY_TASKS()
    o_plot.gen_set["figdir"] = Paths.plots + "all2/"
    o_plot.gen_set["type"] = "cartesian"
    o_plot.gen_set["figsize"] = (4.2, 3.6)  # <->, |]
    o_plot.gen_set["figname"] = "disk_mass_evol_SR.png"
    o_plot.gen_set["sharex"] = False
    o_plot.gen_set["sharey"] = True
    o_plot.gen_set["dpi"] = 128
    o_plot.gen_set["subplots_adjust_h"] = 0.3
    o_plot.gen_set["subplots_adjust_w"] = 0.0
    o_plot.set_plot_dics = []

    for sim, color, ls, lw, alpha in zip(sims, colors, lss, lws, alphas):
        print("{}".format(sim))
        o_data = ADD_METHODS_ALL_PAR(sim)
        data = o_data.get_disk_mass()
        tmerg = o_data.get_par("tmerg")
        tarr = (data[:, 0] - tmerg) * 1e3
        marr = data[:, 1]

        if sim == "DD2_M13641364_M0_LK_SR_R04":
            tarr = tarr[3:]  # 3ms, 6ms, 51ms.... Removing initial profiles
            marr = marr[3:]  #
        #
        tcoll = o_data.get_par("tcoll_gw")
        if not np.isnan(tcoll) and tcoll < tarr[-1]:
            tcoll = (tcoll - tmerg) * 1e3
            print(tcoll, tarr[0])
            mcoll = interpolate.interp1d(tarr, marr, kind="linear")(tcoll)
            tcoll_dic = {
                'task': 'line', 'ptype': 'cartesian',
                'position': (1, 1),
                'xarr': [tcoll], 'yarr': [mcoll],
                'v_n_x': "time", 'v_n_y': "mass",
                'color': color, 'marker': "x", 'ms': 5., 'alpha': alpha,
                'xmin': -10, 'xmax': 100, 'ymin': 0, 'ymax': .3,
                'xlabel': Labels.labels("t-tmerg"), 'ylabel': Labels.labels("diskmass"),
                'label': None, 'yscale': 'linear',
                'fancyticks': True, 'minorticks': True,
                'fontsize': 14,
                'labelsize': 14,
                'legend': {}  # 'loc': 'best', 'ncol': 2, 'fontsize': 18
            }
            o_plot.set_plot_dics.append(tcoll_dic)
        #
        plot_dic = {
            'task': 'line', 'ptype': 'cartesian',
            'position': (1, 1),
            'xarr': tarr, 'yarr': marr,
            'v_n_x': "time", 'v_n_y': "mass",
            'color': color, 'ls': ls, 'lw': 0.8, 'ds': 'steps', 'alpha': 1.0,
            'xmin': -10, 'xmax': 100, 'ymin': 0, 'ymax': .35,
            'xlabel': Labels.labels("t-tmerg"), 'ylabel': Labels.labels("diskmass"),
            'label': str(sim).replace('_', '\_'), 'yscale': 'linear',
            'fancyticks': True, 'minorticks': True,
            'fontsize': 14,
            'labelsize': 14,
            'legend': {'bbox_to_anchor': (1.1, 1.05),
                       'loc': 'lower right', 'ncol': 2, 'fontsize': 8}  # 'loc': 'best', 'ncol': 2, 'fontsize': 18
        }
        if sim == sims[-1]:
            plot_dic['legend'] = {'bbox_to_anchor': (1.1, 1.05),
                                  'loc': 'lower right', 'ncol': 2, 'fontsize': 8}
        o_plot.set_plot_dics.append(plot_dic)

    o_plot.main()
    exit(1)


def plot_disk_mass_evol_LR():
    sims = ["BLh_M16351146_M0_LK_LR", "SLy4_M10651772_M0_LK_LR", "SFHo_M10651772_M0_LK_LR", "SFHo_M16351146_M0_LK_LR",
            "LS220_M10651772_M0_LK_LR", "LS220_M16351146_M0_LK_LR", "DD2_M16351146_M0_LK_LR"] + \
           ["DD2_M13641364_M0_LR", "LS220_M13641364_M0_LR"] + \
           ["DD2_M14971246_M0_LR", "DD2_M14861254_M0_LR", "DD2_M14351298_M0_LR", "DD2_M14321300_M0_LR",
            "SLy4_M14521283_M0_LR"]
    #
    colors = ["black", "orange", "pink", "olive", "red", "purple", "blue"] + \
             ["blue", "red"] + \
             ["darkblue", "blue", "cornflowerblue", "orange"]
    #
    lss = ["-", "-", "-", "-", "-", "-"] + \
          ['--', '--', '--'] + \
          ["-.", "-.", "-.", "-."]
    #
    lws = [1., 1., 1., 1., 1., 1., 1.] + \
          [1., 1.] + \
          [1., 1., 1., 1., 1.]
    #
    alphas = [1., 1., 1., 1., 1., 1., 1.] + \
             [1., 1.] + \
             [1., 1., 1., 1., 1.]

    o_plot = PLOT_MANY_TASKS()
    o_plot.gen_set["figdir"] = Paths.plots + "all2/"
    o_plot.gen_set["type"] = "cartesian"
    o_plot.gen_set["figsize"] = (4.2, 3.6)  # <->, |]
    o_plot.gen_set["figname"] = "disk_mass_evol_LR.png"
    o_plot.gen_set["sharex"] = False
    o_plot.gen_set["sharey"] = True
    o_plot.gen_set["dpi"] = 128
    o_plot.gen_set["subplots_adjust_h"] = 0.3
    o_plot.gen_set["subplots_adjust_w"] = 0.0
    o_plot.set_plot_dics = []

    for sim, color, ls, lw, alpha in zip(sims, colors, lss, lws, alphas):
        print("{}".format(sim))
        o_data = ADD_METHODS_ALL_PAR(sim)
        data = o_data.get_disk_mass()
        assert len(data) > 0
        tmerg = o_data.get_par("tmerg")
        tarr = (data[:, 0] - tmerg) * 1e3
        marr = data[:, 1]

        if sim == "DD2_M13641364_M0_LK_SR_R04":
            tarr = tarr[3:]  # 3ms, 6ms, 51ms.... Removing initial profiles
            marr = marr[3:]  #
        #
        tcoll = o_data.get_par("tcoll_gw")
        if not np.isnan(tcoll) and tcoll < tarr[-1]:
            tcoll = (tcoll - tmerg) * 1e3
            print(tcoll, tarr[0])
            mcoll = interpolate.interp1d(tarr, marr, kind="linear")(tcoll)
            tcoll_dic = {
                'task': 'line', 'ptype': 'cartesian',
                'position': (1, 1),
                'xarr': [tcoll], 'yarr': [mcoll],
                'v_n_x': "time", 'v_n_y': "mass",
                'color': color, 'marker': "x", 'ms': 5., 'alpha': alpha,
                'xmin': -10, 'xmax': 40, 'ymin': 0, 'ymax': .3,
                'xlabel': Labels.labels("t-tmerg"), 'ylabel': Labels.labels("diskmass"),
                'label': None, 'yscale': 'linear',
                'fancyticks': True, 'minorticks': True,
                'fontsize': 14,
                'labelsize': 14,
                'legend': {}  # 'loc': 'best', 'ncol': 2, 'fontsize': 18
            }
            o_plot.set_plot_dics.append(tcoll_dic)
        #
        plot_dic = {
            'task': 'line', 'ptype': 'cartesian',
            'position': (1, 1),
            'xarr': tarr, 'yarr': marr,
            'v_n_x': "time", 'v_n_y': "mass",
            'color': color, 'ls': ls, 'lw': 0.8, 'ds': 'steps', 'alpha': 1.0,
            'xmin': -10, 'xmax': 40, 'ymin': 0, 'ymax': .35,
            'xlabel': Labels.labels("t-tmerg"), 'ylabel': Labels.labels("diskmass"),
            'label': str(sim).replace('_', '\_'), 'yscale': 'linear',
            'fancyticks': True, 'minorticks': True,
            'fontsize': 14,
            'labelsize': 14,
            'legend': {'bbox_to_anchor': (1.1, 1.05),
                       'loc': 'lower right', 'ncol': 2, 'fontsize': 8}  # 'loc': 'best', 'ncol': 2, 'fontsize': 18
        }
        if sim == sims[-1]:
            plot_dic['legend'] = {'bbox_to_anchor': (1.1, 1.05),
                                  'loc': 'lower right', 'ncol': 2, 'fontsize': 8}
        o_plot.set_plot_dics.append(plot_dic)

    o_plot.main()
    exit(1)


def plot_disk_mass_evol_HR():
    #
    # SFHo_M14521283_M0_HR, SFHo_M13641364_M0_HR, DD2_M14971245_M0_HR, DD2_M14861254_M0_HR
    #

    sims = ["SFHo_M13641364_M0_HR",
            "DD2_M14971245_M0_HR", "DD2_M14861254_M0_HR", "SFHo_M14521283_M0_HR"]
    #
    colors = ["green",
              "blue", "cornflowerblue", "green"]
    #
    lss = ['--'] + \
          ["-.", "-.", "-."]
    #
    lws = [1., ] + \
          [1., 1., 1.]
    #
    alphas = [1.] + \
             [1., 1., 1.]

    o_plot = PLOT_MANY_TASKS()
    o_plot.gen_set["figdir"] = Paths.plots + "all2/"
    o_plot.gen_set["type"] = "cartesian"
    o_plot.gen_set["figsize"] = (4.2, 3.6)  # <->, |]
    o_plot.gen_set["figname"] = "disk_mass_evol_HR.png"
    o_plot.gen_set["sharex"] = False
    o_plot.gen_set["sharey"] = True
    o_plot.gen_set["dpi"] = 128
    o_plot.gen_set["subplots_adjust_h"] = 0.3
    o_plot.gen_set["subplots_adjust_w"] = 0.0
    o_plot.set_plot_dics = []

    for sim, color, ls, lw, alpha in zip(sims, colors, lss, lws, alphas):
        if not sim.__contains__("10651772"):
            print("{}".format(sim))
            o_data = ADD_METHODS_ALL_PAR(sim)
            data = o_data.get_disk_mass()
            assert len(data) > 0
            tmerg = o_data.get_par("tmerg")
            tarr = (data[:, 0] - tmerg) * 1e3
            marr = data[:, 1]

            if sim == "DD2_M13641364_M0_LK_SR_R04":
                tarr = tarr[3:]  # 3ms, 6ms, 51ms.... Removing initial profiles
                marr = marr[3:]  #
            #
            tcoll = o_data.get_par("tcoll_gw")
            if not np.isnan(tcoll) and tcoll < tarr[-1]:
                tcoll = (tcoll - tmerg) * 1e3
                print(tcoll, tarr[0])
                mcoll = interpolate.interp1d(tarr, marr, kind="linear")(tcoll)
                tcoll_dic = {
                    'task': 'line', 'ptype': 'cartesian',
                    'position': (1, 1),
                    'xarr': [tcoll], 'yarr': [mcoll],
                    'v_n_x': "time", 'v_n_y': "mass",
                    'color': color, 'marker': "x", 'ms': 5., 'alpha': alpha,
                    'xmin': -10, 'xmax': 40, 'ymin': 0, 'ymax': .3,
                    'xlabel': Labels.labels("t-tmerg"), 'ylabel': Labels.labels("diskmass"),
                    'label': None, 'yscale': 'linear',
                    'fancyticks': True, 'minorticks': True,
                    'fontsize': 14,
                    'labelsize': 14,
                    'legend': {}  # 'loc': 'best', 'ncol': 2, 'fontsize': 18
                }
                o_plot.set_plot_dics.append(tcoll_dic)
            #
            plot_dic = {
                'task': 'line', 'ptype': 'cartesian',
                'position': (1, 1),
                'xarr': tarr, 'yarr': marr,
                'v_n_x': "time", 'v_n_y': "mass",
                'color': color, 'ls': ls, 'lw': 0.8, 'ds': 'steps', 'alpha': 1.0,
                'xmin': -10, 'xmax': 40, 'ymin': 0, 'ymax': .35,
                'xlabel': Labels.labels("t-tmerg"), 'ylabel': Labels.labels("diskmass"),
                'label': str(sim).replace('_', '\_'), 'yscale': 'linear',
                'fancyticks': True, 'minorticks': True,
                'fontsize': 14,
                'labelsize': 14,
                'legend': {'bbox_to_anchor': (1.1, 1.05),
                           'loc': 'lower right', 'ncol': 2, 'fontsize': 8}  # 'loc': 'best', 'ncol': 2, 'fontsize': 18
            }
            if sim == sims[-1]:
                plot_dic['legend'] = {'bbox_to_anchor': (1.1, 1.05),
                                      'loc': 'lower right', 'ncol': 2, 'fontsize': 8}
            o_plot.set_plot_dics.append(plot_dic)

    o_plot.main()
    exit(1)


''' disk slice xy-xz '''


def plot_den_unb__vel_z_sly4_evol():
    # tmp = d3class.get_data(688128, 3, "xy", "ang_mom_flux")
    # print(tmp.min(), tmp.max())
    # print(tmp)
    # exit(1) # dens_unb_geo

    """ --- --- --- """

    '''sly4 '''
    simlist = ["SLy4_M13641364_M0_SR", "SLy4_M13641364_M0_SR", "SLy4_M13641364_M0_SR", "SLy4_M13641364_M0_SR"]
    # itlist = [434176, 475136, 516096, 565248]
    # itlist = [606208, 647168, 696320, 737280]
    # itlist = [434176, 516096, 647168, 737280]
    ''' ls220 '''
    simlist = ["LS220_M14691268_M0_LK_SR", "LS220_M14691268_M0_LK_SR",
               "LS220_M14691268_M0_LK_SR"]  # , "LS220_M14691268_M0_LK_SR"]
    itlist = [1515520, 1728512, 1949696]  # , 2162688]
    ''' dd2 '''
    simlist = ["DD2_M13641364_M0_LK_SR_R04", "DD2_M13641364_M0_LK_SR_R04",
               "DD2_M13641364_M0_LK_SR_R04"]  # , "DD2_M13641364_M0_LK_SR_R04"]
    itlist = [1111116, 1741554, 2213326]  # ,2611022]
    #
    simlist = ["DD2_M13641364_M0_LK_SR_R04", "BLh_M13641364_M0_LK_SR", "LS220_M14691268_M0_LK_SR",
               "SLy4_M13641364_M0_SR"]
    itlist = [2611022, 1974272, 1949696, 737280]
    #

    #
    o_plot = PLOT_MANY_TASKS()
    o_plot.gen_set["figdir"] = Paths.plots + 'all2/'
    o_plot.gen_set["type"] = "cartesian"
    o_plot.gen_set["figsize"] = (4 * len(simlist), 6.0)  # <->, |] # to match hists with (8.5, 2.7)
    o_plot.gen_set["figname"] = "disk_structure_last.png".format(simlist[0])  # "DD2_1512_slices.png" # LS_1412_slices
    o_plot.gen_set["sharex"] = False
    o_plot.gen_set["sharey"] = True
    o_plot.gen_set["dpi"] = 128
    o_plot.gen_set["subplots_adjust_h"] = -0.35
    o_plot.gen_set["subplots_adjust_w"] = 0.05
    o_plot.set_plot_dics = []
    #
    rl = 3
    #
    o_plot.gen_set["figsize"] = (4.2 * len(simlist), 8.0)  # <->, |] # to match hists with (8.5, 2.7)

    plot_x_i = 1
    for sim, it in zip(simlist, itlist):
        print("sim:{} it:{}".format(sim, it))
        d3class = LOAD_PROFILE_XYXZ(sim)
        d1class = ADD_METHODS_ALL_PAR(sim)

        t = d3class.get_time_for_it(it, d1d2d3prof="prof")
        tmerg = d1class.get_par("tmerg")
        xmin, xmax, ymin, ymax, zmin, zmax = UTILS.get_xmin_xmax_ymin_ymax_zmin_zmax(rl)

        # --------------------------------------------------------------------------

        # --------------------------------------------------------------------------
        mask = "x>0"
        #
        v_n = "rho"
        data_arr = d3class.get_data(it, rl, "xz", v_n)
        x_arr = d3class.get_data(it, rl, "xz", "x")
        z_arr = d3class.get_data(it, rl, "xz", "z")
        # print(data_arr); exit(1)

        contour_dic_xz = {
            'task': 'contour',
            'ptype': 'cartesian', 'aspect': 1.,
            'xarr': x_arr, "yarr": z_arr, "zarr": data_arr, 'levels': [1.e13 / 6.176e+17],
            'position': (1, plot_x_i),  # 'title': '[{:.1f} ms]'.format(time_),
            'colors': ['white'], 'lss': ["-"], 'lws': [1.],
            'v_n_x': 'x', 'v_n_y': 'y', 'v_n': 'rho',
            'xscale': None, 'yscale': None,
            'fancyticks': True,
            'sharey': False,
            'sharex': True,  # removes angular citkscitks
            'fontsize': 14,
            'labelsize': 14}
        o_plot.set_plot_dics.append(contour_dic_xz)

        rho_dic_xz = {'task': 'colormesh', 'ptype': 'cartesian', 'aspect': 1.,
                      'xarr': x_arr, "yarr": z_arr, "zarr": data_arr,
                      'position': (1, plot_x_i),  # 'title': '[{:.1f} ms]'.format(time_),
                      'cbar': {},
                      'v_n_x': 'x', 'v_n_y': 'z', 'v_n': v_n,
                      'xmin': xmin, 'xmax': xmax, 'ymin': zmin, 'ymax': zmax, 'vmin': 1e-9, 'vmax': 1e-5,
                      'fill_vmin': False,  # fills the x < vmin with vmin
                      'xscale': None, 'yscale': None,
                      'mask': mask, 'cmap': 'Greys', 'norm': "log",
                      'fancyticks': True,
                      'minorticks': True,
                      'title': {"text": sim.replace('_', '\_'), 'fontsize': 12},
                      # 'title': {"text": r'$t-t_{merg}:$' + r'${:.1f}$ [ms]'.format((t - tmerg) * 1e3), 'fontsize': 14},
                      'sharey': False,
                      'sharex': True,  # removes angular citkscitks
                      'fontsize': 14,
                      'labelsize': 14
                      }
        #
        data_arr = d3class.get_data(it, rl, "xy", v_n)
        x_arr = d3class.get_data(it, rl, "xy", "x")
        y_arr = d3class.get_data(it, rl, "xy", "y")

        contour_dic_xy = {
            'task': 'contour',
            'ptype': 'cartesian', 'aspect': 1.,
            'xarr': x_arr, "yarr": y_arr, "zarr": data_arr, 'levels': [1.e13 / 6.176e+17],
            'position': (2, plot_x_i),  # 'title': '[{:.1f} ms]'.format(time_),
            'colors': ['white'], 'lss': ["-"], 'lws': [1.],
            'v_n_x': 'x', 'v_n_y': 'y', 'v_n': 'rho',
            'xscale': None, 'yscale': None,
            'fancyticks': True,
            'sharey': False,
            'sharex': True,  # removes angular citkscitks
            'fontsize': 14,
            'labelsize': 14}
        o_plot.set_plot_dics.append(contour_dic_xy)

        rho_dic_xy = {'task': 'colormesh', 'ptype': 'cartesian', 'aspect': 1.,
                      'xarr': x_arr, "yarr": y_arr, "zarr": data_arr,
                      'position': (2, plot_x_i),  # 'title': '[{:.1f} ms]'.format(time_),
                      'cbar': {},
                      'v_n_x': 'x', 'v_n_y': 'y', 'v_n': v_n,
                      'xmin': xmin, 'xmax': xmax, 'ymin': ymin, 'ymax': ymax, 'vmin': 1e-9, 'vmax': 1e-5,
                      'fill_vmin': False,  # fills the x < vmin with vmin
                      'xscale': None, 'yscale': None,
                      'mask': mask, 'cmap': 'Greys', 'norm': "log",
                      'fancyticks': True,
                      'minorticks': True,
                      'title': {},
                      'sharey': False,
                      'sharex': False,  # removes angular citkscitks
                      'fontsize': 14,
                      'labelsize': 14
                      }
        #
        if plot_x_i == 1:
            rho_dic_xy['cbar'] = {'location': 'bottom -.05 .00', 'label': r'$\rho$ [GEO]',  # 'fmt': '%.1e',
                                  'labelsize': 14,
                                  'fontsize': 14}
        if plot_x_i > 1:
            rho_dic_xz['sharey'] = True
            rho_dic_xy['sharey'] = True

        o_plot.set_plot_dics.append(rho_dic_xz)
        o_plot.set_plot_dics.append(rho_dic_xy)

        # ----------------------------------------------------------------------
        v_n = "dens_unb_bern"
        #
        data_arr = d3class.get_data(it, rl, "xz", v_n)
        x_arr = d3class.get_data(it, rl, "xz", "x")
        z_arr = d3class.get_data(it, rl, "xz", "z")
        dunb_dic_xz = {'task': 'colormesh', 'ptype': 'cartesian', 'aspect': 1.,
                       'xarr': x_arr, "yarr": z_arr, "zarr": data_arr,
                       'position': (1, plot_x_i),  # 'title': '[{:.1f} ms]'.format(time_),
                       'cbar': {},
                       'v_n_x': 'x', 'v_n_y': 'z', 'v_n': v_n,
                       'xmin': xmin, 'xmax': xmax, 'ymin': zmin, 'ymax': zmax, 'vmin': 1e-10, 'vmax': 1e-7,
                       'fill_vmin': False,  # fills the x < vmin with vmin
                       'xscale': None, 'yscale': None,
                       'mask': mask, 'cmap': 'Blues', 'norm': "log",
                       'fancyticks': True,
                       'minorticks': True,
                       'title': {},
                       # {"text": r'$t-t_{merg}:$' + r'${:.1f}$ [ms]'.format((t - tmerg) * 1e3), 'fontsize': 14},
                       'sharex': True,  # removes angular citkscitks
                       'sharey': False,
                       'fontsize': 14,
                       'labelsize': 14
                       }
        #
        data_arr = d3class.get_data(it, rl, "xy", v_n)
        x_arr = d3class.get_data(it, rl, "xy", "x")
        y_arr = d3class.get_data(it, rl, "xy", "y")
        dunb_dic_xy = {'task': 'colormesh', 'ptype': 'cartesian', 'aspect': 1.,
                       'xarr': x_arr, "yarr": y_arr, "zarr": data_arr,
                       'position': (2, plot_x_i),  # 'title': '[{:.1f} ms]'.format(time_),
                       'cbar': {},
                       'fill_vmin': False,  # fills the x < vmin with vmin
                       'v_n_x': 'x', 'v_n_y': 'y', 'v_n': v_n,
                       'xmin': xmin, 'xmax': xmax, 'ymin': ymin, 'ymax': ymax, 'vmin': 1e-10, 'vmax': 1e-7,
                       'xscale': None, 'yscale': None,
                       'mask': mask, 'cmap': 'Blues', 'norm': "log",
                       'fancyticks': True,
                       'minorticks': True,
                       'title': {},
                       'sharey': False,
                       'sharex': False,  # removes angular citkscitks
                       'fontsize': 14,
                       'labelsize': 14
                       }
        #
        if plot_x_i == 2:
            dunb_dic_xy['cbar'] = {'location': 'bottom -.05 .00', 'label': r'$D_{\rm{unb}}$ [GEO]',  # 'fmt': '%.1e',
                                   'labelsize': 14,
                                   'fontsize': 14}
        if plot_x_i > 1:
            dunb_dic_xz['sharey'] = True
            dunb_dic_xy['sharey'] = True

        o_plot.set_plot_dics.append(dunb_dic_xz)
        o_plot.set_plot_dics.append(dunb_dic_xy)

        # ----------------------------------------------------------------------
        mask = "x<0"
        #
        v_n = "Ye"
        cmap = "bwr_r"
        #
        data_arr = d3class.get_data(it, rl, "xz", v_n)
        x_arr = d3class.get_data(it, rl, "xz", "x")
        z_arr = d3class.get_data(it, rl, "xz", "z")
        ye_dic_xz = {'task': 'colormesh', 'ptype': 'cartesian', 'aspect': 1.,
                     'xarr': x_arr, "yarr": z_arr, "zarr": data_arr,
                     'position': (1, plot_x_i),  # 'title': '[{:.1f} ms]'.format(time_),
                     'cbar': {},
                     'fill_vmin': False,  # fills the x < vmin with vmin
                     'v_n_x': 'x', 'v_n_y': 'z', 'v_n': v_n,
                     'xmin': xmin, 'xmax': xmax, 'ymin': zmin, 'ymax': zmax, 'vmin': 0.05, 'vmax': 0.5,
                     'xscale': None, 'yscale': None,
                     'mask': mask, 'cmap': cmap, 'norm': None,
                     'fancyticks': True,
                     'minorticks': True,
                     'title': {},
                     # {"text": r'$t-t_{merg}:$' + r'${:.1f}$ [ms]'.format((t - tmerg) * 1e3), 'fontsize': 14},
                     'sharey': False,
                     'sharex': True,  # removes angular citkscitks
                     'fontsize': 14,
                     'labelsize': 14
                     }
        #
        data_arr = d3class.get_data(it, rl, "xy", v_n)
        x_arr = d3class.get_data(it, rl, "xy", "x")
        y_arr = d3class.get_data(it, rl, "xy", "y")
        ye_dic_xy = {'task': 'colormesh', 'ptype': 'cartesian', 'aspect': 1.,
                     'xarr': x_arr, "yarr": y_arr, "zarr": data_arr,
                     'position': (2, plot_x_i),  # 'title': '[{:.1f} ms]'.format(time_),
                     'cbar': {},
                     'fill_vmin': False,  # fills the x < vmin with vmin
                     'v_n_x': 'x', 'v_n_y': 'y', 'v_n': v_n,
                     'xmin': xmin, 'xmax': xmax, 'ymin': ymin, 'ymax': ymax, 'vmin': 0.01, 'vmax': 0.5,
                     'xscale': None, 'yscale': None,
                     'mask': mask, 'cmap': cmap, 'norm': None,
                     'fancyticks': True,
                     'minorticks': True,
                     'title': {},
                     'sharey': False,
                     'sharex': False,  # removes angular citkscitks
                     'fontsize': 14,
                     'labelsize': 14
                     }
        #
        if plot_x_i == 3:
            ye_dic_xy['cbar'] = {'location': 'bottom -.05 .00', 'label': r'$Y_e$', 'fmt': '%.1f',
                                 'labelsize': 14,
                                 'fontsize': 14}
        if plot_x_i > 1:
            ye_dic_xz['sharey'] = True
            ye_dic_xy['sharey'] = True

        o_plot.set_plot_dics.append(ye_dic_xz)
        o_plot.set_plot_dics.append(ye_dic_xy)

        # ----------------------------------------------------------
        tcoll = d1class.get_par("tcoll_gw")
        if not np.isnan(tcoll) and t >= tcoll:
            print(tcoll, t)
            v_n = "lapse"
            mask = "z>0.15"
            data_arr = d3class.get_data(it, rl, "xz", v_n)
            x_arr = d3class.get_data(it, rl, "xz", "x")
            z_arr = d3class.get_data(it, rl, "xz", "z")
            lapse_dic_xz = {'task': 'colormesh', 'ptype': 'cartesian', 'aspect': 1.,
                            'xarr': x_arr, "yarr": z_arr, "zarr": data_arr,
                            'position': (1, plot_x_i),  # 'title': '[{:.1f} ms]'.format(time_),
                            'cbar': {},
                            'v_n_x': 'x', 'v_n_y': 'z', 'v_n': v_n,
                            'xmin': xmin, 'xmax': xmax, 'ymin': zmin, 'ymax': zmax, 'vmin': 0., 'vmax': 0.15,
                            'fill_vmin': False,  # fills the x < vmin with vmin
                            'xscale': None, 'yscale': None,
                            'mask': mask, 'cmap': 'Greys', 'norm': None,
                            'fancyticks': True,
                            'minorticks': True,
                            'title': {},  # ,{"text": r'$t-t_{merg}:$' + r'${:.1f}$ [ms]'.format((t - tmerg) * 1e3),
                            # 'fontsize': 14},
                            'sharey': False,
                            'sharex': True,  # removes angular citkscitks
                            'fontsize': 14,
                            'labelsize': 14
                            }
            #
            data_arr = d3class.get_data(it, rl, "xy", v_n)
            # print(data_arr.min(), data_arr.max()); exit(1)
            x_arr = d3class.get_data(it, rl, "xy", "x")
            y_arr = d3class.get_data(it, rl, "xy", "y")
            lapse_dic_xy = {'task': 'colormesh', 'ptype': 'cartesian', 'aspect': 1.,
                            'xarr': x_arr, "yarr": y_arr, "zarr": data_arr,
                            'position': (2, plot_x_i),  # 'title': '[{:.1f} ms]'.format(time_),
                            'cbar': {},
                            'v_n_x': 'x', 'v_n_y': 'y', 'v_n': v_n,
                            'xmin': xmin, 'xmax': xmax, 'ymin': ymin, 'ymax': ymax, 'vmin': 0, 'vmax': 0.15,
                            'fill_vmin': False,  # fills the x < vmin with vmin
                            'xscale': None, 'yscale': None,
                            'mask': mask, 'cmap': 'Greys', 'norm': None,
                            'fancyticks': True,
                            'minorticks': True,
                            'title': {},
                            'sharey': False,
                            'sharex': False,  # removes angular citkscitks
                            'fontsize': 14,
                            'labelsize': 14
                            }
            #
            # if plot_x_i == 1:
            #     rho_dic_xy['cbar'] = {'location': 'bottom -.05 .00', 'label': r'$\rho$ [GEO]',  # 'fmt': '%.1e',
            #                           'labelsize': 14,
            #                           'fontsize': 14}
            if plot_x_i > 1:
                lapse_dic_xz['sharey'] = True
                lapse_dic_xy['sharey'] = True

            o_plot.set_plot_dics.append(lapse_dic_xz)
            o_plot.set_plot_dics.append(lapse_dic_xy)

        plot_x_i += 1

    o_plot.main()

    exit(0)


''' density moes '''


def plot_desity_modes():
    sims = ["DD2_M13641364_M0_SR", "DD2_M13641364_M0_LK_SR_R04", "DD2_M15091235_M0_LK_SR", "LS220_M14691268_M0_LK_SR"]
    lbls = ["DD2", "DD2 136 136", "DD2 151 124", "LS220 147 127"]
    ls_m1 = ["-", "-", '-', '-']
    ls_m2 = [":", ":", ":", ":"]
    colors = ["black", "green", "blue", "red"]
    lws_m1 = [1., 1., 1., 1.]
    lws_m2 = [0.8, 0.8, 0.8, 0.8]
    alphas = [1., 1., 1., 1.]
    #
    norm_to_m = 0
    #
    o_plot = PLOT_MANY_TASKS()
    o_plot.gen_set["figdir"] = Paths.plots + "all2/"
    o_plot.gen_set["type"] = "cartesian"
    o_plot.gen_set["figsize"] = (9.0, 2.7)  # <->, |]
    o_plot.gen_set["figname"] = "dm_dd2_dd2_ls220.png"
    o_plot.gen_set["sharex"] = False
    o_plot.gen_set["sharey"] = False
    o_plot.set_plot_dics = []
    #

    #
    for sim, lbl, ls1, ls2, color, lw1, lw2, alpha in zip(sims, lbls, ls_m1, ls_m2, colors, lws_m1, lws_m2, alphas):
        o_dm = LOAD_DENSITY_MODES(sim)
        o_dm.gen_set['fname'] = Paths.ppr_sims + sim + "/" + "profiles/" + "density_modes_lap15.h5"
        o_par = ADD_METHODS_ALL_PAR(sim)
        tmerg = o_par.get_par("tmerg")
        #
        mags1 = o_dm.get_data(1, "int_phi_r")
        mags1 = np.abs(mags1)
        if norm_to_m != None:
            # print('Normalizing')
            norm_int_phi_r1d = o_dm.get_data(norm_to_m, 'int_phi_r')
            # print(norm_int_phi_r1d); exit(1)
            mags1 = mags1 / abs(norm_int_phi_r1d)[0]
        times = o_dm.get_grid("times")
        #
        print(mags1)
        #
        times = (times - tmerg) * 1e3  # ms
        #
        densmode_m1 = {
            'task': 'line', 'ptype': 'cartesian',
            'xarr': times, 'yarr': mags1,
            'position': (1, 1),
            'v_n_x': 'times', 'v_n_y': 'int_phi_r abs',
            'ls': ls1, 'color': color, 'lw': lw1, 'ds': 'default', 'alpha': alpha,
            'label': lbl, 'ylabel': r'$C_m/C_0$ Magnitude', 'xlabel': Labels.labels("t-tmerg"),
            'xmin': 45, 'xmax': 110, 'ymin': 1e-5, 'ymax': 1e-1,
            'xscale': None, 'yscale': 'log', 'legend': {},
            'fancyticks': True, 'minorticks': True,
            'fontsize': 14,
            'labelsize': 14
        }
        #
        mags2 = o_dm.get_data(2, "int_phi_r")
        mags2 = np.abs(mags2)
        if norm_to_m != None:
            # print('Normalizing')
            norm_int_phi_r1d = o_dm.get_data(norm_to_m, 'int_phi_r')
            # print(norm_int_phi_r1d); exit(1)
            mags2 = mags2 / abs(norm_int_phi_r1d)[0]
        # times = (times - tmerg) * 1e3 # ms
        # print(mags2); exit(1)
        densmode_m2 = {
            'task': 'line', 'ptype': 'cartesian',
            'xarr': times, 'yarr': mags2,
            'position': (1, 1),
            'v_n_x': 'times', 'v_n_y': 'int_phi_r abs',
            'ls': ls2, 'color': color, 'lw': lw2, 'ds': 'default', 'alpha': alpha,
            'label': None, 'ylabel': r'$C_m/C_0$ Magnitude', 'xlabel': Labels.labels("t-tmerg"),
            'xmin': 45, 'xmax': 110, 'ymin': 1e-5, 'ymax': 1e-1,
            'xscale': None, 'yscale': 'log',
            'fancyticks': True, 'minorticks': True,
            'legend': {'loc': 'best', 'ncol': 1, 'fontsize': 12},
            'fontsize': 14,
            'labelsize': 14
        }
        #
        o_plot.set_plot_dics.append(densmode_m1)
        o_plot.set_plot_dics.append(densmode_m2)
        #
    o_plot.main()
    exit(1)


def plot_desity_modes2():
    _fpath = "slices/" + "rho_modes.h5"  # "profiles/" + "density_modes_lap15.h5"
    sims = ["DD2_M13641364_M0_SR", "DD2_M13641364_M0_LK_SR_R04"]
    lbls = ["DD2 136 136", "DD2 136 136 LK"]
    ls_m1 = ["-", "-"]
    ls_m2 = [":", ":"]
    colors = ["green", "orange"]
    lws_m1 = [1., 1., ]
    lws_m2 = [0.8, 0.8]
    alphas = [1., 1.]
    #
    norm_to_m = 0
    #
    o_plot = PLOT_MANY_TASKS()
    o_plot.gen_set["figdir"] = Paths.plots + "all2/"
    o_plot.gen_set["type"] = "cartesian"
    o_plot.gen_set["figsize"] = (9.0, 3.6)  # <->, |]
    o_plot.gen_set["figname"] = "dm_dd2_dd2_ls220.png"
    o_plot.gen_set["sharex"] = False
    o_plot.gen_set["sharey"] = False
    o_plot.gen_set["subplots_adjust_h"] = 0.2
    o_plot.gen_set["subplots_adjust_w"] = 0.0
    o_plot.set_plot_dics = []
    #

    #
    for sim, lbl, ls1, ls2, color, lw1, lw2, alpha in zip(sims, lbls, ls_m1, ls_m2, colors, lws_m1, lws_m2, alphas):
        o_dm = LOAD_DENSITY_MODES(sim)
        o_dm.gen_set['fname'] = Paths.ppr_sims + sim + "/" + _fpath
        o_par = ADD_METHODS_ALL_PAR(sim)
        tmerg = o_par.get_par("tmerg")
        #
        mags1 = o_dm.get_data(1, "int_phi_r")
        mags1 = np.abs(mags1)
        if norm_to_m != None:
            # print('Normalizing')
            norm_int_phi_r1d = o_dm.get_data(norm_to_m, 'int_phi_r')
            # print(norm_int_phi_r1d); exit(1)
            mags1 = mags1 / abs(norm_int_phi_r1d)[0]
        times = o_dm.get_grid("times")
        #
        print(mags1)
        #
        times = (times - tmerg) * 1e3  # ms
        #
        densmode_m1 = {
            'task': 'line', 'ptype': 'cartesian',
            'xarr': times, 'yarr': mags1,
            'position': (1, 1),
            'v_n_x': 'times', 'v_n_y': 'int_phi_r abs',
            'ls': ls1, 'color': 'gray', 'lw': lw1, 'ds': 'default', 'alpha': alpha,
            'label': None, 'ylabel': None, 'xlabel': Labels.labels("t-tmerg"),
            'xmin': -10, 'xmax': 110, 'ymin': 1e-4, 'ymax': 5e-1,
            'xscale': None, 'yscale': 'log', 'legend': {},
            'fancyticks': True, 'minorticks': True,
            'fontsize': 14,
            'labelsize': 14
        }
        #
        mags2 = o_dm.get_data(2, "int_phi_r")
        mags2 = np.abs(mags2)
        if norm_to_m != None:
            # print('Normalizing')
            norm_int_phi_r1d = o_dm.get_data(norm_to_m, 'int_phi_r')
            # print(norm_int_phi_r1d); exit(1)
            mags2 = mags2 / abs(norm_int_phi_r1d)[0]
        # times = (times - tmerg) * 1e3 # ms
        # print(mags2); exit(1)
        densmode_m2 = {
            'task': 'line', 'ptype': 'cartesian',
            'xarr': times, 'yarr': mags2,
            'position': (1, 1),
            'v_n_x': 'times', 'v_n_y': 'int_phi_r abs',
            'ls': ls2, 'color': 'gray', 'lw': lw2, 'ds': 'default', 'alpha': alpha,
            'label': None, 'ylabel': r'$C_m/C_0$', 'xlabel': Labels.labels("t-tmerg"),
            'xmin': 0, 'xmax': 110, 'ymin': 1e-4, 'ymax': 5e-1,
            'xscale': None, 'yscale': 'log',
            'fancyticks': True, 'minorticks': True,
            'legend': {},
            'fontsize': 14,
            'labelsize': 14,
            'title': {'text': "Density Mode Evolution", 'fontsize': 14}
            # 'sharex': True
        }
        #
        if sim == sims[0]:
            densmode_m1['label'] = r"$m=1$"
            densmode_m2['label'] = r"$m=2$"
        o_plot.set_plot_dics.append(densmode_m1)
        o_plot.set_plot_dics.append(densmode_m2)
        #
        # ---
        #
        densmode_m1 = {
            'task': 'line', 'ptype': 'cartesian',
            'xarr': times, 'yarr': mags1,
            'position': (1, 1),
            'v_n_x': 'times', 'v_n_y': 'int_phi_r abs',
            'ls': ls1, 'color': color, 'lw': lw1, 'ds': 'default', 'alpha': alpha,
            'label': None, 'ylabel': None, 'xlabel': Labels.labels("t-tmerg"),
            'xmin': -10, 'xmax': 110, 'ymin': 1e-4, 'ymax': 5e-1,
            'xscale': None, 'yscale': 'log',
            'fancyticks': True, 'minorticks': True,
            'legend': {'loc': 'upper right', 'ncol': 2, 'fontsize': 12, 'shadow': False, 'framealpha': 0.5,
                       'borderaxespad': 0.0},
            'fontsize': 14,
            'labelsize': 14
        }
        #
        mags2 = o_dm.get_data(2, "int_phi_r")
        mags2 = np.abs(mags2)
        if norm_to_m != None:
            # print('Normalizing')
            norm_int_phi_r1d = o_dm.get_data(norm_to_m, 'int_phi_r')
            # print(norm_int_phi_r1d); exit(1)
            mags2 = mags2 / abs(norm_int_phi_r1d)[0]
        # times = (times - tmerg) * 1e3 # ms
        # print(mags2); exit(1)
        densmode_m2 = {
            'task': 'line', 'ptype': 'cartesian',
            'xarr': times, 'yarr': mags2,
            'position': (1, 1),
            'v_n_x': 'times', 'v_n_y': 'int_phi_r abs',
            'ls': ls2, 'color': color, 'lw': lw2, 'ds': 'default', 'alpha': alpha,
            'label': None, 'ylabel': r'$C_m/C_0$', 'xlabel': Labels.labels("t-tmerg"),
            'xmin': 0, 'xmax': 110, 'ymin': 1e-4, 'ymax': 5e-1,
            'xscale': None, 'yscale': 'log',
            'fancyticks': True, 'minorticks': True,
            # 'legend2': {'loc': 'lower right', 'ncol': 1, 'fontsize': 12, 'shadow':False, 'framealpha': 1.0, 'borderaxespad':0.0},
            'fontsize': 14,
            'labelsize': 14,
            'title': {'text': "Density Mode Evolution", 'fontsize': 14}
            # 'sharex': True
        }
        #
        if sim == sims[0]:
            densmode_m1['label'] = "DD2 136 136"
        else:
            densmode_m1['label'] = "DD2 136 136 Viscosity"
        o_plot.set_plot_dics.append(densmode_m1)
        o_plot.set_plot_dics.append(densmode_m2)

    #
    _fpath = "profiles/" + "density_modes_lap15.h5"

    #
    sims = ["LS220_M13641364_M0_SR", "LS220_M13641364_M0_LK_SR_restart"]
    lbls = ["LS220 136 136", "LS220 136 136 LK"]
    ls_m1 = ["-", "-"]
    ls_m2 = [":", ":"]
    colors = ["green", "orange"]
    lws_m1 = [1., 1., ]
    lws_m2 = [0.8, 0.8]
    alphas = [1., 1.]
    #
    for sim, lbl, ls1, ls2, color, lw1, lw2, alpha in zip(sims, lbls, ls_m1, ls_m2, colors, lws_m1, lws_m2, alphas):
        o_dm = LOAD_DENSITY_MODES(sim)
        o_dm.gen_set['fname'] = Paths.ppr_sims + sim + "/" + _fpath
        o_par = ADD_METHODS_ALL_PAR(sim)
        tmerg = o_par.get_par("tmerg")
        #
        mags1 = o_dm.get_data(1, "int_phi_r")
        mags1 = np.abs(mags1)
        if norm_to_m != None:
            # print('Normalizing')
            norm_int_phi_r1d = o_dm.get_data(norm_to_m, 'int_phi_r')
            # print(norm_int_phi_r1d); exit(1)
            mags1 = mags1 / abs(norm_int_phi_r1d)[0]
        times = o_dm.get_grid("times")
        #
        print(mags1)
        #
        times = (times - tmerg) * 1e3  # ms
        #
        densmode_m1 = {
            'task': 'line', 'ptype': 'cartesian',
            'xarr': times, 'yarr': mags1,
            'position': (2, 1),
            'v_n_x': 'times', 'v_n_y': 'int_phi_r abs',
            'ls': ls1, 'color': color, 'lw': lw1, 'ds': 'default', 'alpha': alpha,
            'label': lbl, 'ylabel': r'$C_m/C_0$ Magnitude', 'xlabel': Labels.labels("t-tmerg"),
            'xmin': -0, 'xmax': 50, 'ymin': 1e-5, 'ymax': 5e-1,
            'xscale': None, 'yscale': 'log', 'legend': {},
            'fancyticks': True,
            'minorticks': True,
            'fontsize': 14,
            'labelsize': 14
        }
        #
        mags2 = o_dm.get_data(2, "int_phi_r")
        mags2 = np.abs(mags2)
        if norm_to_m != None:
            # print('Normalizing')
            norm_int_phi_r1d = o_dm.get_data(norm_to_m, 'int_phi_r')
            # print(norm_int_phi_r1d); exit(1)
            mags2 = mags2 / abs(norm_int_phi_r1d)[0]
        # times = (times - tmerg) * 1e3 # ms
        # print(mags2); exit(1)
        densmode_m2 = {
            'task': 'line', 'ptype': 'cartesian',
            'xarr': times, 'yarr': mags2,
            'position': (2, 1),
            'v_n_x': 'times', 'v_n_y': 'int_phi_r abs',
            'ls': ls2, 'color': color, 'lw': lw2, 'ds': 'default', 'alpha': alpha,
            'label': None, 'ylabel': r'$C_m/C_0$', 'xlabel': Labels.labels("t-tmerg"),
            'xmin': 0, 'xmax': 40, 'ymin': 1e-5, 'ymax': 5e-1,
            'xscale': None, 'yscale': 'log',
            'fancyticks': True,
            'minorticks': True,
            'legend': {'loc': 'best', 'ncol': 1, 'fontsize': 12, 'shadow': False, 'framealpha': 1.0,
                       'borderaxespad': 0.0},
            'fontsize': 14,
            'labelsize': 14
        }
        #
        if sim == sims[0]:
            densmode_m1['label'] = "LS220 136 136"
        else:
            densmode_m1['label'] = "LS220 136 136 Viscosity"
        o_plot.set_plot_dics.append(densmode_m1)
        o_plot.set_plot_dics.append(densmode_m2)

    o_plot.main()
    exit(1)


''' Nucleo '''


def many_yeilds():
    sims = ["DD2_M14971245_M0_SR", "DD2_M13641364_M0_SR", "DD2_M15091235_M0_LK_SR", "BLh_M13641364_M0_LK_SR",
            "LS220_M14691268_M0_LK_SR"]
    lbls = [sim.replace('_', '\_') for sim in sims]
    masks = ["geo", "geo", "geo", "geo", "geo"]
    # masks = ["geo bern_geoend", "geo bern_geoend", "geo bern_geoend", "geo bern_geoend", "geo bern_geoend"]
    colors = ["blue", "cyan", "green", "black", "red"]
    alphas = [1., 1., 1., 1., 1.]
    lss = ['-', '-', '-', '-', '-']
    lws = [1., 1., 1., 1., 1.]
    det = 0
    method = "sum"  # "Asol=195"
    #
    sims = ["BLh_M11841581_M0_LK_SR",
            "DD2_M13641364_M0_LK_SR_R04", "DD2_M13641364_M0_SR_R04", "DD2_M15091235_M0_LK_SR", "DD2_M14971245_M0_SR",
            "LS220_M13641364_M0_LK_SR_restart", "LS220_M13641364_M0_SR", "LS220_M14691268_M0_LK_SR", "LS220_M14351298_M0_SR",  # "LS220_M14691268_M0_SR",
            "SFHo_M13641364_M0_LK_SR_2019pizza", "SFHo_M13641364_M0_SR", "SFHo_M14521283_M0_LK_SR_2019pizza", "SFHo_M14521283_M0_SR",
            "SLy4_M13641364_M0_LK_SR", "SLy4_M14521283_M0_SR"]

    lbls = [sim.replace('_', '\_') for sim in sims]
    masks = ["geo",
             "geo", "geo", "geo", "geo",
             "geo", "geo", "geo", "geo",
             "geo", "geo", "geo", "geo",
             "geo", "geo"]
    # masks = ["geo bern_geoend", "geo bern_geoend", "geo bern_geoend", "geo bern_geoend", "geo bern_geoend"]
    colors = ["black",
              "blue", "blue", "blue", "blue",
              "red", "red", "red", "red",
              "green", "green", "green", "green",
              "orange", "orange"]
    alphas = [1.,
              1., 1., 1., 1.,
              1., 1., 1., 1.,
              1., 1., 1., 1.,
              1., 1.]
    lss = ['-',
           '-', '--', '-.', ':',
           '-', '--', '-.', ':',
           '-', '--', '-.', ':',
           '-', '--']
    lws = [1.,
           1., 0.8, 0.5, 0.5,
           1., 0.8, 0.5, 0.5,
           1., 0.8, 0.5, 0.5,
           1., 0.8]
    det = 0
    method = "Asol=195"  # "Asol=195"
    #
    o_plot = PLOT_MANY_TASKS()
    o_plot.gen_set["figdir"] = Paths.plots + "all2/"
    o_plot.gen_set["type"] = "cartesian"
    o_plot.gen_set["figsize"] = (4.2, 3.6)  # <->, |]
    o_plot.gen_set["figname"] = "yields_all_geo.png"
    o_plot.gen_set["sharex"] = False
    o_plot.gen_set["sharey"] = False
    o_plot.gen_set["dpi"] = 128
    o_plot.gen_set["subplots_adjust_h"] = 0.3
    o_plot.gen_set["subplots_adjust_w"] = 0.0
    o_plot.set_plot_dics = []
    #
    o_data = ADD_METHODS_ALL_PAR(sims[0])
    a_sol, y_sol = o_data.get_normalized_sol_data("sum")
    sol_yeilds = {
        'task': 'line', 'ptype': 'cartesian',
        'position': (1, 1),
        'xarr': a_sol, 'yarr': y_sol,
        'v_n_x': 'Asun', 'v_n_y': 'Ysun',
        'color': 'gray', 'marker': 'o', 'ms': 4, 'alpha': 0.4,
        'ymin': 1e-5, 'ymax': 2e-1, 'xmin': 50, 'xmax': 210,
        'xlabel': Labels.labels("A"), 'ylabel': Labels.labels("Y_final"),
        'label': 'solar', 'yscale': 'log',
        'fancyticks': True, 'minorticks': True,
        'fontsize': 14,
        'labelsize': 14,
    }
    o_plot.set_plot_dics.append(sol_yeilds)

    for sim, mask, color, ls, alpha, lw, lbl in zip(sims, masks, colors, lss, alphas, lws, lbls):
        o_data = ADD_METHODS_ALL_PAR(sim, add_mask=mask)
        a_sim, y_sim = o_data.get_outflow_yields(det, mask, method=method)
        sim_nucleo = {
            'task': 'line', 'ptype': 'cartesian',
            'position': (1, 1),
            'xarr': a_sim, 'yarr': y_sim,
            'v_n_x': 'A', 'v_n_y': 'abundances',
            'color': color, 'ls': ls, 'lw': lw, 'ds': 'steps', 'alpha': alpha,
            'ymin': 1e-5, 'ymax': 2e-1, 'xmin': 50, 'xmax': 210,
            'xlabel': Labels.labels("A"), 'ylabel': Labels.labels("Y_final"),
            'label': lbl, 'yscale': 'log',
            'fancyticks': True, 'minorticks': True,
            'fontsize': 14,
            'labelsize': 14,
        }

        if sim == sims[-1]:
            sim_nucleo['legend'] = {
                'bbox_to_anchor': (1.0, -0.1),
                # 'loc': 'lower left',
                'loc': 'lower left', 'ncol': 1, 'fontsize': 9, 'framealpha': 0., 'borderaxespad': 0.,
                                    'borderayespad': 0.}

        o_plot.set_plot_dics.append(sim_nucleo)

    o_plot.main()
    exit(1)


def tmp_many_yeilds():
    # sims = ["DD2_M14971245_M0_SR", "DD2_M13641364_M0_SR", "DD2_M15091235_M0_LK_SR", "BLh_M13641364_M0_LK_SR",
    #         "LS220_M14691268_M0_LK_SR"] # long-lasting sims

    sims = ["BLh_M11841581_M0_LK_SR",
            "DD2_M13641364_M0_LK_SR_R04", "DD2_M13641364_M0_SR_R04", "DD2_M15091235_M0_LK_SR", "DD2_M14971245_M0_SR",
            "LS220_M13641364_M0_LK_SR_restart", "LS220_M13641364_M0_SR", "LS220_M14691268_M0_LK_SR", "LS220_M14351298_M0_SR", #"LS220_M14691268_M0_SR",
            "SFHo_M13641364_M0_LK_SR_2019pizza", "SFHo_M13641364_M0_SR", "SFHo_M14521283_M0_LK_SR_2019pizza", "SFHo_M14521283_M0_SR",
            "SLy4_M13641364_M0_LK_SR", "SLy4_M14521283_M0_SR"]

    lbls = [sim.replace('_', '\_') for sim in sims]
    masks = ["geo",
             "geo", "geo", "geo", "geo",
             "geo", "geo", "geo", "geo", "geo",
             "geo", "geo", "geo", "geo",
             "geo", "geo"]
    # masks = ["geo bern_geoend", "geo bern_geoend", "geo bern_geoend", "geo bern_geoend", "geo bern_geoend"]
    colors = ["black",
              "blue", "blue", "blue", "blue",
              "red", "red", "red", "red", "red",
              "green", "green", "green", "green",
              "orange", "orange"]
    alphas = [1.,
              1., 1., 1., 1.,
              1., 1., 1., 1., 1.,
              1., 1., 1., 1.,
              1., 1.]
    lss = ['-',
           '-', '--', '-.', ':',
           '-', '--', '-.', ':', '-',
           '-', '--', '-.', ':',
           '-', '--']
    lws = [1.,
            1., 0.8, 0.5, 0.5,
            1., 0.8, 0.5, 0.5, 0.5,
            1., 0.8, 0.5, 0.5,
            1., 0.8]
    det = 0
    method = "Asol=195"  # "Asol=195"
    #
    o_plot = PLOT_MANY_TASKS()
    o_plot.gen_set["figdir"] = Paths.plots + "all2/"
    o_plot.gen_set["type"] = "cartesian"
    o_plot.gen_set["figsize"] = (16.2, 3.6)  # <->, |]
    o_plot.gen_set["figname"] = "yields_all_geo.png"
    o_plot.gen_set["sharex"] = False
    o_plot.gen_set["sharey"] = False
    o_plot.gen_set["dpi"] = 128
    o_plot.gen_set["subplots_adjust_h"] = 0.3
    o_plot.gen_set["subplots_adjust_w"] = 0.0
    o_plot.set_plot_dics = []
    #
    o_data = ADD_METHODS_ALL_PAR(sims[0])
    a_sol, y_sol = o_data.get_normalized_sol_data("sum")
    sol_yeilds = {
        'task': 'line', 'ptype': 'cartesian',
        'position': (1, 1),
        'xarr': a_sol, 'yarr': y_sol,
        'v_n_x': 'Asun', 'v_n_y': 'Ysun',
        'color': 'gray', 'marker': 'o', 'ms': 4, 'alpha': 0.4,
        'ymin': 1e-5, 'ymax': 8e-1, 'xmin': 50, 'xmax': 230,
        'xlabel': Labels.labels("A"), 'ylabel': Labels.labels("Y_final"),
        'label': 'solar', 'yscale': 'log',
        'fancyticks': True, 'minorticks': True,
        'fontsize': 14,
        'labelsize': 14,
    }
    o_plot.set_plot_dics.append(sol_yeilds)

    for sim, mask, color, ls, alpha, lw, lbl in zip(sims, masks, colors, lss, alphas, lws, lbls):
        o_data = ADD_METHODS_ALL_PAR(sim, add_mask=mask)
        a_sim, y_sim = o_data.get_outflow_yields(det, mask, method=method)
        sim_nucleo = {
            'task': 'line', 'ptype': 'cartesian',
            'position': (1, 1),
            'xarr': a_sim, 'yarr': y_sim,
            'v_n_x': 'A', 'v_n_y': 'abundances',
            'color': color, 'ls': ls, 'lw': lw, 'ds': 'steps', 'alpha': alpha,
            'ymin': 1e-5, 'ymax': 8e-1, 'xmin': 50, 'xmax': 220,
            'xlabel': Labels.labels("A"), 'ylabel': Labels.labels("Y_final"),
            'label': lbl, 'yscale': 'log',
            'fancyticks': True, 'minorticks': True,
            'fontsize': 14,
            'labelsize': 14,
            'title': {'text': "Mask:{} Norm:{}".format(mask.replace('_', '\_'), method), 'fontsize': 14}
        }

        o_plot.set_plot_dics.append(sim_nucleo)

    # # --- --- --- --- --- 1
    # sol_yeilds = {
    #     'task': 'line', 'ptype': 'cartesian',
    #     'position': (1, 2),
    #     'xarr': a_sol, 'yarr': y_sol,
    #     'v_n_x': 'Asun', 'v_n_y': 'Ysun',
    #     'color': 'gray', 'marker': 'o', 'ms': 4, 'alpha': 0.4,
    #     'ymin': 1e-5, 'ymax': 2e-1, 'xmin': 50, 'xmax': 230,
    #     'xlabel': Labels.labels("A"), 'ylabel': Labels.labels("Y_final"),
    #     'label': 'solar', 'yscale': 'log',
    #     'fancyticks': True, 'minorticks': True,
    #     'fontsize': 14,
    #     'labelsize': 14,
    #     'sharey': True
    # }
    # o_plot.set_plot_dics.append(sol_yeilds)
    #
    # method = "Asol=195"
    # #
    # for sim, mask, color, ls, alpha, lw, lbl in zip(sims, masks, colors, lss, alphas, lws, lbls):
    #     o_data = ADD_METHODS_ALL_PAR(sim, add_mask=mask)
    #     a_sim, y_sim = o_data.get_outflow_yields(det, mask, method=method)
    #     sim_nucleo = {
    #         'task': 'line', 'ptype': 'cartesian',
    #         'position': (1, 2),
    #         'xarr': a_sim, 'yarr': y_sim,
    #         'v_n_x': 'A', 'v_n_y': 'abundances',
    #         'color': color, 'ls': ls, 'lw': lw, 'ds': 'steps', 'alpha': alpha,
    #         'ymin': 1e-5, 'ymax': 2e-1, 'xmin': 50, 'xmax': 220,
    #         'xlabel': Labels.labels("A"), 'ylabel': Labels.labels("Y_final"),
    #         'label': lbl, 'yscale': 'log',
    #         'fancyticks': True, 'minorticks': True,
    #         'fontsize': 14,
    #         'labelsize': 14,
    #         'sharey': True,
    #         'title': {'text': "Mask:{} Norm:{}".format(mask.replace('_', '\_'), method), 'fontsize': 14}
    #     }
    #
    #     o_plot.set_plot_dics.append(sim_nucleo)

    # --- --- --- --- --- 2
    # sol_yeilds = {
    #     'task': 'line', 'ptype': 'cartesian',
    #     'position': (1, 3),
    #     'xarr': a_sol, 'yarr': y_sol,
    #     'v_n_x': 'Asun', 'v_n_y': 'Ysun',
    #     'color': 'gray', 'marker': 'o', 'ms': 4, 'alpha': 0.4,
    #     'ymin': 1e-5, 'ymax': 2e-1, 'xmin': 50, 'xmax': 230,
    #     'xlabel': Labels.labels("A"), 'ylabel': Labels.labels("Y_final"),
    #     'label': 'solar', 'yscale': 'log',
    #     'fancyticks': True, 'minorticks': True,
    #     'fontsize': 14,
    #     'labelsize': 14,
    #     'sharey': True
    # }
    # o_plot.set_plot_dics.append(sol_yeilds)
    #
    # method = "sum"
    # masks = ["geo bern_geoend", "geo bern_geoend", "geo bern_geoend", "geo bern_geoend", "geo bern_geoend"]
    # #
    # for sim, mask, color, ls, alpha, lw, lbl in zip(sims, masks, colors, lss, alphas, lws, lbls):
    #     o_data = ADD_METHODS_ALL_PAR(sim, add_mask=mask)
    #     a_sim, y_sim = o_data.get_outflow_yields(det, mask, method=method)
    #     sim_nucleo = {
    #         'task': 'line', 'ptype': 'cartesian',
    #         'position': (1, 3),
    #         'xarr': a_sim, 'yarr': y_sim,
    #         'v_n_x': 'A', 'v_n_y': 'abundances',
    #         'color': color, 'ls': ls, 'lw': lw, 'ds': 'steps', 'alpha': alpha,
    #         'ymin': 1e-5, 'ymax': 2e-1, 'xmin': 50, 'xmax': 220,
    #         'xlabel': Labels.labels("A"), 'ylabel': Labels.labels("Y_final"),
    #         'label': lbl, 'yscale': 'log',
    #         'fancyticks': True, 'minorticks': True,
    #         'fontsize': 14,
    #         'labelsize': 14,
    #         'sharey': True,
    #         'title': {'text': "Mask:{} Norm:{}".format(mask.replace('_', '\_'), method), 'fontsize': 14}
    #     }
    #
    #     o_plot.set_plot_dics.append(sim_nucleo)

    # --- --- --- --- --- 3
    sol_yeilds = {
        'task': 'line', 'ptype': 'cartesian',
        'position': (1, 2),
        'xarr': a_sol, 'yarr': y_sol,
        'v_n_x': 'Asun', 'v_n_y': 'Ysun',
        'color': 'gray', 'marker': 'o', 'ms': 4, 'alpha': 0.4,
        'ymin': 1e-5, 'ymax': 8e-1, 'xmin': 50, 'xmax': 210,
        'xlabel': Labels.labels("A"), 'ylabel': Labels.labels("Y_final"),
        'label': 'solar', 'yscale': 'log',
        'fancyticks': True, 'minorticks': True,
        'fontsize': 14,
        'labelsize': 14,
        'sharey': True
    }
    o_plot.set_plot_dics.append(sol_yeilds)

    method = "Asol=195"
    masks = ["geo bern_geoend", "geo bern_geoend", "geo bern_geoend", "geo bern_geoend", "geo bern_geoend"]
    #
    for sim, mask, color, ls, alpha, lw, lbl in zip(sims, masks, colors, lss, alphas, lws, lbls):
        o_data = ADD_METHODS_ALL_PAR(sim, add_mask=mask)
        a_sim, y_sim = o_data.get_outflow_yields(det, mask, method=method)
        sim_nucleo = {
            'task': 'line', 'ptype': 'cartesian',
            'position': (1, 2),
            'xarr': a_sim, 'yarr': y_sim,
            'v_n_x': 'A', 'v_n_y': 'abundances',
            'color': color, 'ls': ls, 'lw': lw, 'ds': 'steps', 'alpha': alpha,
            'ymin': 1e-5, 'ymax': 8e-1, 'xmin': 50, 'xmax': 210,
            'xlabel': Labels.labels("A"), 'ylabel': Labels.labels("Y_final"),
            'label': lbl, 'yscale': 'log',
            'fancyticks': True, 'minorticks': True,
            'fontsize': 14,
            'labelsize': 14,
            'sharey': True,
            'title': {'text': "Mask:{} Norm:{}".format(mask.replace('_', '\_'), method), 'fontsize': 14}
        }

        if sim == sims[-1]:
            sim_nucleo['legend'] = {'loc': 'lower left', 'ncol': 1, 'fontsize': 9, 'framealpha': 0.,
                                    'borderaxespad': 0., 'borderayespad': 0.}

        o_plot.set_plot_dics.append(sim_nucleo)

    o_plot.main()
    exit(1)


''' MKN '''


def plot_many_mkn():
    bands = ["g", "z", "Ks"]
    #
    sims = ["DD2_M14971245_M0_SR", "DD2_M13641364_M0_SR", "DD2_M15091235_M0_LK_SR", "BLh_M13641364_M0_LK_SR",
            "LS220_M14691268_M0_LK_SR"]
    lbls = [sim.replace('_', '\_') for sim in sims]
    fnames = ["mkn_model.h5", "mkn_model.h5", "mkn_model.h5", "mkn_model.h5", "mkn_model.h5"]
    lss = ["-", "-", "-", "-", "-"]
    lws = [1., 1., 1., 1., 1.]
    alphas = [1., 1., 1., 1., 1.]
    colors = ["blue", "cyan", "green", "black", "red"]
    #
    sims = ["LS220_M14691268_M0_LK_SR", "LS220_M14691268_M0_LK_SR", "LS220_M14691268_M0_LK_SR", "LS220_M14691268_M0_LK_SR"]
    lbls = [r"LR $\kappa \rightarrow Y_e$", r"PBR $\kappa \rightarrow Y_e$", "LR", "PBR"]
    fnames = ["mkn_model_k_lr.h5", "mkn_model_k_pbr.h5", "mkn_model_lr.h5", "mkn_model_pbr.h5"]
    lss = ["-", "-", "--", "--"]
    lws = [1., 1., 1., 1.]
    alphas = [1., 1., 1., 1.]
    colors = ["blue", "red", "blue", "red"]





    #

    #
    compute_models = True
    #
    if compute_models:
        #
        heat_rates = ["LR", "PBR", "LR", "PBR"]
        kappas = [True, True, False, False]
        #
        components = ["dynamics", "spiral"]
        detectors = [0, 0]
        masks = ["geo", "bern_geoend"]
        #
        for sim, fname, heating, kappa in zip(sims, fnames, heat_rates, kappas):
            o_mkn = COMPUTE_LIGHTCURVE(sim)
            o_mkn.output_fname = fname
            #
            for component, detector, mask in zip(components, detectors, masks):
                if component == "dynamics":
                    o_mkn.set_dyn_ej_nr(detector, mask)
                    o_mkn.set_dyn_par_var("aniso", detector, mask)
                    o_mkn.ejecta_params[component]['eps_ye_dep'] = heating#"PBR"
                    o_mkn.ejecta_params[component]['use_kappa_table'] = kappa  # "PBR"
                elif component == "spiral":
                    o_mkn.set_bern_ej_nr(detector, mask)
                    o_mkn.set_spiral_par_var("aniso", detector, mask)
                    o_mkn.ejecta_params[component]['eps_ye_dep'] = heating#"PBR"
                    o_mkn.ejecta_params[component]['use_kappa_table'] = kappa  # "PBR"
                else:
                    raise AttributeError("no method to set NR data for component:{}".format(component))
            #
            o_mkn.set_wind_par_war("")  # No wind
            o_mkn.set_secular_par_war("")  # No secular
            o_mkn.set_glob_par_var_source(True, True)  # use both NR files
            #

            o_mkn.compute_save_lightcurve(True, fname)  # save output
    #
    figname = ''
    for band in bands:
        figname = figname + band
        if band != bands[-1]:
            figname = figname + '_'
    figname = figname + '.png'
    #
    #
    o_plot = PLOT_MANY_TASKS()
    o_plot.gen_set["figdir"] = Paths.plots + 'all2/'
    o_plot.gen_set["type"] = "cartesian"
    o_plot.gen_set["figsize"] = (len(bands) * 3.0, 3.6)  # <->, |] # to match hists with (8.5, 2.7)
    o_plot.gen_set["figname"] = figname
    o_plot.gen_set["dpi"] = 128
    o_plot.gen_set["sharex"] = False
    o_plot.gen_set["sharey"] = False
    o_plot.gen_set["subplots_adjust_h"] = 0.3
    o_plot.gen_set["subplots_adjust_w"] = 0.0
    o_plot.set_plot_dics = []
    fontsize = 14
    labelsize = 14

    i_sim = 0
    for sim, fname, lbl, ls, lw, alpha, color in zip(sims, fnames, lbls, lss, lws, alphas, colors):
        o_res = COMBINE_LIGHTCURVES(sim)
        for i_plot, band in enumerate(bands):
            i_plot = i_plot + 1
            times, mags = o_res.get_model_median(band, fname)
            model = {
                'task': 'line', "ptype": "cartesian",
                'position': (1, i_plot),
                'xarr': times, 'yarr': mags,
                'v_n_x': 'time', 'v_n_y': 'mag',
                'color': color, 'ls': ls, 'lw': lw, 'ds': 'default', 'alpha': alpha,
                'ymin': 25, 'ymax': 15, 'xmin': 3e-1, 'xmax': 3e1,
                'xlabel': r"time [days]", 'ylabel': r"AB magnitude at 40 Mpc",
                'label': lbl, 'xscale': 'log',
                'fancyticks': True, 'minorticks': True,
                'sharey': False,
                'fontsize': fontsize,
                'labelsize': labelsize,
                'legend': {}  # {'loc': 'best', 'ncol': 2, 'fontsize': 18}
            }
            #
            if i_sim == len(sims)-1:
                obs = {
                    'task': 'mkn obs', "ptype": "cartesian",
                    'position': (1, i_plot),
                    'data': o_res, 'band': band, 'obs': True,
                    'v_n_x': 'time', 'v_n_y': 'mag',
                    'color': 'gray', 'marker': 'o', 'ms': 5., 'alpha': 0.8,
                    'ymin': 25, 'ymax': 15, 'xmin': 3e-1, 'xmax': 3e1,
                    'xlabel': r"time [days]", 'ylabel': r"AB magnitude at 40 Mpc",
                    'label': "AT2017gfo", 'xscale': 'log',
                    'fancyticks': True, 'minorticks': True,
                    'title': {'text': '{} band'.format(band), 'fontsize': 14},
                    'sharey': False,
                    'fontsize': fontsize,
                    'labelsize': labelsize,
                    'legend': {}
                }

            # if sim == sims[-1] and band != bands[-1]:
            #     model['label'] = None

            if i_sim == len(sims)-1 and band != bands[0]:
                model['sharey'] = True
                obs['sharey'] = True

            if i_sim == len(sims)-1 and band == bands[-1]:
                model['legend'] = {
                    'ncol': 1, 'fontsize': 9, 'framealpha': 0., 'borderaxespad': 0.,
                                    'borderayespad': 0.}

            if i_sim == len(sims)-1:
                o_plot.set_plot_dics.append(obs)
            o_plot.set_plot_dics.append(model)

        i_sim = i_sim + 1

    o_plot.main()
    exit(1)

def plot_many_mkn_long(heating="PBR"):
    #
    bands = ["g", "z", "Ks"]
    #
    sims1 = ["DD2_M14971245_M0_SR", "DD2_M13641364_M0_SR", "DD2_M15091235_M0_LK_SR", "BLh_M13641364_M0_LK_SR", "LS220_M14691268_M0_LK_SR"]
    lbls1 = [sim.replace('_', '\_') for sim in sims1]
    fnames1 = ["mkn_model_{}.h5".format(heating) for sim in sims1]
    lss1 = ["-", "-", "-", "-", "-"]
    lws1 = [1., 1., 1., 1., 1.]
    alphas1 = [1., 1., 1., 1., 1.]
    colors1 = ["blue", "cyan", "green", "black", "red"]
    #
    sims2 = ["DD2_M14971245_M0_SR", "DD2_M13641364_M0_SR", "DD2_M15091235_M0_LK_SR", "BLh_M13641364_M0_LK_SR", "LS220_M14691268_M0_LK_SR"]
    lbls2 = [None for sim in sims2]
    fnames2 = ["mkn_model_k_{}.h5".format(heating) for sim in sims2]
    lss2 = ["--", "--", "--", "--", "--"]
    lws2 = [0.7, 0.7, 0.7, 0.7, 0.7]
    alphas2 = [1., 1., 1., 1., 1.]
    colors2 = ["blue", "cyan", "green", "black", "red"]

    sims = sims1 + sims2
    lbls = lbls1 + lbls2
    fnames = fnames1 + fnames2
    lss = lss1 + lss2
    lws = lws1 + lws2
    alphas = alphas1 + alphas2
    colors = colors1 + colors2

    #

    #
    compute_models = True
    #
    if compute_models:
        #
        heat_rates = [heating for i in sims]
        kappas = [False for i in sims1] + [True for i in sims2]
        #
        components = ["dynamics", "spiral"]
        detectors = [0, 0]
        masks = ["geo", "bern_geoend"]
        #
        for sim, fname, heating, kappa in zip(sims, fnames, heat_rates, kappas):
            o_mkn = COMPUTE_LIGHTCURVE(sim)
            o_mkn.output_fname = fname
            #
            for component, detector, mask in zip(components, detectors, masks):
                if component == "dynamics":
                    o_mkn.set_dyn_ej_nr(detector, mask)
                    o_mkn.set_dyn_par_var("aniso", detector, mask)
                    o_mkn.ejecta_params[component]['eps_ye_dep'] = heating#"PBR"
                    o_mkn.ejecta_params[component]['use_kappa_table'] = kappa  # "PBR"
                elif component == "spiral":
                    o_mkn.set_bern_ej_nr(detector, mask)
                    o_mkn.set_spiral_par_var("aniso", detector, mask)
                    o_mkn.ejecta_params[component]['eps_ye_dep'] = heating#"PBR"
                    o_mkn.ejecta_params[component]['use_kappa_table'] = kappa  # "PBR"
                else:
                    raise AttributeError("no method to set NR data for component:{}".format(component))
            #
            o_mkn.set_wind_par_war("")  # No wind
            o_mkn.set_secular_par_war("")  # No secular
            o_mkn.set_glob_par_var_source(True, True)  # use both NR files
            #

            o_mkn.compute_save_lightcurve(True, fname)  # save output
    #
    figname = ''
    for band in bands:
        figname = figname + band
        if band != bands[-1]:
            figname = figname + '_'
    figname = figname + '_{}_all_long.png'.format(heating)
    #
    #
    o_plot = PLOT_MANY_TASKS()
    o_plot.gen_set["figdir"] = Paths.plots + 'all2/'
    o_plot.gen_set["type"] = "cartesian"
    o_plot.gen_set["figsize"] = (len(bands) * 3.0, 3.6)  # <->, |] # to match hists with (8.5, 2.7)
    o_plot.gen_set["figname"] = figname
    o_plot.gen_set["dpi"] = 128
    o_plot.gen_set["sharex"] = False
    o_plot.gen_set["sharey"] = False
    o_plot.gen_set["subplots_adjust_h"] = 0.3
    o_plot.gen_set["subplots_adjust_w"] = 0.0
    o_plot.set_plot_dics = []
    fontsize = 14
    labelsize = 14

    i_sim = 0
    for sim, fname, lbl, ls, lw, alpha, color in zip(sims, fnames, lbls, lss, lws, alphas, colors):
        o_res = COMBINE_LIGHTCURVES(sim)
        for i_plot, band in enumerate(bands):
            i_plot = i_plot + 1
            times, mags = o_res.get_model_median(band, fname)
            model = {
                'task': 'line', "ptype": "cartesian",
                'position': (1, i_plot),
                'xarr': times, 'yarr': mags,
                'v_n_x': 'time', 'v_n_y': 'mag',
                'color': color, 'ls': ls, 'lw': lw, 'ds': 'default', 'alpha': alpha,
                'ymin': 25, 'ymax': 15, 'xmin': 3e-1, 'xmax': 3e1,
                'xlabel': r"time [days]", 'ylabel': r"AB magnitude at 40 Mpc",
                'label': lbl, 'xscale': 'log',
                'fancyticks': True, 'minorticks': True,
                'sharey': False,
                'fontsize': fontsize,
                'labelsize': labelsize,
                'legend': {}  # {'loc': 'best', 'ncol': 2, 'fontsize': 18}
            }
            #
            obs = {
                'task': 'mkn obs', "ptype": "cartesian",
                'position': (1, i_plot),
                'data': o_res, 'band': band, 'obs': True,
                'v_n_x': 'time', 'v_n_y': 'mag',
                'color': 'gray', 'marker': 'o', 'ms': 5., 'alpha': 0.8,
                'ymin': 25, 'ymax': 15, 'xmin': 3e-1, 'xmax': 3e1,
                'xlabel': r"time [days]", 'ylabel': r"AB magnitude at 40 Mpc",
                'label': "AT2017gfo", 'xscale': 'log',
                'fancyticks': True, 'minorticks': True,
                'title': {'text': '{} band'.format(band), 'fontsize': 14},
                'sharey': False,
                'fontsize': fontsize,
                'labelsize': labelsize,
                'legend': {}
            }
            # if sim == sims[-1] and band != bands[-1]:
            #     model['label'] = None

            if i_sim == len(sims)-1 and band != bands[0]:
                model['sharey'] = True
                obs['sharey'] = True

            if i_sim == len(sims)-1 and band == bands[-1]:
                model['legend'] = {
                    'loc':"lower left",
                    'ncol': 1, 'fontsize': 9, 'framealpha': 0., 'borderaxespad': 0.,
                                    'borderayespad': 0.}
                model['textold'] = {'coords':(0.8, 0.8), 'text':heating, 'color':'black', 'fs':16}

            if i_sim == 0:
                o_plot.set_plot_dics.append(obs)
            o_plot.set_plot_dics.append(model)

        i_sim = i_sim + 1

    o_plot.main()
    exit(1)

def plot_many_mkn_dyn_only_long(heating="PBR"):
    #
    bands = ["g", "z", "Ks"]
    #
    sims1 = ["BLh_M11841581_M0_LK_SR",
            "DD2_M13641364_M0_LK_SR_R04", "DD2_M13641364_M0_SR_R04", "DD2_M15091235_M0_LK_SR", "DD2_M14971245_M0_SR",
            "LS220_M13641364_M0_LK_SR_restart", "LS220_M13641364_M0_SR", "LS220_M14691268_M0_LK_SR", "LS220_M14351298_M0_SR",  # "LS220_M14691268_M0_SR",
            "SFHo_M13641364_M0_LK_SR_2019pizza", "SFHo_M13641364_M0_SR", "SFHo_M14521283_M0_LK_SR_2019pizza",
            "SFHo_M14521283_M0_SR",
            "SLy4_M13641364_M0_LK_SR", "SLy4_M14521283_M0_SR"]

    lbls1 = [sim.replace('_', '\_') for sim in sims1]

    fnames1 = ["mkn_model_1_{}.h5".format(heating) for sim in sims1]
    colors1 = ["black",
              "blue", "blue", "blue", "blue",
              "red", "red", "red", "red", #"red",
              "green", "green", "green", "green",
              "orange", "orange"]
    alphas1 = [1.,
              1., 1., 1., 1.,
              1., 1., 1., 1.,# 1.,
              1., 1., 1., 1.,
              1., 1.]
    lss1 = ['-',
           '-', '--', '-.', ':',
           '-', '--', '-.', ':', #'-',
           '-', '--', '-.', ':',
           '-', '--']
    lws1 = [1.,
           1., 0.8, 0.5, 0.5,
           1., 0.8, 0.5, 0.5,#0.5,
           1., 0.8, 0.5, 0.5,
           1., 0.8]
    #
    sims2 = sims1
    lbls2 = [None for sim in sims2]
    fnames2 = ["mkn_model_1_k_{}.h5".format(heating) for sim in sims2]
    lss2 = lss1
    lws2 = lws1
    alphas2 = [0.5,
              0.5, 0.5, 0.5, 0.5,
              0.5, 0.5, 0.5, 0.5,
              0.5, 0.5, 0.5, 0.5,
              0.5, 0.5]
    colors2 = colors1

    sims = sims1 + sims2
    lbls = lbls1 + lbls2
    fnames = fnames1 + fnames2
    lss = lss1 + lss2
    lws = lws1 + lws2
    alphas = alphas1 + alphas2
    colors = colors1 + colors2

    #

    #
    compute_models = True
    #
    if compute_models:
        #
        heat_rates = [heating for i in sims]
        kappas = [False for i in sims1] + [True for i in sims2]
        #
        components = ["dynamics"]#, "spiral"]
        detectors = [0, 0]
        masks = ["geo"]#, "bern_geoend"]
        #
        for sim, fname, heating, kappa in zip(sims, fnames, heat_rates, kappas):
            o_mkn = COMPUTE_LIGHTCURVE(sim)
            o_mkn.output_fname = fname
            #
            for component, detector, mask in zip(components, detectors, masks):
                if component == "dynamics":
                    o_mkn.set_dyn_ej_nr(detector, mask)
                    o_mkn.set_dyn_par_var("aniso", detector, mask)
                    o_mkn.ejecta_params[component]['eps_ye_dep'] = heating#"PBR"
                    o_mkn.ejecta_params[component]['use_kappa_table'] = kappa  # "PBR"
                elif component == "spiral":
                    o_mkn.set_bern_ej_nr(detector, mask)
                    o_mkn.set_spiral_par_var("aniso", detector, mask)
                    o_mkn.ejecta_params[component]['eps_ye_dep'] = heating#"PBR"
                    o_mkn.ejecta_params[component]['use_kappa_table'] = kappa  # "PBR"
                else:
                    raise AttributeError("no method to set NR data for component:{}".format(component))
            #
            o_mkn.set_wind_par_war("")  # No wind
            o_mkn.set_secular_par_war("")  # No secular
            o_mkn.set_glob_par_var_source(True, True)  # use both NR files
            #
            o_mkn.glob_vars['m_disk'] = None
            #

            o_mkn.compute_save_lightcurve(True, fname)  # save output
    #
    figname = ''
    for band in bands:
        figname = figname + band
        if band != bands[-1]:
            figname = figname + '_'
    figname = figname + '_{}_all_short.png'.format(heating)
    #
    #
    o_plot = PLOT_MANY_TASKS()
    o_plot.gen_set["figdir"] = Paths.plots + 'all2/'
    o_plot.gen_set["type"] = "cartesian"
    o_plot.gen_set["figsize"] = (len(bands) * 3.0, 3.6)  # <->, |] # to match hists with (8.5, 2.7)
    o_plot.gen_set["figname"] = figname
    o_plot.gen_set["dpi"] = 128
    o_plot.gen_set["sharex"] = False
    o_plot.gen_set["sharey"] = False
    o_plot.gen_set["subplots_adjust_h"] = 0.3
    o_plot.gen_set["subplots_adjust_w"] = 0.0
    o_plot.set_plot_dics = []
    fontsize = 14
    labelsize = 14

    i_sim = 0
    for sim, fname, lbl, ls, lw, alpha, color in zip(sims, fnames, lbls, lss, lws, alphas, colors):
        o_res = COMBINE_LIGHTCURVES(sim)
        for i_plot, band in enumerate(bands):
            i_plot = i_plot + 1
            times, mags = o_res.get_model_median(band, fname)
            model = {
                'task': 'line', "ptype": "cartesian",
                'position': (1, i_plot),
                'xarr': times, 'yarr': mags,
                'v_n_x': 'time', 'v_n_y': 'mag',
                'color': color, 'ls': ls, 'lw': lw, 'ds': 'default', 'alpha': alpha,
                'ymin': 25, 'ymax': 15, 'xmin': 3e-1, 'xmax': 3e1,
                'xlabel': r"time [days]", 'ylabel': r"AB magnitude at 40 Mpc",
                'label': lbl, 'xscale': 'log',
                'fancyticks': True, 'minorticks': True,
                'sharey': False,
                'fontsize': fontsize,
                'labelsize': labelsize,
                'legend': {}  # {'loc': 'best', 'ncol': 2, 'fontsize': 18}
            }
            #
            obs = {
                'task': 'mkn obs', "ptype": "cartesian",
                'position': (1, i_plot),
                'data': o_res, 'band': band, 'obs': True,
                'v_n_x': 'time', 'v_n_y': 'mag',
                'color': 'gray', 'marker': 'o', 'ms': 5., 'alpha': 0.8,
                'ymin': 25, 'ymax': 15, 'xmin': 3e-1, 'xmax': 3e1,
                'xlabel': r"time [days]", 'ylabel': r"AB magnitude at 40 Mpc",
                'label': "AT2017gfo", 'xscale': 'log',
                'fancyticks': True, 'minorticks': True,
                'title': {'text': '{} band'.format(band), 'fontsize': 14},
                'sharey': False,
                'fontsize': fontsize,
                'labelsize': labelsize,
                'legend': {}
            }
            # if sim == sims[-1] and band != bands[-1]:
            #     model['label'] = None

            if i_sim == len(sims)-1 and band != bands[0]:
                model['sharey'] = True
                obs['sharey'] = True

            if i_sim == len(sims)-1 and band == bands[-1]:
                # model['legend'] = {
                #     'loc':"lower left",
                #     'ncol': 1, 'fontsize': 9, 'framealpha': 0., 'borderaxespad': 0.,
                #                     'borderayespad': 0.}
                # {
                model['legend'] = {'bbox_to_anchor': (1.0, -0.1),
                    # 'loc': 'lower left',
                    'loc': 'lower left', 'ncol': 1, 'fontsize': 9, 'framealpha': 0., 'borderaxespad': 0.,
                    'borderayespad': 0.}
                model['textold'] = {'coords':(0.8, 0.8), 'text':heating, 'color':'black', 'fs':16}

            if i_sim == 0:
                o_plot.set_plot_dics.append(obs)
            o_plot.set_plot_dics.append(model)

        i_sim = i_sim + 1

    o_plot.main()
    exit(1)

""" ---------------------------------------------- MIXED ------------------------------------------------------------"""


def plot_2ejecta_1disk_timehists():
    # columns
    sims = ["DD2_M14971245_M0_SR", "DD2_M13641364_M0_SR", "DD2_M13641364_M0_LK_SR_R04", "DD2_M15091235_M0_LK_SR", "BLh_M13641364_M0_LK_SR",
            "LS220_M14691268_M0_LK_SR"]
    # rows
    masks2 = ["bern_geoend", "bern_geoend", "bern_geoend", "bern_geoend"]
    masks1 = ["geo", "geo", "geo", "geo"]
    v_ns = ["vel_inf", "Y_e", "theta", "temperature"]
    v_ns_diks = ["Ye", "velz", "theta", "temp"]
    det = 0
    norm_to_m = 0
    _fpath = "slices/" + "rho_modes.h5"
    #
    o_plot = PLOT_MANY_TASKS()
    o_plot.gen_set["figdir"] = Paths.plots + "all2/"
    o_plot.gen_set["type"] = "cartesian"
    o_plot.gen_set["figsize"] = (14.0, 10.0)  # <->, |]
    o_plot.gen_set["figname"] = "timecorr_ej_disk.png"
    o_plot.gen_set["sharex"] = False
    o_plot.gen_set["sharey"] = True
    o_plot.gen_set["dpi"] = 128
    o_plot.gen_set["subplots_adjust_h"] = 0.03  # w
    o_plot.gen_set["subplots_adjust_w"] = 0.01
    o_plot.set_plot_dics = []
    #
    i_col = 1
    for sim in sims:
        #
        o_data = ADD_METHODS_ALL_PAR(sim)
        #
        i_row = 1
        # Time of the merger
        fpath = Paths.ppr_sims + sim + "/" + "waveforms/" + "tmerger.dat"
        if not os.path.isfile(fpath):
            raise IOError("File does not exist: {}".format(fpath))
        tmerg = float(np.loadtxt(fname=fpath, unpack=True)) * Constants.time_constant  # ms

        # Total Ejecta Mass
        for v_n, mask1, ls in zip(["Mej_tot", "Mej_tot"], ["geo", "bern_geoend"], ["--", "-"]):
            # Time to end dynamical ejecta
            fpath = Paths.ppr_sims + sim + "/" + "outflow_{}/".format(det) + mask1 + '/' + "total_flux.dat"
            if not os.path.isfile(fpath):
                raise IOError("File does not exist: {}".format(fpath))
            timearr, mass = np.loadtxt(fname=fpath, unpack=True, usecols=(0, 2))
            tend = float(timearr[np.where(mass >= (mass.max() * 0.98))][0]) * 1e3  # ms
            tend = tend - tmerg
            # print(time*1e3); exit(1)
            # Dybamical
            timearr = (timearr * 1e3) - tmerg
            mass = mass * 1e2
            plot_dic = {
                'task': 'line', 'ptype': 'cartesian',
                'position': (i_row, i_col),
                'xarr': timearr, 'yarr': mass,
                'v_n_x': "time", 'v_n_y': "mass",
                'color': "black", 'ls': ls, 'lw': 0.8, 'ds': 'default', 'alpha': 1.0,
                'ymin': 0.05, 'ymax': 2.9, 'xmin': timearr.min(), 'xmax': timearr.max(),
                'xlabel': Labels.labels("t-tmerg"), 'ylabel': "M $[M_{\odot}]$",
                'label': None, 'yscale': 'linear',
                'fontsize': 14,
                'labelsize': 14,
                'fancyticks': True,
                'minorticks': True,
                'sharex': True,  # removes angular citkscitks
                'sharey': True,
                'title': {"text": sim.replace('_', '\_'), 'fontsize': 12},
                'legend': {}  # 'loc': 'best', 'ncol': 2, 'fontsize': 18
            }
            if sim == sims[0]:
                plot_dic["sharey"] = False
                if mask1 == "geo":
                    plot_dic['label'] = r"$M_{\rm{ej}}$ $[10^{-2} M_{\odot}]$"
                else:
                    plot_dic['label'] = r"$M_{\rm{ej}}^{\rm{w}}$ $[10^{-2} M_{\odot}]$"

            o_plot.set_plot_dics.append(plot_dic)
        # Total Disk Mass
        timedisk_massdisk = o_data.get_disk_mass()
        timedisk = timedisk_massdisk[:, 0]
        massdisk = timedisk_massdisk[:, 1]
        timedisk = (timedisk * 1e3) - tmerg
        massdisk = massdisk * 1e1
        plot_dic = {
            'task': 'line', 'ptype': 'cartesian',
            'position': (i_row, i_col),
            'xarr': timedisk, 'yarr': massdisk,
            'v_n_x': "time", 'v_n_y': "mass",
            'color': "black", 'ls': ':', 'lw': 0.8, 'ds': 'default', 'alpha': 1.0,
            'ymin': 0.05, 'ymax': 3.0, 'xmin': timearr.min(), 'xmax': timearr.max(),
            'xlabel': Labels.labels("t-tmerg"), 'ylabel': "M $[M_{\odot}]$",
            'label': None, 'yscale': 'linear',
            'fontsize': 14,
            'labelsize': 14,
            'fancyticks': True,
            'minorticks': True,
            'sharex': True,  # removes angular citkscitks
            'sharey': True,
            # 'title': {"text": sim.replace('_', '\_'), 'fontsize': 12},
            'legend': {}  # 'loc': 'best', 'ncol': 2, 'fontsize': 18
        }
        if sim == sims[0]:
            plot_dic["sharey"] = False
            plot_dic['label'] = r"$M_{\rm{disk}}$ $[10^{-1} M_{\odot}]$"
            plot_dic['legend'] = {'loc': 'best', 'ncol': 1, 'fontsize': 9, 'framealpha': 0.}
        o_plot.set_plot_dics.append(plot_dic)
        #
        i_row = i_row + 1

        # DEBSITY MODES
        o_dm = LOAD_DENSITY_MODES(sim)
        o_dm.gen_set['fname'] = Paths.ppr_sims + sim + "/" + _fpath
        #
        mags1 = o_dm.get_data(1, "int_phi_r")
        mags1 = np.abs(mags1)
        # if sim == "DD2_M13641364_M0_SR": print("m1", mags1)#; exit(1)
        if norm_to_m != None:
            # print('Normalizing')
            norm_int_phi_r1d = o_dm.get_data(norm_to_m, 'int_phi_r')
            # print(norm_int_phi_r1d); exit(1)
            mags1 = mags1 / abs(norm_int_phi_r1d)[0]
        times = o_dm.get_grid("times")
        #
        assert len(times) > 0
        # if sim == "DD2_M13641364_M0_SR": print("m0", abs(norm_int_phi_r1d)); exit(1)
        #
        times = (times * 1e3) - tmerg  # ms
        #
        densmode_m1 = {
            'task': 'line', 'ptype': 'cartesian',
            'xarr': times, 'yarr': mags1,
            'position': (i_row, i_col),
            'v_n_x': 'times', 'v_n_y': 'int_phi_r abs',
            'ls': '-', 'color': 'black', 'lw': 0.8, 'ds': 'default', 'alpha': 1.,
            'label': None, 'ylabel': None, 'xlabel': Labels.labels("t-tmerg"),
            'xmin': timearr.min(), 'xmax': timearr.max(), 'ymin': 1e-4, 'ymax': 1e0,
            'xscale': None, 'yscale': 'log', 'legend': {},
            'fontsize': 14,
            'labelsize': 14,
            'fancyticks': True,
            'minorticks': True,
            'sharex': True,  # removes angular citkscitks
            'sharey': True
        }
        #
        mags2 = o_dm.get_data(2, "int_phi_r")
        mags2 = np.abs(mags2)
        print(mags2)
        if norm_to_m != None:
            # print('Normalizing')
            norm_int_phi_r1d = o_dm.get_data(norm_to_m, 'int_phi_r')
            # print(norm_int_phi_r1d); exit(1)
            mags2 = mags2 / abs(norm_int_phi_r1d)[0]
        # times = (times - tmerg) * 1e3 # ms
        # print(abs(norm_int_phi_r1d)); exit(1)
        densmode_m2 = {
            'task': 'line', 'ptype': 'cartesian',
            'xarr': times, 'yarr': mags2,
            'position': (i_row, i_col),
            'v_n_x': 'times', 'v_n_y': 'int_phi_r abs',
            'ls': '-', 'color': 'gray', 'lw': 0.5, 'ds': 'default', 'alpha': 1.,
            'label': None, 'ylabel': r'$C_m/C_0$', 'xlabel': Labels.labels("t-tmerg"),
            'xmin': timearr.min(), 'xmax': timearr.max(), 'ymin': 1e-4, 'ymax': 9e-1,
            'xscale': None, 'yscale': 'log',
            'legend': {},
            'fontsize': 14,
            'labelsize': 14,
            'fancyticks': True,
            'minorticks': True,
            'sharex': True,  # removes angular citkscitks
            'sharey': True,
            'title': {}  # {'text': "Density Mode Evolution", 'fontsize': 14}
            # 'sharex': True
        }
        #
        if sim == sims[0]:
            densmode_m1['label'] = r"$m=1$"
            densmode_m2['label'] = r"$m=2$"
        if sim == sims[0]:
            densmode_m1["sharey"] = False
            densmode_m1['label'] = r"$m=1$"
            densmode_m1['legend'] = {'loc': 'upper center', 'ncol': 2, 'fontsize': 9, 'framealpha': 0.,
                                     'borderayespad': 0.}
        if sim == sims[0]:
            densmode_m2["sharey"] = False
            densmode_m2['label'] = r"$m=2$"
            densmode_m2['legend'] = {'loc': 'upper center', 'ncol': 2, 'fontsize': 9, 'framealpha': 0.,
                                     'borderayespad': 0.}

        o_plot.set_plot_dics.append(densmode_m2)
        o_plot.set_plot_dics.append(densmode_m1)
        i_row = i_row + 1

        # TIME CORR EJECTA
        for v_n, mask1, mask2 in zip(v_ns, masks1, masks2):
            # Time to end dynamical ejecta
            fpath = Paths.ppr_sims + sim + "/" + "outflow_{}/".format(det) + mask1 + '/' + "total_flux.dat"
            if not os.path.isfile(fpath):
                raise IOError("File does not exist: {}".format(fpath))
            timearr, mass = np.loadtxt(fname=fpath, unpack=True, usecols=(0, 2))
            tend = float(timearr[np.where(mass >= (mass.max() * 0.98))][0]) * 1e3  # ms
            tend = tend - tmerg
            # print(time*1e3); exit(1)
            # Dybamical
            #
            fpath = Paths.ppr_sims + sim + "/" + "outflow_{}/".format(det) + mask1 + '/' + "timecorr_{}.h5".format(v_n)
            if not os.path.isfile(fpath):
                raise IOError("File does not exist: {}".format(fpath))
            # loadind data
            dfile = h5py.File(fpath, "r")
            timearr = np.array(dfile["time"]) - tmerg
            v_n_arr = np.array(dfile[v_n])
            mass = np.array(dfile["mass"])
            timearr, v_n_arr = np.meshgrid(timearr, v_n_arr)
            # mass = np.maximum(mass, mass.min())
            #
            corr_dic2 = {  # relies on the "get_res_corr(self, it, v_n): " method of data object
                'task': 'corr2d', 'dtype': 'corr', 'ptype': 'cartesian',
                'xarr': timearr, 'yarr': v_n_arr, 'zarr': mass,
                'position': (i_row, i_col),
                'v_n_x': "time", 'v_n_y': v_n, 'v_n': 'mass', 'normalize': True,
                'cbar': {},
                'cmap': 'inferno_r',
                'xlabel': Labels.labels("time"), 'ylabel': Labels.labels(v_n, alternative=True),
                'xmin': timearr.min(), 'xmax': timearr.max(), 'ymin': None, 'ymax': None, 'vmin': 1e-4, 'vmax': 1e-1,
                'xscale': "linear", 'yscale': "linear", 'norm': 'log',
                'mask_below': None, 'mask_above': None,
                'title': {},  # {"text": o_corr_data.sim.replace('_', '\_'), 'fontsize': 14},
                # 'text': {'text': lbl.replace('_', '\_'), 'coords': (0.05, 0.9), 'color': 'white', 'fs': 12},
                'axvline': {"x": tend, "linestyle": "--", "color": "black", "linewidth": 1.},
                'mask': "x>{}".format(tend),
                'fancyticks': True,
                'minorticks': True,
                'sharex': True,  # removes angular citkscitks
                'sharey': True,
                'fontsize': 14,
                'labelsize': 14
            }
            if sim == sims[0]:
                corr_dic2["sharey"] = False
            if v_n == v_ns[-1]:
                corr_dic2["sharex"] = False

            if v_n == "vel_inf":
                corr_dic2['ymin'], corr_dic2['ymax'] = 0., 0.45
            elif v_n == "Y_e":
                corr_dic2['ymin'], corr_dic2['ymax'] = 0.05, 0.45
            elif v_n == "temperature":
                corr_dic2['ymin'], corr_dic2['ymax'] = 0.1, 1.8

            o_plot.set_plot_dics.append(corr_dic2)

            # WIND
            fpath = Paths.ppr_sims + sim + "/" + "outflow_{}/".format(det) + mask2 + '/' + "timecorr_{}.h5".format(v_n)
            if not os.path.isfile(fpath):
                raise IOError("File does not exist: {}".format(fpath))
            # loadind data
            dfile = h5py.File(fpath, "r")
            timearr = np.array(dfile["time"]) - tmerg
            v_n_arr = np.array(dfile[v_n])
            mass = np.array(dfile["mass"])
            timearr, v_n_arr = np.meshgrid(timearr, v_n_arr)
            # print(timearr);exit(1)
            # mass = np.maximum(mass, mass.min())
            #
            corr_dic2 = {  # relies on the "get_res_corr(self, it, v_n): " method of data object
                'task': 'corr2d', 'dtype': 'corr', 'ptype': 'cartesian',
                'xarr': timearr, 'yarr': v_n_arr, 'zarr': mass,
                'position': (i_row, i_col),
                'v_n_x': "time", 'v_n_y': v_n, 'v_n': 'mass', 'normalize': True,
                'cbar': {},
                'cmap': 'inferno_r',
                'xlabel': Labels.labels("time"), 'ylabel': Labels.labels(v_n, alternative=True),
                'xmin': timearr.min(), 'xmax': timearr.max(), 'ymin': None, 'ymax': None, 'vmin': 1e-4, 'vmax': 1e-1,
                'xscale': "linear", 'yscale': "linear", 'norm': 'log',
                'mask_below': None, 'mask_above': None,
                'title': {},  # {"text": o_corr_data.sim.replace('_', '\_'), 'fontsize': 14},
                # 'text': {'text': lbl.replace('_', '\_'), 'coords': (0.05, 0.9), 'color': 'white', 'fs': 12},
                'mask': "x<{}".format(tend),
                'fancyticks': True,
                'minorticks': True,
                'sharex': True,  # removes angular citkscitks
                'sharey': True,
                'fontsize': 14,
                'labelsize': 14
            }
            if sim == sims[0]:
                corr_dic2["sharey"] = False
            if v_n == v_ns[-1] and len(v_ns_diks) == 0:
                corr_dic2["sharex"] = False

            if v_n == "vel_inf":
                corr_dic2['ymin'], corr_dic2['ymax'] = 0., 0.45
            elif v_n == "Y_e":
                corr_dic2['ymin'], corr_dic2['ymax'] = 0.05, 0.45
            elif v_n == "theta":
                corr_dic2['ymin'], corr_dic2['ymax'] = 0, 85
            elif v_n == "temperature":
                corr_dic2['ymin'], corr_dic2['ymax'] = 0, 1.8

            if sim == sims[-1] and v_n == v_ns[-1]:
                corr_dic2['cbar'] = {'location': 'right .02 0.', 'label': Labels.labels("mass"),
                                     # 'right .02 0.' 'fmt': '%.1e',
                                     'labelsize': 14,  # 'aspect': 6.,
                                     'fontsize': 14}

            o_plot.set_plot_dics.append(corr_dic2)
            i_row = i_row + 1

        # DISK
        if len(v_ns_diks) > 0:
            d3_corr = LOAD_RES_CORR(sim)
            iterations = d3_corr.list_iterations
            #
            for v_n in v_ns_diks:
                # Loading 3D data
                print("v_n:{}".format(v_n))
                times = []
                bins = []
                values = []
                for it in iterations:
                    fpath = Paths.ppr_sims + sim + "/" + "profiles/" + str(it) + "/" + "hist_{}.dat".format(v_n)
                    if os.path.isfile(fpath):
                        times.append(d3_corr.get_time_for_it(it, "prof"))
                        print("\tLoading it:{} t:{}".format(it, times[-1]))
                        data = np.loadtxt(fpath, unpack=False)
                        bins = data[:, 0]
                        values.append(data[:, 1])
                    else:
                        print("\tFile not found it:{}".format(fpath))

                assert len(times) > 0
                times = np.array(times) * 1e3
                bins = np.array(bins)
                values = np.reshape(np.array(values), newshape=(len(times), len(bins))).T
                #
                times = times - tmerg
                #
                values = values / np.sum(values)
                values = np.maximum(values, 1e-10)
                #
                def_dic = {'task': 'colormesh', 'ptype': 'cartesian',  # 'aspect': 1.,
                           'xarr': times, "yarr": bins, "zarr": values,
                           'position': (i_row, i_col),  # 'title': '[{:.1f} ms]'.format(time_),
                           'cbar': {},
                           'v_n_x': 'x', 'v_n_y': 'z', 'v_n': v_n,
                           'xlabel': Labels.labels("t-tmerg"), 'ylabel': Labels.labels(v_n, alternative=True),
                           'xmin': timearr.min(), 'xmax': timearr.max(), 'ymin': bins.min(), 'ymax': bins.max(),
                           'vmin': 1e-6,
                           'vmax': 1e-2,
                           'fill_vmin': False,  # fills the x < vmin with vmin
                           'xscale': None, 'yscale': None,
                           'mask': None, 'cmap': 'inferno_r', 'norm': "log",
                           'fancyticks': True,
                           'minorticks': True,
                           'title': {},
                           # "text": r'$t-t_{merg}:$' + r'${:.1f}$'.format((time_ - tmerg) * 1e3), 'fontsize': 14
                           # 'sharex': True,  # removes angular citkscitks
                           'text': {},
                           'fontsize': 14,
                           'labelsize': 14,
                           'sharex': True,
                           'sharey': True,
                           }
                if sim == sims[-1] and v_n == v_ns_diks[-1]:
                    def_dic['cbar'] = {'location': 'right .02 0.',  # 'label': Labels.labels("mass"),
                                       # 'right .02 0.' 'fmt': '%.1e',
                                       'labelsize': 14,  # 'aspect': 6.,
                                       'fontsize': 14}
                if v_n == v_ns[0]:
                    def_dic['text'] = {'coords': (1.0, 1.05), 'text': sim.replace("_", "\_"), 'color': 'black',
                                       'fs': 16}
                if v_n == "Ye":
                    def_dic['ymin'] = 0.05
                    def_dic['ymax'] = 0.45
                if v_n == "velz":
                    def_dic['ymin'] = -.25
                    def_dic['ymax'] = .25
                elif v_n == "temp":
                    # def_dic['yscale'] = "log"
                    def_dic['ymin'] = 1e-1
                    def_dic['ymax'] = 2.5e1
                elif v_n == "theta":
                    def_dic['ymin'] = 0
                    def_dic['ymax'] = 85
                    def_dic["yarr"] = 90 - (def_dic["yarr"] / np.pi * 180.)
                #
                if v_n == v_ns_diks[-1]:
                    def_dic["sharex"] = False
                if sim == sims[0]:
                    def_dic["sharey"] = False

                o_plot.set_plot_dics.append(def_dic)
                i_row = i_row + 1

        i_col = i_col + 1
    o_plot.main()
    exit(1)


if __name__ == '__main__':
    plot_2ejecta_1disk_timehists()

    ''' density modes '''
    # plot_desity_modes()
    # plot_desity_modes2()

    ''' --- neutrinos --- '''
    # plot_several_q_eff("Q_eff_nua", ["LS220_M14691268_M0_LK_SR"], [1302528, 1515520, 1843200], "ls220_q_eff.png")
    # plot_several_q_eff("Q_eff_nua", ["DD2_M15091235_M0_LK_SR"], [1277952, 1425408, 1540096], "dd2_q_eff.png")
    #
    # plot_several_q_eff("R_eff_nua", ["LS220_M14691268_M0_LK_SR"], [1302528, 1515520, 1843200], "ls220_r_eff.png")
    # plot_several_q_eff("R_eff_nua", ["DD2_M15091235_M0_LK_SR"], [1277952, 1425408, 1540096], "dd2_r_eff.png")

    ''' ejecta properties '''

    # plot_histograms_ejecta_for_many_sims()
    # plot_histograms_ejecta("geo", "geo")
    # plot_histograms_ejecta("geo", "bern_geoend")
    # plot_total_fluxes_q1_and_qnot1("Y_e04_geoend")
    # plot_total_fluxes_q1_and_qnot1("theta60_geoend")
    # plot_2ejecta_1disk_timehists()
    # plot_2ejecta_1disk_timehists()

    ''' disk ejecta summory properties '''

    # plot_last_disk_mass_with_lambda("Lambda", "q", "Mdisk3Dmax", None, None)
    # plot_last_disk_mass_with_lambda("Lambda", "q", "Mej_tot", det=0, mask="geo")
    # plot_last_disk_mass_with_lambda("Lambda", "q", "Mej_tot", det=0, mask="bern_geoend")
    # plot_last_disk_mass_with_lambda("Lambda", "q", "Ye_ave", det=0, mask="geo")
    # plot_last_disk_mass_with_lambda("Lambda", "q", "Ye_ave", det=0, mask="bern_geoend")
    # plot_last_disk_mass_with_lambda("Lambda", "q", "vel_inf_ave", det=0, mask="geo")
    # plot_last_disk_mass_with_lambda("Lambda", "q", "vel_inf_ave", det=0, mask="bern_geoend")
    ''' - '''
    # plot_last_disk_mass_with_lambda2(v_n_x="Lambda", v_n_y="Mej_tot", v_n_col="q",
    #                                  mask_x=None,mask_y="geo",mask_col=None,det=0, plot_legend=True)
    # plot_last_disk_mass_with_lambda2(v_n_x="Lambda", v_n_y="Mej_tot", v_n_col="q",
    #                                  mask_x=None,mask_y="bern_geoend",mask_col=None,det=0, plot_legend=False)
    # plot_last_disk_mass_with_lambda2(v_n_x="Lambda", v_n_y="Ye_ave", v_n_col="q",
    #                                  mask_x=None,mask_y="geo",mask_col=None,det=0, plot_legend=False)
    # plot_last_disk_mass_with_lambda2(v_n_x="Lambda", v_n_y="Ye_ave", v_n_col="q",
    #                                  mask_x=None,mask_y="bern_geoend",mask_col=None,det=0, plot_legend=False)
    # plot_last_disk_mass_with_lambda2(v_n_x="Lambda", v_n_y="vel_inf_ave", v_n_col="q",
    #                                  mask_x=None,mask_y="geo",mask_col=None,det=0, plot_legend=False)
    # plot_last_disk_mass_with_lambda2(v_n_x="Lambda", v_n_y="vel_inf_ave", v_n_col="q",
    #                                  mask_x=None,mask_y="bern_geoend",mask_col=None,det=0, plot_legend=False)
    # plot_last_disk_mass_with_lambda2(v_n_x="Lambda", v_n_y="Mdisk3Dmax", v_n_col="q",
    #                                  mask_x=None,mask_y=None, mask_col=None,det=0, plot_legend=False)
    exit(0)
    ''' disk properties '''

    # plot_histograms_ejecta("geo")

    # plot_disk_mass_evol_SR()
    # plot_disk_mass_evol_LR()
    # plot_disk_mass_evol_HR()

    # plot_disk_hist_evol("LS220_M13641364_M0_SR", "ls220_no_lk_disk_hists.png")
    # plot_disk_hist_evol("LS220_M13641364_M0_LK_SR_restart", "ls220_disk_hists.png")
    # plot_disk_hist_evol("BLh_M13641364_M0_LK_SR", "blh_disk_hists.png")
    # plot_disk_hist_evol("DD2_M13641364_M0_SR", "dd2_nolk_disk_hists.png")
    # plot_disk_hist_evol("SFHo_M13641364_M0_SR", "sfho_nolk_disk_hists.png")
    # plot_disk_hist_evol("SLy4_M13641364_M0_SR", "sly_nolk_disk_hists.png")
    # plot_disk_hist_evol("SFHo_M14521283_M0_SR", "sfho_qnot1_nolk_disk_hists.png")
    # plot_disk_hist_evol("SLy4_M14521283_M0_SR", "sly_qnot1_nolk_disk_hists.png")
    # plot_disk_hist_evol("DD2_M14971245_M0_SR", "dd2_qnot1_nolk_disk_hists.png")
    # plot_disk_hist_evol("LS220_M13641364_M0_SR", "ls220_nolk_disk_hists.png")

    # plot_disk_hist_evol_one_v_n("Ye", "LS220_M13641364_M0_LK_SR_restart", "ls220_ye_disk_hist.png")
    # plot_disk_hist_evol_one_v_n("temp", "LS220_M13641364_M0_LK_SR_restart", "ls220_temp_disk_hist.png")
    # plot_disk_hist_evol_one_v_n("rho", "LS220_M13641364_M0_LK_SR_restart", "ls220_rho_disk_hist.png")
    # plot_disk_hist_evol_one_v_n("dens_unb_bern", "LS220_M13641364_M0_LK_SR_restart", "ls220_dens_unb_bern_disk_hist.png")
    # plot_disk_hist_evol_one_v_n("velz", "LS220_M13641364_M0_LK_SR_restart", "ls220_velz_disk_hist.png")

    # o_err = ErrorEstimation("DD2_M15091235_M0_LK_SR","DD2_M14971245_M0_SR")
    # o_err.main(rewrite=False)
    # # plot_total_fluxes_lk_on_off("bern_geoend")
    # exit(1)

    ''' disk slices '''

    # plot_den_unb__vel_z_sly4_evol()

    ''' nucleo '''

    # many_yeilds()
    # tmp_many_yeilds()

    ''' mkn '''

    # plot_many_mkn()
    # plot_many_mkn_long("PBR")
    # plot_many_mkn_dyn_only_long("LR")
    # plot_many_mkn_dyn_only_long("PBR")
    ''' --- COMPARISON TABLE --- '''
    # tbl = COMPARISON_TABLE()

    ### --- effect of viscosity
    # tbl.print_mult_table([["DD2_M15091235_M0_LK_SR", "DD2_M14971245_M0_SR"],
    #                       ["DD2_M13641364_M0_LK_SR_R04", "DD2_M13641364_M0_SR_R04"],
    #                       ["LS220_M14691268_M0_LK_SR", "LS220_M14691268_M0_SR"],
    #                       ["SFHo_M14521283_M0_LK_SR", "SFHo_M14521283_M0_SR"]],
    #                      [r"\hline",
    #                       r"\hline",
    #                       r"\hline",
    #                       r"\hline"],
    #                       comment=r"{Analysis of the viscosity effect on the outflow properties and disk mass. "
    #                       r"Here the $t_{\text{disk}}$ is the maximum postmerger time, for which the 3D is "
    #                       r"available for both simulations For that time, the disk mass is interpolated using "
    #                       r"linear inteprolation. The $\Delta t_{\text{wind}}$ is the maximum common time window "
    #                       r"between the time at which dynamical ejecta reaches 98\% of its total mass and the end of the "
    #                       r"simulation Cases where $t_{\text{disk}}$ or $\Delta t_{\text{wind}}$ is N/A indicate the absence "
    #                      r"of the ovelap between 3D data fro simulations or absence of this data entirely and "
    #                      r"absence of overlap between the time window in which the spiral-wave wind is computed "
    #                      r"which does not allow to do a proper, one-to-one comparison. $\Delta$ is a estimated "
    #                      r"change as $|value_1 - value_2|/value_1$ in percentage }",
    #                      label=r"{tbl:vis_effect}"
    #                      )
    # exit(0)

    #### --- resulution effect on simulations with viscosity
    # tbl.print_mult_table([["DD2_M13641364_M0_LK_SR_R04", "DD2_M13641364_M0_LK_LR_R04", "DD2_M13641364_M0_LK_HR_R04"], # HR too short
    #                      ["DD2_M15091235_M0_LK_SR", "DD2_M15091235_M0_LK_HR"],          # no
    #                      ["LS220_M14691268_M0_LK_SR", "LS220_M14691268_M0_LK_HR"],      # no
    #                      ["SFHo_M13641364_M0_LK_SR", "SFHo_M13641364_M0_LK_HR"],        # no
    #                      ["SFHo_M14521283_M0_LK_SR", "SFHo_M14521283_M0_LK_HR"]],       # no
    #                      [r"\hline",
    #                       r"\hline",
    #                       r"\hline",
    #                       r"\hline",
    #                       r"\hline"],
    #                      comment=r"{Resolution effect to on the outflow properties and disk mass on the simulations with "
    #                      r"subgird turbulence. Here the $t_{\text{disk}}$ "
    #                      r"is the maximum postmerger time, for which the 3D is available for both simulations "
    #                      r"For that time, the disk mass is interpolated using linear inteprolation. The "
    #                      r"$\Delta t_{\text{wind}}$ is the maximum common time window between the time at "
    #                      r"which dynamical ejecta reaches 98\% of its total mass and the end of the simulation "
    #                      r"Cases where $t_{\text{disk}}$ or $\Delta t_{\text{wind}}$ is N/A indicate the absence "
    #                      r"of the ovelap between 3D data fro simulations or absence of this data entirely and "
    #                      r"absence of overlap between the time window in which the spiral-wave wind is computed "
    #                      r"which does not allow to do a proper, one-to-one comparison. $\Delta$ is a estimated "
    #                      r"change as $|value_1 - value_2|/value_1$ in percentage }",
    #                      label=r"{tbl:res_effect_vis}"
    #                      )
    # exit(0)

    #### --- resolution effect on simulations without voscosity
    # tbl.print_mult_table([["DD2_M13641364_M0_SR_R04", "DD2_M13641364_M0_LR_R04", "DD2_M13641364_M0_HR_R04"], # DD2_M13641364_M0_LR_R04
    #                      ["DD2_M14971245_M0_SR", "DD2_M14971246_M0_LR", "DD2_M14971245_M0_HR"], # DD2_M14971246_M0_LR
    #                      ["LS220_M13641364_M0_SR", "LS220_M13641364_M0_LR", "LS220_M13641364_M0_HR"], # LS220_M13641364_M0_LR
    #                      ["LS220_M14691268_M0_SR", "LS220_M14691268_M0_LR", "LS220_M14691268_M0_HR"], # LS220_M14691268_M0_LR
    #                      ["SFHo_M13641364_M0_SR", "SFHo_M13641364_M0_HR"], # no
    #                      ["SFHo_M14521283_M0_SR", "SFHo_M14521283_M0_HR"]], # no
    #                      [r"\hline",
    #                       r"\hline",
    #                       r"\hline",
    #                       r"\hline",
    #                       r"\hline",
    #                       r"\hline"],
    #                      comment=r"{Resolution effec to on the outflow properties and disk mass on the simulations without "
    #                      r"subgird turbulence. Here the $t_{\text{disk}}$ "
    #                      r"is the maximum postmerger time, for which the 3D is available for both simulations "
    #                      r"For that time, the disk mass is interpolated using linear inteprolation. The "
    #                      r"$\Delta t_{\text{wind}}$ is the maximum common time window between the time at "
    #                      r"which dynamical ejecta reaches 98\% of its total mass and the end of the simulation "
    #                      r"Cases where $t_{\text{disk}}$ or $\Delta t_{\text{wind}}$ is N/A indicate the absence "
    #                      r"of the ovelap between 3D data fro simulations or absence of this data entirely and "
    #                      r"absence of overlap between the time window in which the spiral-wave wind is computed "
    #                      r"which does not allow to do a proper, one-to-one comparison. $\Delta$ is a estimated "
    #                      r"change as $|value_1 - value_2|/value_1$ in percentage }",
    #                      label=r"{tbl:res_effect}"
    #                      )
    #
    #
    # exit(0)

    ''' --- OVERALL TABLE --- '''
    tbl = TEX_TABLES()

    # tbl.print_mult_table([simulations["BLh"]["q=1"], simulations["BLh"]["q=1.3"], simulations["BLh"]["q=1.4"], simulations["BLh"]["q=1.7"], simulations["BLh"]["q=1.8"],
    #                       simulations["DD2"]["q=1"], simulations["DD2"]["q=1.1"], simulations["DD2"]["q=1.2"], simulations["DD2"]["q=1.4"],
    #                       simulations["LS220"]["q=1"], simulations["LS220"]["q=1.1"], simulations["LS220"]["q=1.2"], simulations["LS220"]["q=1.4"], simulations["LS220"]["q=1.7"],
    #                       simulations["SFHo"]["q=1"], simulations["SFHo"]["q=1.1"], simulations["SFHo"]["q=1.4"],
    #                       simulations["SLy4"]["q=1"], simulations["SLy4"]["q=1.1"]],
    #                      [r"\hline", r"\hline", r"\hline", r"\hline",
    #                       r"\hline\hline",
    #                       r"\hline", r"\hline", r"\hline",
    #                       r"\hline\hline",
    #                       r"\hline", r"\hline", r"\hline", r"\hline",
    #                       r"\hline\hline",
    #                       r"\hline", r"\hline",
    #                       r"\hline\hline",
    #                       r"\hline", r"\hline"])

    tbl.init_data_v_ns = ["EOS", "q", "note", "res", "vis"]
    tbl.init_data_prec = ["", ".1f", "", "", ""]
    #
    tbl.col_d3_gw_data_v_ns = []
    tbl.col_d3_gw_data_prec = []
    #
    tbl.outflow_data_v_ns = ['Mej_tot', 'Ye_ave', 'vel_inf_ave',
                             'Mej_tot', 'Ye_ave', 'vel_inf_ave']
    tbl.outflow_data_prec = [".4f", ".3f", ".3f",
                             ".4f", ".3f", ".3f"]
    tbl.outflow_data_mask = ["theta60_geoend", "theta60_geoend", "theta60_geoend", "theta60_geoend",
                             "Y_e04_geoend", "Y_e04_geoend", "Y_e04_geoend", "Y_e04_geoend"]

    tbl.print_mult_table([["DD2_M14971245_M0_SR", "DD2_M13641364_M0_SR", "DD2_M15091235_M0_LK_SR",
                           "BLh_M13641364_M0_LK_SR", "LS220_M14691268_M0_LK_SR"]],
                         [r"\hline"])

    # par = COMPUTE_PAR("LS220_M14691268_M0_LK_SR")

    # print("tcoll",par.get_par("tcoll_gw"))
    # print("Mdisk",par.get_par("Mdisk3D"))

    # o_lf = COMPUTE_PAR("SLy4_M13641364_M0_LK_SR")
    # print(o_lf.get_outflow_data(0, "geo", "corr_vel_inf_theta.h5"))
    # print(o_lf.get_collated_data("dens_unbnd.norm1.asc"))
    # print(o_lf.get_gw_data("tmerger.dat"))

    # print(o_lf.get_outflow_par(0, "geo", "Mej_tot"))
    # print(o_lf.get_outflow_par(0, "geo", "Ye_ave"))
    # print(o_lf.get_outflow_par(0, "geo", "vel_inf_ave"))
    # print(o_lf.get_outflow_par(0, "geo", "s_ave"))
    # print(o_lf.get_outflow_par(0, "geo", "theta_rms"))
    # print(o_lf.get_disk_mass())
    # print("---")
    # print(o_lf.get_par("tmerg"))
    # print(o_lf.get_par("Munb_tot"))
    # print(o_lf.get_par("Munb_tot"))
    # print(o_lf.get_par("Munb_bern_tot"))
    # print(o_lf.get_par("tcoll_gw"))

