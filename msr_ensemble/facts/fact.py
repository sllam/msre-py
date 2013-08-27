
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

from collections import defaultdict

FACT_SYMBOL_ID = 0
FACT_CLASSES = {}

DUMMY_VALUE = 'X'

def register_fact(fact_class):
	global FACT_SYMBOL_ID
	FACT_SYMBOL_ID += 1
	fact_class.sym_id = FACT_SYMBOL_ID
	FACT_CLASSES[FACT_SYMBOL_ID] = fact_class

def get_all_fact_classes():
	return FACT_CLASSES

def get_fact_class(sym_id):
	return FACT_CLASSES[sym_id]

def get_fact_name(sym_id):
	return FACT_CLASSES[sym_id].__name__

class Id:

	def __init__(self, id):
		self.id   = id
		self.live = True
		self.hash_values = []

	def is_alive(self):
		return self.live 

	def set_dead(self):
		self.live = False

	def add_hash_value(self, key):
		self.hash_values.append(key)

	def __str__(self):
		return "#%s" % self.id

# Id as dict
def new_id(i):
	return { 'id':i, 'hash_values':[], 'history_entries':defaultdict(list) }

def add_hash_value(fact_id, key):
	fact_id['hash_values'].append( key )

def pretty_id(fact_id):
	return "#%s" % fact_id['id']

class Fact:
	terms = None

	def __init__(self, sym_id, *terms):
		self.sym_id = sym_id
		self.terms  = terms
		self.hash_indices = []
		self.location = None
		self.is_located = False
		self.priority = 0

	def initialize(self, *terms):
		self.sym_id = self.__class__.sym_id
		self.terms  = terms
		self.hash_indices = []
		self.location = None
		self.is_located = False
		self.priority = 0

	def set_hash_indices(self, indices):
		self.hash_indices = indices

	def get_terms(self):
		return self.terms + tuple([self.location] if self.is_located else [])

	def unbind_terms(self):
		terms = self.terms
		for term in terms:
			term.unbind()
		if self.is_located:
			self.location.unbind()

	def exist_bind_terms(self):
		terms = self.terms
		for term in terms:
			term.bind(DUMMY_VALUE)
		if self.is_located:
			self.location.bind(DUMMY_VALUE)

	def set_location(self, loc):
		self.location = loc
		self.is_located = True

	def set_priority(self, p):
		self.priority = p

	def __str__(self):
		global FACT_CLASSES
		if not self.is_located:
			return "%s(%s)" % (FACT_CLASSES[self.sym_id].__name__,','.join(map(str,self.terms)))
		else:
			return "[%s]%s(%s)" % (str(self.location),FACT_CLASSES[self.sym_id].__name__,','.join(map(str,self.terms)))

@Infix
def at(fact, loc):
	fact.set_location(loc)
	return fact

@Infix
def priority(fact, p):
	fact.set_priority(p)
	return fact



