
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

from msr_ensemble.facts.term import Term
from msr_ensemble.facts.fact import Fact, Id, new_id, pretty_id, get_all_fact_classes, get_fact_name
from msr_ensemble.rules.rule import get_all_rule_classes
from msr_ensemble.context.fact_repr import pretty_fact_repr

class PropHistory:

	def __init__(self, rule_id):
		self.rule_id = rule_id
		self.history = {}

	def check_history(self, ids):
		history = self.history
		rule_id = self.rule_id
		id_sig = ','.join(map(lambda id: str(id['id']) ,ids))
		if id_sig not in history:
			# print id_sig
			history[id_sig] = ()
			for id in ids:
				id['history_entries'][rule_id].append(id_sig)
			return True
		else:
			return False

	def remove_history_entries(self, id_sigs):
		history = self.history
		for id_sig in id_sigs:
			if id_sig in history:
				del history[id_sig]
		
	def __str__(self):
		hist_str = "%s Rule Propagate History:\n" % str(self.rule_id)
		return hist_str + "\n".join(self.history)

def new_histories():
	histories = {}
	for rule_id in get_all_rule_classes():
		histories[rule_id] = PropHistory(rule_id)
	return histories

def check_history(histories, rule_id, ids):
	return histories[rule_id].check_history(ids)

def remove_history_entry(histories, rule_id, id):
	history = histories[rule_id]
	history.remove_history_entries(id['history_entries'][rule_id])

