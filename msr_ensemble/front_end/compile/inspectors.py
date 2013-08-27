
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

import msr_ensemble.front_end.parser.msr_ast as ast
import msr_ensemble.misc.visit as visit

class Inspector:

	# Get Fact from LHS and RHS wrappers

	def get_facts(self, ast_nodes):
		return map(self.get_fact, ast_nodes)

	@visit.on('ast_node')
	def get_fact(self, ast_node):
		pass

	@visit.when(ast.LHSFact)
	def get_fact(self, ast_node):
		return ast_node.elem

	@visit.when(ast.RHSFact)
	def get_fact(self, ast_node):
		return ast_node.elem

	@visit.when(ast.RHSSetComp)
	def get_fact(self, ast_node):
		return ast_node.elem

	# Filter Facts from FactLoc or SetComprehension

	@visit.on('fact')
	def filter_facts(self, fact, fact_atoms=False, comprehensions=False):
		pass

	@visit.when(list)
	def filter_facts(self, fact, fact_atoms=False, comprehensions=False):
		facts = []
		for f in fact:
			facts += self.filter_facts(f, fact_atoms=fact_atoms, comprehensions=comprehensions)
		return facts
	
	@visit.when(ast.FactLoc)
	def filter_facts(self, fact, fact_atoms=False, comprehensions=False):
		return [fact] if fact_atoms else []

	@visit.when(ast.SetComprehension)
	def filter_facts(self, fact, fact_atoms=False, comprehensions=False):
		return [fact] if comprehensions else []

	# Get Location from FactLoc

	def get_loc(self, loc_fact):
		return loc_fact.loc

	# Get Term arguments from FactLoc

	@visit.on('ast_node')
	def get_args(self, ast_node):
		pass

	@visit.when(list)
	def get_args(self, ast_node):
		args = []
		for node in ast_node:
			args += self.get_args(node)
		return args

	@visit.when(ast.FactLoc)
	def get_args(self, ast_node):
		args = []
		for fact in ast_node.facts:
			args += self.get_args(fact)
		return args
	
	@visit.when(ast.FactBase)
	def get_args(self, ast_node):
		args = []
		for term in ast_node.terms:
			args.append(term)
		return args
		
	# Get Term Atoms from Terms
	
	@visit.on('term')
	def get_atoms(self, term):
		pass

	@visit.when(list)
	def get_atoms(self, term):
		atoms = []
		for t in term:
			atoms += self.get_atoms(t)
		return atoms

	@visit.when(ast.TermVar)
	def get_atoms(self, term):
		return [term]

	@visit.when(ast.TermCons)
	def get_atoms(self, term):
		return [term]

	@visit.when(ast.TermApp)
	def get_atoms(self, term):
		return self.get_atoms(term.term1) + self.get_atoms(term.term2)

	@visit.when(ast.TermTuple)
	def get_atoms(self, term):
		atoms = []
		for t in term.terms:
			atoms += self.get_atoms(t)
		return atoms

	@visit.when(ast.TermList)
	def get_atoms(self, term):
		atoms = []
		for t in term.terms:
			atoms += self.get_atoms(t)
		return atoms

	@visit.when(ast.TermBinOp)
	def get_atoms(self, term):
		return self.get_atoms(term.term1) + self.get_atoms(term.term2)
		
	@visit.when(ast.TermUnaryOp)
	def get_atoms(self, term):
		return self.get_atoms(term.term)

	@visit.when(ast.TermLit)
	def get_atoms(self, term):
		return [term]

	@visit.when(ast.TermUnderscore)
	def get_atoms(self, term):
		return []

	# Filtering from Term Atoms
	
	@visit.on('term')
	def filter_atoms(self, term, var=False, lit=False, cons=False):
		pass

	@visit.when(list)
	def filter_atoms(self, term, var=False, lit=False, cons=False):
		atoms = []
		for t in term:
			atoms += self.filter_atoms(t, var=var, lit=lit, cons=cons)
		return atoms

	@visit.when(ast.TermVar)
	def filter_atoms(self, term, var=False, lit=False, cons=False):
		return [term] if var else []

	@visit.when(ast.TermLit)
	def filter_atoms(self, term, var=False, lit=False, cons=False):
		return [term] if lit else []

	@visit.when(ast.TermCons)
	def filter_atoms(self, term, var=False, lit=False, cons=False):
		return [term] if cons else []

	# Filtering from Decs

	@visit.on('dec')
	def filter_decs(self, dec, ensem=False, extern=False, execute=False, fact=False, rule=False, assign=False, init=False):
		pass

	@visit.when(list)
	def filter_decs(self, dec, ensem=False, extern=False, execute=False, fact=False, rule=False, assign=False, init=False):
		decs = []
		for d in dec:
			decs += self.filter_decs(d, ensem=ensem, extern=extern, execute=execute, fact=fact, rule=rule, assign=assign, init=init)
		return decs

	@visit.when(ast.EnsemDec)
	def filter_decs(self, dec, ensem=False, extern=False, execute=False, fact=False, rule=False, assign=False, init=False):
		return [dec] if ensem else []

	@visit.when(ast.ExternDec)
	def filter_decs(self, dec, ensem=False, extern=False, execute=False, fact=False, rule=False, assign=False, init=False):
		return [dec] if extern else []

	@visit.when(ast.ExecDec)
	def filter_decs(self, dec, ensem=False, extern=False, execute=False, fact=False, rule=False, assign=False, init=False):
		return [dec] if execute else []

	@visit.when(ast.FactDec)
	def filter_decs(self, dec, ensem=False, extern=False, execute=False, fact=False, rule=False, assign=False, init=False):
		return [dec] if fact else []

	@visit.when(ast.RuleDec)
	def filter_decs(self, dec, ensem=False, extern=False, execute=False, fact=False, rule=False, assign=False, init=False):
		return [dec] if rule else []

	@visit.when(ast.AssignDec)
	def filter_decs(self, dec, ensem=False, extern=False, execute=False, fact=False, rule=False, assign=False, init=False):
		return [dec] if assign else []

	@visit.when(ast.InitDec)
	def filter_decs(self, dec, ensem=False, extern=False, execute=False, fact=False, rule=False, assign=False, init=False):
		return [dec] if init else []

	# Filtering Facts from FactLoc

	@visit.on('loc_fact')
	def filter_facts(self, loc_fact, loc_var):
		pass

	@visit.when(list)
	def filter_facts(self, loc_fact, loc_var):
		facts = []
		for lf in loc_fact:
			facts += self.filter_facts(lf, loc_var)
		return facts	

	@visit.when(ast.FactLoc)
	def filter_facts(self, loc_fact, loc_var):
		locs = self.filter_atoms( self.get_loc(loc_fact) , var=True)
		if len(locs) == 1:
			if locs[0].name == loc_var:
				return loc_fact.facts
			else:
				return []
		else:
			return []

