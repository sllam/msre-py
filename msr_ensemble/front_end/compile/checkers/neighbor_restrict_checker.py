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

class NeighborRestrictChecker(Checker):

	def __init__(self, decs, source_text):
		self.initialize(decs, source_text)


	# Main checking operation

	def check(self):
		for dec in self.decs:
			self.int_check(dec)

	@visit.on('ast_node')
	def int_check(self, ast_node):
		pass

	@visit.when(ast.EnsemDec)
	def int_check(self, ast_node):
		for dec in ast_node.decs:
			self.int_check(dec)

	@visit.when(ast.RuleDec)
	def int_check(self, ast_node):
		heads   = ast_node.slhs + ast_node.plhs
		inspect = Inspector()

		# Build the neighborhood free variables mapping of the rule heads (NFV mapping)
		locs    = []
		neighbor_fvs = {}
		for fact in map(inspect.get_fact, heads):
			loc = inspect.get_loc(fact)
			loc_key = loc.name		
			if loc_key not in neighbor_fvs:
				neighbor_fvs[loc_key] = []
			args = inspect.get_args(fact)
			atoms = inspect.get_atoms(args)
			locs.append( loc )
			neighbor_fvs[loc_key] += inspect.filter_atoms(atoms, var=True)

		# From NFV mapping, nominate the primary location
		all_locs = neighbor_fvs.keys()
		ast_node.primary_loc = None
		ast_node.primary_fv  = None
		missing_vars = {}
		for loc in neighbor_fvs:
			fv = map(lambda t: t.name, neighbor_fvs[loc])
			contains_all_locs = True
			for t_loc in all_locs:
				if (t_loc not in fv) and t_loc != loc:
					contains_all_locs = False
					if loc in missing_vars:
						missing_vars[loc].append( t_loc )
					else:
						missing_vars[loc] = [t_loc]
			if contains_all_locs:
				ast_node.primary_loc = loc
				ast_node.primary_fv  = neighbor_fvs[loc]
				del neighbor_fvs[loc]
				break
		ast_node.neighbor_fvs = neighbor_fvs
		ast_node.neighbor_restriction = len(neighbor_fvs.keys())

		if ast_node.primary_loc == None:
			legend = ("%s %s: Location variable(s).\n" % (terminal.T_GREEN_BACK,terminal.T_NORM)) + ("%s %s: Argument variable.\n" % (terminal.T_RED_BACK,terminal.T_NORM))
			for loc in missing_vars:
				legend += "Location %s has no links to %s.\n" % (loc,','.join(missing_vars[loc]))
			error_report = "Rule %s is not neighbor restricted; None of location(s) %s can be primary location." % (ast_node.name,','.join(neighbor_fvs.keys()) )
			error_idx = self.declare_error(error_report , legend)
			for loc in neighbor_fvs:
				map(lambda t: self.extend_error(error_idx,t), neighbor_fvs[loc])
			map(lambda t: self.extend_info(error_idx,t), locs)
			return None

		# print "\n\n\n"
		# print ast_node.primary_loc
		# print ast_node.primary_fv
		# print ast_node.neighbor_fvs
		# print ast_node.neighbor_restriction

		primary_loc = ast_node.primary_loc
		primary_fv  = ast_node.primary_fv		
	
		primary_grds = []
		neighbor_grds = {}

		# Identify guards that are grounded by primary location
		for g_term in ast_node.grd: 
			g_vars = inspect.filter_atoms( inspect.get_atoms(g_term), var=True)
			excluded = not_contained(primary_fv, g_vars, key=lambda t:t.name)
			# print (ast_node.primary_loc,map(lambda t:t.name,excluded))
			if len(excluded) == 0:
				primary_grds.append(g_term)
			else:
				for loc in neighbor_fvs:
					excluded = not_contained(primary_fv + neighbor_fvs[loc], g_vars, key=lambda t:t.name)
					if len(excluded) == 0:
						if loc in neighbor_grds:
							neighbor_grds[loc].append( g_term )
						else:
							neighbor_grds[loc] = [g_term]

		# TODO: Add neighbor restriction guard test
		
		ast_node.primary_grds  = primary_grds
		ast_node.neighbor_grds = neighbor_grds
		
		# print ast_node.primary_grds
		# print ast_node.neighbor_grds

def not_contained(ls, es, key=lambda x: x):
	keys = map(key,ls)
	nots = []
	for e in es:
		if key(e) not in keys:
			nots.append(e)
	return nots

