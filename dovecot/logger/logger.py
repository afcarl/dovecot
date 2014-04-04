#!/usr/bin/env python
# encoding: utf-8
"""
logger.py

Created by Paul Fudal on 2014-04-2.
Copyright (c) 2014 INRIA. All rights reserved.
"""

import time
import cPickle
import os
import atexit
import threading
import bz2
from threading import Thread
from shutil import copyfileobj

DF_FOLDER = "~/.dovecot/logger/"
DF_DELAY = 60

def writter_function(logger):
    """Function call by the deamon thread"""
    while logger.run_writter == True:
        time.sleep(logger.write_delay)
        logger.save()

def exit_function(logger):
    """Called when exiting"""
    logger.save()

class Logger(object):
    """This describe a logger system able to write data in a file"""
    def __init__(self, file_name, folder=DF_FOLDER, write_delay=DF_DELAY, verbose=False):
        self.file_name = file_name
        self.folder = os.path.expanduser(folder)
        self.write_delay = write_delay
        self.verbose = verbose
        if not os.path.exists(self.folder):
            os.makedirs(self.folder)
        self.datas = []
        self.lock = threading.Lock()
        self.run_writter = False
        self.writter = None
        atexit.register(exit_function, self)

    def start(self):
        """Starts the writing thread"""
        self.writter = Thread(target=writter_function, args={self,})
        self.run_writter = True
        self.writter.daemon = True
        self.writter.start()

    def log(self, data, timestamp=True):
        """Adds data to log"""
        self.lock.acquire()
        if timestamp:
            self.datas.append({'timestamp' : time.time(), 'datas' : data})
        else:
            self.datas.append({'datas' : data})
        self.lock.release()

    def save(self):
        """Write each datas in the log file"""
        self.lock.acquire()
        if self.datas:
            start = time.time()
            file_path = self.folder + '/' + self.file_name + '.bz2'
            if not os.path.isfile(file_path):
                with open(file_path, 'wb') as f_path:
                    f_path.write(bz2.compress('',9))
            data_bz2 = None
            loaded_datas = self._load()
            for data in self.datas:
                loaded_datas.append(data)
            self.datas[:] = []
            data_bz2 = cPickle.dumps(loaded_datas, cPickle.HIGHEST_PROTOCOL)
            with open(file_path, 'wb') as f_path:
                f_path.write(bz2.compress(data_bz2, 9))
            comp_time = time.time() - start
            if self.verbose:
                print "Saving time took : {}".format(comp_time)
        self.lock.release()

    def _load(self):
        """Allows to reload datas written in the log file"""
        loaded_datas = []
        file_path = self.folder + '/' + self.file_name + '.bz2'
        if os.path.exists(file_path):
            with open(file_path, 'rb') as f_path:
                try:
                    data_bz2 = bz2.decompress(f_path.read())
                    loaded_datas = cPickle.loads(data_bz2)
                except EOFError:
                    pass
                except cPickle.PickleError:
                    if self.verbose:
                        print "Error while unpickling..."
        return loaded_datas

    def load(self):
        self.lock.acquire()
        loaded_datas = self._load()
        self.lock.release()
        return loaded_datas


    def print_datas(self):
        """Prints current datas"""
        self.lock.acquire()
        print self.datas
        self.lock.release()
