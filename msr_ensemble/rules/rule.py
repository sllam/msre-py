
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


from msr_ensemble.misc.infix import Infix
from msr_ensemble.facts.term import new_vars, new_destinations, lift
from msr_ensemble.facts.location import new_loc

RULE_ID = 0
RULE_CLASSES = {}

def register_rule(rule_class):
	global RULE_ID
	RULE_ID += 1
	rule_class.rule_id = RULE_ID
	RULE_CLASSES[RULE_ID] = rule_class

def get_all_rule_classes():
	return RULE_CLASSES

class Rule:

	def initialize(self, forall=0, exist_locs=0):
		self.create_vars(forall)
		self.exist_locations = new_vars(exist_locs)
		self.rank = -1
		if exist_locs > 0:
			self.req_dynamic_spawning = True
		else:
			self.req_dynamic_spawning = False
		
	def create_vars(self,n):
		self.variables = new_vars(n)

	def exist_locs(self):
		for exist_location in self.exist_locations:
			exist_location.unbind()
			exist_location.bind( new_loc(self.rank) )
		return self.exist_locations

	def get_exist_locs(self):
		return map(lambda e: e.value,self.exist_locations)

	def set_rank(self, rank):
		self.rank = rank

	def exists(self, n):
		return new_destinations(n)

	def get_vars(self):
		return self.variables

	def get_values(self):
		return [ term.value for term in self.variables]

	def propagate(self):
		return []

	def simplify(self):
		return []

	def guards(self):
		return []

	def consequents(self):
		return []


"""
class ColorRule1(Rule):

	def __init__(self):
		self.initialize(forall=4, exist_dest=2)

	def propagate(self):
		return []

	def simplify(self):
		x,y,c,f = self.get_vars()
		return Color(x,c),Neighbor(x,y,f)

	def guards(self):
		x,y,c,f = self.get_vars()
		return x |leq| y

	def consequents(self):
		x,y,c,f = self.get_vars()
		c1,c2 = lift(mix(c.val))
		return Color(x,c1),Color(x,c2)
"""
