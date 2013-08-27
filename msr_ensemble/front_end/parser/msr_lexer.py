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

from ply import lex

reserved = { "module"    : "MODULE"
           , "extern"    : "EXTERN"
           , "fact"      : "FACT"
           , "predicate" : "PRED"
           , "in"     : "IN"
           , "where"  : "WHERE" 
           , "exists" : "EXISTS"
           , "rule"   : "RULE"
           , "with"   : "WITH"
           , "such"   : "SUCH"
           , "that"   : "THAT"
           , "init"   : "INIT"
           , "ensem"  : "ENSEM"
           , "execute"   : "EXEC"
           , "priority"  : "PRIORITY" }

tokens = [
	"IMPLIES",		# ==>
	"ARROW",                # ->
	"FLOAT",		# 1.0, 2.1, etc..
	"INT",			# 1, 2, etc..
	"STRING",		# "asd","..", etc..
	"CHAR",			# 'c','a',etc..
	"COMMA",		# , 
	"STOP",			# .
	"NEQ",			# !=
	"EQUAL",		# ==
	"LEQ",                  # <=
	"GEQ",			# >=
	"VARIABLE",		# A, B, etc..
	"NAME",			# a, b, etc..
	"RLPAREN",		# (
	"RRPAREN",		# )
	"SLPAREN",		# [
	"SRPAREN",		# ]
	"CLPAREN",		# {
	"CRPAREN",		# }
	"TLPAREN",		# <
	"TRPAREN",		# >
	# "MID",			# |
	"BANG",			# !
	"PLUS",			# +
	"MINUS",		# -
	"TIMES",		# *
	"DIV",			# /
	"COLON",		# :
	"ASSIGN",		# =
	"AT",			# @
	"UNDERSCORE",		# _
	"BACK",			# \
	"BAR",			# |
] + list(reserved.values())

t_ignore   = " \t\n"
t_ignore_COMMENT = r'\#.*'
t_AT       = r"@"
t_UNDERSCORE = r'\_'
t_IMPLIES = r'\-\-o'
t_ARROW = r'\->'

def t_FLOAT(t):
	r'[0-9][0-9]*\.[0-9][0-9]*'
	t.value = float(t.value)
	return t

def t_INT(t):
	r'[0-9][0-9]*'
	t.value = int(t.value)
	return t

t_STRING   = r'\"[a-zA-Z0-9_+ ]*\"'

t_CHAR = r'\'[a-zA-Z0-9_+ ]\'' 

t_NEQ      = r'!='
t_EQUAL    = r'=='
t_LEQ      = r'<='
t_GEQ      = r'>='

t_BAR      = r'\|'
t_BACK     = r'\\'
t_COMMA    = r','
t_STOP     = r'\.'
t_BANG     = r'!'
t_PLUS     = r'\+'
t_MINUS    = r'\-'
t_TIMES    = r'\*'
t_DIV      = r'/'
t_COLON    = r':'
t_VARIABLE = r'[A-Z][a-zA-Z0-9_]*'

def t_NAME(t):
	r'[a-z][a-zA-Z0-9_]*'
	t.type = reserved.get(t.value,'NAME')
	return t

t_RLPAREN  = r'\('
t_RRPAREN  = r'\)'
t_SLPAREN  = r'\['
t_SRPAREN  = r'\]'
t_TLPAREN  = r'<'
t_TRPAREN  = r'>'
t_CLPAREN  = r'\{'
t_CRPAREN  = r'\}'
t_ASSIGN   = r'='


