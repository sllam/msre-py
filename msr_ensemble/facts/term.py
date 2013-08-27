
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

from uuid import uuid4

TERM_VARIABLE_ID = 0

def next_variable_id():
	global TERM_VARIABLE_ID
	TERM_VARIABLE_ID += 1
	return TERM_VARIABLE_ID

TERM_EXIST_ID = 0

def next_exist_id():
	global TERM_EXIST_ID
	TERM_EXIST_ID += 1
	return TERM_EXIST_ID

VAR_TERM     = 0
CONST_TERM   = 1
DUNCARE_TERM = 2 

class Term:

	identity = None
	value = None

	def __init__(self, value=None, dun_care=False):
		if dun_care:
			self.term_type = DUNCARE_TERM
			self.value    = None
			self.identity = None
		if value == None:
			self.term_type = VAR_TERM
			self.value     = None
			self.identity  = next_variable_id()
		else:
			self.term_type = CONST_TERM
			self.value     = value
			self.identity  = value
		self.binded = False

	def is_ground(self):
		term_type = self.term_type
		return (term_type != VAR_TERM) or (self.binded == True)

	def is_binded(self):
		return self.term_type == VAR_TERM and self.binded

	def is_unbinded(self):
		return self.term_type == VAR_TERM and not self.binded

	def is_var(self):
		return self.term_type == VAR_TERM

	def is_const(self):
		return self.term_type == CONST_TERM

	def is_duncare(self):
		return self.term_type == DUNCARE_TERM

	def unbind(self):
		if self.term_type == VAR_TERM:
			self.value = None
			self.binded = False

	def bind(self,value):
		if self.term_type == VAR_TERM:
			self.value = value
			self.binded = True

	def __str__(self):
		term_type = self.term_type
		if term_type == DUNCARE_TERM:
			return '_'
		if self.is_ground():
			return str(self.value)
		else:
			return '$' + str(self.identity)

	def __eq__(self, other):
		if self.is_ground() and other.is_ground():
			return self.identity == other.identity
		elif not self.is_ground() and not other.is_ground():
			return self.value == other.value
		else:
			return False

def new_destination():
	# e = "D%s" % next_exist_id()
	# return Term(e)
	return Term(str(uuid4()))

def new_destinations(n):
	return [new_destination() for i in range(0,n)]

def new_var():
	return Term()

def new_vars(n):
	return [Term() for i in range(0,n)]

def lift(value):
	return Term(value)

def lift_many(*values):
	return [Term(v) for v in values]

def val(term):
	return term.value

def inst(term):
	return lift( val(term) )

_ = Term(dun_care=True)

def __(t):
	return t.value

