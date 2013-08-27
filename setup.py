#!/usr/bin/env python

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

from distutils.core import setup

setup(name='msr_ensemble',
      version='0.9',
      description='MSR Ensemble for Python',
      author='Edmund S. L. Lam',
      author_email='sllam@qatar.cmu.edu',
      url='http://www.qatar.cmu.edu/~sllam/msr3e',
      packages=[
		'msr_ensemble', 
		'msr_ensemble.context', 
		'msr_ensemble.facts', 
		'msr_ensemble.front_end', 
		'msr_ensemble.front_end.compile',
		'msr_ensemble.front_end.compile.checkers',
		'msr_ensemble.front_end.compile.transformers',
		'msr_ensemble.front_end.parser',
		'msr_ensemble.interpret', 
		'msr_ensemble.misc', 
		'msr_ensemble.python', 
		'msr_ensemble.rules',
      ],
      install_requires=[
		'mpi4py', 'ply',
      ],
     )
