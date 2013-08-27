
'''
This file is part of MSR Ensemble for Python (MSRE-Py).

MSRE-Py is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

MSRE-Py is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with MSRE-Py. If not, see <http://www.gnu.org/licenses/>.

MSR Ensemble for Python (MSRE-Py) Version 0.9, Prototype Alpha

Authors:
Edmund S. L. Lam      sllam@qatar.cmu.edu
Iliano Cervesato      iliano@cmu.edu

* Development of MSRE-Py is funded by the Qatar National Research Fund as project NPRP 09-667-1-100 (Effective Programming for Large Distributed Ensembles)
'''


import logging
import sys

# Specialization of Python logging facilities for MSR

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')

def init_logger(logger_name, default_log_level=logging.DEBUG, log_file=None, log_file_level=logging.DEBUG
               ,log_format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'):

	logger = logging.getLogger(logger_name)
	logger.setLevel(default_log_level)

	if not (log_file == None):
		ch = logging.FileHandler(log_file)
		ch.setLevel(log_file_level)
		fm = logging.Formatter(log_format)
		ch.setFormatter(fm)
		logger.addHandler(ch)

	return logger

def get_logger(logger_name):
	return logging.getLogger(logger_name)

def log_debug(logger, msg):
	if __debug__:
		logger.debug(msg) 

def log_info(logger, msg):
	if __debug__:
		logger.info(msg)

def log_warn(logger, msg):
	if __debug__:
		logger.warn(msg)

def log_error(logger, msg):
	if __debug__:
		logger.error(msg)

def log_critical(logger, msg):
	if __debug__:
		logger.critical(msg)

