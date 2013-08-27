
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

from msr_ensemble.front_end.parser.msr_lexer import *
from msr_ensemble.front_end.parser.msr_ast import *

import ply.lex
import ply.yacc as yacc

# Declarations

def p_declarations(p):
	'''
	declarations : declaration declarations
                     |
	'''
	if len(p) == 3:
		p[0] = [p[1]] + p[2]
	else:
		p[0] = []

def p_assign_declaration(p):
	'''
	declaration : assign_stmt STOP
	'''
	p[0] = p[1]

def p_declaration_scope(p):
	'''
	declaration : ENSEM NAME CLPAREN declarations CRPAREN
	'''
	# print p.linespan(0)
	# print p.lexspan(0)
	p[0] = EnsemDec(p[2],p[4],parse_frag=p)

# Extern Declarations

def p_declaration_extern(p):
	'''
	declaration : EXTERN mod_name extern_list
	'''
	p[0] = ExternDec(p[2],p[3],parse_frag=p)

def p_mod_name(p):
	'''
	mod_name : NAME STOP mod_name
                 | NAME
	'''
	if len(p) == 4:
		p[0] = p[1] + "." + p[3]
	else:
		p[0] = p[1]

def p_extern_list(p):
	'''
	extern_list : CLPAREN extern_elems CRPAREN 
                    | extern_elem STOP
	'''
	if len(p) == 4:
		p[0] = p[2]
	else:
		p[0] = [p[1]]

def p_extern_elems(p):
	'''
	extern_elems : extern_elem COMMA extern_elems
                     | extern_elem
	'''
	if len(p) == 4:
		p[0] = [p[1]] + p[3]
	else:
		p[0] = [p[1]]

def p_extern_elem(p):
	'''
	extern_elem : NAME COLON COLON type 
	'''
	p[0] = (p[1],p[4])

# Type Declarations


def p_declaration_fact(p):
	'''
	declaration : PRED NAME COLON COLON FACT STOP
                    | PRED NAME COLON COLON type ARROW FACT STOP
                    | PRED typemodifiers NAME COLON COLON FACT STOP
	            | PRED typemodifiers NAME COLON COLON type ARROW FACT STOP
	'''
	# print p.linespan(0)
	# print p.lexspan(0)
	if len(p) == 7:
		p[0] = FactDec([],p[2],None,parse_frag=p)
	elif len(p) == 9:
		p[0] = FactDec([],p[2],p[5],parse_frag=p)
	elif len(p) == 8:
		p[0] = FactDec(p[2],p[3],None,parse_frag=p)
	else:
		p[0] = FactDec(p[2],p[3],p[6],parse_frag=p)

# Location Declarations

def p_declaration_init(p):
	'''
	declaration : EXEC NAME WITH loc_name_list CLPAREN declarations CRPAREN
	'''
	p[0] = ExecDec(p[2],p[4],p[6],parse_frag=p)

def p_loc_name_list(p):
	'''
	loc_name_list : NAME COMMA loc_name_list
                      | NAME
	'''
	if len(p) == 4:
		p[0] = [p[1]] + p[3]
	else:
		p[0] = [p[1]]

def p_declaration_loc(p):
	'''
	declaration : INIT NAME COLON COLON fact_list STOP
	'''
	p[0] = InitDec(p[2],p[5],parse_frag=p)

def p_fact_list(p):
	'''
	fact_list : fact COMMA fact_list
	          | fact
	'''
	if len(p) == 4:
		p[0] = [p[1]] + p[3]
	else:
		p[0] = [p[1]]

# Rule Declarations

def p_declaration_rule(p):
	'''
	declaration : RULE NAME COLON COLON rule_lhs IMPLIES exists_dec rule_rhs STOP
                    | RULE NAME COLON COLON rule_lhs IMPLIES exists_dec rule_rhs WHERE assign_stmts STOP
	'''
	if len(p) == 10:
		p[0] = RuleDec(p[2],p[5],p[8],exists=p[7],parse_frag=p)
	else:
		p[0] = RuleDec(p[2],p[5],p[8],where=p[10],exists=p[7],parse_frag=p)

def p_exists_dec(p):
	'''
	exists_dec : EXISTS var_list STOP
                   |
	'''
	if len(p) == 4:
		p[0] = p[2]
	else:
		p[0] = []

def p_assign_stmts(p):
	'''
	assign_stmts : assign_stmt COMMA assign_stmts
	             | assign_stmt
	'''
	if len(p) == 4:
		p[0] = [p[1]] + p[3]
	else:
		p[0] = [p[1]]

def p_assign_stmt(p):
	'assign_stmt : term ASSIGN term'
	p[0] = AssignDec(p[1],p[3],parse_frag=p)	

def p_var_list(p):
	'''
	var_list : var_atom COMMA var_list
	         | var_atom
	'''
	if len(p) == 4:
		p[0] = [p[1]] + p[3]
	else:
		p[0] = [p[1]]

def p_var(p):
	'''
	var_atom : VARIABLE
	'''
	p[0] = TermVar(p[1],parse_frag=p)

def p_location_var(p):
	'location : VARIABLE'
	p[0] = TermVar(p[1],parse_frag=p)

def p_location_name(p):
	'location : NAME'
	p[0] = TermCons(p[1],parse_frag=p)

def p_location_lit(p):
	'location : INT'
	p[0] = TermLit(p[1],parse_frag=p)

def p_rule_lhs(p):
	'''
	rule_lhs : rule_heads
                 | rule_heads WITH rule_heads
                 | rule_heads SUCH THAT lhs_guards
                 | rule_heads WITH rule_heads SUCH THAT lhs_guards
	'''
	if len(p) == 2:
		p[0] = (p[1],[],[])
	elif len(p) == 4:
		p[0] = (p[1],p[3],[])
	elif len(p) == 5:
		p[0] = (p[1],[],p[4])		
	else:
		p[0] = (p[1],p[3],p[6])

def p_rule_chr_lhs(p):
	'''
	rule_lhs : rule_heads BACK rule_heads
                 | rule_heads BACK rule_heads BAR lhs_guards
	'''
	if len(p) == 4:
		p[0] = (p[3],p[1],[])
	else:
		p[0] = (p[3],p[1],p[5])
		
def p_rule_chr_lhs_2(p):
	'''
	rule_lhs : rule_heads BAR lhs_guards
	'''
	p[0] = (p[1],[],p[3])

def p_rule_heads(p):
	'''
	rule_heads : lhs_pat COMMA rule_heads
                   | lhs_pat  
	'''
	if len(p) == 4:
		if p[1] != None:
			p[0] = [p[1]] + p[3]
		else:
			p[0] = p[3]
	else:
		if p[1] != None:
			p[0] = [p[1]]
		else:
			p[0] = []

def p_rule_heads_one(p):
	'''
	rule_heads : INT
	'''
	p[0] = []

def p_lhs_fact(p):
	'lhs_pat : loc_fact'
	p[0] = LHSFact(p[1],parse_frag=p)

def p_lhs_none(p):
	'lhs_pat : INT'
	p[0] = None

def p_lhs_guard(p):
	'''
	lhs_guards : term COMMA lhs_guards
                   | term
	'''
	if len(p) == 4:
		p[0] = [p[1]] + p[3]
	else:
		p[0] = [p[1]]

def p_rule_rhs(p):
	'''
	rule_rhs : rhs_pat COMMA rule_rhs
	         | rhs_pat
	'''
	if len(p) == 4:
		if p[1] != None:
			p[0] = [p[1]] + p[3]
		else:
			p[0] = p[3]
	else:
		if p[1] != None:
			p[0] = [p[1]]
		else:
			p[0] = []	

def p_rule_rhs_one(p):
	'rule_rhs : INT'
	p[0] = []

def p_rhs_fact(p):
	'rhs_pat : loc_fact'
	p[0] = RHSFact(p[1],parse_frag=p)

def p_rhs_fact_priority(p):
	'rhs_pat : loc_fact PRIORITY INT'
	p[1].priority = p[3]
	p[0] = RHSFact(p[1],parse_frag=p)

def p_rhs_none(p):
	'rhs_pat : INT'
	p[0] = None

def p_rhs_set_comprehension(p):
	'rhs_pat : CLPAREN loc_fact_list BAR term IN term CRPAREN'
	p[0] = RHSSetComp(SetComprehension(p[2],p[4],p[6],parse_frag=p),parse_frag=p)

def p_loc_fact(p):
	'''
	loc_fact : fact
                 | SLPAREN location SRPAREN fact
                 | SLPAREN location SRPAREN RLPAREN loc_fact_list RRPAREN 
	'''
	if len(p) == 2:
		p[0] = p[1]
	elif len(p) == 5:
		p[0] = FactLoc(p[2],[p[4]],parse_frag=p)
	else:
		p[0] = FactLoc(p[2],p[5],parse_frag=p)

def p_loc_fact_list(p):
	'''
	loc_fact_list : loc_fact COMMA loc_fact_list
	              | loc_fact
	'''
	if len(p) == 4:
		p[0] = [p[1]] + p[3]
	else:
		p[0] = [p[1]]


def p_fact(p):
	'''
	fact : NAME RLPAREN termargs RRPAREN
             | NAME RLPAREN RRPAREN 
	'''
	if len(p) == 5:
		p[0] = FactBase(p[1],p[3],parse_frag=p)
	else:
		p[0] = FactBase(p[1],[],parse_frag=p)

def p_termargs(p):
	"""
	termargs : term
	         | term COMMA termargs
	"""
	if len(p) == 2:
		p[0] = [p[1]]
	else:
		p[0] = [p[1]] + p[3]

def p_term_std(p):
	"""
	term : simp_term
             | simp_term term
	"""
	if len(p) == 2:
		p[0] = p[1]
	else:
		p[0] = TermApp(p[1],p[2],parse_frag=p)

def p_term_op(p):
	"""
	term : simp_term term_binop simp_term
	     | term_unaryop simp_term
	"""
	if len(p) == 4:
		p[0] = TermBinOp(p[1],p[2],p[3],parse_frag=p)
	else:
		p[0] = TermUnaryOp(p[1],p[2],parse_frag=p)

def p_term_binop(p):
	'''
	term_binop : NEQ
	           | EQUAL
	           | LEQ
	           | GEQ
	           | TLPAREN
	           | TRPAREN
	           | PLUS
	           | MINUS
	           | TIMES
	           | DIV
	           | COLON
	''' 
	p[0] = p[1]

def p_term_unary_op(p):
	'term_unaryop : BANG'
	p[0] = p[1]

def p_simp_term_tuple(p):
	'''
	simp_term : RLPAREN termargs RRPAREN
	          | RLPAREN RRPAREN
	'''
	if len(p) == 4:
		p[0] = TermTuple(p[2],parse_frag=p)
	else:
		p[0] = TermTuple([],parse_frag=p)
		

def p_simp_term_list(p):
	'''
	simp_term : SLPAREN termargs SRPAREN
	          | SLPAREN SRPAREN
	'''
	if len(p) == 4:
		p[0] = TermList(p[2],parse_frag=p)
	else:
		p[0] = TermList([],parse_frag=p)

def p_simp_term_brackets(p):
	'simp_term : RLPAREN term RRPAREN'
	p[0] = p[2]

def p_simp_term_underscore(p):
	'simp_term : UNDERSCORE'
	p[0] = TermUnderscore(parse_frag=p)

def p_simp_term_cons(p):
	'simp_term : NAME'
	p[0] = TermCons(p[1],parse_frag=p) 

def p_simp_term_var(p):
	'simp_term : VARIABLE'
	p[0] = TermVar(p[1],parse_frag=p)

def p_simp_term_others(p):
	'''
	simp_term : FLOAT
	          | INT
                  | STRING
	          | CHAR
	'''
	p[0] = TermLit(p[1],parse_frag=p)

# Builtin Exp

def p_builtin_exp(p):
	'''
	builtin_exp : simp_builtin_exp
	            | simp_builtin_exp builtin_binop simp_builtin_exp
                    | builtin_unaryop simp_builtin_exp
	'''
	if len(p) == 2:
		p[0] = p[1]
	elif len(p) == 4:
		p[0] = BuiltinBinOp(p[1],p[2],p[3],parse_frag=p)
	else:
		p[0] = BuiltinUnaryOp(p[1],p[2],parse_frag=p)

def p_builtin_binop(p):
	'''
	builtin_binop : NEQ
	              | EQUAL
	              | LEQ
	              | GEQ
	              | TLPAREN
	              | TRPAREN
	              | PLUS
	              | MINUS
	              | TIMES
	              | DIV
	              | COLON
	''' 
	p[0] = p[1]

def p_builtin_unaryop(p):
	'''
	builtin_unaryop : BANG
	'''
	p[0] = p[1]

def p_simp_builtin_exp_func(p):
	'simp_builtin_exp : NAME RLPAREN builtin_args RRPAREN'
	p[0] = BuiltinFunCall(p[1],p[3],parse_frag=p)

def p_simp_builtin_exp_bracket(p):
	'simp_builtin_exp : RLPAREN builtin_exp RRPAREN'
	p[0] = p[2]

def p_simp_builtin_exp_var(p):
	'simp_builtin_exp : VARIABLE'
	p[0] = BuiltinVar(p[1],parse_frag=p)

def p_simp_builtin_exp_others(p):
	'''
	simp_builtin_exp : FLOAT
	                 | INT
                         | STRING
	                 | CHAR
	'''
	p[0] = BuiltinLit(p[1],parse_frag=p)

def p_builtin_args(p):
	'''
	builtin_args : builtin_exp COMMA builtin_args
                     | builtin_exp
	             |
	'''
	if len(p) == 4:
		p[0] = [p[1]] + p[3]
	elif len(p) == 2:
		p[0] = [p[1]]
	else:
		p[0] = []

# Types

'''
def p_externtype(p):
	"""
	externtype : NAME RLPAREN typeargs RRPAREN
	"""
	p[0] = ExternType(p[1],p[3])
'''

def p_typemodifiers(p):
	"""
	typemodifiers : NAME
	              | typemodifiers NAME
	"""	
	if len(p) == 2:
		p[0] = [p[1]]
	else:
		p[0] = p[1] + [p[2]]

'''
def p_facttype(p):
	"""
	facttype : NAME RLPAREN typeargs RRPAREN
	"""
	p[0] = FactType(p[1],p[3])
'''

def p_typeargs(p):
	"""
	typeargs : type
	         | type COMMA typeargs
	"""
	if len(p) == 2:
		p[0] = [p[1]]
	else:
		p[0] = [p[1]] + p[3]

def p_type(p):
	"""
	type : singletype
	     | singletype type
	"""
	if len(p) == 2:
		p[0] = p[1]
	else:
		p[0] = TypeApp(p[1],p[2],parse_frag=p)

def p_singletype_func(p):
	'singletype : type ARROW type'
	p[0] = TypeArrow(p[1],p[3],parse_frag=p)

def p_singletype_tuple(p):
	'singletype : RLPAREN typeargs RRPAREN'
	p[0] = TypeTuple(p[2],parse_frag=p) 

def p_singletype_list(p):
	'singletype : SLPAREN type SRPAREN'
	p[0] = TypeList(p[2],parse_frag=p)

def p_singletype_brackets(p):
	'singletype : RLPAREN type RRPAREN'
	p[0] = p[2]
	
def p_singletype_cons(p):
	'singletype : NAME'
	p[0] = TypeCons(p[1],parse_frag=p)

def p_singletype_var(p):
	'singletype : VARIABLE'
	p[0] = TypeVar(p[1],parse_frag=p)


def p_error(p):
    raise TypeError("unknown text at %r" % (p.value,))

'''
lex.lex()

# f = open('test.msr')
f = open('hyper_quick_sort.msr')
# lex.input("type a . a(X,1,1.03),b(X,Y,\" sadfs+\") == -o = c(X,Y/X-).")
#lex.input(f.read())

lex.input(f.read())

for tok in iter(lex.token, None):
    print repr(tok.type), repr(tok.value)

f = open('hyper_quick_sort.msr')
# f = open('test.msr')

yacc.yacc()

ast = yacc.parse(f.read())

for n in ast:
	print str(n)
'''

def run_parser(file):
	lex.lex()
	f = open(file)
	yacc.yacc()
	input = f.read()
	# print "\033[41m" + input[94:134] + "\033[0m Ha ha"
	ast = yacc.parse(input, tracking=True)
	return (input, ast)

def run_parser_input(input):
	ast = yacc.parse(input, tracking=True)
	return ast


