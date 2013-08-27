
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


def take(a,i):
	return a[:i]

def drop(a,i):
	return a[i:]

def take_half(a):
	return a[:(len(a)/2)]

def drop_half(a):
	return a[(len(a)/2):]

def first(a):
	return a[0]

def median(a):
	return a[len(a)/2]

def partition(a,m):
	l = []
	g = []
	for i in a:
		if i <= m:
			l.append(i)
		else:
			g.append(i)
	return (l,g)

def merge(a,b):
	a_i = 0
	b_i = 0
	c = []
	while True:
		if a_i >= len(a):
			c += b[b_i:]
			break
		if b_i >= len(b):
			c += a[a_i:]
			break
		if a[a_i] < b[b_i]:
			c.append(a[a_i])
			a_i += 1
		else:
			c.append(b[b_i])
			b_i += 1
	return c

def sort(a):
	return sorted(a)

def retrieve_mwoe(es):
	curr_min  = 1000000
	curr_mwoe = None
	for i,o,w in es:
		if w < curr_min:
			curr_mwoe = [i,o,w]
			curr_min  = w
	return curr_mwoe

def combine_out_edges(es1,es2):
	es3 = []
	for i,o,w in es1 + es2:
 		if o not in map(lambda e: e[0],es1 + es2):
			es3.append( [i,o,w] )
	return es3 

