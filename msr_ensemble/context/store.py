
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

import sys

from msr_ensemble.facts.term import Term
from msr_ensemble.facts.fact import Fact, Id, new_id, pretty_id, get_all_fact_classes, get_fact_name
from msr_ensemble.context.fact_repr import pretty_fact_repr

from collections import defaultdict
from cPickle import dumps

class FactStore:

	def __init__(self, sym_id):
		self.sym_id   = sym_id
		self.next_id  = 0
		self.hash_pats   = []
		self.hash_tables = []
		self.main_table  = {}
		#self.size = 0

	def generate_lookup(self, fact):
		lookup_pat = build_lookup_pat(fact)
		lookup_filter_info = build_lookup_and_filter(fact, lookup_pat)
		
		if 'lookup_key' in lookup_filter_info:
			hash_pat    = (lookup_pat['binded_keys'],lookup_pat['binded_hashs'])
			hash_pats   = self.hash_pats
			hash_tables = self.hash_tables
			lookup_index = -1
			for i in xrange(0,len(hash_pats)):
				if hash_pat == hash_pats[i]:
					lookup_index = i
					break
			if lookup_index == -1:
				hash_pats.append(hash_pat)
				hash_tables.append({ 'hash_table' : defaultdict(dict) 
                                                   , 'hash_key'   : lookup_filter_info['lookup_key']
                                                   , 'hash_str'   : str(fact) })
				lookup_index = len(hash_pats) - 1
		else:
			lookup_index = -1
		return { 'lookup_index':lookup_index, 'filter':lookup_filter_info['filter'] }
			
	def add_to_store(self, fact_repr):
		self.next_id += 1
		fact_id = new_id(self.next_id)
		fact_repr['fact_id'] = fact_id
		id_val = fact_id['id']
		self.main_table[id_val] = fact_repr
		#self.size += 1
		values  = fact_repr['values']
		# id      = fact_repr['fact_id']
		fact_id_add_hash_value = fact_id['hash_values'].append
		for hash_table in self.hash_tables:
			hash_val = hash_table['hash_key'](values)
			# print hash_val
			fact_id_add_hash_value(hash_val)
			table = hash_table['hash_table'][hash_val]
			table[id_val] = fact_repr

	def del_from_store(self, fact_id):
		id_val      = fact_id['id']
		hash_values = fact_id['hash_values']
		hash_tables = self.hash_tables
		# sys.stdout.write("%s\n" % pretty_candidates(self.main_table))
		del self.main_table[id_val]
		for i in xrange(0,len(hash_values)):
			hash_table = hash_tables[i]['hash_table']
			can_table = hash_table[hash_values[i]]
			del can_table[id_val]
			if None == next(can_table.itervalues(),None):
				del hash_table[hash_values[i]]
		#self.size -= 1

	def get_candidates(self, lookup_index, term_values):
		if lookup_index >= 0:
			hash_table_data = self.hash_tables[lookup_index]
			hash_table = hash_table_data['hash_table']
			hash_value = hash_table_data['hash_key'](term_values)
			if hash_value in hash_table:
				return hash_table[hash_value].itervalues()
			else:
				return {}.itervalues()
		else:
			return self.main_table.itervalues()

	def get_candidate_lookup_func_from_store(self, lookup_index, term_pats):
		if lookup_index >= 0:
			hash_table_data = self.hash_tables[lookup_index]
			hash_table = hash_table_data['hash_table']
			hash_key   = hash_table_data['hash_key']
			def lookup_func():
				# hash_value = hash_key(map(lambda t: t.value,term_pats))
				values = []
				for t in term_pats:
					values.append( t.value )
				hash_value = hash_key(values)
				if hash_value in hash_table:
					return hash_table[hash_value].itervalues()
				else:
					return {}.itervalues()
			return lookup_func
		else:
			return self.main_table.itervalues

	def __str__(self):
		store_header  = "%s Store:" % get_fact_name(self.sym_id)
		main_header   = "--- Main ---"
		main_contents = pretty_candidates(self.main_table)
		hash_tables   = self.hash_tables
		hash_contents = ""
		for i in xrange(0,len(hash_tables)):
			hash_contents += "--- Hash Lookup %s: %s ---\n" % (i,hash_tables[i]['hash_str'])
			hash_contents += pretty_hash_table(hash_tables[i]) + "\n"
		return '%s' % '\n'.join([store_header,main_header,main_contents,hash_contents])

	def str_brief(self):
		fact_name  = get_fact_name(self.sym_id)
		fact_strs = []
		for fact in candidate_args(self.main_table):
			fact_strs.append( "%s(%s)" % (fact_name, ','.join( map(str,fact) )) )
		if len(fact_strs) > 0:
			return ','.join(fact_strs)
		else:
			return None

def new_stores():
	fact_stores = {}
	for sym_id in get_all_fact_classes():
		fact_stores[sym_id] = FactStore(sym_id)
	return fact_stores

def pretty_stores(fact_stores, brief=False):
	fact_classes = get_all_fact_classes()
	strs = []
	for sym_id,st in fact_stores.items():
		if not brief:
			strs.append( str(st) )
		else:
			my_str = st.str_brief()
			if my_str != None:
				strs.append( my_str )
	return '\n'.join(strs) + '\n'

def add_to_stores(fact_stores, fact_repr):
	fact_stores[fact_repr['sym_id']].add_to_store(fact_repr)
	
def del_from_stores(fact_stores, fact_repr):
	fact_stores[fact_repr['sym_id']].del_from_store(fact_repr['fact_id'])

def get_candidates_from_stores(fact_stores, lookup_index, sym_id, term_pats):
	return fact_stores[sym_id].get_candidates(lookup_index, map(lambda t: t.value,term_pats))

def get_candidate_lookup_func_from_stores(fact_stores, lookup_index, sym_id, term_pats):
	return fact_stores[sym_id].get_candidate_lookup_func_from_store(lookup_index, term_pats)

def build_lookup_pat(fact):
	terms = fact.terms
	hash_indices = fact.hash_indices
	num_of_terms = len(terms)

	binded_key_indices  = []
	binded_hash_indices = []
	free_indices    = []
	const_indices   = []
	duncare_indices = []
	for index in xrange(0,num_of_terms):
		term = terms[index]
		if term.is_binded():
			# if not (index in hash_indices):
			if False:
				binded_key_indices.append(index)
			else:
				binded_hash_indices.append(index)
		elif term.is_const():
			const_indices.append(index)
		elif term.is_duncare():
			duncare_indices.append(index)
		else:
			free_indices.append(index)
	
	res = { 'binded_keys'  : binded_key_indices, 
                 'binded_hashs' : binded_hash_indices, 
                 'free'         : free_indices, 
                 'const'        : const_indices, 
                 'duncare'      : duncare_indices }
	
	# print "%s" % fact
	# print "%s" % res

	return res

def build_lookup_and_filter(fact, lookup_pat):
	terms = fact.terms
	binded_key_indices  = lookup_pat['binded_keys']	
	binded_hash_indices = lookup_pat['binded_hashs']
	const_indices  = lookup_pat['const']

	lookup_info = {}

	# Lookup key function
	if len(binded_key_indices) + len(binded_hash_indices) > 0:
		def lookup_key(vs):
			ks = [vs[index] for index in binded_key_indices] + [ str(vs[index]) for index in binded_hash_indices]		
			return tuple(ks) if len(ks) > 1 else ks[0]
		lookup_info['lookup_key'] = lookup_key

	# Post lookup filter function
	if len(const_indices) > 0:
		const_values = [terms[index].value for index in const_indices]
		filter_func = lambda vs: [vs[index] for index in const_indices] == const_values 
		lookup_info['filter'] = filter_func
	else:
		lookup_info['filter'] = lambda _: True

	return lookup_info

def pretty_hash_table(hash_table):
	iterate = hash_table['hash_table'].iteritems()
	strs = []
	while True:
		key,cans = next(iterate,(None,None))
		if cans != None:
			strs.append("%s -> %s" % (key,pretty_candidates(cans)))
		else:
			return "%s" % '\n'.join(strs)

def pretty_candidates(candidate_dict):
	iterate  = candidate_dict.itervalues()
	can_strs = []
	while True:
		can = next(iterate,None)
		if can != None:
			can_strs.append(pretty_fact_repr(can))
		else:
			return "{ %s }" % ', '.join(can_strs)	
	
def candidate_args(candidate_dict):
	iterate  = candidate_dict.itervalues()
	can_args = []
	while True:
		can = next(iterate,None)
		if can != None:
			can_args.append(can['values'])
		else:
			return can_args
	
class Candidates:
	
	def add_fact(self, fact, fact_id):
		pass

	def del_fact(self, fact_id):
		pass

	def get_iterate(self):
		return None

class DictCandidates(Candidates):

	def __init__(self):
		self.candidates = {}
	
	def add_fact(self, fact, fact_id):
		self.candidates[fact_id] = fact

	def del_fact(self, fact_id):
		del self.candidates[fact_id]

	def get_iterate(self):
		return self.candidates.iteritems()

