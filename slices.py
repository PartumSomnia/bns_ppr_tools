from __future__ import division
from sys import path
path.append('modules/')
import os.path
import click
import h5py
from argparse import ArgumentParser
from math import pi, log10
import sys
from scidata.utils import locate
import scidata.carpet.hdf5 as h5
from scidata.carpet.interp import Interpolator


# from _curses import raw
# from mpl_toolkits.axes_grid1 import make_axes_locatable
# from matplotlib import ticker
# import matplotlib.pyplot as plt
# from matplotlib import rc
# plt.rc('text', usetex=True)
# plt.rc('font', family='serif')
# import scivis.units as ut # for tmerg
# import statsmodels.formula.api as smf
# import scipy.optimize as opt
# from math import pi, sqrt
# import matplotlib as mpl
# import pandas as pd
# import numpy as np
# from glob import glob
# import itertools
# import os.path
# import cPickle
# import click
# import time
# import copy
# import h5py
# import csv
# import os
#
# import time



# import scidata.xgraph as xg


# from scipy import interpolate
# cmap = plt.get_cmap("viridis")
# from sklearn.linear_model import LinearRegression-
# from scipy.optimize import fmin
# from matplotlib.ticker import AutoMinorLocator, FixedLocator, NullFormatter, \
#     MultipleLocator
# from matplotlib.colors import LogNorm, Normalize

# from utils import *
from utils import *
from preanalysis import LOAD_ITTIME
from plotting_methods import PLOT_MANY_TASKS

""" ================================================================================================================ """
__d3slicesplanes__ = ["xy", "xz"]
__slices__ = {
    "name": "slices",
    "outdir": "slices",
    "tasklist": ["plot", "movie", "addm0", "dm"],
    "reflevels": [0, 1, 2, 3, 4, 5, 6]
}

""" ===============================================================================================================  """


class LOAD_STORE_DATASETS(LOAD_ITTIME):
    """
    Allows easy access to a scidata datasets of 2d data of a given simulation,
    loading them only if they are needed, and storing them for future accesses.

    Assumes that the simulation data is stired in /output-xxxx/data/ folders, where
    'xxxx' stands for the number.
    To know, which iterations are stored in what output-xxxx it first loads an ascii
    file <'file_for_it'> which should be present in all output-xxxx and have a
    structure with columns: 1:it 2:time (other columns do not matter)

    The 2d datasets, located in output-xxxx, expected to be named like:
    'rho.xy.h5'. The list of possible variables, (like 'rho') is set in
    <'self.list_v_ns'>. The list of possible planes (like 'xy') in set in
    <'self.list_planes'>.

    Logic:
        Every time when the dataset is requested via <'get_dataset(it, plane, v_n)'>,
        the class do:
            1. Checks what output-xxxx contains iteration 'it'
            2. Checks if the dataset for this output, plane and variable name 'v_n'
                has already been loaded and is present in the storage
                <'self.dataset_matrix[]'>
                If so: it will return the dataset from the storage.
                If not: it will load the required dataset and add it to the storage
                for future uses.

    """

    list_neut_v_ns = ["Q_eff_nua", "Q_eff_nue", "Q_eff_nux", "R_eff_nua", "R_eff_nue", "R_eff_nux",
                      "optd_0_nua", "optd_0_nux", "optd_0_nue", "optd_1_nua", "optd_1_nux", "optd_1_nue"]

    def __init__(self, sim):

        LOAD_ITTIME.__init__(self, sim)

        self.sim = sim
        self.nlevels = 7
        self.gen_set = {'nlevels':7,
                        'sim': sim,
                        'file_for_it': 'H.norm2.asc',
                        'iterations':0,
                        'indir': Paths.gw170817 + sim + '/',
                        'outdir': Paths.ppr_sims + sim + '/res_2d/'}

        # self.output_it_map = {}

        self.list_outputs = self.get_list_outputs()
        _, self.iterations, self.times = \
            self.get_ittime(output="overall", d1d2d3prof="d2")
        # print(self.iterations[0], self.iterations[-1]); exit(1)

        # self.output_it_map, self.it_time = \
        #     set_it_output_map(Paths.gw170817+self.sim+'/')

        # self.iterations = np.array(self.it_time[:, 0], dtype=int)
        # self.times =  np.array(self.it_time[:, 1], dtype=float)


        self.list_v_ns = ['rho', 'Y_e', 'temperature', 's_phi', 'entropy', 'dens_unbnd'] + self.list_neut_v_ns
        self.list_planes=['xy', 'xz', 'xy']

        self.set_use_new_output_if_duplicated = False

        self.dataset_matrix = [[[0
                                  for z in range(len(self.list_v_ns))]
                                  for k in range(len(self.list_planes))]
                                  for s in range(len(self.list_outputs))]

    # def set_it_output_map(self):
    #     """
    #     Loads set of files that have '1:it 2:time ...' structure to get a map
    #     of what output-xxxx contains what iteration (and time)
    #     """
    #     print('-' * 25 + 'LOADING it list ({})'
    #           .format(self.gen_set['file_for_it']) + '-' * 25)
    #     print("\t loading from: {}".format(self.gen_set['indir']))
    #     files = locate(self.gen_set['file_for_it'], root=self.gen_set["indir"], followlinks=True)
    #     # remove folders like 'collated'
    #     selected = []
    #     for file in files:
    #         if file.__contains__('output-'):
    #             selected.append(file)
    #     # for overall count of number of iterations and files
    #     it_time = np.zeros(2)
    #     for file in selected:
    #         o_name = file.split('/')
    #         o_dir = ''
    #         for o_part in o_name:
    #             if o_part.__contains__('output-'):
    #                 o_dir = o_part
    #         if o_dir == '':
    #             raise NameError("Did not find output-xxxx in {}".format(o_name))
    #         it_time_i = np.loadtxt(file, usecols=(0,1))
    #         self.output_it_map[o_dir] = it_time_i
    #         it_time = np.vstack((it_time, it_time_i))
    #     it_time = np.delete(it_time, 0, 0)
    #     print('outputs:{} iterations:{} [{}->{}]'.format(len(selected),
    #                                                      len(it_time[:,0]),
    #                                                      int(it_time[:,0].min()),
    #                                                      int(it_time[:,0].max())))
    #     print('-' * 30 + '------DONE-----' + '-' * 30)
    #
    #     self.output_it_map, it_time = set_it_output_map(Paths.gw170817+self.sim+'/')
    #
    #     return it_time

    def check_v_n(self, v_n):
        if v_n not in self.list_v_ns:
            raise NameError("v_n:{} not in the v_n list (in the class)\n{}".format(v_n, self.list_v_ns))

    def check_plane(self, plane):
        if plane not in self.list_planes:
            raise NameError("plane:{} not in the plane_list (in the class)\n{}".format(plane, self.list_planes))

    def i_v_n(self, v_n):
        self.check_v_n(v_n)
        return int(self.list_v_ns.index(v_n))
    #
    def i_plane(self, plane):
        self.check_plane(plane)
        return int(self.list_planes.index(plane))

    def load_dataset(self, o_dir, plane, v_n):
        fname = v_n + '.' + plane + '.h5'
        files = locate(fname, root=self.gen_set['indir'] + o_dir +'/', followlinks=False)
        print("\t Loading: {} plane:{} v_n:{} dataset ({} files)"
              .format(o_dir, plane, v_n, len(files)))
        if len(files) > 1:
            raise ValueError("More than 1 file ({}) found. \nFile:{} location:{}"
                             "\nFiles: {}"
                             .format(len(files), fname, self.gen_set['indir'] + o_dir +'/', files))
        if len(files) == 0:
            raise IOError("NO fils found for {}. \nlocation:{}"
                             .format(fname, self.gen_set['indir'] + o_dir +'/'))
        dset = h5.dataset(files)
        # grid = dset.get_grid(iteration=it)
        # print("grid.origin: {}".format(grid.origin))
        # print("grid.dim   : {}".format(grid.dim))
        # print("grid.coordinates(): {}".format([ [np.array(coord).min(), np.array(coord).max()] for coord in grid.coordinates()]))
        # print("grid.levels: {}".format([level for level in grid.levels]))
        # print("grid.extent: {}".format(grid.extent))

        # exit(1)
        # print("\t loading it:{} plane:{} v_n:{} dset:{}"
        #       .format(o_dir, plane, v_n, dset))
        dset.get_grid().mesh()
        self.dataset_matrix[self.i_output(o_dir)][self.i_plane(plane)][self.i_v_n(v_n)] = dset

    def i_output(self, o_dir):
        if o_dir not in self.list_outputs:
            raise NameError("plane:{} not in the plane_list (in the class)\n{}"
                            .format(o_dir, self.list_outputs))

        return int(self.list_outputs.index(o_dir))

    def is_dataset_loaded(self, o_dir, plane, v_n):
        if isinstance(self.dataset_matrix[self.i_output(o_dir)][self.i_plane(plane)][self.i_v_n(v_n)], int):
            self.load_dataset(o_dir, plane, v_n)

    # def it_to_output_dir(self, it):
    #     req_output_data_dir = []
    #     for output_data_dir in self.list_outputs:
    #         if int(it) in np.array(self.output_it_map[output_data_dir], dtype=int)[:, 0]:
    #             req_output_data_dir.append(output_data_dir)
    #
    #     if len(req_output_data_dir) > 1:
    #         if self.set_use_new_output_if_duplicated:
    #             print("Warning: it:{} is found in multiple outputs:{}"
    #                          .format(it, req_output_data_dir))
    #             return req_output_data_dir[0]
    #
    #         raise ValueError("it:{} is found in multiple outputs:{}\n"
    #                          "to overwrite, set 'set_use_new_output_if_duplicated=True' "
    #                          .format(it, req_output_data_dir))
    #     elif len(req_output_data_dir) == 0:
    #         raise ValueError("it:{} not found in a output_it_map:\n{}\n"
    #                              .format(it, self.output_it_map.keys()))
    #     else:
    #         return req_output_data_dir[0]

    def get_dataset(self, it, plane, v_n):
        # o_dir = self.it_to_output_dir(it)
        output = self.get_output_for_it(it)
        self.is_dataset_loaded(output, plane, v_n)
        dset = self.dataset_matrix[self.i_output(output)][self.i_plane(plane)][self.i_v_n(v_n)]
        if not it in dset.iterations:
            it__ = int(dset.iterations[self.find_nearest_index(np.array(dset.iterations), it)])
            raise ValueError("Iteration it:{} (located in {}) \n"
                             "not in the dataset list. Closest:{} Full list:\n{}"
                             .format(it, output, it__, dset.iterations))
        return dset

    def del_dataset(self, it, plane, v_n):
        # o_dir = self.it_to_output_dir(it)
        output = self.get_output_for_it(it)
        self.dataset_matrix[self.i_output(output)][self.i_plane(plane)][self.i_v_n(v_n)] = 0

    # def get_time(self, it):
    #
    #     time = self.it_time[np.where(self.it_time[:,0] == it), 1]
    #     time = [item for sublist in time for item in sublist]
    #     print(time)
    #     if len(time) == 2:
    #         Printcolor.yellow("for it:{} more than one timestep found {}"
    #                          .format(it, time))
    #         if time[0] == time[1]:
    #             return float(time[0]) * time_constant / 1000
    #         else:
    #             raise ValueError("for it:{} more than one timestep found {}"
    #                              .format(it, time))
    #     if len(time) == 0:
    #         raise ValueError("for it:{} no timesteps found"
    #                          .format(it))
    #     return float(time[0]) * time_constant / 1000

    def load_all(self, plane, v_n):

        print('-' * 25 + 'LOADING ALL DATASETS ({})'
              .format(self.gen_set['file_for_it']) + '-' * 25)
        Printcolor.yellow("Warning: loading all {} datasets "
                          "is a slow process".format(len(self.list_outputs)))
        for o_dir in self.list_outputs:
            try:
                self.is_dataset_loaded(o_dir, plane, v_n)
            except ValueError:
                Printcolor.red("Failed to load o_dir:{} plane:{} v_n:{}"
                               .format(o_dir, plane, v_n))

        self.set_all_it_times_from_outputs(plane, v_n)

        print('-' * 30 + '------DONE-----' + '-' * 30)

    def get_all_iterations_times(self, plane, v_n):

        iterations = []
        times = []
        for output in self.list_outputs:
            if isinstance(self.dataset_matrix[self.i_output(output)][self.i_plane(plane)][self.i_v_n(v_n)], int):
                raise ValueError("Not all datasets are loaded. Missing: {}".format(output))
            dset = self.dataset_matrix[self.i_output(output)][self.i_plane(plane)][self.i_v_n(v_n)]
            # iterations.append(dset.iterations)
            for it in dset.iterations:
                iterations.append(it)
                time = dset.get_time(it) * 0.004925794970773136 / 1000
                times.append(time)
                # print("it:{}, time:{}".format(it, time))

        assert len(list(set(iterations))) == len(list(set(times)))

        iterations = np.sort(list(set(iterations)))
        times = np.sort(list(set(times)))

        return iterations, times

    def set_all_it_times_from_outputs(self, plane, v_n):

        self.iterations, self.times = self.get_all_iterations_times(plane, v_n)
        print('\tIterations [{}->{}] and times [{:.3f}->{:.3f}] have been reset.'
              .format(self.iterations[0], self.iterations[-1],
                      self.times[0], self.times[-1]))

        # return list(set([item for sublist in iterations for item in sublist])), \
        #        list(set([item for sublist in iterations for item in sublist]))

    # def get_all_timesteps(self, plane, v_n):
    #
    #     iterations = self.get_all_iterations(plane, v_n)
    #     times = []
    #     for iteration in iterations:
    #         times.append(self.get_time(iteration))
    #     return times


class EXTRACT_STORE_DATA(LOAD_STORE_DATASETS):
    """
    blablabla
    """

    def __init__(self, sim):

        LOAD_STORE_DATASETS.__init__(self, sim)

        # self.gen_set = {'nlevels': 7,
        #                 'file_for_it': 'H.norm2.asc',
        #                 'iterations': 0,
        #                 'indir': Paths.gw170817 + sim + '/',
        #                 'outdir': Paths.ppr_sims + sim + '/2d/'}

        # self.list_v_ns   = ['rho', 'Y_e', 'temperature', 's_phi', 'entropy', 'dens_unbnd']
        # self.list_planes = ['xy', 'xz']
        self.v_n_map = {
            'rho':          "HYDROBASE::rho",
            'Y_e':          "HYDROBASE::Y_e",
            's_phi':        "BNSANALYSIS::s_phi",
            'temperature':  "HYDROBASE::temperature",
            'entropy':      "HYDROBASE::entropy",
            'dens_unbnd':   "BNSANALYSIS::dens_unbnd",
            'R_eff_nua':    "THC_LEAKAGEBASE::R_eff_nua",
            'R_eff_nue':    "THC_LEAKAGEBASE::R_eff_nue",
            'R_eff_nux':    "THC_LEAKAGEBASE::R_eff_nux",
            'Q_eff_nua':    "THC_LEAKAGEBASE::Q_eff_nua",
            'Q_eff_nue':    "THC_LEAKAGEBASE::Q_eff_nue",
            'Q_eff_nux':    "THC_LEAKAGEBASE::Q_eff_nux",
            'optd_0_nua':   "THC_LEAKAGEBASE::optd_0_nua",
            'optd_0_nue':   "THC_LEAKAGEBASE::optd_0_nue",
            'optd_0_nux':   "THC_LEAKAGEBASE::optd_0_nux",
            'optd_1_nua':   "THC_LEAKAGEBASE::optd_1_nua",
            'optd_1_nue':   "THC_LEAKAGEBASE::optd_1_nue",
            'optd_1_nux':   "THC_LEAKAGEBASE::optd_1_nux",
        }


        # self.output_it_map = {}
        # self.it_time = self.set_it_output_map()

        self.data_matrix = [[[np.zeros(0,)
                            for z in range(len(self.list_v_ns))]
                            for k in range(len(self.list_planes))]
                            for s in range(len(self.iterations))]

        self.grid_matrix = [[[0
                            for z in range(len(self.list_v_ns))]
                            for k in range(len(self.list_planes))]
                            for s in range(len(self.iterations))]

    def check_it(self, it):
        if not int(it) in np.array(self.iterations, dtype=int):
            it_ = int(self.iterations[self.find_nearest_index(self.iterations, it), 0])
            raise NameError("it:{} not in the list on iterations: Closest one: {}"
                            .format(it, it_))

        idx = np.where(np.array(self.iterations, dtype=int) == int(it))

        if len(idx) == 0:
            raise ValueError("For it:{} NO it are found in the it_time[:,0]".format(it))

        if len(idx) > 1:
            raise ValueError("For it:{} multiple it are found in the it_time[:,0]".format(it))

        # print("it:{} idx:{}".format(it, idx))

    def i_it(self, it):
        self.check_it(it)
        idx = list(self.iterations).index(int(it))
        return idx
        #
        #
        #
        #
        # self.check_it(it)
        # idx = np.array(np.where(np.array(self.it_time[:,0], dtype=int) == int(it)), dtype=int)
        # idx = list(set([item for sublist in idx for item in sublist]))
        # print("it:{} idx:{}, type:{} len:{}".format(it, idx, type(idx), len(idx)))
        # return int(idx)

    # ---------- GRID

    def extract_grid(self, it, plane, v_n):
        print("\t extracting grid it:{} plane:{} v_n:{}".format(it, plane, v_n))
        dset = self.get_dataset(it, plane, v_n)
        self.grid_matrix[self.i_it(it)][self.i_plane(plane)][self.i_v_n(v_n)] = \
            dset.get_grid(iteration=it)

    def is_grid_extracted(self, it, plane, v_n):

        if isinstance(self.grid_matrix[self.i_it(it)][self.i_plane(plane)][self.i_v_n(v_n)], int):
            self.extract_grid(it, plane, v_n)

    def get_grid(self, it, plane, v_n):

        self.check_plane(plane)
        self.check_v_n(v_n)
        self.is_grid_extracted(it, plane, v_n)

        return self.grid_matrix[self.i_it(it)][self.i_plane(plane)][self.i_v_n(v_n)]

    def del_grid(self, it, plane, v_n):

        self.check_plane(plane)
        self.check_v_n(v_n)

        self.grid_matrix[self.i_it(it)][self.i_plane(plane)][self.i_v_n(v_n)] = 0

    # ---------- DATA

    def extract(self, it, plane, v_n):

        print("\t extracting it:{} plane:{} v_n:{}".format(it, plane, v_n))
        dset = self.get_dataset(it, plane, v_n)
        try:
            data = dset.get_grid_data(self.get_grid(it, plane, v_n),
                                        iteration=it,
                                        variable=self.v_n_map[v_n])
            self.data_matrix[self.i_it(it)][self.i_plane(plane)][self.i_v_n(v_n)] = data
        except KeyError:
            raise KeyError("Wrong Key. Data not found. dset contains:{} attmeped:{} {} {}".format(dset.metadata[0],
                                                                                         self.v_n_map[v_n],
                                                                                                  plane,
                                                                                                  it))

    def is_data_extracted(self, it, plane, v_n):

        if len(self.data_matrix[self.i_it(it)][self.i_plane(plane)][self.i_v_n(v_n)]) == 0:
            self.extract(it, plane, v_n)

    def get_data(self, it, plane, v_n):
        self.check_plane(plane)
        self.check_v_n(v_n)

        self.is_data_extracted(it, plane, v_n)

        return self.data_matrix[self.i_it(it)][self.i_plane(plane)][self.i_v_n(v_n)]

    def del_data(self, it, plane, v_n):

        self.check_plane(plane)
        self.check_v_n(v_n)

        self.data_matrix[self.i_it(it)][self.i_plane(plane)][self.i_v_n(v_n)] = np.zeros(0,)

    # ----------- TIME

    # def get_time(self, it):
    #     self.check_it(it)
    #     return float(self.it_time[np.where(self.it_time[:,0] == it), 1][0]) * time_constant / 1000



    # def get_time_(self, it):
    #     return self.get_time__(it)


class EXTRACT_FOR_RL(EXTRACT_STORE_DATA):

    def __init__(self, sim):
        EXTRACT_STORE_DATA.__init__(self, sim)

        self.list_grid_v_ns = ["x", "y", "z", "delta"]


        self.extracted_grid_matrix = [[[[np.zeros(0,)
                            for z in range(len(self.list_grid_v_ns))]
                            for j in range(self.nlevels)]
                            for k in range(len(self.list_planes))]
                            for s in range(len(self.iterations))]

        self.extracted_data_matrix = [[[[np.zeros(0,)
                            for z in range(len(self.list_v_ns))]
                            for j in range(self.nlevels)]
                            for k in range(len(self.list_planes))]
                            for s in range(len(self.iterations))]

        self.default_v_n = "rho"

    def check_rl(self, rl):
        if rl < 0:
            raise ValueError("Unphysical rl:{} ".format(rl))
        if rl < 0 or rl > self.nlevels:
            raise ValueError("rl is not in limits: {}"
                             .format(rl, self.nlevels))

    def i_rl(self, rl):
        return int(rl)

    def check_grid_v_n(self, v_n):
        if not v_n in self.list_grid_v_ns:
            raise NameError("v_n:{} not in list_grid_v_ns:{}"
                            .format(v_n, self.list_grid_v_ns))

    def i_gr_v_n(self, v_n):
        return int(self.list_grid_v_ns.index(v_n))

    def __extract_grid_data_rl(self, it, plane, rl, grid):

        coords = grid.coordinates()
        mesh = list(np.meshgrid(coords[self.i_rl(rl)], indexing='ij'))
        points = np.column_stack([x.flatten() for x in mesh])
        xyz = []
        delta = grid.levels[self.i_rl(rl)].delta
        # for x in mesh:
        #     xyz.append(x)
        #     print("x: {} ".format(x.shape))
        # print(len(coords))
        # # print(mesh)
        # print(len(mesh))
        # print(len(xyz))
        # print(points.shape)

        self.extracted_grid_matrix[self.i_it(it)][self.i_plane(plane)][self.i_rl(rl)][self.i_gr_v_n("delta")] = delta
        if plane == "xy":
            x, y = grid.mesh()[rl]
            # print(x.shape)
            # print(y.shape)
            self.extracted_grid_matrix[self.i_it(it)][self.i_plane(plane)][self.i_rl(rl)][self.i_gr_v_n("x")] = x
            self.extracted_grid_matrix[self.i_it(it)][self.i_plane(plane)][self.i_rl(rl)][self.i_gr_v_n("y")] = y
        elif plane == "xz":
            x, z = grid.mesh()[rl]
            # print(x.shape)
            # print(z.shape)
            self.extracted_grid_matrix[self.i_it(it)][self.i_plane(plane)][self.i_rl(rl)][self.i_gr_v_n("x")] = x
            self.extracted_grid_matrix[self.i_it(it)][self.i_plane(plane)][self.i_rl(rl)][self.i_gr_v_n("z")] = z
        else:
            raise NameError("Plane: {} is not recognized")
        # exit(0)

    def extract_grid_data_rl(self, it, plane, rl, v_n):

        self.check_grid_v_n(v_n)

        for data_v_n in self.list_v_ns:
            # scrolling through all possible v_ns, looking for the one loaded
            if not isinstance(self.grid_matrix[self.i_it(it)][self.i_plane(plane)][self.i_v_n(data_v_n)], int):
                grid = self.get_grid(it, plane, data_v_n)
                self.__extract_grid_data_rl(it, plane, rl, grid)
                return 0
        print("\tNo pre-loaded data found. Loading default ({}))".format(self.default_v_n))
        grid = self.get_grid(it, plane, self.default_v_n)
        self.__extract_grid_data_rl(it, plane, rl, grid)
        return 0


    def is_grid_extracted_for_rl(self, it, plane, rl, v_n):

        arr = self.extracted_grid_matrix[self.i_it(it)][self.i_plane(plane)][self.i_rl(rl)][self.i_gr_v_n(v_n)]
        if len(arr) == 0:
            self.extract_grid_data_rl(it, plane, rl, v_n)

    def get_grid_v_n_rl(self, it, plane, rl, v_n):

        self.check_grid_v_n(v_n)
        self.check_plane(plane)
        self.check_it(it)
        self.check_rl(rl)

        self.is_grid_extracted_for_rl(it, plane, rl, v_n)

        data = self.extracted_grid_matrix[self.i_it(it)][self.i_plane(plane)][self.i_rl(rl)][self.i_gr_v_n(v_n)]
        return data



    def extract_data_rl(self, it, plane, rl, v_n):

        data = self.get_data(it, plane, v_n)
        data = np.array(data[self.i_rl(rl)])

        self.extracted_data_matrix[self.i_it(it)][self.i_plane(plane)][self.i_rl(rl)][self.i_v_n(v_n)] = data

    def is_data_extracted_for_rl(self, it, plane,rl, v_n):

        arr = self.extracted_data_matrix[self.i_it(it)][self.i_plane(plane)][self.i_rl(rl)][self.i_v_n(v_n)]
        if len(arr) == 0:
            self.extract_data_rl(it, plane, rl, v_n)

    def get_data_rl(self, it, plane, rl, v_n):

        self.check_v_n(v_n)
        self.check_plane(plane)
        self.check_it(it)
        self.check_rl(rl)

        self.is_data_extracted_for_rl(it, plane, rl, v_n)

        data = self.extracted_data_matrix[self.i_it(it)][self.i_plane(plane)][self.i_rl(rl)][self.i_v_n(v_n)]
        return data


class COMPUTE_STORE(EXTRACT_FOR_RL):

    def __init__(self, sim):
        EXTRACT_FOR_RL.__init__(self, sim)

    def get_rho_modes_for_rl(self, rl=6, mmax=8):
        import numexpr as ne

        iterations = self.iterations  # apply limits on it
        #
        times = []
        modes = [[] for m in range(mmax + 1)]
        xcs = []
        ycs = []
        #
        for idx, it in enumerate(iterations):
            print("\tprocessing iteration: {}/{}".format(idx, len(iterations)))
            # get z=0 slice
            # lapse = o_slice.get_data_rl(it, "xy", rl, "lapse")
            rho = o_slice.get_data_rl(it, "xy", rl, "rho")
            # o_slice.get_data_rl(it, "xy", rl, "vol")
            # w_lorentz = o_slice.get_data_rl(it, "xy", rl, "w_lorentz")

            delta = self.get_grid_v_n_rl(it, "xy", rl, "delta")#[:-1]
            #
            dxyz = np.prod(delta)
            x = self.get_grid_v_n_rl(it, "xy", rl, "x")
            y = self.get_grid_v_n_rl(it, "xy", rl, "y")
            # z = self.get_grid_v_n_rl(it, "xy", rl, "z")
            # x = x[:, :, 0]
            # y = y[:, :, 0]

            # apply mask to cut off the horizon
            # rho[lapse < 0.15] = 0

            # Exclude region outside refinement levels
            idx = np.isnan(rho)
            rho[idx] = 0.0
            # vol[idx] = 0.0
            # w_lorentz[idx] = 0.0

            # Compute center of mass
            # modes[0].append(dxyz * ne.evaluate("sum(rho * w_lorentz * vol)"))
            # Ix = dxyz * ne.evaluate("sum(rho * w_lorentz * vol * x)")
            # Iy = dxyz * ne.evaluate("sum(rho * w_lorentz * vol * y)")
            # xc = Ix / modes[0][-1]
            # yc = Iy / modes[0][-1]
            # phi = ne.evaluate("arctan2(y - yc, x - xc)")
            #
            modes[0].append(dxyz * ne.evaluate("sum(rho)"))
            Ix = dxyz * ne.evaluate("sum(rho * x)")
            Iy = dxyz * ne.evaluate("sum(rho * y)")
            xc = Ix / modes[0][-1]
            yc = Iy / modes[0][-1]
            phi = ne.evaluate("arctan2(y - yc, x - xc)")


            # phi = ne.evaluate("arctan2(y, x)")

            xcs.append(xc)
            ycs.append(yc)

            # Extract modes
            times.append(self.get_time_for_it(it, "overall", d1d2d3prof="d2"))
            for m in range(1, mmax + 1):
                # modes[m].append(dxyz * ne.evaluate("sum(rho * w_lorentz * vol * exp(-1j * m * phi))"))
                modes[m].append(dxyz * ne.evaluate("sum(rho * exp(-1j * m * phi))"))

        return times, iterations, xcs, ycs, modes

    def density_with_radis(self):

        v_n = "rho"
        rl = 0
        it = self.iterations[0]
        #
        x = self.get_grid_v_n_rl(it, "xy", rl, "x")
        y = self.get_grid_v_n_rl(it, "xy", rl, "y")
        r = np.sqrt(x**2 + y**2)
        rho = o_slice.get_data_rl(it, "xy", rl, "rho")


class CYLINDRICAL_GRID:
    """
        Creates a stretched cylindrical grid and allows
        to interpolate any data from carpet grid onto it.
        Stretched means, that the grid consists of 2 parts:
            1) linear distribution in terms of radius (0-15)
            2) logarithmic dist. in terms of radius (15-512)
        Class stores the grid information in its own variables
        that can be accessed directly or through
        `get_new_grid(v_n)` method

        Requirements:
            > dictionary grid_info{} that describes the grid:
            > class `carpet_grid` from scidata
        Usage:
            to access the new grid mesh arrays use:
                get_new_grid(v_n)
            to do the interpolation of arr, use
                get_int_arr(arr)
    """

    def __init__(self, grid_info):

        self.grid_info = grid_info # "n_r", "n_phi", "n_z"
        self.grid_type = "cyl"
        self.list_int_grid_v_ns = ["x_cyl", "y_cyl", "z_cyl",
                          "r_cyl", "phi_cyl",
                          "dr_cyl", "dphi_cyl", "dz_cyl"]

        print('-' * 25 + 'INITIALIZING CYLINDRICAL GRID' + '-' * 25)

        phi_cyl, r_cyl, z_cyl, \
        self.dphi_cyl_3d, self.dr_cyl_3d, self.dz_cyl_3d = self.get_phi_r_z_grid()

        self.r_cyl_3d, self.phi_cyl_3d, self.z_cyl_3d \
            = np.meshgrid(r_cyl, phi_cyl, z_cyl, indexing='ij')
        self.x_cyl_3d = self.r_cyl_3d * np.cos(self.phi_cyl_3d)
        self.y_cyl_3d = self.r_cyl_3d * np.sin(self.phi_cyl_3d)

        # print(self.z_cyl_3d[0, 0, :]); exit(1)

        print("\t GRID: [phi:r:z] = [{}:{}:{}]".format(len(phi_cyl), len(r_cyl), len(z_cyl)))

        print('-' * 30 + '------DONE-----' + '-' * 30)
        print('\n')

    # cylindrical grid
    @staticmethod
    def make_stretched_grid(x0, x1, x2, nlin, nlog):
        assert x1 > 0
        assert x2 > 0
        x_lin_f = np.linspace(x0, x1, nlin)
        x_log_f = 10.0 ** np.linspace(log10(x1), log10(x2), nlog)
        return np.concatenate((x_lin_f, x_log_f))

    def get_phi_r_z_grid(self):

        # extracting grid info
        n_r = self.grid_info["n_r"]
        n_phi = self.grid_info["n_phi"]
        n_z = self.grid_info["n_z"]

        # constracting the grid
        r_cyl_f = self.make_stretched_grid(0., 15., 512., n_r, n_phi)
        z_cyl_f = self.make_stretched_grid(0., 15., 512., n_r, n_phi)
        phi_cyl_f = np.linspace(0, 2 * np.pi, n_phi)

        # edges -> bins (cells)
        r_cyl = 0.5 * (r_cyl_f[1:] + r_cyl_f[:-1])
        z_cyl = 0.5 * (z_cyl_f[1:] + z_cyl_f[:-1])
        phi_cyl = 0.5 * (phi_cyl_f[1:] + phi_cyl_f[:-1])

        # 1D grind -> 3D grid (to mimic the r, z, phi structure)
        dr_cyl = np.diff(r_cyl_f)[:, np.newaxis, np.newaxis]
        dphi_cyl = np.diff(phi_cyl_f)[np.newaxis, :, np.newaxis]
        dz_cyl = np.diff(z_cyl_f)[np.newaxis, np.newaxis, :]

        return phi_cyl, r_cyl, z_cyl, dphi_cyl, dr_cyl, dz_cyl

    def get_xi(self):
        return np.column_stack([self.x_cyl_3d.flatten(),
                                self.y_cyl_3d.flatten(),
                                self.z_cyl_3d.flatten()])

    def get_shape(self):
        return self.x_cyl_3d.shape

    # generic methods to be present in all INTERPOLATION CLASSES
    # def get_int_arr(self, arr_3d):
    #
    #     # if not self.x_cyl_3d.shape == arr_3d.shape:
    #     #     raise ValueError("Passed for interpolation 3d array has wrong shape:\n"
    #     #                      "{} Expected {}".format(arr_3d.shape, self.x_cyl_3d.shape))
    #     xi = np.column_stack([self.x_cyl_3d.flatten(),
    #                           self.y_cyl_3d.flatten(),
    #                           self.z_cyl_3d.flatten()])
    #     F = Interpolator(self.carpet_grid, arr_3d, interp=1)
    #     res_arr_3d = F(xi).reshape(self.x_cyl_3d.shape)
    #     return res_arr_3d

    # def get_int_grid(self, v_n):
    #     if v_n == "x_cyl":
    #         return self.x_cyl_3d
    #     elif v_n == "y_cyl":
    #         return self.y_cyl_3d
    #     elif v_n == "z_cyl":
    #         return self.z_cyl_3d
    #     elif v_n == "r_cyl":
    #         return self.r_cyl_3d
    #     elif v_n == "phi_cyl":
    #         return self.phi_cyl_3d
    #     elif v_n == "dr_cyl":
    #         return self.dr_cyl_3d
    #     elif v_n == "dphi_cyl":
    #         return self.dphi_cyl_3d
    #     elif v_n == "dz_cyl":
    #         return self.dz_cyl_3d
    #     else:
    #         raise NameError("v_n: {} not recogized in grid. Available:{}"
    #                         .format(v_n, self.grid_v_ns))

    def get_int_grid(self, v_n, projection='xyz'):

        if v_n == "x_cyl":
            d3arr = self.x_cyl_3d
        elif v_n == "y_cyl":
            d3arr = self.y_cyl_3d
        elif v_n == "z_cyl":
            d3arr = self.z_cyl_3d
        elif v_n == "r_cyl":
            d3arr = self.r_cyl_3d
        elif v_n == "phi_cyl":
            d3arr = self.phi_cyl_3d
        elif v_n == "dr_cyl":
            d3arr = self.dr_cyl_3d
        elif v_n == "dphi_cyl":
            d3arr = self.dphi_cyl_3d
        elif v_n == "dz_cyl":
            d3arr = self.dz_cyl_3d
        else:
            raise NameError("v_n: {} not recogized in grid. Available:{}"
                            .format(v_n, self.list_int_grid_v_ns))

        if projection == 'xyz':
            return d3arr
        elif projection == 'xy':
            return d3arr[:, :, 0]
        elif projection == 'xz':
            return d3arr[0, :, :]
        elif projection == 'yz':
            return d3arr[:, 0, :]
        else:
            raise NameError("projection: {} not recogized".format(projection))

    def save_grid(self, sim, projection):

        grid_type = self.grid_type

        path = Paths.ppr_sims + sim + "/res_2d/"
        if projection == 'xyz' or projection == None:
            fname = path + self.grid_type  + '_' + 'grid.h5'
        else:
            fname = path + self.grid_type + '_' + 'grid' + '_' + projection + '.h5'

        outfile = h5py.File(fname, "w")

        if not os.path.exists(path):
            os.makedirs(path)

        # print("Saving grid...")
        for v_n in self.list_int_grid_v_ns:
            outfile.create_dataset(v_n, data=self.get_int_grid(v_n, projection))
        outfile.close()


class INTERPOLATE_STORE_2D(EXTRACT_STORE_DATA):
    """
    blablabla
    """

    def __init__(self, sim):



        self.gen_set = {'nlevels':7,
                        'file_for_it': 'H.norm2.asc',
                        'iterations':0,
                        'indir': Paths.gw170817 + sim + '/',
                        'outdir': Paths.ppr_sims + sim + '/res_2d/',
                        }
        self.grid_set = {'type': 'cylindrical', 'n_r': 150, 'n_phi': 150, 'n_z': -100}

        # self.output_it_map = {}

        self.list_v_ns = ['rho', 'Y_e', 'temperature', 's_phi', 'entropy', 'dens_unbnd']
        self.list_planes=['xy', 'xz']


        EXTRACT_STORE_DATA.__init__(self, sim)
        # print(self.i_it(1052672)) WORKS
        # self.data_cl = data_cl

        _, itd2, td2 = self.get_ittime("overall", d1d2d3prof="d2")


        self.intdata_matrix = [[[0
                                  for z in range(len(self.list_v_ns))]
                                  for k in range(len(self.list_planes))]
                                  for s in range(len(td2))]

        # select a grid class

        if self.grid_set['type'] == 'cylindrical':
            self.new_grid_cl = CYLINDRICAL_GRID(self.grid_set)
        else:
            raise NameError("Grid:{} is not recognized")

    # def tmp(self):
    #     print(self.i_it(1052672))
    #     print(self.i_plane('xy'))

    def do_interpolate(self, it, plane, v_n):

        print("\t Interpolating it:{} plane:{} v_n:{} onto {} grid"
              .format(it, plane, v_n, self.grid_set['type']))

        data = self.get_data(it, plane, v_n)
        # print("\t using it:{} plane:{} v_n:{} dset:{}"
        #       .format(it, plane, v_n, data))
        grid = self.get_grid(it, plane, v_n)
        # print(grid)
        v_n_interpolator = Interpolator(grid, data, interp=0)
        # print("data")
        # print(data)
        # print('\n')

        self.coords = grid.coordinates()
        for i in range(len(grid)):
            if i == len(grid)-1:
                mesh = list(np.meshgrid(self.coords[i], indexing='ij'))
                points = np.column_stack([x.flatten() for x in mesh])
                for x in mesh:
                    print("x: {} ".format(x.shape))
                print("x[0]: {}".format(x[0].shape))
                print("x[1]: {}".format(x[1].shape))
                print("data: {} ".format(np.array(data[i]).shape))
                print("data: {}".format(np.array(data[i]).shape))
                print(points.shape)
                print(len(mesh))
                # exit(1)
                data = np.array(data[i])
                from matplotlib import colors
                fig = plt.figure()
                ax = fig.add_subplot(111)
                norm = colors.LogNorm(vmin=data.min(), vmax=data.max())
                ax.pcolormesh(x[0], x[1], data.T, norm=norm, cmap="inferno_r")
                plt.ylim(0, 50)
                plt.title(r"$xz$-plane")
                plt.savefig('{}'.format(Paths.ppr_sims + self.sim + '/res_2d/' + "{}_{}_{}.png"
                                        .format(it, plane, v_n)), bbox_inches='tight', dpi=128)
                print("saved pi_test2.png")
                plt.close()


            # print(data[i])
        exit(1)


        if self.grid_set['type'] == 'cylindrical':

            x_cyl_2d = self.new_grid_cl.get_int_grid('x_cyl', plane)
            y_cyl_2d = self.new_grid_cl.get_int_grid('y_cyl', plane)
            z_cyl_2d = self.new_grid_cl.get_int_grid('z_cyl', plane)

            # print(x_cyl_2d[:, 0])
            # print('\n')
            # print(z_cyl_2d[0, :])
            # print('\n')

            if plane == 'xy':
                xi = np.column_stack([x_cyl_2d.flatten(), y_cyl_2d.flatten()])
            elif plane == 'xz':
                xi = np.column_stack([x_cyl_2d.flatten(), z_cyl_2d.flatten()])
            elif plane == 'yz':
                xi = np.column_stack([y_cyl_2d.flatten(), z_cyl_2d.flatten()])
            else:
                raise NameError("plane:{} not supported in a new grid creation".format(plane))

            # print("\n")
            # for xii in xi:
            #     print(xii)
            # print("\n")
            res_arr_2d = v_n_interpolator(xi).reshape(x_cyl_2d.shape)
            # print(res_arr_2d)
            # exit(1)
        else:
            raise NameError("Grid class for '{}' is not found".format(self.grid_set['type']))


        data = res_arr_2d
        from matplotlib import colors
        fig = plt.figure()
        ax = fig.add_subplot(111)
        norm = colors.LogNorm(vmin=data.min(), vmax=data.max())
        ax.pcolormesh(x_cyl_2d[:, 0], z_cyl_2d[0, :], data[:, :].T, norm=norm, cmap="inferno_r")
        plt.ylim(0,50)
        plt.title(r"$xz$-plane")
        plt.savefig('{}'.format(Paths.ppr_sims+self.sim+'/res_2d/' + "{}_{}_{}.png"
                                .format(it, plane, v_n)), bbox_inches='tight', dpi=128)
        print("saved pi_test2.png")
        plt.close()
        # exit(1)


        self.intdata_matrix[self.i_it(it)][self.i_plane(plane)][self.i_v_n(v_n)] = \
            res_arr_2d

    def is_data_interpolated(self, it, plane, v_n):

        # print(it)
        # print(self.i_plane(plane))
        # print(self.i_it(it))

        if isinstance(self.intdata_matrix[self.i_it(it)][self.i_plane(plane)][self.i_v_n(v_n)], int):
            self.do_interpolate(it, plane, v_n)

    def get_int(self, it, plane, v_n):
        self.check_v_n(v_n)
        self.check_plane(plane)
        self.is_data_interpolated(it, plane, v_n)
        return self.intdata_matrix[self.i_it(it)][self.i_plane(plane)][self.i_v_n(v_n)]

    def get_new_grid(self, plane, v_n):
        if self.grid_set['type'] == 'cylindrical':
            return self.new_grid_cl.get_int_grid(v_n, plane)
        else:
            raise NameError("Grid:{} is not recognized")

    def del_int(self, it, plane, v_n):
        self.check_v_n(v_n)
        self.check_plane(plane)
        self.is_data_interpolated(it, plane, v_n)
        self.intdata_matrix[self.i_it(it)][self.i_plane(plane)][self.i_v_n(v_n)] = 0

    def save_all(self, plane, v_n):

        self.load_all(plane, v_n)
        self.iterations, self.times = self.get_all_iterations_times(plane, v_n)
        # self.iterations = np.array(self.iterations, dtype=int)

        self.set_use_new_output_if_duplicated = True

        path = Paths.ppr_sims + self.sim + "/res_2d/"
        outfname = path + self.new_grid_cl.grid_type + \
                            '_' + v_n + '_' + plane + '.h5'

        if os.path.isfile(outfname):
            print("Rewriting file{}".format(outfname))
            os.remove(outfname)
        else:
            print("Writing file:{}".format(outfname))

        outfile = h5py.File(path + self.new_grid_cl.grid_type + \
                            '_' + v_n + '_' + plane + '.h5', "w")

        if not os.path.exists(path):
            os.makedirs(path)

        outfile.create_dataset("iterations", data=self.iterations)
        outfile.create_dataset("times", data=self.times)


        # print("Saving grid...")
        for it, t in zip(self.iterations, self.times):
            print("Writing: it:{} time:{}".format(it, t))
            outfile.create_dataset("it={}".format(int(it)),
                                   data=self.get_int(it, plane, v_n))
        outfile.close()

    # def get_time(self, it):
    #     return self.get_time_(it)

""" --- --- --- """

class LOAD_INT_DATA_2D:

    def __init__(self, sim):

        self.sim = sim

        self.grid_type = "cyl"

        self.list_v_ns = ['rho', 'Y_e', 'temperature', 's_phi', 'entropy', 'dens_unbnd']
        self.list_planes=['xy', 'xz']

        self.set_use_new_output_if_duplicated = False

        self.output_it_map, self.it_time = \
            set_it_output_map(Paths.gw170817+self.sim+'/')

        self.iterations = list(self.it_time[:, 0])
        self.times = list(self.it_time[:, 1])

        self.data_matrix = [[[np.zeros(0,)
                                  for z in range(len(self.list_v_ns))]
                                  for k in range(len(self.list_planes))]
                                  for s in range(len(self.iterations))]

        self.list_grid_v_ns = []
        self.grid_matrix = [[np.zeros(0, )
                             for z in range(len(self.list_grid_v_ns))]
                            for k in range(len(self.list_planes))]

    def check_v_n(self, v_n):
        if v_n not in self.list_v_ns:
            raise NameError("v_n:{} not in the v_n list (in the class)\n{}".format(v_n, self.list_v_ns))

    def check_plane(self, plane):
        if plane not in self.list_planes:
            raise NameError("plane:{} not in the plane_list (in the class)\n{}".format(plane, self.list_planes))

    def i_v_n(self, v_n):
        self.check_v_n(v_n)
        return int(self.list_v_ns.index(v_n))

    def i_plane(self, plane):
        self.check_plane(plane)
        return int(self.list_planes.index(plane))

    def check_it(self, it):
        if not it in self.iterations:
            raise NameError("it:{} is not in the list of iterations \n{}"
                            .format(it, self.iterations))

    def i_it(self, it):
        return int(self.iterations.index(it))

    def load_iteration_list(self):

        path = Paths.ppr_sims + self.sim + "/res_2d/"
        for v_n in self.list_v_ns:
            for plane in self.list_planes:
                fname = path + self.grid_type + \
                            '_' + v_n + '_' + plane + '.h5'
                if os.path.isfile(fname):
                    dfile = h5py.File(fname, "r")
                    iterations = np.array(dfile["iterations"], dtype=int)
                    times = np.array(dfile["times"], dtype=float)
                    self.iterations = list(iterations)
                    self.times = list(times)
                    self.data_matrix = [[[np.zeros(0, )
                                             for z in range(len(self.list_v_ns))]
                                            for k in range(len(self.list_planes))]
                                           for s in range(len(self.iterations))]
                    print("\titerations ({}) are set".format(len(self.iterations)))
                    return 0
        raise IOError("for sim:{} no data for loading iterations found. "
                      "no data for any of the files in a for of "
                      "fname = path + self.grid_type + '_' + v_n + '_' + plane + '.h5'")

    def load_data(self, plane, v_n):
        path = Paths.ppr_sims + self.sim + "/res_2d/"
        fname = path + self.grid_type + '_' + v_n + '_' + plane + '.h5'

        if not os.path.isfile(fname):
            raise IOError("File: {} not found"
                          .format(fname))

        dfile = h5py.File(fname, "r")
        iterations = np.array(dfile["iterations"], dtype=int)

        for it in iterations:

            if int(it) not in self.iterations:
                raise ValueError("it:{} found in dataset:{} "
                                 "is not in preloaded iteration list"
                                 "\n{}"
                                 .format(it, fname, self.iterations))

            self.data_matrix[self.i_it(it)][self.i_plane(plane)][self.i_v_n(v_n)] = \
                np.array(dfile["it={}".format(int(it))])



    def is_data_loaded(self, it, plane, v_n):

        if len(self.data_matrix[self.i_it(it)][self.i_plane(plane)][self.i_v_n(v_n)]) == 0:
            self.load_data(plane, v_n)

    def is_grid_loaded(self, plane = 'xy'):

        if len(self.list_grid_v_ns) == 0:
            self.load_grid(plane)

    def load_grid(self, plane):

        ffpath = ''

        path = Paths.ppr_sims + self.sim + "/res_2d/"
        fname1 = path + self.grid_type + '_' + 'grid.h5'
        if os.path.isfile(fname1):
            ffpath = fname1
        fname2 = path + self.grid_type + '_' + 'grid' + '_' + plane + '.h5'
        if os.path.isfile(fname2):
            ffpath = fname2
        if ffpath == '':
            raise IOError("Grid not found. Neither {} nor {} is found"
                          .format(fname1,fname2))

        dfile = h5py.File(ffpath, "r")

        self.list_grid_v_ns = []
        for v_n in dfile:
            self.list_grid_v_ns.append(v_n)

        self.grid_matrix = [[np.zeros(0, )
                              for z in range(len(self.list_grid_v_ns))]
                              for k in range(len(self.list_planes))]

        for i_v_n, v_n in enumerate(self.list_grid_v_ns):
            self.grid_matrix[self.i_plane(plane)][i_v_n] = np.array(dfile[v_n])





        if plane == 'xyz' or plane == None:
            fname = path + self.grid_type  + '_' + 'grid.h5'
        else:
            fname = path + self.grid_type + '_' + 'grid' + '_' + plane + '.h5'

    def i_gr_v_n(self, v_n):
        return int(self.list_grid_v_ns.index(v_n))

    def get_int_data(self, it, plane, v_n):
        self.check_v_n(v_n)
        self.check_plane(plane)
        self.is_data_loaded(it, plane, v_n)
        return self.data_matrix[self.i_it(it)][self.i_plane(plane)][self.i_v_n(v_n)]

    def get_int_grid(self, plane, v_n):

        self.is_grid_loaded(plane)
        if not v_n in self.list_grid_v_ns:
            raise NameError("v_n:{} not in the loaded list of grid v_ns:{}"
                            .format(v_n, self.list_grid_v_ns))

        return self.grid_matrix[self.i_plane(plane)][self.i_gr_v_n(v_n)]


class ADD_METHODS_FOR_2DINT_DATA(LOAD_INT_DATA_2D):

    def __init__(self, sim):

        LOAD_INT_DATA_2D.__init__(self, sim)

    def fill_pho0_and_phi2pi(self, phi1d_arr, z2d_arr):
        # adding phi = 360 point *copy of phi = 358(
        phi1d_arr = np.append(phi1d_arr, 2 * np.pi)
        z2d_arr = np.vstack((z2d_arr.T, z2d_arr[:, -1])).T
        # adding phi == 0 point (copy of phi=1)
        phi1d_arr = np.insert(phi1d_arr, 0, 0)
        z2d_arr = np.vstack((z2d_arr[:, 0], z2d_arr.T)).T
        return phi1d_arr, z2d_arr

    def get_modified_2d_data(self, it, plane, v_n_x, v_n_y, v_n, mod):

        x_arr = self.get_int_grid(plane, v_n_y)
        y_arr = self.get_int_grid(plane, v_n_x)
        z_arr = self.get_int_data(it, plane, v_n)


        if mod == 'xy slice':
            return np.array(x_arr[:, 0]), np.array(y_arr[0, :]), np.array(z_arr),

        elif mod == 'fill_phi':
            r2d_arr = np.array(x_arr[:, :])
            phi_arr = np.array(y_arr[0, :])
            z2d_arr = np.array(z_arr[:, :])

            phi_arr, rz2d = self.fill_pho0_and_phi2pi(phi_arr, z2d_arr)

            return np.array(x_arr[:, 0]), phi_arr, rz2d

        elif mod == 'fill_phi *r':
            r2d_arr = np.array(x_arr[:, :])
            phi_arr = np.array(y_arr[0, :])
            z2d_arr = np.array(z_arr[:, :])

            rz2d = r2d_arr * z2d_arr
            phi_arr, rz2d = self.fill_pho0_and_phi2pi(phi_arr, rz2d)

            return np.array(x_arr[:, 0]), phi_arr, rz2d

        elif mod == 'fill_phi *r log':

            r2d_arr = np.array(x_arr[:, :])
            phi_arr = np.array(y_arr[0, :])
            z2d_arr = np.array(z_arr[:, :])

            rz2d = r2d_arr * z2d_arr
            phi_arr, rz2d = self.fill_pho0_and_phi2pi(phi_arr, rz2d)

            return np.array(x_arr[:, 0]), phi_arr, np.log10(rz2d)

        elif mod == 'fill_phi -ave(r)':

            r2d_arr = np.array(x_arr[:, :])
            phi_arr = np.array(y_arr[0, :])
            z2d_arr = np.array(z_arr[:, :])

            for i in range(len(x_arr[:, 0])):
                z2d_arr[i, :] = z2d_arr[i, :] - (np.sum(z2d_arr[i, :]) / len(z2d_arr[i, :]))

            phi_arr, rz2d = self.fill_pho0_and_phi2pi(phi_arr, z2d_arr)

            return np.array(x_arr[:, 0]), phi_arr, rz2d

        else:
            raise NameError("Unknown 'mod' parameter:{} ".format(mod))

""" ===============================================================================================================  """

def __plot_data_for_a_slice(o_slice, v_n, it, t, rl, outdir):

    # ---
    data_arr = o_slice.get_data_rl(it, "xz", rl, v_n)
    x_arr    = o_slice.get_grid_v_n_rl(it, "xz", rl,  "x")
    z_arr    = o_slice.get_grid_v_n_rl(it, "xz", rl, "z")
    def_dic_xz = {'task': 'colormesh',
                  'ptype': 'cartesian', 'aspect': 1.,
                  'xarr': x_arr, "yarr": z_arr, "zarr": data_arr,
                  'position': (1, 1),  # 'title': '[{:.1f} ms]'.format(time_),
                  'cbar': {'location': 'right .03 -0.125', 'label': r'$\rho$ [geo]',  # 'fmt': '%.1e',
                           'labelsize': 14,
                           'fontsize': 14},
                  'v_n_x': 'x', 'v_n_y': 'z', 'v_n': 'rho',
                  'xmin': None, 'xmax': None, 'ymin': None, 'ymax': None, 'vmin': 1e-10, 'vmax': 1e-4,
                  'fill_vmin': False,  # fills the x < vmin with vmin
                  'xscale': None, 'yscale': None,
                  'mask': None, 'cmap': 'inferno_r', 'norm': "log",  # 'inferno_r'
                  'fancyticks': True,
                  'title': {"text": r'${}$ [ms]'.format(0), 'fontsize': 14},
                  'sharex': True,  # removes angular citkscitks
                  'fontsize': 14,
                  'labelsize': 14
                  }

    data_arr = o_slice.get_data_rl(it, "xy", rl, v_n)
    x_arr = o_slice.get_grid_v_n_rl(it, "xy", rl, "x")
    y_arr = o_slice.get_grid_v_n_rl(it, "xy", rl,  "y")
    def_dic_xy = {'task': 'colormesh',
                  'ptype': 'cartesian', 'aspect': 1.,
                  'xarr': x_arr, "yarr": y_arr, "zarr": data_arr,
                  'position': (2, 1),  # 'title': '[{:.1f} ms]'.format(time_),
                  'cbar': {},
                  'v_n_x': 'x', 'v_n_y': 'y', 'v_n': 'rho',
                  'xmin': None, 'xmax': None, 'ymin': None, 'ymax': None, 'vmin': 1e-10, 'vmax': 1e-4,
                  'fill_vmin': False,  # fills the x < vmin with vmin
                  'xscale': None, 'yscale': None,
                  'mask': None, 'cmap': 'inferno_r', 'norm': "log",
                  'fancyticks': True,
                  'title': {},
                  'sharex': False,  # removes angular citkscitks
                  'fontsize': 14,
                  'labelsize': 14
                  }



    # setting scales and limits for data
    if v_n == "rho":
        def_dic_xz['v_n'] = 'rho'
        def_dic_xz['vmin'] = 1e-10
        def_dic_xz['vmax'] = 1e-4
        def_dic_xz['cbar']['label'] = r'$\rho$ [geo]'
        def_dic_xz['cmap'] = 'Greys_r'

        def_dic_xy['v_n'] = 'rho'
        def_dic_xy['vmin'] = 1e-10
        def_dic_xy['vmax'] = 1e-4
        def_dic_xy['cmap'] = 'Greys_r'
    elif v_n == "dens_unbnd":
        def_dic_xz['v_n'] = 'rho'
        def_dic_xz['vmin'] = 1e-13
        def_dic_xz['vmax'] = 1e-6
        def_dic_xz['cbar']['label'] = r'$D_{\rm{unb}}$ [geo]'

        def_dic_xy['v_n'] = 'rho'
        def_dic_xy['vmin'] = 1e-13
        def_dic_xy['vmax'] = 1e-6
    elif v_n == "Y_e":
        def_dic_xz['v_n'] = 'Y_e'
        def_dic_xz['vmin'] = 0.05
        def_dic_xz['vmax'] = 0.5
        def_dic_xz['cbar']['label'] = r'$Y_e$ [geo]'
        def_dic_xz['norm'] = "linear"
        def_dic_xz['cmap'] = 'inferno'

        def_dic_xy['v_n'] = 'Y_e'
        def_dic_xy['vmin'] = 0.05
        def_dic_xy['vmax'] = 0.5
        def_dic_xy['norm'] = "linear"
        def_dic_xy['cmap'] = 'inferno'
    elif v_n == "temp" or v_n == "temperature":
        def_dic_xz['v_n'] = 'temperature'
        def_dic_xz['vmin'] = 1e-2
        def_dic_xz['vmax'] = 1e2
        def_dic_xz['cbar']['label'] = r'$Temperature$ [geo]'

        def_dic_xy['v_n'] = 'temperature'
        def_dic_xy['vmin'] = 1e-2
        def_dic_xy['vmax'] = 1e2
    elif v_n == 'entropy' or v_n == "s_phi":
        def_dic_xz['v_n'] = 'entropy'
        def_dic_xz['vmin'] = 1e-1
        def_dic_xz['vmax'] = 1e2
        def_dic_xz['cbar']['label'] = r'$Entropy$ [geo]'

        def_dic_xy['v_n'] = 'entropy'
        def_dic_xy['vmin'] = 1e-1
        def_dic_xy['vmax'] = 1e2
    elif v_n == "Q_eff_nua":
        def_dic_xz['v_n'] = 'Q_eff_nua'
        def_dic_xz['vmin'] = 1e-18
        def_dic_xz['vmax'] = 1e-14
        def_dic_xz['cbar']['label'] = r'$Q_eff_nua$ [geo]'.replace('_', '\_')

        def_dic_xy['v_n'] = 'Q_eff_nua'
        def_dic_xy['vmin'] = 1e-18
        def_dic_xy['vmax'] = 1e-14
    elif v_n == "Q_eff_nue":
        def_dic_xz['v_n'] = 'Q_eff_nue'
        def_dic_xz['vmin'] = 1e-18
        def_dic_xz['vmax'] = 1e-14
        def_dic_xz['cbar']['label'] = r'$Q_eff_nue$ [geo]'.replace('_', '\_')

        def_dic_xy['v_n'] = 'Q_eff_nue'
        def_dic_xy['vmin'] = 1e-18
        def_dic_xy['vmax'] = 1e-14
    elif v_n == "Q_eff_nux":
        def_dic_xz['v_n'] = 'Q_eff_nux'
        def_dic_xz['vmin'] = 1e-18
        def_dic_xz['vmax'] = 1e-14
        def_dic_xz['cbar']['label'] = r'$Q_eff_nux$ [geo]'.replace('_', '\_')

        def_dic_xy['v_n'] = 'Q_eff_nux'
        def_dic_xy['vmin'] = 1e-18
        def_dic_xy['vmax'] = 1e-14
    elif v_n == "R_eff_nua":
        def_dic_xz['v_n'] = 'R_eff_nua'
        def_dic_xz['vmin'] = 1e-9
        def_dic_xz['vmax'] = 1e-5
        def_dic_xz['cbar']['label'] = r'$R_eff_nua$ [geo]'.replace('_', '\_')

        def_dic_xy['v_n'] = 'R_eff_nue'
        def_dic_xy['vmin'] = 1e-9
        def_dic_xy['vmax'] = 1e-5
    elif v_n == "R_eff_nue":
        def_dic_xz['v_n'] = 'R_eff_nue'
        def_dic_xz['vmin'] = 1e-9
        def_dic_xz['vmax'] = 1e-5
        def_dic_xz['cbar']['label'] = r'$R_eff_nue$ [geo]'.replace('_', '\_')

        def_dic_xy['v_n'] = 'R_eff_nue'
        def_dic_xy['vmin'] = 1e-9
        def_dic_xy['vmax'] = 1e-5
    elif v_n == "R_eff_nux":
        def_dic_xz['v_n'] = 'R_eff_nux'
        def_dic_xz['vmin'] = 1e-9
        def_dic_xz['vmax'] = 1e-5
        def_dic_xz['cbar']['label'] = r'$R_eff_nux$ [geo]'.replace('_', '\_')

        def_dic_xy['v_n'] = 'R_eff_nux'
        def_dic_xy['vmin'] = 1e-9
        def_dic_xy['vmax'] = 1e-5
    elif v_n == "optd_0_nua":
        def_dic_xz['v_n'] = 'optd_0_nua'
        def_dic_xz['vmin'] = 1e-5
        def_dic_xz['vmax'] = 1e-2
        def_dic_xz['cbar']['label'] = r'$optd_0_nua$ [geo]'.replace('_', '\_')
        # def_dic_xz['norm'] = "linear"
        def_dic_xz['cmap'] = 'inferno'

        def_dic_xy['v_n'] = 'optd_0_nua'
        def_dic_xy['vmin'] = 1e-5
        def_dic_xy['vmax'] = 1e-1
        # def_dic_xy['norm'] = "linear"
        def_dic_xy['cmap'] = 'inferno'
    elif v_n == "optd_0_nue":
        def_dic_xz['v_n'] = 'optd_0_nue'
        def_dic_xz['vmin'] = 1e-5
        def_dic_xz['vmax'] = 1e-2
        def_dic_xz['cbar']['label'] = r'$optd_0_nue$ [geo]'.replace('_', '\_')
        # def_dic_xz['norm'] = "linear"
        def_dic_xz['cmap'] = 'inferno'

        def_dic_xy['v_n'] = 'optd_0_nue'
        def_dic_xy['vmin'] = 1e-5
        def_dic_xy['vmax'] = 1e-1
        # def_dic_xy['norm'] = "linear"
        def_dic_xy['cmap'] = 'inferno'
    else: raise NameError("v_n:{} not recognized".format(v_n))

    #
    contour_dic_xy = {
        'task': 'contour',
        'ptype': 'cartesian', 'aspect': 1.,
        'xarr': x_arr, "yarr": y_arr, "zarr": data_arr, 'levels': [1.e13 / 6.176e+17],
        'position': (2, 1),  # 'title': '[{:.1f} ms]'.format(time_),
        'colors':['black'], 'lss':["-"], 'lws':[1.],
        'v_n_x': 'x', 'v_n_y': 'y', 'v_n': 'rho',
        'xscale': None, 'yscale': None,
        'fancyticks': True,
        'sharex': False,  # removes angular citkscitks
        'fontsize': 14,
        'labelsize': 14}


    # setting boundaries for plots
    xmin, xmax, ymin, ymax, zmin, zmax = REFLEVEL_LIMITS.get(rl)
    def_dic_xy['xmin'], def_dic_xy['xmax'] = xmin, xmax
    def_dic_xy['ymin'], def_dic_xy['ymax'] = ymin, ymax
    def_dic_xz['xmin'], def_dic_xz['xmax'] = xmin, xmax
    def_dic_xz['ymin'], def_dic_xz['ymax'] = zmin, zmax

    if not os.path.isdir(outdir):
        raise IOError("Outdir does not exists".format(outdir))

    # plotting


    o_plot = PLOT_MANY_TASKS()
    o_plot.gen_set["figdir"] = outdir
    o_plot.gen_set["type"] = "cartesian"
    o_plot.gen_set["dpi"] = 128
    o_plot.gen_set["figsize"] = (4.2, 8.0)  # <->, |] # to match hists with (8.5, 2.7)
    o_plot.gen_set["figname"] = "{0:07d}.png".format(int(it))
    o_plot.gen_set["sharex"] = False
    o_plot.gen_set["sharey"] = False
    o_plot.gen_set["subplots_adjust_h"] = -0.35
    o_plot.gen_set["subplots_adjust_w"] = 0.2
    o_plot.gen_set['style'] = 'dark_background'
    o_plot.set_plot_dics = []

    def_dic_xz["it"] = int(it)
    def_dic_xz["title"]["text"] = r'$t:{:.1f}ms$'.format(float(t * 1e3))
    o_plot.set_plot_dics.append(def_dic_xz)

    def_dic_xy["it"] = int(it)
    o_plot.set_plot_dics.append(def_dic_xy)

    if v_n == "rho":
        o_plot.set_plot_dics.append(contour_dic_xy)

    # plot reflevel boundaries
    for rl in range(o_slice.nlevels):
        try:
            x_arr = o_slice.get_grid_v_n_rl(it, "xy", rl, "x")
            y_arr = o_slice.get_grid_v_n_rl(it, "xy", rl, "y")
            x_b = [x_arr.min(), x_arr.max()]
            y_b = [y_arr.min(), y_arr.max()]
            #
            for x_b_line, y_b_line in zip([[x_b[0], x_b[-1]], [x_b[0], x_b[0]], [x_b[0], x_b[-1]], [x_b[-1], x_b[-1]]],
                                          [[y_b[0], y_b[0]], [y_b[0], y_b[-1]], [y_b[-1], y_b[-1]], [y_b[-1], y_b[0]]]):
                #
                contour_dic_xy = {
                    'task': 'line',
                    'ptype': 'cartesian', 'aspect': 1.,
                    'xarr': x_b_line, "yarr": y_b_line,
                    'position': (2, 1),  # 'title': '[{:.1f} ms]'.format(time_),
                    'color': 'cyan', 'ls': "-", 'lw': 1., 'alpha': 1., 'ds': 'default',
                    'v_n_x': 'x', 'v_n_y': 'y', 'v_n': 'rho',
                    'xscale': None, 'yscale': None,
                    'fancyticks': True,
                    'sharex': False,  # removes angular citkscitks
                    'fontsize': 14,
                    'labelsize': 14}
                o_plot.set_plot_dics.append(contour_dic_xy)
            #
            x_arr = o_slice.get_grid_v_n_rl(it, "xz", rl, "x")
            z_arr = o_slice.get_grid_v_n_rl(it, "xz", rl, "z")
            x_b = [x_arr.min(), x_arr.max()]
            z_b = [z_arr.min(), z_arr.max()]
            #
            for x_b_line, z_b_line in zip([[x_b[0], x_b[-1]], [x_b[0], x_b[0]], [x_b[0], x_b[-1]], [x_b[-1], x_b[-1]]],
                                          [[z_b[0], z_b[0]], [z_b[0], z_b[-1]], [z_b[-1], z_b[-1]], [z_b[-1], z_b[0]]]):
                #
                contour_dic_xz = {
                    'task': 'line',
                    'ptype': 'cartesian', 'aspect': 1.,
                    'xarr': x_b_line, "yarr": z_b_line,
                    'position': (1, 1),  # 'title': '[{:.1f} ms]'.format(time_),
                    'color': 'cyan', 'ls': "-", 'lw': 1., 'alpha': 1., 'ds': 'default',
                    'v_n_x': 'x', 'v_n_y': 'y', 'v_n': 'rho',
                    'xscale': None, 'yscale': None,
                    'fancyticks': True,
                    'sharex': False,  # removes angular citkscitks
                    'fontsize': 14,
                    'labelsize': 14}
                o_plot.set_plot_dics.append(contour_dic_xz)
        except IndexError:
            Printcolor.print_colored_string(["it:", str(it), "rl:", str(rl), "IndexError"],
                                            ["blue", "green", "blue", "green", "red"])

    o_plot.main()
    o_plot.set_plot_dics = []

    # plotfpath = outdir + "{0:07d}.png".format(int(it))
    # if True:
    #     if (os.path.isfile(plotfpath) and rewrite) or not os.path.isfile(plotfpath):
    #         if os.path.isfile(plotfpath): os.remove(plotfpath)
    #         Printcolor.print_colored_string(
    #         ["task:", "plot slice", "t:", "{:.1f} [ms] ({:d}/{:d})".format(t*1e3, i, len(list_times)),
    #          "rl:", "{}".format(rl), "v_n:", v_n, ':', "plotting"],
    #         ["blue",  "green",     "blue", "green",   "blue", "green",      "blue", "green", "", "green"]
    #         )
    #         # --- --- --- --- --- --- --- --- --- --- --- --- --- --- --- ---
    #
    #         def_dic_xz["it"] = int(it)
    #         def_dic_xz["title"]["text"] = r'$t:{:.1f}ms$'.format(float(t*1e3))
    #         o_plot.set_plot_dics.append(def_dic_xz)
    #
    #         def_dic_xy["it"] = int(it)
    #         o_plot.set_plot_dics.append(def_dic_xy)
    #
    #         o_plot.main()
    #         o_plot.set_plot_dics = []
    #
    #         # --- --- --- --- --- --- --- --- --- --- --- --- --- --- --- ---
    #     else:
    #         Printcolor.print_colored_string(
    #             ["task:", "plot slice", "t:", "{:.1f} [ms] ({:d}/{:d})".format(t * 1e3, i, len(list_times)), "rl:",
    #              "{}".format(rl), "v_n:", v_n, ':', "skipping"],
    #             ["blue", "green", "blue", "green", "blue", "green", "blue", "green", "", "blue"]
    #         )
    #
    # # except KeyboardInterrupt:
    # #     exit(1)
    # else:
    #     Printcolor.print_colored_string(
    #         ["task:", "plot slice", "t:", "{:.1f} [ms] ({:d}/{:d})".format(t * 1e3, i, len(list_times)), "rl:",
    #          "{}".format(rl), "v_n:", v_n, ':', "failed"],
    #         ["blue", "green", "blue", "green", "blue", "green", "blue", "green", "", "red"]
    #     )

def plot_selected_data(o_slice, v_ns, times, rls, rootdir, rewrite=False):

    _, d2it, d2t = o_slice.get_ittime("overall", d1d2d3prof="d2")
    if len(d2it) == 0:
        raise ValueError("No d2 data found in ittime.h5")

    for t in times:
        if t > d2t.max():
            raise ValueError("given t:{} is above max time available:{}"
                             .format(t, d2t.max()))
        if t < d2t.min():
            raise ValueError("given t:{} is below min time available:{}"
                             .format(t, d2t.min()))

    i = 1
    for t in times:
        nearest_time = o_slice.get_nearest_time(t, d1d2d3="d2")
        it = o_slice.get_it_for_time(nearest_time, d1d2d3="d2")
        for v_n in v_ns:
            outdir_ = rootdir + v_n + '/'
            if not os.path.isdir(outdir_):
                os.mkdir(outdir_)
            for rl in rls:
                outdir__ = outdir_ + str("rl_{:d}".format(rl)) + '/'
                if not os.path.isdir(outdir__):
                    os.mkdir(outdir__)
                plotfpath = outdir__ + "{0:07d}.png".format(int(it))
                if True:
                    if (os.path.isfile(plotfpath) and rewrite) or not os.path.isfile(plotfpath):
                        if os.path.isfile(plotfpath): os.remove(plotfpath)
                        Printcolor.print_colored_string(
                            ["task:", "plot slice", "t:", "{:.1f} [ms] ({:d}/{:d})".format(t * 1e3, i, len(times)),
                             "rl:", "{}".format(rl), "v_n:", v_n, ':', "plotting"],
                            ["blue", "green", "blue", "green", "blue", "green", "blue", "green", "", "green"]
                        )
                        # --- --- --- --- --- --- --- --- --- --- --- --- --- --- --- ---
                        __plot_data_for_a_slice(o_slice, v_n, it, t, rl, outdir__)
                        # --- --- --- --- --- --- --- --- --- --- --- --- --- --- --- ---
                    else:
                        Printcolor.print_colored_string(
                            ["task:", "plot slice", "t:", "{:.1f} [ms] ({:d}/{:d})".format(t * 1e3, i, len(times)),
                             "rl:",
                             "{}".format(rl), "v_n:", v_n, ':', "skipping"],
                            ["blue", "green", "blue", "green", "blue", "green", "blue", "green", "", "blue"]
                        )
                # except KeyboardInterrupt:
                #     exit(1)
                # except:
                #     Printcolor.print_colored_string(
                #         ["task:", "plot slice", "t:", "{:.1f} [ms] ({:d}/{:d})".format(t * 1e3, i, len(times)),
                #          "rl:",
                #          "{}".format(rl), "v_n:", v_n, ':', "failed"],
                #         ["blue", "green", "blue", "green", "blue", "green", "blue", "green", "", "red"]
                #     )
        sys.stdout.flush()
        i += 1

def make_movie(v_ns, rls, rootdir, rewrite=False):

    rewrite = True

    for v_n in v_ns:
        outdir_ = rootdir + v_n + '/'
        if not os.path.isdir(outdir_):
            os.mkdir(outdir_)
        for rl in rls:
            outdir__ = outdir_ + str("rl_{:d}".format(rl)) + '/'
            if not os.path.isdir(outdir__):
                os.mkdir(outdir__)
            fname = "{}_rl{}.mp4".format(v_n, rl)
            moviefath = outdir__ + fname
            nfiles = len(glob(outdir__))
            if nfiles < 1:
                Printcolor.red("No plots found to make a movie in: {}".format(outdir__))
                break
            try:
                if (os.path.isfile(moviefath) and rewrite) or not os.path.isfile(moviefath):
                    if os.path.isfile(moviefath): os.remove(moviefath)
                    Printcolor.print_colored_string(
                        ["task:", "movie slice", "N files", "{:d}".format(nfiles),
                         "rl:", "{}".format(rl), "v_n:", v_n, ':', "plotting"],
                        ["blue", "green", "blue", "green", "blue", "green", "blue", "green", "", "green"]
                    )
                    # --- --- --- --- --- --- --- --- --- --- --- --- --- --- --- ---
                    # ffmpeg -framerate 10 -pattern_type glob -i "*.png" -s:v 1280x720 -c:v libx264 -profile:v high -crf 20 -pix_fmt yuv420p dt.mp4

                    os.system("ffmpeg -framerate 10 -pattern_type glob -i '{}*.png' -s:v 1280x720 "
                              "-c:v libx264 -profile:v high -crf 20 -pix_fmt yuv420p {}"
                              .format(outdir__, outdir__ + fname))
                    # --- --- --- --- --- --- --- --- --- --- --- --- --- --- --- ---
                else:
                    Printcolor.print_colored_string(
                        ["task:", "movie slice", "N files", "{:d}".format(nfiles),
                         "rl:",
                         "{}".format(rl), "v_n:", v_n, ':', "skipping"],
                        ["blue", "green", "blue", "green", "blue", "green", "blue", "green", "", "blue"]
                    )
            except KeyboardInterrupt:
                exit(1)
            except:
                Printcolor.print_colored_string(
                    ["task:", "plot slice", "N files", "{:d}".format(nfiles),
                     "rl:",
                     "{}".format(rl), "v_n:", v_n, ':', "failed"],
                    ["blue", "green", "blue", "green", "blue", "green", "blue", "green", "", "red"]
                )

def add_q_r_t_to_prof_xyxz(v_ns, rls):
    # glob_sim = "LS220_M14691268_M0_LK_SR"
    glob_profxyxz_path = Paths.ppr_sims+glob_sim+'/profiles/'
    glob_nlevels = 7
    # glob_overwrite = False

    from preanalysis import LOAD_ITTIME
    ititme = LOAD_ITTIME(glob_sim)
    _, profit, proft = ititme.get_ittime("profiles", d1d2d3prof="prof")
    #
    if len(profit) == 0:
        Printcolor.yellow("No profiles found. Q R T values are not added to prof.xy.h5")
        return 0
    #
    d2data = COMPUTE_STORE(glob_sim)
    #
    assert len(glob_reflevels) > 0
    assert len(v_ns) > 0
    #
    for it in glob_it:
        for plane in glob_planes:
            fpath = glob_profxyxz_path + str(int(it)) + '/' + "profile.{}.h5".format(plane)
            if os.path.isfile(fpath):
                try:
                    dfile = h5py.File(glob_profxyxz_path + str(int(it)) + '/' + "profile.{}.h5".format(plane), "a")

                    Printcolor.print_colored_string(
                        ["task:", "addm0", "it:", "{}".format(it), "plane", plane, ':', "Adding"], ["blue", "green", "blue", "green","blue", "green",  "", "green"]
                    )
                    for rl in rls:
                        gname = "reflevel=%d" % rl
                        for v_n in v_ns:
                            if (v_n in dfile[gname] and glob_overwrite) or not v_n in dfile[gname]:
                                if v_n in dfile[gname]:
                                        del dfile[gname][v_n]
                                #
                                prof_rho = dfile[gname]["rho"]
                                rho_arr = d2data.get_data(it, plane, "rho")[rl][3:-3, 3:-3]
                                nu_arr = d2data.get_data(it, plane, v_n)[rl][3:-3, 3:-3]
                                assert rho_arr.shape == nu_arr.shape

                                if prof_rho.shape != nu_arr.shape:
                                    Printcolor.yellow("Size Mismatch. Profile:{} 2D data:{} Filling with nans..."
                                                      .format(prof_rho.shape, nu_arr.shape))
                                    px, py, pz = dfile[gname]["x"], dfile[gname]["y"], dfile[gname]["z"]
                                    nx, nz = d2data.get_grid_v_n_rl(it, plane, rl, "x")[3:-3, 3:-3], \
                                           d2data.get_grid_v_n_rl(it, plane, rl, "z")[3:-3, 3:-3]
                                    # print("mismatch prof_rho:{} nu:{}".format(prof_rho.shape, nu_arr.shape))
                                    # print("mismatch prof x:{} prof z:{}".format(px.shape, pz.shape))
                                    # print("mismatch x:{} z:{}".format(nx.shape, nz.shape))
                                    # arr = np.full(prof_rho[:,0,:].shape, 1)

                                    # tst = np.where((px>=nx.min()) | (px<=nx.max()), arr, nu_arr)
                                    # print(tst)

                                    tmp = np.full(prof_rho.shape, np.nan)
                                    # for ipx in range(len(px)):

                                    for ipx in range(len(px[:, 0])):
                                        for ipz in range(len(pz[0, :])):
                                            if px[ipx] in nx and pz[ipz] in nz:
                                                # print("found: {} {}".format(px[ipx], py[ipz]))
                                                # print(px[(px[ipx] == nx)&(pz[ipz] == nz)])
                                                # print(pz[(px[ipx] == nx) & (pz[ipz] == nz)])
                                                # print(nu_arr[(px[ipx] == nx)&(pz[ipz] == nz)])
                                                # print("x:{} z:{}".format(px[ipx, 0], pz[0,  ipz]))
                                                # print(nu_arr[(px[ipx, 0] == nx)&(pz[0, ipz] == nz)])
                                                # print(float(nu_arr[(px[ipx, 0] == nx) & (pz[0, ipz] == nz)]))
                                                tmp[ipx, ipz] = float(nu_arr[(px[ipx, 0] == nx) & (pz[0, ipz] == nz)])
                                                # print("x:{} z:{} filling with:{}".format(px[ipx, 0], pz[0, ipz], tmp[ipx, ipz]))
                                    #
                                    nu_arr = tmp
                                            # else:
                                                # print("wrong: {}".format(px[ipx], py[ipz]))
                                    # print(tmp)
                                    # print(tmp.shape)
                                    # exit(1)

                                    # UTILS.find_nearest_index()
                                    #
                                    #
                                    #
                                    # for ix in range(len(arr[:, 0])):
                                    #     for iz in range(len(arr[0, :])):
                                    #         x = np.round(px[ix, iz], decimals=1)
                                    #         z = np.round(py[ix, iz], decimals=1)
                                    #
                                    #
                                    #
                                    #         if x in np.round(nx, decimals=1) and z in np.round(nz, decimals=1):
                                    #             arr[ix, iz] = nu_arr[np.where((np.round(nx, decimals=1) == x) & (np.round(nz, decimals=1) == z))]
                                    #             print('\t\treplacing {} {}'.format(ix, iz))
                                    # print(arr)
                                    #
                                    # exit(1)
                                    #
                                    #
                                    # ileft, iright = np.where(px<nx.min()), np.where(px>nx.max())
                                    # print(ileft)  # (axis=0 -- array, axis=1 -- array)
                                    # print(iright)
                                    # ilower, iupper = np.where(pz<nz.min()), np.where(pz>nz.max())
                                    # print(ilower)
                                    # print(iupper)
                                    #
                                    # #
                                    # import copy
                                    # tmp = copy.deepcopy(nu_arr)
                                    # for axis in range(len(ileft)):
                                    #     for element in ileft[axis]:
                                    #         tmp = np.insert(tmp, 0, np.full(len(tmp[0,:]), np.nan), axis=0)
                                    #
                                    # # tmp = copy.deepcopy(nu_arr)
                                    # for axis in range(len(iright)):
                                    #     print("\taxis:{} indexes:{}".format(axis, iright[axis]))
                                    #     for element in iright[axis]:
                                    #         tmp = np.insert(tmp, -1, np.full(len(tmp[0,:]), np.nan), axis=0)
                                    #     print(tmp.shape)
                                    #
                                    # print(prof_rho.shape)
                                    # print(tmp.shape)

                                    # indexmap = np.where((px<nx.min()) | (px>nx.max()), arr, 0)
                                    # arr[indexmap] = nu_arr
                                    # print(indexmap)
                                    # print(arr)
                                    # print(indexmap.shape)

                                    # insert coordinates
                                    # exit(1)


                                    # arr = np.full(prof_rho.shape, np.nan)



                                    # exit(1)
                                    #
                                    #
                                    #
                                    #
                                    # arr = np.full(prof_rho.shape,np.nan)
                                    # for ix in range(len(arr[:, 0])):
                                    #     for iz in range(len(arr[0,:])):
                                    #         x = px[ix, iz]
                                    #         z = py[ix, iz]
                                    #         if x in nx and z in nz:
                                    #             arr[ix, iz] = nu_arr[np.where((nx == x)&(nz == z))]
                                    #             print('\t\treplacing {} {}'.format(ix, iz))
                                    # print(arr);
                                    #
                                    # exit(1)

                                print("\t{} nu:{} prof_rho:{}".format(rl, nu_arr.shape, prof_rho.shape))
                                # nu_arr = nu_arr[3:-3, 3:-3]
                                # hydro_arr = d3data.get_data(it, rl, plane, "rho")
                                # assert nu_arr.shape == hydro_arr.shape
                                gname = "reflevel=%d" % rl
                                dfile[gname].create_dataset(v_n, data=np.array(nu_arr, dtype=np.float32))
                            else:
                                Printcolor.print_colored_string(["\trl:", str(rl), "v_n:", v_n, ':',
                                     "skipping"],
                                    ["blue", "green","blue", "green", "", "blue"]
                                )
                    dfile.close()
                except KeyboardInterrupt:
                    exit(1)
                except ValueError:
                    Printcolor.print_colored_string(
                        ["task:", "addm0", "it:", "{}".format(it), "plane", plane, ':', "ValueError"],
                        ["blue", "green", "blue", "green","blue", "green", "", "red"]
                    )
                except IOError:
                    Printcolor.print_colored_string(
                        ["task:", "addm0", "it:", "{}".format(it), "plane", plane, ':', "IOError"],
                        ["blue", "green", "blue", "green","blue", "green", "", "red"]
                    )
                except:
                    Printcolor.print_colored_string(
                        ["task:", "addm0", "it:", "{}".format(it), "plane", plane, ':', "FAILED"],
                        ["blue", "green", "blue", "green", "blue", "green", "", "red"]
                    )
            else:
                Printcolor.print_colored_string(
                    ["task:", "adding neutrino data to prof. slice", "it:", "{}".format(it), ':', "IOError: profile.{}.h5 does not exist".format(plane)],
                    ["blue", "green", "blue", "green", "", "red"]
                )
    # for it in profit:
    #     #
    #     fpathxy = glob_profxyxz_path + str(int(it)) + '/' + "profile.xy.h5"
    #     fpathxz = glob_profxyxz_path + str(int(it)) + '/' + "profile.xz.h5"

def compute_density_modes(o_slice, rls, outdir, rewrite=True):


    if not len(rls) == 1:
        raise NameError("for task 'dm' please set one reflevel: --rl ")
    #
    if not os.path.isdir(outdir):
        os.mkdir(outdir)
    #
    rl = rls[0]
    #
    mmax = 8
    #
    fname = "rho_modes.h5"
    fpath = outdir + fname
    #
    if True:#try:
        if (os.path.isfile(fpath) and rewrite) or not os.path.isfile(fpath):
            if os.path.isfile(fpath): os.remove(fpath)
            Printcolor.print_colored_string(["task:", "rho modes", "rl:", str(rl), "mmax:", str(mmax), ":", "computing"],
                                 ["blue", "green", "blue", "green", "blue", "green", "", "green"])
            times, iterations, xcs, ycs, modes = o_slice.get_rho_modes_for_rl(rl=rl, mmax=mmax)
            dfile = h5py.File(fpath, "w")
            dfile.create_dataset("times", data=times)  # times that actually used
            dfile.create_dataset("iterations", data=iterations)  # iterations for these times
            dfile.create_dataset("xc", data=xcs)  # x coordinate of the center of mass
            dfile.create_dataset("yc", data=ycs)  # y coordinate of the center of mass
            for m in range(mmax + 1):
                group = dfile.create_group("m=%d" % m)
                group["int_phi"] = np.zeros(0, )  # NOT USED (suppose to be data for every 'R' in disk and NS)
                group["int_phi_r"] = np.array(modes[m]).flatten()  # integrated over 'R' data
            dfile.close()
        else:
            Printcolor.print_colored_string(["task:", "rho modes", "rl:", str(rl), "mmax:", str(mmax), ":", "skipping"],
                                 ["blue", "green", "blue", "green", "blue", "green", "", "blue"])
    # except:
    #     Printcolor.print_colored_string(["task:", "rho modes", "rl:", str(rl), "mmax:", str(mmax), ":", "failed"],
    #                          ["blue", "green", "blue", "green", "blue", "green", "", "red"])

""" ================================================================================================================ """

if __name__ == '__main__':

    parser = ArgumentParser(description="postprocessing pipeline")
    parser.add_argument("-s", dest="sim", required=True, help="name of the simulation dir")
    parser.add_argument("-t", dest="tasklist", nargs='+', required=False, default=[], help="tasks to perform")
    #
    parser.add_argument("--v_n", dest="v_ns", nargs='+', required=False, default=[], help="variable names to compute")
    parser.add_argument("--time", dest="times", nargs='+', required=False, default=[], help="times to iterate over [ms]")
    parser.add_argument("--it", dest="it", nargs='+', required=False, default=[],
                        help="iterations to use ")
    parser.add_argument("--rl", dest="reflevels", nargs='+', required=False, default=[], help="reflevels to use")
    parser.add_argument('--plane', dest="plane", required=False, nargs='+', default=[], help='Plane: xy,xz,yz for slice analysis')
    #
    parser.add_argument("-o", dest="outdir", required=False, default=Paths.ppr_sims, help="path for output dir")
    parser.add_argument("-i", dest="simdir", required=False, default=Paths.gw170817, help="path to simulation dir")
    parser.add_argument("--overwrite", dest="overwrite", required=False, default="no", help="overwrite if exists")
    #
    args = parser.parse_args()
    glob_sim = args.sim
    glob_simdir = args.simdir
    glob_outdir = args.outdir
    glob_tasklist = args.tasklist
    glob_overwrite = args.overwrite
    glob_v_ns = args.v_ns
    glob_times =args.times
    glob_it = args.it
    glob_reflevels = args.reflevels
    glob_planes = args.plane
    #
    glob_profxyxz_path = Paths.ppr_sims+glob_sim+'/profiles/'
    #
    if not os.path.isdir(glob_simdir + glob_sim):
        raise NameError("simulation dir: {} does not exist in rootpath: {} "
                        .format(glob_sim, glob_simdir))
    if len(glob_tasklist) == 0:
        raise NameError("tasklist is empty. Set what tasks to perform with '-t' option")
    else:
        for task in glob_tasklist:
            if task not in __slices__["tasklist"]:
                raise NameError("task: {} is not among available ones: {}"
                                .format(task, __slices__["tasklist"]))
    if glob_overwrite == "no":
        glob_overwrite = False
    elif glob_overwrite == "yes":
        glob_overwrite = True
    else:
        raise NameError("for '--overwrite' option use 'yes' or 'no'. Given: {}"
                        .format(glob_overwrite))
    glob_outdir_sim = Paths.ppr_sims + glob_sim
    if not os.path.isdir(glob_outdir_sim):
        os.mkdir(glob_outdir_sim)

    # check plane
    if len(glob_planes) == 0:
        raise IOError("Option --plane unfilled")
    elif len(glob_planes) == 1 and "all" in glob_planes:
        glob_planes = __d3slicesplanes__
    elif len(glob_planes) > 1:
        for plane in glob_planes:
            if not plane in __d3slicesplanes__:
                raise NameError("plane:{} is not in the list of the __d3slicesplanes__:{}"
                                .format(plane, __d3slicesplanes__))

    # set globals
    Paths.gw170817 = glob_simdir
    Paths.ppr_sims = glob_outdir

    #
    if len(glob_tasklist) == 1 and "all" in glob_tasklist:
        # do all tasksk
        pass
    #
    o_slice = COMPUTE_STORE(glob_sim)
    #
    do_all_iterations = False
    if len(glob_it) == 0 and len(glob_times) == 0:
        raise IOError("please specify timesteps to use '--time' or iterations '--it' ")
    elif len(glob_it) != 0 and len(glob_times) != 0:
        raise IOError("please specify Either timesteps to use '--time' or iterations '--it' (not both)")
    elif len(glob_times) == 0 and len(glob_it) == 1 and "all" in glob_it:
        do_all_iterations = True
        glob_times = o_slice.times
        glob_it = o_slice.iterations
    elif len(glob_it) == 0 and len(glob_times) == 1 and "all" in glob_times:
        do_all_iterations = True
        glob_times = o_slice.times
        glob_it = o_slice.iterations
    elif len(glob_it) > 0 and not "all" in glob_it and len(glob_times) == 0:
        glob_it = np.array(glob_it, dtype=int) # array of iterations
        glob_times = []
        for it in glob_it:
            glob_times.append(o_slice.get_time_for_it(it, "overall", "d2"))
        glob_times = np.array(glob_times, dtype=float)
    elif len(glob_times) > 0 and not "all" in glob_times and len(glob_it) == 0:
        glob_times = np.array(glob_times, dtype=float) / 1e3  # back to seconds
    else:
        raise IOError("input times and iterations are not recognized: --time {} --it {}"
                      .format(glob_times, glob_it))
    #
    do_all_reflevels = False
    if len(glob_reflevels) == 1 and "all" in glob_reflevels:
        glob_reflevels = __slices__["reflevels"]
        do_all_reflevels = True
    else:
        glob_reflevels = np.array(glob_reflevels, dtype=int)
    #
    do_all_v_ns = False
    if len(glob_v_ns) == 1 and "all" in glob_v_ns:
        glob_v_ns=o_slice.list_v_ns
        do_all_v_ns = True
    else:
        pass
    #
    if do_all_v_ns or do_all_iterations or do_all_reflevels:
        Printcolor.yellow("Selected all", comma=True)
        if do_all_iterations:
            Printcolor.print_colored_string(["timesteps", "({})".format(len(glob_times))],
                                            ["blue", "green"], comma=True)
        if do_all_v_ns: Printcolor.print_colored_string(["v_ns", "({})".format(len(glob_v_ns))],
                                                        ["blue", "green"], comma=True)
        if do_all_reflevels: Printcolor.print_colored_string(["reflevels", "({})".format(len(glob_reflevels))],
                                                             ["blue", "green"], comma=True)
        Printcolor.yellow("this might take time.")
        # if not click.confirm(text="Confirm?",default=True,show_default=True):
        #     exit(0)

    # print(glob_it, glob_times); exit(1)

    for task in glob_tasklist:
        # do tasks one by one
        if task == "plot":
            assert len(glob_v_ns) > 0
            assert len(glob_times) > 0
            assert len(glob_reflevels) > 0
            outdir = Paths.ppr_sims + glob_sim + '/' + __slices__["outdir"] + '/'
            if not os.path.isdir(outdir):
                os.mkdir(outdir)
            outdir += 'plots/'
            if not os.path.isdir(outdir):
                os.mkdir(outdir)
            plot_selected_data(o_slice, glob_v_ns, glob_times, glob_reflevels, outdir, rewrite=glob_overwrite)

        if task == "movie":

            assert len(glob_v_ns) > 0
            assert len(glob_times) > 0
            assert len(glob_reflevels) > 0
            outdir = Paths.ppr_sims + glob_sim + '/' + __slices__["outdir"] + '/'
            if not os.path.isdir(outdir):
                os.mkdir(outdir)
            outdir += 'movie/'
            if not os.path.isdir(outdir):
                os.mkdir(outdir)

            plot_selected_data(o_slice, glob_v_ns, glob_times, glob_reflevels, outdir, rewrite=glob_overwrite)

            assert len(glob_v_ns) > 0
            assert len(glob_reflevels) > 0
            outdir = Paths.ppr_sims + glob_sim + '/' + __slices__["outdir"] + '/'
            if not os.path.isdir(outdir):
                os.mkdir(outdir)
            outdir += 'movie/'

            make_movie(glob_v_ns, glob_reflevels, outdir, rewrite=glob_overwrite)

        if task == "addm0":
            if len(glob_v_ns) == len(o_slice.list_v_ns):
                glob_v_ns = o_slice.list_neut_v_ns
            print glob_it
            add_q_r_t_to_prof_xyxz(glob_v_ns, glob_reflevels)

        if task == "dm":
            outdir = Paths.ppr_sims + glob_sim + '/' + __slices__["outdir"] + '/'
            compute_density_modes(o_slice, glob_reflevels, outdir, rewrite=glob_overwrite)