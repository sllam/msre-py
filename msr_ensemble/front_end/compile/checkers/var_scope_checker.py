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
import msr_ensemble.misc.terminal_color as terminal
from msr_ensemble.front_end.compile.inspectors import Inspector

from msr_ensemble.front_end.compile.checkers.base_checker import Checker

class VarScopeChecker(Checker):

	def __init__(self, decs, source_text):
		self.initialize(decs, source_text)
		self.curr_out_scopes = new_ctxt()
		self.curr_duplicates = new_ctxt()

	# Main checking operation

	def check(self):
		for dec in self.decs:
			self.check_scope(dec, new_ctxt())

	@visit.on('ast_node')
	def check_scope(self, ast_node, ctxt):
		pass

	@visit.when(ast.EnsemDec)
	def check_scope(self, ast_node, ctxt):
		old_ctxt = ctxt
		ctxt = copy_ctxt(ctxt)
		decs = ast_node.decs
		inspect = Inspector()
	
		dec_preds = {}

		# Check scoping of predicate declarations
		for dec in inspect.filter_decs(decs, fact=True):
			local_ctxt = self.check_scope(dec, ctxt)
			for pred in local_ctxt['preds']:
				if pred.name in dec_preds:
					dec_preds[pred.name].append(pred)
				else:
					dec_preds[pred.name] = [pred]
			extend_ctxt(ctxt, local_ctxt)

		self.compose_duplicate_error_reports("predicate", dec_preds)

		# Check scoping of rule declarations
		for dec in inspect.filter_decs(decs, rule=True):
			self.check_scope(dec, ctxt)

		return old_ctxt

	@visit.when(ast.FactDec)
	def check_scope(self, ast_node, ctxt):
		ctxt = new_ctxt()
		ctxt['preds'].append( ast_node )
		# TODO: check types
		return ctxt

	@visit.when(ast.RuleDec)
	def check_scope(self, ast_node, ctxt):
		ctxt = copy_ctxt(ctxt)
		heads   = ast_node.slhs + ast_node.plhs
		inspect = Inspector()

		# Extend location context with all rule head variables
		for fact in map(inspect.get_fact, heads):
			terms = inspect.get_atoms( [inspect.get_loc(fact)] + inspect.get_args(fact) )
			ctxt['vars'] += inspect.filter_atoms(terms, var=True)
			
		# Check scope of rule heads. This step is mainly for checking for constant name and 
		# predicate name scope of rule heads
		map(lambda h: self.check_scope(h, ctxt) , heads)
		map(lambda g: self.check_scope(g, ctxt) , ast_node.grd)

		# Include exist variables scopes
		ctxt['vars'] += ast_node.exists

		# Incremental include where assign statements
		for ass_stmt in ast_node.where:
			self.check_scope(ass_stmt.builtin_exp, ctxt)
			self.compose_out_scope_error_report(ctxt)
			ctxt['vars'] += inspect.filter_atoms( inspect.get_atoms(ass_stmt.term_pat), var=True)

		map(lambda b: self.check_scope(b, ctxt) , ast_node.rhs)

		'''
		for fact in map(inspect.get_fact, ast_node.rhs), fact_atoms=True ):
			loc = inspect.get_loc(fact)
			loc_key = loc.compare_value()
			args = inspect.get_args(fact)
			atoms = inspect.get_atoms(args)
			arg_map[loc_key] += map(lambda t: t.name,inspect.filter_atoms(atoms, var=True))
		'''

		self.compose_out_scope_error_report(ctxt)
		
	@visit.when(ast.LHSFact)
	def check_scope(self, ast_node, ctxt):
		return self.check_scope(ast_node.elem, ctxt)

	@visit.when(ast.RHSFact)
	def check_scope(self, ast_node, ctxt):
		return self.check_scope(ast_node.elem, ctxt)

	@visit.when(ast.RHSSetComp)
	def check_scope(self, ast_node, ctxt):
		return self.check_scope(ast_node.elem, ctxt)

	@visit.when(ast.FactLoc)
	def check_scope(self, ast_node, ctxt):
		ctxt = copy_ctxt(ctxt)
		self.check_scope(ast_node.loc, ctxt)
		for fact in ast_node.facts:
			self.check_scope(fact, ctxt)
		return ctxt

	@visit.when(ast.FactBase)
	def check_scope(self, ast_node, ctxt):
		ctxt = copy_ctxt(ctxt)
		self.check_pred(ctxt, ast_node)
		# print ast_node
		map(lambda t: self.check_scope(t, ctxt), ast_node.terms)
		return ctxt

	@visit.when(ast.TermCons)
	def check_scope(self, ast_node, ctxt):
		self.check_cons(ctxt, ast_node)
		return ctxt

	@visit.when(ast.TermVar)
	def check_scope(self, ast_node, ctxt):
		self.check_var(ctxt, ast_node)
		return ctxt

	@visit.when(ast.TermApp)
	def check_scope(self, ast_node, ctxt):
		self.check_scope(ast_node.term1, ctxt)
		self.check_scope(ast_node.term2, ctxt)
		return ctxt

	@visit.when(ast.TermTuple)
	def check_scope(self, ast_node, ctxt):
		map(lambda t: self.check_scope(t, ctxt), ast_node.terms)
		return ctxt

	@visit.when(ast.TermList)
	def check_scope(self, ast_node, ctxt):
		map(lambda t: self.check_scope(t, ctxt), ast_node.terms)
		return ctxt

	@visit.when(ast.TermBinOp)
	def check_scope(self, ast_node, ctxt):
		self.check_scope(ast_node.term1, ctxt)
		self.check_scope(ast_node.term2, ctxt)
		return ctxt

	@visit.when(ast.TermUnaryOp)
	def check_scope(self, ast_node, ctxt):
		self.check_scope(ast_node.term, ctxt)
		return ctxt

	@visit.when(ast.TermLit)
	def check_scope(self, ast_node, ctxt):
		return ctxt

	@visit.when(ast.TermUnderscore)
	def check_scope(self, ast_node, ctxt):
		return ctxt

	# Error state operations
	def flush_error_ctxt(self):
		self.curr_out_scopes = new_ctxt()
		self.curr_duplicates = new_ctxt()

	def check_var(self, ctxt, var):
		if not lookup_var(ctxt, var):
			self.curr_out_scopes['vars'].append( var )
			return False
		else:
			return True

	def check_pred(self, ctxt, pred):
		if not lookup_pred(ctxt, pred):
			self.curr_out_scopes['preds'].append( pred )
			return False
		else:
			return True

	def check_cons(self, ctxt, cons):
		if not lookup_cons(ctxt, cons):
			self.curr_out_scopes['cons'].append( cons )
			return False
		else:
			return True

	# Reporting

	def compose_out_scope_error_report(self, ctxt):
		err = self.curr_out_scopes
		if len(err['vars']) > 0:
			legend = ("%s %s: Scope context variable(s).\n" % (terminal.T_GREEN_BACK,terminal.T_NORM)) + ("%s %s: Out of scope variable(s)." % (terminal.T_RED_BACK,terminal.T_NORM))
			error_idx = self.declare_error("Variable(s) %s not in scope." % (','.join(set(map(lambda t: t.name,err['vars'])))), legend)
			map(lambda t: self.extend_error(error_idx,t), err['vars'])
			map(lambda t: self.extend_info(error_idx,t), ctxt['vars'])
		self.curr_out_scopes = new_ctxt()

	def compose_duplicate_error_reports(self, kind, dups):
		for name in dups:
			elems = dups[name]
			if len(elems) > 1:
				error_idx = self.declare_error("Duplicated declaration of %s %s." % (kind,name))
				map(lambda p: self.extend_error(error_idx,p), elems)

def new_ctxt():
	return { 'vars':[], 'preds':[], 'cons':[] }

def lookup_var(ctxt, v):
	return v.name in map(lambda t: t.name,ctxt['vars'])

def lookup_pred(ctxt, p):
	return p.name in map(lambda t: t.name,ctxt['preds'])

def lookup_cons(ctxt, c):
	return c.name in map(lambda t: t.name,ctxt['cons'])

def copy_ctxt(c):
	output = new_ctxt()
	extend_ctxt(output, c)
	return output

def extend_ctxt(c1, c2):
	map(lambda v: remove_ctxt(c1,'vars',v), c2['vars'])
	map(lambda p: remove_ctxt(c1,'preds',p), c2['preds'])
	map(lambda c: remove_ctxt(c1,'cons',c), c2['cons'])
	c1['vars']  += c2['vars']
	c1['preds'] += c2['preds']
	c1['cons']  += c2['cons']

def union_ctxt(c1, c2):
	output = new_ctxt()
	extend_ctxt(output,c1)	
	extend_ctxt(output,c2)
	return output

def remove_ctxt(c, ty, e):
	ls = c[ty]
	for idx in range(0,len(ls)):
		if e.name == ls[idx].name:
			del ls[idx]
			break



