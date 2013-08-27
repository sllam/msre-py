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

from msr_ensemble.front_end.compile.code_gen import MSRCodeGen
from msr_ensemble.front_end.compile.transformers.neighbor_restrict_trans import NeighborRestrictTrans

import sys

args = sys.argv

if len(args) < 2:
	print "Usage: python %s <MSR File Name>" % args[0]
else:
	msr_code_gen = MSRCodeGen(args[1])
	if msr_code_gen.has_errors():
		err_reports = msr_code_gen.error_reports
		for err_report in err_reports:
			print err_report + "\n"
		print "There are %s error(s) in total." % len(err_reports)
	else:
		msr_code_gen.decs = NeighborRestrictTrans(msr_code_gen.decs, msr_code_gen.source_text).trans()
		msr_code_gen.gen_code()
	print "Done!"
