
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


from collections import defaultdict

from msr_ensemble.facts.term import Term
from msr_ensemble.facts.fact import Fact, get_all_fact_classes
from msr_ensemble.rules.rule import Rule, get_all_rule_classes
from msr_ensemble.context.store import FactStore, new_stores
from msr_ensemble.context.fact_repr import make_fact_pat

# interp_rules :: { <sym_id> : [<interp_rule>] }
# interp_rule  :: { 'rule_id':int, 'occ_id':int, 'propagated':bool, 'entry':<fact_pat>, 'match_steps':[<lookup_step>], 'has_no_simplify':bool, 'rhs': _ -> [<fact_pat>]  
#                 , 'exist_locs': _ -> [String], 'has_exist_locs':bool }
# match_step   :: { 'is_lookup':True, 'propagated':bool, 'lookup_index':int, 'fact_pat':<fact_pat>, 'filter':[Term] -> bool, 'free_terms':[Term] }
#              or { 'is_lookup':False, 'guard':_ -> bool, 'guard_str':str }
# fact_pat     :: { 'sym_id':int, 'terms':[Term] }

def interpret_rules(rules, fact_stores):
	interp_rules = defaultdict(list)

	for rule in rules:
		interp_rule = interpret_rule(rule, fact_stores)
		for rule_occ in interp_rule:
			interp_rules[rule_occ['entry']['sym_id']].append(rule_occ)

	for fact_sym_id in get_all_fact_classes():
		if fact_sym_id not in interp_rules:
			interp_rules[fact_sym_id] = []

	return interp_rules

def interpret_rule(rule, fact_stores):
	
	rule_entries = map(lambda s: (False,s),rule.simplify()) + map(lambda p: (True,p),rule.propagate())
	rule_lhs     = map(lambda t: t[1],rule_entries)
	guards       = rule.guards()
	variables    = rule.get_vars()

	if len(rule.simplify()) == 0:
		has_no_simplify = True
	else:
		has_no_simplify = False

	rule_name = get_all_rule_classes()[rule.rule_id].__name__

	interp_rule = []

	for i in xrange(0,len(rule_entries)):
		propagated,rule_entry = rule_entries[i]
		partners   = rule_entries[:i] + rule_entries[(i+1):]

		rule_entry.exist_bind_terms()
		early_guard_steps,guards_rest = schedule_guards(guards)
		match_steps = compute_optimal_matching(fact_stores, partners, guards_rest, early_guard_steps)
		for var in variables:
			var.unbind()

		interp_rule.append( { 'rule_id'         : rule.rule_id, 
                                      'occ_id'          : i,
                                      'propagated'      : propagated, 
                                      'entry'           : make_fact_pat(rule_entry), 
                                      'match_steps'     : match_steps,
                                      'has_no_simplify' : has_no_simplify,
                                      'rhs'             : rule.consequents,
                                      'exist_locs'      : rule.get_exist_locs,
                                      'has_exist_locs'  : len(rule.exist_locations) > 0 } )

	return interp_rule

def compute_optimal_matching(fact_stores, partners, guards, match_steps):
	if len(partners) == 0:
		return match_steps

	curr_max_score   = -100
	curr_guard_steps = []
	curr_guards_rest = []
	curr_best_partner = None
	curr_propagated = None
	curr_index = -1
	curr_free_terms = None

	for index in xrange(0,len(partners)):
		propagated,partner = partners[index]
		num_of_joins = 0
		num_of_free  = 0
		num_of_const = 0
		free_terms = []
		for term in partner.get_terms():
			if term.is_var():
				if term.is_binded():
					num_of_joins += 1
				else:
					free_terms.append(term)
					num_of_free += 1
			elif term.is_const():
				num_of_const += 1
		partner.exist_bind_terms()
		guard_steps,guards_rest = schedule_guards(guards)
		guard_count = len(guard_steps)
		new_max_score = num_of_joins*10 + guard_count + num_of_const - num_of_free
		if curr_max_score <= new_max_score:
			curr_max_score = new_max_score
			curr_guard_steps = guard_steps
			curr_guards_rest = guards_rest
			curr_best_partner = partner
			curr_propagated   = propagated
			curr_index = index
			curr_free_terms = free_terms
		for term in free_terms:
			term.unbind()
		
	lookup_info = fact_stores[curr_best_partner.sym_id].generate_lookup(curr_best_partner)
	best_match_step = { 'is_lookup'    : True
                          , 'propagated'   : curr_propagated
                          , 'lookup_index' : lookup_info['lookup_index']
                          , 'fact_pat'     : make_fact_pat(curr_best_partner)
                          , 'filter'       : lookup_info['filter']
                          , 'free_terms'   : curr_free_terms }	
	match_steps.append( best_match_step )
	for curr_guard_step in curr_guard_steps:
		match_steps.append( curr_guard_step )
	curr_best_partner.exist_bind_terms()

	return compute_optimal_matching(fact_stores, partners[:curr_index]+partners[(curr_index+1):], curr_guards_rest, match_steps)

def schedule_guards(guards):
	guard_match_steps = []
	unground_guards   = []
	for guard in guards: 
		if guard.is_ground():
			guard_match_steps.append({ 'is_lookup':False, 'guard':guard.evaluate, 'guard_str':str(guard) })
		else:
			unground_guards.append( guard )
	return (guard_match_steps,unground_guards)



def pretty_interp_rules(interp_rules):
	fact_classes = get_all_fact_classes()
	interp_rule_strs = []
	for sym_id,irules in interp_rules.items():
		fact_class = fact_classes[sym_id]
		interp_rule_strs.append("============= " + fact_class.__name__ + " =============")
		interp_rule_strs += map(pretty_interp_rule,irules)
		interp_rule_strs.append("======================================")
	return '\n'.join( interp_rule_strs )

def pretty_interp_rule(interp_rule):
	strs = []
	strs.append( "Rule: %s # %s" % (get_all_rule_classes()[interp_rule['rule_id']].__name__,interp_rule['occ_id']) )
	strs.append( "Entry: %s %s" % ('Propagate' if interp_rule['propagated'] else 'Simplify', pretty_fact_pat(interp_rule['entry']) ) )
	strs.append( "Matching Steps:" )
	for match_step in interp_rule['match_steps']:
		if match_step['is_lookup']:
			match_type = 'Propagate' if match_step['propagated'] else 'Simplify'
			match_pat  = pretty_fact_pat(match_step['fact_pat'])
			strs.append( "Lookup: %s %s (Store Index: %s)" % (match_type,match_pat,match_step['lookup_index']) )
		else:
			strs.append( "Schedule Guard: %s" % match_step['guard_str'] )
	return "-----------------------\n" + '\n'.join(strs) + "\n"

def pretty_fact_pat(fact_pat):
	fact_classes = get_all_fact_classes()
	return "%s(%s)" % ( fact_classes[fact_pat['sym_id']].__name__ , ','.join(map(str,fact_pat['terms'])) )


