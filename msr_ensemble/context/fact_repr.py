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

from msr_ensemble.facts.location import loc_rank, loc_proc_id

def make_fact_repr(fact):
	return { 'prior':fact.priority, 'sym_id':fact.sym_id, 'values':[ term.value for term in fact.terms ] }

def make_fact_repr_loc(fact):
	location = fact.location.value
	return { 'prior':fact.priority, 'sym_id':fact.sym_id, 'values':[ term.value for term in fact.terms ]
               , 'rank':loc_rank(location), 'proc_id':loc_proc_id(location) }

def make_fact_pat(fact):
	return { 'sym_id':fact.sym_id, 'terms':fact.terms, 'location':fact.location }

def pretty_fact_repr(fact_repr):
	return "%s%s" % (tuple(fact_repr['values']), ("#%s" % fact_repr['fact_id']['id']) if 'fact_id' in fact_repr else "")
