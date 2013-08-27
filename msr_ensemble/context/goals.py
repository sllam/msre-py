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

from msr_ensemble.facts.fact import Fact, get_fact_class
from msr_ensemble.context.fact_repr import make_fact_repr

def add_goals(goals, facts):
	map(lambda fact: add_goal(goals,fact),facts)

def add_goal(goals, fact):
	fact_repr = make_fact_repr(fact)
	# fact_repr = { 'sym_id' : fact['sym_id'], 'values':map(lambda f: f.value,fact['terms']) }
	goals.append(fact_repr)
	
def next_goal(goals):
	return goals.pop()


class Goals:
	
	def pop(self):
		pass

	def push(self, fact):
		pass

	def push_many(self, facts):
		pass

class ListGoals(Goals):

	def __init__(self):
		self.goals = []

	def pop(self):
		return self.goals.pop()

	def push(self, fact):
		self.goals.append(fact)

	def push_many(self, facts):
		goals = self.goals
		map(lambda fact: goals.append(fact), facts)

HEAP_LEAF = 0
HEAP_LEFT_PARENT = 1
HEAP_RIGHT_PARENT = 2

def new_heap_leaf():
	return { 'type':HEAP_LEAF, 'key':None, 'data':None, 'left':None, 'right':None }

def new_heap_left_parent(key, data, left_heap, right_heap):
	return { 'type':HEAP_LEFT_PARENT, 'key':key, 'data':data, 'left':left_heap, 'right':right_heap }

def new_heap_right_parent(key, data, left_heap, right_heap):
	return { 'type':HEAP_RIGHT_PARENT, 'key':key, 'data':data, 'left':left_heap, 'right':right_heap }

def insert_heap(heap, key, data):
	type = heap['type']
	if type == HEAP_LEAF:
		heap['type']  = HEAP_LEFT_PARENT
		heap['key']   = key
		heap['data']  = data
		heap['left']  = new_heap_leaf()
		heap['right'] = new_heap_leaf()
	else:
		if type == HEAP_LEFT_PARENT:
			new_type = HEAP_RIGHT_PARENT
			i_heap   = heap['left']
		else:
			new_type = HEAP_LEFT_PARENT
			i_heap   = heap['right']
		my_key  = heap['key']
		my_data = heap['data']
		heap['type'] = new_type
		if key < my_key:
			insert_heap(i_heap,my_key,my_data)
			heap['key'] = key
			heap['data'] = data
		else:
			insert_heap(i_heap,key,data)
			

def get_min_heap(heap):
	return heap['data']

def to_array_heap(heap):
	ls = []
	data = get_min_heap(heap)
	while data != None:	
		ls.append((heap['key'],data))
		delete_min_heap(heap)
		data = get_min_heap(heap)
	return ls		

def delete_min_heap(heap):
	type = heap['type']
	if type == HEAP_LEAF:
		pass
	else:
		new_heap = merge_heap(heap['left'],heap['right'])
		heap['type']  = new_heap['type']
		heap['key']   = new_heap['key']
		heap['data']  = new_heap['data']
		heap['left']  = new_heap['left']
		heap['right'] = new_heap['right']

def merge_heap(heap1,heap2):
	type1 = heap1['type']
	type2 = heap2['type']
	if type1 == HEAP_LEAF and type2 == HEAP_LEAF:
		return new_heap_leaf()
	elif type2 == HEAP_LEAF:
		return heap1
	elif type1 == HEAP_LEAF:
		return heap2
	else:
		key1 = heap1['key']
		key2 = heap2['key']
		if key1 < key2:
			data1 = heap1['data']
			delete_min_heap(heap1)
			return new_heap_left_parent(key1,data1,heap1,heap2) 
		else:
			data2 = heap2['data']
			delete_min_heap(heap2)
			return new_heap_right_parent(key2,data2,heap1,heap2)

class HeapGoals(Goals):

	def __init__(self):
		self.goals = new_heap_leaf()

	def pop(self):
		heap = self.goals
		if heap['type'] == HEAP_LEAF:
			raise IndexError
		fact = heap['data']
		delete_min_heap(heap)
		return fact

	def push(self, fact):
		heap = self.goals
		insert_heap(heap, fact['prior'], fact)

	def push_many(self, facts):
		heap = self.goals
		for fact in facts:
			insert_heap(heap, fact['prior'], fact)

	def pop_all(self):
		return to_array_heap(self.goals)


def test_heap():
	hg = HeapGoals()
	hg.push({ 'prior':42, 'value':'gaga' })
	hg.push({ 'prior':1, 'value':'goa' })
	hg.push({ 'prior':24, 'value':'asdga' })
	hg.push({ 'prior':897, 'value':'gsdfga' })
	hg.push({ 'prior':3, 'value':'gag' })
	return hg.pop_all()

