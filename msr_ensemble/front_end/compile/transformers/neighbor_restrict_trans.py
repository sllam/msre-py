
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

from msr_ensemble.front_end.compile.code_gen import MSRCodeGen

from msr_ensemble.front_end.compile.transformers.base_trans import Trans
from msr_ensemble.front_end.compile.inspectors import Inspector
from msr_ensemble.misc.template import compile_template, template, compact

import msr_ensemble.front_end.parser.msr_ast as ast
import msr_ensemble.misc.visit as visit

class NeighborRestrictTrans(Trans):

	def __init__(self, decs, source_text):
		self.initialize(decs, source_text)

	def trans(self):
		return self.init_trans(self.decs)

	@visit.on('ast_node')
	def init_trans(self, ast_node):
		pass

	@visit.when(list)
	def init_trans(self, ast_node):
		return map(self.init_trans, ast_node)

	@visit.when(ast.EnsemDec)
	def init_trans(self, ast_node):
		new_decs = []
		for dec in ast_node.decs:
			trans_dec = self.init_trans(dec)
			if not isinstance(trans_dec, list):
				new_decs.append( trans_dec )
			else:
				new_decs += trans_dec
		ast_node.decs = new_decs
		return ast_node

	@visit.when(ast.ExternDec)
	def init_trans(self, ast_node):
		return ast_node

	@visit.when(ast.ExecDec)
	def init_trans(self, ast_node):
		return ast_node

	@visit.when(ast.FactDec)
	def init_trans(self, ast_node):
		return ast_node

	@visit.when(ast.InitDec)
	def init_trans(self, ast_node):
		return ast_node

	@visit.when(ast.AssignDec)
	def init_trans(self, ast_node):
		return ast_node

	@visit.when(ast.RuleDec)
	def init_trans(self, ast_node):
		if ast_node.neighbor_restriction == 1:
			return self.one_neighbor_restrict_trans(ast_node)
		elif ast_node.neighbor_restriction == 0:
			return ast_node
		else:
			# TODO: N-neighbor restriction
			return ast_node

	def one_neighbor_restrict_trans(self, rule_dec):

		inspect = Inspector()

		prop_heads = inspect.get_facts( rule_dec.plhs )
		simp_heads = inspect.get_facts( rule_dec.slhs )

		rule_name = rule_dec.name
		x = rule_dec.primary_loc		
		y = rule_dec.neighbor_fvs.keys()[0]

		x_prop_heads = ','.join(map(lambda f: "[%s]%s" % (x,f.gen_snippet(self.source_text)), inspect.filter_facts( prop_heads, x ) ))
		y_prop_heads = ','.join(map(lambda f: "[%s]%s" % (y,f.gen_snippet(self.source_text)), inspect.filter_facts( prop_heads, y ) ))
		x_simp_heads = ','.join(map(lambda f: "[%s]%s" % (x,f.gen_snippet(self.source_text)), inspect.filter_facts( simp_heads, x ) ))
		y_simp_heads = ','.join(map(lambda f: "[%s]%s" % (y,f.gen_snippet(self.source_text)), inspect.filter_facts( simp_heads, y ) ))

		x_prop_heads = x_prop_heads if len(x_prop_heads) > 0 else "1"
		y_prop_heads = y_prop_heads if len(y_prop_heads) > 0 else "1"
		x_simp_heads = x_simp_heads if len(x_simp_heads) > 0 else "1"
		y_simp_heads = y_simp_heads if len(y_simp_heads) > 0 else "1"

		x_guards = ','.join( map(lambda f: f.gen_snippet(self.source_text), rule_dec.primary_grds) )
		if y in rule_dec.neighbor_grds:
			y_guards = ','.join( map(lambda f: f.gen_snippet(self.source_text), rule_dec.neighbor_grds[y]) ) 
		else:
			y_guards = []
		x_guards = ("| %s" % x_guards) if len(x_guards) > 0 else ""
		y_guards = ("| %s" % y_guards) if len(y_guards) > 0 else ""

		lxs = set(map(lambda t:t.name,rule_dec.primary_fv) + [x])
		lrs = set(map(lambda t:t.name,rule_dec.primary_fv + rule_dec.neighbor_fvs[y]) + [x])
		xs = ','.join( lxs )
		rs = ','.join( lrs )
		xs_types = ','.join( map(lambda _: "int" ,lxs) )
		rs_types = ','.join( map(lambda _: "int" ,lrs) )

		rule_body = ','.join( map(lambda f: f.gen_snippet(self.source_text), inspect.get_facts(rule_dec.rhs) ) )

		'''
		print "Xs: %s" % xs
		print "Rs: %s" % rs
		print "X Guards: %s" % x_guards
		print "Y Guards: %s" % y_guards
		print "X Prop: %s" % x_prop_heads
		print "Y Prop: %s" % y_prop_heads
		print "X Simp: %s" % x_simp_heads
		print "Y Simp: %s" % y_simp_heads
		'''

		if inspect.filter_facts( simp_heads, x ) > 0:
			match_rule_code = template('''
				{| y_prop_heads |},{| y_simp_heads |} \ [{| y_loc |}]{| rule_name |}_req({| xs_args |}) {| y_guards |} --o [{| x_loc |}]{| rule_name |}_match({| rs_args |}) priority 2.
			''')
		else:
			match_rule_code = template('''
				[{| y_loc |}]{| rule_name |}_req({| xs_args |}),{| y_prop_heads |},{| y_simp_heads |} \ 1 {| y_guards |} --o [{| x_loc |}]{| rule_name |}_match({| rs_args |}) priority 2.
			''')
		match_rule = compile_template(match_rule_code, y_loc=y, xs_args=xs, rs_args=rs, y_prop_heads=y_prop_heads, y_simp_heads=y_simp_heads
                                             ,x_loc=x, rule_name=rule_dec.name, y_guards=y_guards)

		# print match_rule

		exists_code = ""
		if len(rule_dec.exists) > 0:
			exists_code = "exists %s." % ( ','.join(map(lambda e: e.name,rule_dec.exists)) )
			# sys.stdout.write("Here: %s" % exists_code)

		zero_nr_code = template('''
			predicate {| rule_name |}_req    :: ({| xs_types |}) -> fact.
			predicate {| rule_name |}_match  :: ({| rs_types |}) -> fact.
			predicate {| rule_name |}_commit :: ({| rs_types |}) -> fact.

			rule {| rule_name |}1  :: {| x_prop_heads |},{| x_simp_heads |} \ 1 {| x_guards |} --o [{| y_loc |}]{| rule_name |}_req({| xs_args |}).
			rule {| rule_name |}2  :: {| match_rule |}
			rule {| rule_name |}3  :: {| x_prop_heads |},{| x_simp_heads |},[{| x_loc |}]{| rule_name |}_match({| rs_args |}) --o [{| y_loc |}]{| rule_name |}_commit({| rs_args |}).
			rule {| rule_name |}4a :: {| y_prop_heads |} \ [{| y_loc |}]{| rule_name |}_commit({| rs_args |}),{| y_simp_heads |} --o {| exists_code |} {| x_prop_heads |},{| rule_body |}.
			rule {| rule_name |}4b :: [{| y_loc |}]{| rule_name |}_commit({| rs_args |}) --o {| x_prop_heads |},{| x_simp_heads |}.
		''')

		zero_nr_rules = compact( compile_template(zero_nr_code, match_rule=match_rule, rule_name=rule_dec.name, x_loc=x, y_loc=y, xs_args=xs, rs_args=rs
                                                         ,x_guards=x_guards, y_guards=y_guards, x_simp_heads=x_simp_heads, y_simp_heads=y_simp_heads
                                                         ,x_prop_heads=x_prop_heads, y_prop_heads=y_prop_heads, exists_code=exists_code, rule_body=rule_body
                                                         ,xs_types=xs_types, rs_types=rs_types) )
		
		# print zero_nr_rules

		msr_code_gen = MSRCodeGen("", bypass_checkers=True, input=zero_nr_rules)

		trans_decs = msr_code_gen.decs

		for dec in trans_decs:
			dec.add_trans_snippet( dec.gen_snippet( zero_nr_rules ) )

		lead_rule_snippet = "One Neighbor Restriction translation applied.\n\nSource rule:\n%s\n\n" % rule_dec.gen_snippet( self.source_text )
		lead_rule_snippet += "Generated fragment:\n%s\n\n" % zero_nr_rules
		lead_rule_snippet += trans_decs[0].gen_snippet( zero_nr_rules )
		trans_decs[0].add_trans_snippet( lead_rule_snippet )

		trans_decs[len(trans_decs)-2].where = rule_dec.where

		return trans_decs

