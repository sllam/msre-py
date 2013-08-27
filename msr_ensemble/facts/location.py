
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

from msr_ensemble.misc.mpi_process import gen_proc_id

def new_loc(rank):
	return loc(rank, proc_id=gen_proc_id())

def loc(rank, proc_id=None):
	if proc_id == None:
		proc_id = str(rank)
	return u'%s::%s' % (str(rank),proc_id)

def loc_rank(loc):
	(rank,_,proc_id) = loc.partition('::')
	return int(rank)

def loc_proc_id(loc):
	(rank,_,proc_id) = loc.partition('::')
	return str(proc_id)
