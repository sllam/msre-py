
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
from msr_ensemble.facts.term import Term

class Guard:

	def initialize(self, sym_str, *terms, **kwargs):
		self.sym_str = sym_str
		self.terms   = terms
		if 'infix' in kwargs:
			self.infix = kwargs['infix']
		else:
			self.infix = False

	def get_vars(self):
		return self.terms

	def get_values(self):
		return [term.value for term in self.terms]

	def var_scope(self):
		return self.terms

	def is_ground(self):
		for term in self.terms:
			if not term.is_ground():
				return False
		return True

	def evaluate(self):
		return False

	def __str__(self):
		terms = self.terms
		if self.infix:
			v1 = terms[0].value
			v2 = terms[1].value
			terms[0].unbind()
			terms[1].unbind()
			out = "%s %s %s" % (str(terms[0]),self.sym_str,str(terms[1]))
			terms[0].bind(v1)
			terms[1].bind(v2)
			return out
		else:
			vs = [ term.value for term in terms ]
			for term in terms:
				term.unbind()
			out = "%s(%s)" % (self.sym_str,','.join(map(str,terms)))
			for i in xrange(0,len(terms)):
				terms[i].bind(vs[i])
			return out

class Leq(Guard):
	def __init__(self, x, y):
		self.initialize('<=', x, y, infix=True)
	def evaluate(self):
		x,y = self.get_values()
		return x <= y

class Eq(Guard):
	def __init__(self, x, y):
		self.initialize('==', x, y, infix=True)
	def evaluate(self):
		x,y = self.get_values()
		return x == y

class Geq(Guard):
	def __init__(self, x, y):
		self.initialize('>=', x, y, infix=True)
	def evaluate(self):
		x,y = self.get_values()
		return x >= y

class Less(Guard):
	def __init__(self, x, y):
		self.initialize('<', x, y, infix=True)
	def evaluate(self):
		x,y = self.get_values()
		return x < y

class Greater(Guard):
	def __init__(self, x, y):
		self.initialize('>', x, y, infix=True)
	def evaluate(self):
		x,y = self.get_values()
		return x > y


