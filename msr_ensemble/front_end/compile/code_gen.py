
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
import msr_ensemble.front_end.parser.msr_parser as p
import msr_ensemble.misc.visit as visit

from msr_ensemble.front_end.compile.checkers.var_scope_checker import VarScopeChecker
from msr_ensemble.front_end.compile.checkers.neighbor_restrict_checker import NeighborRestrictChecker
from msr_ensemble.front_end.compile.checkers.base_checker import Checker, get_source_header_footer_regions

from msr_ensemble.front_end.compile.inspectors import Inspector

# from msr_ensemble.front_end.compile.transformers.neighbor_restrict_trans import NeighborRestrictTrans

from msr_ensemble.misc.template import template, compile_template, compact

# Code Generation procedures here assumes valid AST inputs that has been type checked and processed by type_checker.py
# TODO:
#   - Currently accepts only "flatly" scoped input: All declarations are within one 'ensem' block.


# Base Generator class
class CodeGen:
	def initialize(self, source_text=None):
		self.var_count   = 0
		self.source_text = source_text
	def next_var(self):
		self.var_count += 1
		x = self.var_count
		return "x%s" % x	
	def next_vars(self, i):
		xs = []
		for _ in range(0,i):
			xs.append(self.next_var())
		return xs
	def get_source_snippet(self, start_idx, end_idx):
		return self.source_text[start_idx:end_idx]

# Top Level Code Generation
class MSRCodeGen(CodeGen):

	def __init__(self, file_name, bypass_checkers=False, input=None):
		if input == None:
			self.file_name = file_name
			(source_text, decs) = p.run_parser(file_name)
			self.decs = decs
			self.initialize(source_text)
			if not bypass_checkers:
				self.check_validity(decs, source_text)
			else:
				self.error_reports = []
		else:
			decs = p.run_parser_input(input)
			self.decs = decs
			self.initialize(input)
			if not bypass_checkers:
				self.check_validity(decs, input)
			else:
				self.error_reports = []

	def check_validity(self, decs, source_text):
		checkers = [VarScopeChecker,NeighborRestrictChecker]
		reports = []
		for checker in checkers:
			c = checker(decs,source_text)
			c.check()
			c.init_build_display_regions()
			reports += c.get_error_reports()
		self.error_reports = reports

	def has_errors(self):
		return len(self.error_reports) > 0

	# Retrieve Init Declarations

	@visit.on('ast_node')
	def each_dec(self, ast_node):
		pass

	@visit.when(ast.EnsemDec)
	def each_dec(self, ast_node):
		return ([ast_node],[])

	@visit.when(ast.ExecDec)
	def each_dec(self, ast_node):
		return ([],[ast_node])

	@visit.when(ast.ASTNode)
	def each_dec(self, ast_node):
		return None

	def get_decs(self):
		ensems = []
		execs  = [] 
		for dec in self.decs:
			ret = self.each_dec(dec)
			if not isinstance(ret, list):
				(ensem,exe) = ret
				ensems += ensem
				execs  += exe	
		return { 'ensems':ensems, 'execs':execs }

	'''
	def trans(self):
		znr_decs = NeighborRestrictTrans(self.decs, self.source_text).trans()
	'''

	def gen_code(self):

		decs = self.get_decs()

		for ensem in decs['ensems']:
			EnsemDecCodeGen(ensem, self.source_text).gen_code()
			print "Output written to %s.py" % ensem.name

		for exe in decs['execs']:
			ExecDecCodeGen(exe).gen_code( mk_py_file_name(self.file_name) )
			print "Output written to %s" % mk_py_file_name(self.file_name)


# Generating Ensemble
class EnsemDecCodeGen(CodeGen):

	def __init__(self, ensem_dec, source_text):
		self.initialize(source_text)
		self.ensem_dec = ensem_dec

	# Retrieve Fact Declarations

	@visit.on('ast_node')
	def fact_dec(self, ast_node):
		pass

	@visit.when(ast.FactDec)
	def fact_dec(self, ast_node):
		return ast_node

	@visit.when(ast.ASTNode)
	def fact_dec(self, ast_node):
		return None

	def get_fact_decs(self):
		fs = []
		for dec in self.ensem_dec.decs:
			f = self.fact_dec(dec)
			if not isinstance(f, list):
				fs.append(f)	
		return fs
		
	# Retrieve Rule Declarations

	@visit.on('ast_node')
	def rule_dec(self, ast_node):
		pass

	@visit.when(ast.RuleDec)
	def rule_dec(self, ast_node):
		return ast_node

	@visit.when(ast.ASTNode)
	def rule_dec(self, ast_node):
		return None

	def get_rule_decs(self):
		fs = []
		for dec in self.ensem_dec.decs:
			f = self.rule_dec(dec)
			if not isinstance(f, list):
				fs.append(f)	
		return fs

	# Retrieve Assign Declarations

	@visit.on('ast_node')
	def assign_dec(self, ast_node):
		pass

	@visit.when(ast.AssignDec)
	def assign_dec(self, ast_node):
		return ast_node

	@visit.when(ast.ASTNode)
	def assign_dec(self, ast_node):
		return None

	def get_assign_decs(self):
		fs = []
		for dec in self.ensem_dec.decs:
			f = self.assign_dec(dec)
			if not isinstance(f, list):
				fs.append(f)	
		return fs

	# Retrieve Extern Declarations

	@visit.on('ast_node')
	def extern_dec(self, ast_node):
		pass

	@visit.when(ast.ExternDec)
	def extern_dec(self, ast_node):
		return ast_node

	@visit.when(ast.ASTNode)
	def extern_dec(self, ast_node):
		return None

	def get_extern_decs(self):
		fs = []
		for dec in self.ensem_dec.decs:
			f = self.extern_dec(dec)
			if not isinstance(f, list):
				fs.append(f)	
		return fs

	# Generating Code

	def gen_code(self):

		extern_codes = []
		for e in self.get_extern_decs():
			extern_codes.append( ExternDecCodeGen(e).gen_code() )

		fact_dec_codes = []
		fs = self.get_fact_decs()
		for f in fs:
			fact_dec_codes.append( FactDecCodeGen(f, self.source_text).gen_code() )

		rule_names = []
		rule_dec_codes = []
		rs = self.get_rule_decs()
		for r in rs:
			rule_dec_codes.append( RuleDecCodeGen(r, self.source_text).gen_code() )
			rule_names.append( mk_rule_name(r.name) )

		assign_dec_codes = []
		ass = self.get_assign_decs()
		for a in ass:
			assign_dec_codes.append( AssignDecCodeGen(a).gen_code() )

		import_list = template('''
			from msr_ensemble.facts.fact import Fact, get_all_fact_classes

			from msr_ensemble.facts.term import Term, new_vars, lift, val, inst, _
			from msr_ensemble.facts.fact import Fact, register_fact, at, priority
			from msr_ensemble.facts.guard import Guard
			
			from msr_ensemble.rules.rule import Rule, register_rule

			from msr_ensemble.context.store import FactStore, pretty_stores
		''')

		ensem_code = template('''
			{| import_list |}

			{| '\\n'.join(extern_codes) |}

			{| '\\n'.join(assign_dec_codes) |}

			{| '\\n'.join(fact_dec_codes) |}

			{| '\\n\\n'.join(rule_dec_codes) |}

			{| ensem_name |}_rule_classes = [{| ', '.join(rule_names) |}]
		''') 

		output = open(self.ensem_dec.name + ".py", 'w')
		output.write( compile_template(ensem_code, fact_dec_codes=fact_dec_codes, rule_dec_codes=rule_dec_codes, import_list=import_list
                                              ,ensem_name=self.ensem_dec.name, rule_names=rule_names, assign_dec_codes=assign_dec_codes
                                              ,extern_codes=extern_codes ) )

# Generating Execution
class ExecDecCodeGen(CodeGen):

	def __init__(self, exec_dec):
		self.initialize()
		self.exec_dec = exec_dec

	# Retrieve Init Declarations

	@visit.on('ast_node')
	def init_dec(self, ast_node):
		pass

	@visit.when(ast.InitDec)
	def init_dec(self, ast_node):
		return ast_node

	@visit.when(ast.ASTNode)
	def init_dec(self, ast_node):
		return None

	def get_init_decs(self):
		inits = []
		for dec in self.exec_dec.decs:
			init = self.init_dec(dec)
			if not isinstance(init, list):
				inits.append(init)	
		return inits

	# Retrieve Assign Declarations

	@visit.on('ast_node')
	def assign_dec(self, ast_node):
		pass

	@visit.when(ast.AssignDec)
	def assign_dec(self, ast_node):
		return ast_node

	@visit.when(ast.ASTNode)
	def assign_dec(self, ast_node):
		return None

	def get_assign_decs(self):
		fs = []
		for dec in self.exec_dec.decs:
			f = self.assign_dec(dec)
			if not isinstance(f, list):
				fs.append(f)	
		return fs

	# Retrieve Extern Declarations

	@visit.on('ast_node')
	def extern_dec(self, ast_node):
		pass

	@visit.when(ast.ExternDec)
	def extern_dec(self, ast_node):
		return ast_node

	@visit.when(ast.ASTNode)
	def extern_dec(self, ast_node):
		return None

	def get_extern_decs(self):
		fs = []
		for dec in self.exec_dec.decs:
			f = self.extern_dec(dec)
			if not isinstance(f, list):
				fs.append(f)	
		return fs

	def gen_code(self, file_name):
		ensem_name = self.exec_dec.name

		extern_dec_codes = []
		for e in self.get_extern_decs():
			extern_dec_codes.append( ExternDecCodeGen(e).gen_code() )

		import_list = compile_template( template('''
			from msr_ensemble.interpret.mpi_runtime import execute_msr
			from msr_ensemble.facts.location import loc

			{| '\\n'.join( extern_dec_codes ) |}

			from {| ensem_name |} import *
		'''), ensem_name=ensem_name, extern_dec_codes=extern_dec_codes)

		assign_dec_codes = []
		for a in self.get_assign_decs():
			assign_dec_codes.append( AssignDecCodeGen(a).gen_code() )		

		locs = {}
		for loc in self.exec_dec.locs:
			locs[loc] = []

		for init in self.get_init_decs():
			loc = init.name
			fact_strs = []
			for fact in init.facts:
				fact_strs.append( LocFactCodeGen(ast.FactLoc(ast.TermCons(loc),[fact])).gen_code() )
			locs[loc] = ', '.join(fact_strs)

		count = 0
		loc_assigns    = []
		loc_inits      = []
		loc_init_names = []
		for loc in locs:
			loc_assigns.append( "%s = lift(loc(%s))" % (loc,count) )
			loc_inits.append( "init_%s = [%s]" % (loc,locs[loc]) )
			loc_init_names.append( "init_%s" % loc )
			count += 1

		exec_dec_code = template('''
			{| import_list |}

			{| '\\n'.join(assign_dec_codes) |}

			{| '\\n'.join(loc_assigns) |}

			{| '\\n'.join(loc_inits) |}

			init_goals = {| ' + '.join(loc_init_names) |}

			execute_msr(init_goals, {| ensem_name |}_rule_classes)
		''')

		output = open(file_name, 'w')

		output.write( compile_template(exec_dec_code, ensem_name=ensem_name, loc_assigns=loc_assigns, loc_inits=loc_inits
                                              ,loc_init_names=loc_init_names, import_list=import_list, assign_dec_codes=assign_dec_codes) )

# generating External Dec
class ExternDecCodeGen(CodeGen):

	def __init__(self, extern_dec):
		self.initialize()
		self.extern_dec = extern_dec

	def gen_code(self):
		
		extern_funcs = []
		for (name,type) in self.extern_dec.type_sigs:
			extern_funcs.append( name )

		extern_code = template('''
			from {| extern_mod_name |} import {| ','.join(extern_funcs) |} 
		''')

		return compile_template(extern_code, extern_mod_name=self.extern_dec.name, extern_funcs=extern_funcs)

# Generating Assign
class AssignDecCodeGen(CodeGen):
	
	def __init__(self, assign_dec):
		self.initialize()
		self.assign_dec = assign_dec

	@visit.on('term_pat')
	def get_exp_wrapper(self, term_pat):
		pass

	@visit.when(ast.TermCons)
	def get_exp_wrapper(self, term_pat):
		return "lift(%s)"

	@visit.when(ast.TermVar)
	def get_exp_wrapper(self, term_pat):
		return "lift(%s)"

	@visit.when(ast.TermTuple)
	def get_exp_wrapper(self, term_pat):
		# Assumes that term tuples are flat, i.e. all elements of the tuple are term constants
		return "tuple(map(lift,%s))"

	@visit.when(ast.TermList)
	def get_exp_wrapper(self, term_pat):
		# Assumes that term lists are flat, i.e. all elements of the list are term constants
		return "map(lift,%s)"

	# Generating Assign decs
	def gen_code(self):
		term_str = TermCodeGen(self.assign_dec.term_pat).gen_code(IGNORE, inner=IGNORE)
		# bexp_str = BuiltinExpCodeGen(self.assign_dec.builtin_exp).gen_code()
		bexp_str = TermCodeGen(self.assign_dec.builtin_exp).gen_code(IGNORE)

		return term_str + " = " + (self.get_exp_wrapper(self.assign_dec.term_pat) % bexp_str)


# Generating Fact 
class FactDecCodeGen(CodeGen):

	def __init__(self, fact_dec, source_text):
		self.initialize(source_text)
		self.fact_dec = fact_dec

	# Counting the number of term arguments for given fact declaration

	@visit.on('ast_node')
	def count_terms(self, ast_node):
		pass

	@visit.when(ast.FactDec)
	def count_terms(self, ast_node):
		if ast_node.type == None:
			return 0
		c = self.count_terms(ast_node.type)
		if isinstance(c, list):
			return c[0]
		else:
			return c

	@visit.when(ast.TypeTuple)
	def count_terms(self, ast_node):
		return len(ast_node.types)

	@visit.when(ast.ASTNode)
	def count_terms(self, ast_node):
		return 1

	# Generating Fact Declarations

	def gen_code(self):
		num_of_terms = self.count_terms(self.fact_dec)		
		terms = self.next_vars(num_of_terms)
		fact_dec_code = template('''
			\'\'\'
			{| source_snippet |}
			\'\'\'
			class {|fact_name|}(Fact):
				def __init__(self, {| ', '.join(terms) |}):
					self.initialize({| ', '.join(terms) |})
			register_fact({|fact_name|})
		''')
	
		source_snippet = self.fact_dec.gen_snippet(self.source_text)

		return compile_template(fact_dec_code, fact_name=pred_name(self.fact_dec.name), terms=terms
                                       ,source_snippet=source_snippet)

# Generating Terms:

IGNORE = -1
TERM_LEVEL = 0
META_LEVEL = 1

class TermCodeGen(CodeGen):

	def __init__(self, term):
		self.initialize()
		self.term = term


	@visit.on('term')
	def gen_term_code(self, term, inner=META_LEVEL):
		pass

	@visit.when(ast.TermUnderscore)
	def gen_term_code(self, term, inner=META_LEVEL):
		return (TERM_LEVEL, "_")

	@visit.when(ast.TermLit)
	def gen_term_code(self, term, inner=META_LEVEL):
		return (META_LEVEL, term.literal)

	@visit.when(ast.TermCons)
	def gen_term_code(self, term, inner=META_LEVEL):
		return (TERM_LEVEL, term.name)

	@visit.when(ast.TermVar)
	def gen_term_code(self, term, inner=META_LEVEL):
		return (TERM_LEVEL, var_name(term.name))

	@visit.when(ast.TermApp)
	def gen_term_code(self, term, inner=META_LEVEL):
		(gen_level1,term_str1) = self.gen_term_code(term.term1, inner=inner)
		(gen_level2,term_str2) = self.gen_term_code(term.term2, inner=inner)
		if term_str2[0] == '(':
			return (META_LEVEL, "%s %s" % ( coerce_term(term_str1,gen_level1,IGNORE) , coerce_term(term_str2,gen_level2,META_LEVEL) ))
		else:
			return (META_LEVEL, "%s (%s)" % ( coerce_term(term_str1,gen_level1,IGNORE) , coerce_term(term_str2,gen_level2,META_LEVEL) ))
			

	@visit.when(ast.TermTuple)		
	def gen_term_code(self, term, inner=META_LEVEL):
		term_strs = []
		for t in term.terms:
			(gen_level,term_str) = self.gen_term_code(t, inner=inner)		
			# term_strs.append( coerce_term(term_str, gen_level, TERM_LEVEL if not flatten else META_LEVEL) )
			term_strs.append( str( coerce_term(term_str, gen_level, inner) ) )
		return (META_LEVEL, "(%s)" % (','.join(term_strs)) )

	@visit.when(ast.TermList)
	def gen_term_code(self, term, inner=META_LEVEL):
		term_strs = []
		for t in term.terms:
			(gen_level,term_str) = self.gen_term_code(t, inner=inner)
			# term_strs.append( coerce_term(term_str, gen_level, TERM_LEVEL if not flatten else META_LEVEL) )
			term_strs.append( str( coerce_term(term_str, gen_level, inner) ) )
			# term_strs.append( str(term_str) )
		return (META_LEVEL, "[%s]" % (','.join(term_strs)) )

	@visit.when(ast.TermBinOp)
	def gen_term_code(self, term, inner=META_LEVEL):
		(gen_level1,term_str1) = self.gen_term_code(term.term1, inner=inner)
		(gen_level2,term_str2) = self.gen_term_code(term.term2, inner=inner)
		return (META_LEVEL, "%s %s %s" % ( coerce_term(term_str1,gen_level1,META_LEVEL), term.op, coerce_term(term_str2,gen_level2,META_LEVEL) ))

	@visit.when(ast.TermUnaryOp)
	def gen_term_code(self, term, inner=META_LEVEL):
		(gen_level,term_str) = self.gen_term_code(term.term, inner=inner)
		return (META_LEVEL, "%s %s" % ( term.op, coerce_term(term_str,gen_level,META_LEVEL) ))

	def gen_code(self, req_level=TERM_LEVEL, inner=META_LEVEL):
		(gen_level,term_str) = self.gen_term_code(self.term, inner=inner)
		return coerce_term(term_str, gen_level, req_level) 

# Generating Facts:
class LocFactCodeGen(CodeGen):

	def __init__(self, loc_fact):
		self.initialize()
		self.loc_fact = loc_fact

	'''
	# Generating term code

	@visit.on('term')
	def gen_term_code(self, term, lift=True, inst=False, drop=False):
		pass

	@visit.when(ast.TermCons)
	def gen_term_code(self, term, lift=True, inst=False, drop=False):
		return lift_name(term.name, lift)

	@visit.when(ast.TermVar)
	def gen_term_code(self, term, lift=False, inst=False, drop=False):
		if drop:
			return "val(%s)" % var_name(term.name)
		if not inst:
			return var_name(term.name)
		else:
			return "inst(%s)" % var_name(term.name)

	@visit.when(ast.TermApp)
	def gen_term_code(self, term, lift=True, inst=False, drop=False):
		term_str1 = self.gen_term_code(term.term1, lift=False, inst=False, drop=True)
		term_str2 = self.gen_term_code(term.term2, lift=False, inst=False, drop=True)
		return lift_name( "%s %s" % (term_str1,term_str2), lift)

	@visit.when(ast.TermTuple)
	def gen_term_code(self, term, lift=True, inst=False, drop=False):
		term_strs = map(lambda t: self.gen_term_code(t, lift=False, inst=inst, drop=drop) ,term.terms)
		return lift_name( "(%s)" % (','.join(term_strs)), lift )

	@visit.when(ast.TermList)
	def gen_term_code(self, term, lift=True, inst=False, drop=False):
		term_strs = map(lambda t: self.gen_term_code(t, lift=False, inst=inst, drop=drop) ,term.terms)
		return lift_name( "[%s]" % (','.join(term_strs)), lift)
	
	@visit.when(ast.TermBinOp)
	def gen_term_code(self, term, lift=True, inst=False, drop=False):
		term1_str = self.gen_term_code(term.term1, lift=False, inst=inst, drop=drop)
		term2_str = self.gen_term_code(term.term2, lift=False, inst=inst, drop=drop)
		return lift_name( "%s %s %s" % (term1_str, term.op, term2_str), lift )

	@visit.when(ast.TermUnaryOp)
	def gen_term_code(self, term, lift=True, inst=False, drop=False):
		term_str = self.gen_term_code(term.term, lift=False, inst=inst, drop=drop)
		return lift_name( "%s %s" % (term.op, term_str) )

	@visit.when(ast.TermLit)
	def gen_term_code(self, term, lift=True, inst=False, drop=False):
		return lift_name( "%s" % term.literal, lift)

	@visit.when(ast.TermUnderscore)
	def gen_term_code(self, term, lift=True, inst=False, drop=False):
		return "_" 
	'''
	# Code Generation

	def gen_code(self):
		loc  = self.loc_fact.loc
		fact = self.loc_fact.facts[0]
		priority = self.loc_fact.priority

		# loc_str   = self.gen_term_code(loc, inst=inst)
		loc_str = TermCodeGen(loc).gen_code(TERM_LEVEL)
		pred_str  = pred_name(fact.name)
		# term_strs = map(lambda t: self.gen_term_code(t, inst=inst), fact.terms)

		term_strs = []
		for term in fact.terms:
			 term_strs.append( TermCodeGen(term).gen_code(TERM_LEVEL) )

		fact_code = template("{| pred_str |}({| ','.join(term_strs) |}) |at| {| loc_str |}")

		gen_fact_code = compile_template(fact_code, pred_str=pred_str, term_strs=term_strs, loc_str=loc_str)

		if priority == 0:
			return gen_fact_code
		else:
			return "(%s) |priority| %s" % (gen_fact_code,priority)

# Generating Builtin Exp

class BuiltinExpCodeGen(CodeGen):

	def __init__(self, builtin_exp):
		self.initialize()
		self.builtin_exp = builtin_exp

	@visit.on('bexp')
	def gen_exp_code(self, bexp):
		pass

	@visit.when(ast.BuiltinFunCall)
	def gen_exp_code(self, bexp):
		arg_strs = map(lambda a: self.gen_exp_code(a),bexp.args)
		return "%s(%s)" % (bexp.name,','.join(arg_strs))

	@visit.when(ast.BuiltinVar)
	def gen_exp_code(self, bexp):
		return "val(%s)" % var_name(bexp.name)

	@visit.when(ast.BuiltinLit)
	def gen_exp_code(self, bexp):
		return "%s" % bexp.name

	@visit.when(ast.BuiltinBinOp)
	def gen_exp_code(self, bexp):
		bexp1_str = self.gen_exp_code(bexp.bexp1)
		bexp2_str = self.gen_exp_code(bexp.bexp2)
		return "%s %s %s" % (bexp1_str, bexp.op, bexp2_str)

	@visit.when(ast.BuiltinUnaryOp)
	def gen_exp_code(self, bexp):
		bexp_str = self.gen_exp_code(bexp.bexp)
		return "%s %s" % (bexp.op, bexp_str)

	def gen_code(self):
		# print self.builtin_exp
		return self.gen_exp_code(self.builtin_exp)

# Generating Rules

class RuleDecCodeGen(CodeGen):

	def __init__(self, rule_dec, source_text):
		self.initialize(source_text)
		self.rule_dec = rule_dec

	# Counting variables

	@visit.on('ast_node')
	def get_vars(self, ast_node):
		pass

	@visit.when(ast.TermCons)
	def get_vars(self, ast_node):
		return []

	@visit.when(ast.TermVar)
	def get_vars(self, ast_node):
		return [ast_node.name]

	@visit.when(ast.LHSFact)
	def get_vars(self, ast_node):
		return self.get_vars(ast_node.elem)

	@visit.when(ast.FactLoc)
	def get_vars(self, ast_node):
		vs = self.get_vars(ast_node.loc)
		for fact in ast_node.facts:
			# print fact
			for v in self.get_vars(fact):
				vs.append(v)
		return vs

	@visit.when(ast.FactBase)
	def get_vars(self, ast_node):
		vs = []
		for term in ast_node.terms:
			vs += self.get_vars(term)
		return vs

	@visit.when(ast.RuleDec)
	def get_vars(self, ast_node):
		simp_heads = ast_node.slhs
		prop_heads = ast_node.plhs
		exist_vars = ast_node.exists

		# print "HEheh!"

		var_dict = {}
		for simp_head in simp_heads:
			vs = self.get_vars(simp_head)
			for v in vs:
				# print v
				var_dict[v] = ()
		for prop_head in prop_heads:
			vs = self.get_vars(prop_head)
			for v in vs:
				# print "%s %s" % (prop_head.elem,v)
				var_dict[v] = ()
		return var_dict

	# Generate Fact Multisets

	def gen_facts(self, fs):

		fstr = []
		for f in fs:
			fstr.append( LocFactCodeGen(f).gen_code() )
		
		return fstr

	# Partitioning RHS

	def partition_rhs(self, rhs):
		atoms = []
		comps = []
		for f in rhs:
			if isinstance(f, ast.RHSFact):
				atoms.append( f )
			elif isinstance(f, ast.RHSSetComp):
				comps.append( f )
		return (atoms,comps)

	# Top Level Code Generation

	def gen_code(self):
		vars  = map(var_name, self.get_vars(self.rule_dec) )
		
		props = self.gen_facts( map(lambda f: f.elem, self.rule_dec.plhs) )
		simps = self.gen_facts( map(lambda f: f.elem, self.rule_dec.slhs) )
		grds  = map(lambda g: TermCodeGen(g).gen_code(IGNORE), self.rule_dec.grd)

		rhs_atoms,rhs_comps = self.partition_rhs(self.rule_dec.rhs)
		consq = self.gen_facts( map(lambda f: f.elem, rhs_atoms) )

		if len(rhs_comps) > 0:
			comp_set_names = []
			comp_codes = []
			comp_idx = 0
			for comp in rhs_comps:
				comp_facts = self.gen_facts( comp.elem.facts )
				term_pat   = TermCodeGen(comp.elem.term_pat).gen_code(IGNORE, inner=IGNORE)
				# term_subj  = TermCodeGen(comp.elem.term_subj).gen_code(META_LEVEL)
				term_subj = TermCodeGen(comp.elem.term_subj).gen_code(META_LEVEL)
				wrapper_pat = "lambda t: %s" % (AssignDecCodeGen(None).get_exp_wrapper(comp.elem.term_pat) % "t")
				term_subj =  "map(%s,%s)"  % (wrapper_pat ,term_subj)
				comp_set_name = "comp_set_%s" % comp_idx 
				comp_code = compile_template( template('''
					{| comp_set_name |} = []
					for {| term_pat |} in {| term_subj |}:
						{| comp_set_name |} += [{| ', '.join(comp_facts) |}]
				'''), term_pat=term_pat, term_subj=term_subj, comp_set_name=comp_set_name, comp_facts=comp_facts)
				comp_set_names.append( comp_set_name )
				comp_codes.append( comp_code )
				comp_idx += 1
			comp_set_post_fix = " + " + ' + '.join(comp_set_names)
		else:
			comp_codes = []
			comp_set_post_fix = ""

		wheres = []
		for assign in self.rule_dec.where:
			wheres.append( AssignDecCodeGen(assign).gen_code() )

		grd_class = ""
		grd_inst = ""
		if len(grds) > 0:
			grd_inst = mk_rule_name(self.rule_dec.name) + "Grd(%s)" % ','.join(vars)
			grd_class = compile_template(template(
				'''
				class {| grd_class_name |}(Guard):
					def __init__(self, {| ', '.join(vars) |}):
						self.initialize(\"{| grd_class_name |}\",{| ','.join(vars) |})
					def evaluate(self):
						{| ','.join(vars) |} = self.get_vars()
						return {| ' and '.join(grds) |}
				'''
			), grd_class_name=mk_rule_name(self.rule_dec.name) + "Grd", vars=vars, grds=grds)

	
		# Generate code to handle existential variables
		inspect = Inspector()

		exists_code = ""
		loc_exist_code = ""
		num_of_loc_exists = 0
		if len(self.rule_dec.exists) > 0:

			rule_rhs_locs = map(lambda v: v.name, inspect.filter_atoms( map(lambda a: inspect.get_loc(a.elem),rhs_atoms), var=True ) )
			
			loc_exists  = []
			pure_exists = []
			for exist_var in self.rule_dec.exists:
				if exist_var.name in rule_rhs_locs:
					loc_exists.append( exist_var.name )
				else:
					pure_exists.append( exist_var.name )

			if len(pure_exists) > 0:
				exists_code = "%s = self.exists(%s)" % (','.join(map(var_name,pure_exists)),len(pure_exists))
			if len(loc_exists) > 0:
				num_of_loc_exists = len(loc_exists)
				loc_exist_code = "%s, = self.exist_locs()" % (','.join(map(var_name,loc_exists)))

		rule_dec_code = template('''
			\'\'\'
			{| source_snippet |}
			\'\'\'
			class {| rule_name |}(Rule):
				def __init__(self):
					self.initialize(forall={| len(vars) |},exist_locs={| num_of_loc_exists |})
				def propagate(self):
					{| ','.join(vars) |} = self.get_vars()
					return [{| ', '.join(props) |}]
				def simplify(self):
					{| ','.join(vars) |} = self.get_vars()
					return [{| ', '.join(simps) |}]
				def guards(self):
					{| ','.join(vars) |} = self.get_vars()
					return [{| grd_inst |}]
				def consequents(self):
					{| ','.join(vars) |} = self.get_vars()
					{| exists_code |}
					{| loc_exist_code |}
					{| '\\n'.join(wheres) |}
					{| '\\n'.join(comp_codes) |}
					return [{| ', '.join(consq) |}] {| comp_set_post_fix |}
			register_rule({| rule_name |})
			 
			{| grd_class |}
		''')

		source_snippet = self.rule_dec.gen_snippet(self.source_text)

		output = compile_template(rule_dec_code, rule_name=mk_rule_name(self.rule_dec.name),source_snippet=source_snippet
                                         ,vars=vars, props=props, simps=simps, grd_class=grd_class, grd_inst=grd_inst, wheres=wheres
                                         ,consq=consq, exists_code=exists_code, loc_exist_code=loc_exist_code, num_of_loc_exists=num_of_loc_exists
                                         ,comp_codes=comp_codes, comp_set_post_fix=comp_set_post_fix)
	
		return compact(output)

# Auxiliary Helper Functions

def lift_name(name, lift):
	if lift:
		return "lift(%s)" % name
	else:
		return name

def var_name(name):
	return name.lower()

def pred_name(name):
	return name[0].upper() + name[1:].replace("_","")

def mk_rule_name(name):
	return name[0].upper() + name[1:].replace("_","")

def mk_py_file_name(file_name):
	return file_name.replace(".msr",".py")

def coerce_term(term_str, gen_level, req_level):
	if req_level == IGNORE:
		return term_str
	if gen_level == req_level:
		return term_str
	elif gen_level == TERM_LEVEL:
		return "val(%s)" % term_str
	else:
		return "lift(%s)" % term_str


