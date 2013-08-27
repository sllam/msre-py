
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


from mpi4py import MPI
import sys
import time

from msr_ensemble.facts.location import loc, loc_rank, loc_proc_id
from msr_ensemble.facts.term import lift
from msr_ensemble.context.fact_repr import make_fact_repr, make_fact_repr_loc, make_fact_pat, pretty_fact_repr
from msr_ensemble.context.store import new_stores, add_to_stores, del_from_stores, pretty_stores, get_candidates_from_stores, get_candidate_lookup_func_from_stores
from msr_ensemble.context.goals import add_goals, next_goal, HeapGoals
from msr_ensemble.rules.rule import get_all_rule_classes
from msr_ensemble.context.prop_history import new_histories

from msr_ensemble.misc.timeout import exec_timeout_in

from msr_ensemble.interpret.interpreter import interpret_rules, pretty_interp_rules

from msr_ensemble.misc.mpi_process import MasterProcess, WorkerProcess, send_facts, receive_fact_future_mpi
from msr_ensemble.misc.msr_logging import init_logger, get_logger, log_debug, log_info, log_warn, log_error, log_critical

# Top-level Execution

def execute_msr(init_goals, rule_classes, use_mpi=True):

	if not use_mpi:
		logger = init_logger("msr", log_file="msr.log")
		log_info(logger,"Started")
		rewrite_loop(rule_classes, init_goals, logger, (lambda: lambda: None), (lambda _: None), (lambda x: None), None )
		log_info(logger,"Shutting Down!")
	else:
		comm = MPI.COMM_WORLD
		rank = comm.Get_rank()

		# Check rules for dynamic spawning pattern.
		allow_dynamic_spawning = False
		for rule_class in rule_classes:
			rule = rule_class()
			if rule.req_dynamic_spawning:
				allow_dynamic_spawning = True
				break

		if allow_dynamic_spawning:
			mp = MSRMasterProcess(rank, init_goals, rule_classes, file_logging=True, output_file="output.log")
			mp.start()
		else:
			logger = init_logger("rank_%s" % rank, log_file="rank_%s.log" % rank)
			output_logger = init_logger("output", log_file="output.log")
			log_info(logger,"Started")
			init_goals = filter_goals_by_rank(init_goals, rank)
			rewrite_loop(rule_classes, init_goals, logger, receive_fact_future_mpi, send_facts, lambda x: None, lift(loc(rank)), output_logger=output_logger)
			log_info(logger,"Shutting Down!")

# Goal filtering

def filter_goals_by_rank(goals, rank):
	return filter(lambda goal: loc_rank(goal.location.value) == rank ,goals)

def filter_goals_by_proc_id(goals, proc_id):
	return filter(lambda goal: loc_proc_id(goal.location.value) == proc_id ,goals)

def partition_goals_by_rank(goals, rank):
	filtered = filter(lambda goal: loc_rank(goal.location.value) == rank ,goals)
	rest = filter(lambda goal: loc_rank(goal.location.value) != rank ,goals)
	return (filtered,rest)

def partition_goals_by_proc_id(goals, proc_id):
	filtered = filter(lambda goal: loc_proc_id(goal.location.value) == proc_id ,goals)
	rest = filter(lambda goal: loc_proc_id(goal.location.value) != proc_id ,goals)
	return (filtered,rest)

# MSR Process Instances

class MSRMasterProcess(MasterProcess):

	def __init__(self, rank, init_goals, rule_classes, sleep_length=0.1, sleep_factor=2, sleep_limit=3, init_workers=1, file_logging=False, output_file=None):
		self.initialize(rank, sleep_length=sleep_length, sleep_factor=sleep_factor, sleep_limit=sleep_limit
                               ,init_workers=init_workers, file_logging=file_logging)
		self.init_goals   = filter_goals_by_rank(init_goals, rank)
		self.rule_classes = rule_classes
		if not (output_file == None):
			self.output_logger = init_logger("output", log_file=output_file)
		else:
			self.output_logger = None

	def new_worker(self, rank, proc_id, worker_channel, master_channel):
		worker_channel = self.worker_channels[proc_id]
		(filtered,rest) = partition_goals_by_proc_id(self.init_goals, proc_id)
		self.init_goals = rest
		return MSRWorkerProcess(rank, proc_id, worker_channel, master_channel, filtered, self.rule_classes, file_logging=self.file_logging
                                       ,output_logger=self.output_logger)

pause_times    = 5
default_steps  = 1
backoff_factor = 2

class MSRWorkerProcess(WorkerProcess):

	def __init__(self, rank, proc_id, worker_channel, master_channel, init_goals, rule_classes, file_logging=False, output_logger=None):
		self.initialize(rank, proc_id, worker_channel, master_channel, file_logging=file_logging)
		self.init_goals   = init_goals
		self.rule_classes = rule_classes
		self.location = lift( loc(rank, proc_id) )
		self.output_logger = output_logger

	def routine(self):
		log_info(self.logger,"Started")

		rewrite_loop(self.rule_classes, self.init_goals, self.logger, lambda: self.get_msg, self.send_msgs, self.create_new_worker
                            ,self.location, output_logger=self.output_logger)

		log_info(self.logger,"Shutting Down")

#################################

def rewrite_loop(rule_classes, init_goals, logger, recv_msg_future_func, send_msgs_func, create_new_location_func, location, output_logger=None):
	fact_stores = new_stores()
	histories = new_histories()

	rules = map(lambda rule_class: rule_class(), rule_classes)
	if location != None:
		for rule in rules:
			rule.set_rank( loc_rank(location.value) )
	interp_rules = interpret_rules(rules, fact_stores)

	goals = HeapGoals()
	matching_funcs = generate_matching_functions(goals, fact_stores, histories, interp_rules, logger, send_msgs_func, create_new_location_func, location=location)

	for goal in init_goals:
		goals.push( make_fact_repr(goal) )

	recv_msg_func = recv_msg_future_func()
	current_steps  = default_steps
	current_factor = backoff_factor
	done = False

	while not done:
		current_steps = default_steps
		ext_fact_repr = recv_msg_func()

		if ext_fact_repr != None:
			while ext_fact_repr != None:
				goals.push(ext_fact_repr)
				recv_msg_func = recv_msg_future_func()
				ext_fact_repr = recv_msg_func()
			current_factor = backoff_factor
		else:
			current_steps  *= current_factor 
			current_factor *= 2

		while current_steps > 0:
			try:
				act_fact_repr = goals.pop()
				matching_funcs[act_fact_repr['sym_id']](act_fact_repr)
				current_steps -= 1
			except IndexError:
				ext_fact_repr = try_until(recv_msg_func, times=pause_times)
				if ext_fact_repr != None:
					goals.push(ext_fact_repr)
					recv_msg_func = recv_msg_future_func()
					current_factor = backoff_factor
					current_steps  = 0
				else:
					done = True
					break

	log_info(logger,pretty_stores( fact_stores ))

	if not (output_logger == None):
		log_info(output_logger,"Location %s:\n%s" % (location.value,pretty_stores(fact_stores,brief=True)) )


def try_until(func, times=5, sleep_time=0.2, sleep_factor=2):
	data = None
	while data == None:
		data = func()
		if data != None:
			return data
		else:
			if times > 0:
				time.sleep(sleep_time*sleep_factor)
				sleep_factor *= 2
				times -= 1
			else:
				return None

##################################

def generate_matching_functions(goals, fact_stores, histories, interp_rules, logger, send_goal_func, create_new_location_func, location=None):
	matching_funcs = {}
	for sym_id in interp_rules:
		irules = interp_rules[sym_id]
		matching_funcs[sym_id] = string_up_funcs(fact_stores, 
                                                         map(lambda interp_rule: generate_matching_function(goals, fact_stores, histories, sym_id, 
                                                                                                            interp_rule, logger, send_goal_func,
                                                                                                            create_new_location_func, location=location)
                                                            ,irules) )
	return matching_funcs

def string_up_funcs(fact_stores, funcs):
	def match_func(act_fact_repr):
		proceed = True
		add_to_stores(fact_stores, act_fact_repr)
		for func in funcs:
			proceed = func(act_fact_repr)
			if not proceed:
				break
		# if proceed:
		#	add_to_stores(fact_stores, act_fact_repr)
	return match_func

def generate_matching_function(goals, fact_stores, histories, sym_id, interp_rule, logger, send_goal_func, create_new_location_func, location=None):

	rule_id   = interp_rule['rule_id']

	fact_pat  = interp_rule['entry']
	term_pats = fact_pat['terms']

	has_no_simplify = interp_rule['has_no_simplify']

	match_partners = generate_partner_matching_function(goals, rule_id, has_no_simplify, fact_stores, histories, interp_rule['match_steps']
                                                           ,interp_rule['exist_locs'], interp_rule['has_exist_locs'], interp_rule['rhs']
                                                           ,logger, send_goal_func, create_new_location_func, location=location)

	rule_name = "Rule: %s # %s" % (get_all_rule_classes()[interp_rule['rule_id']].__name__,interp_rule['occ_id'])

	if location != None:
		loc_pat = fact_pat['location']
		def match_loc():
			return match_terms_inplace([loc_pat], [location.value])
		def unbind_loc():
			loc_pat.unbind()
	else:
		def match_loc():
			return True
		def unbind_loc():
			pass

	if interp_rule['propagated']:

		def match_func(act_fact_repr):
			# print rule_name
			if match_terms_inplace(term_pats, act_fact_repr['values']) and match_loc():
				matched = True
				ids = [(act_fact_repr['sym_id'],act_fact_repr['fact_id']['id'])] 
				while matched:
					matched = match_partners(ids, [], [act_fact_repr])
				# map(lambda t: t.unbind(),term_pats)
				for t in term_pats:
					t.unbind()
				unbind_loc()
			return True
	else:
		def match_func(act_fact_repr):
			# print rule_name
			if match_terms_inplace(term_pats, act_fact_repr['values']) and match_loc():
				ids = [(act_fact_repr['sym_id'],act_fact_repr['fact_id']['id'])] 
				done = match_partners(ids, [act_fact_repr], [])
				# map(lambda t: t.unbind(),term_pats)
				for t in term_pats:
					t.unbind()
				unbind_loc()
				return not done
			else:
				return True
			
	return match_func

def generate_partner_matching_function(goals, rule_id, has_no_simplify, fact_stores, histories, match_steps, exist_locs_func, has_exist_locs,
                                       rhs, logger, send_goal_func, create_new_location_func, location=None):
	if len(match_steps) == 0:
		if location != None:
			if has_exist_locs:
				def spawn_new_locs():
					new_locations = exist_locs_func()
					log_info(logger, "Creating new %s locations: %s" % (len(new_locations),new_locations))
					for location in new_locations:
						proc_id = loc_proc_id( location )
						create_new_location_func( proc_id )
			else:
				def spawn_new_locs():
					pass
			def exec_rhs():
				log_info(logger, "Applying rule %s" % rule_id)
				# sys.stdout.write("Local: ")
				# for goal in local_goals:
				#	sys.stdout.write("%s, " % goal)
				# sys.stdout.write("\nExternal: ")
				# for goal in external_goals:
				# 	sys.stdout.write("%s, " % goal)
				# sys.stdout.write("\n\n")
				# add_goals(goals, local_goals)
				(local_goals,external_goals) = partition_goals_by_proc_id(rhs(), loc_proc_id(location.value))
				spawn_new_locs()
				log_info(logger, "Sending internal goals: %s" % map(make_fact_repr_loc,local_goals) )
				log_info(logger, "Sending external goals: %s" % map(make_fact_repr_loc,external_goals) )
				goals.push_many( map(make_fact_repr,local_goals) )
				send_goal_func( map(make_fact_repr_loc,external_goals) )
		else:
			def exec_rhs():
				goals.push_many(map(make_fact_repr,rhs()))
				# add_goals(goals, rhs())

		if not has_no_simplify:
			def match_partners(ids, simplify, propagate):
				# print "Ids: %s" % ids
				# print "Deleting: %s" % ','.join( map(pretty_fact_repr,simplify) )
				for fact_pat in simplify:
					del_from_stores(fact_stores, fact_pat)
				# print "Adding: %s" % ','.join( map(str,rhs_goals) )
				# add_goals(goals, rhs())
				
				exec_rhs()
					
				return True
		else:
			check_history = histories[rule_id].check_history
			remove_history_entries = histories[rule_id].remove_history_entries
			def match_partners(ids, simplify, propagate):
				fact_ids = map(lambda can: can['fact_id'],propagate)
				if check_history(fact_ids):
					# print "Deleting: %s" % ','.join( map(pretty_fact_repr,simplify) )
					# for fact_pat in simplify:
					# 	del_from_stores(fact_stores, fact_pat)
					# print "Adding: %s" % ','.join( map(str,rhs_goals) )
					# for id in fact_ids:
					#	remove_history_entries(id['history_entries'][rule_id])
					# add_goals(goals, rhs())
					
					exec_rhs()

					return True
				else:
					return False
	else:
		curr_step  = match_steps[0] 
		rest_steps = match_steps[1:]
		rest_match_partners = generate_partner_matching_function(goals, rule_id, has_no_simplify, fact_stores, histories, rest_steps, exist_locs_func
                                                                        ,has_exist_locs, rhs, logger, send_goal_func, create_new_location_func, location=location)
		if curr_step['is_lookup']:
			lookup_index = curr_step['lookup_index']
			filter_func  = curr_step['filter']
			fact_pat     = curr_step['fact_pat']
			sym_id       = fact_pat['sym_id']
			term_pats    = fact_pat['terms']
			free_terms   = curr_step['free_terms']
			get_candidates = get_candidate_lookup_func_from_stores(fact_stores, lookup_index, sym_id, term_pats)
			if curr_step['propagated']:
				def match_partners(ids, simplify, propagate):
					#iter_cans = get_candidates_from_stores(fact_stores, lookup_index, sym_id, term_pats) 
					iter_cans = get_candidates()
					while True:
						curr_can = next(iter_cans,None)
						if curr_can != None:
							# print "trying %s" % str(curr_can)
							curr_id = curr_can['fact_id']['id'] 
							can_values = curr_can['values']
							if (sym_id,curr_id) not in ids and filter_func(can_values) and match_terms_inplace(term_pats, can_values):
								done = rest_match_partners(ids+[(sym_id,curr_id)], simplify, propagate+[curr_can])
								for free_term in free_terms:
									free_term.unbind()
								if done:
									return True
						else:
							return False
			else:
				def match_partners(ids, simplify, propagate):
					# iter_cans = get_candidates_from_stores(fact_stores, lookup_index, sym_id, term_pats) 
					iter_cans = get_candidates()
					while True:
						curr_can = next(iter_cans,None)
						if curr_can != None:
							# print "trying %s" % str(curr_can)
							curr_id = curr_can['fact_id']['id'] 
							can_values = curr_can['values']
							# sys.stdout.write("\n\n(%s,%s) not in %s\n\n" % (sym_id,curr_id,ids))
							if (sym_id,curr_id) not in ids and filter_func(can_values) and match_terms_inplace(term_pats, can_values):
								done = rest_match_partners(ids+[(sym_id,curr_id)], simplify+[curr_can], propagate)
								for free_term in free_terms:
									free_term.unbind()
								if done:
									return True
						else:
							return False
		else:		
			guard = curr_step['guard']
			def match_partners(ids, simplify, propagate):
				if guard():
					return rest_match_partners(ids, simplify, propagate)
				else:
					return False
	return match_partners

def match_term_inplace(term_pat, subj):
	# if term_pat.is_duncare():
	#	return True
	if not term_pat.is_ground():
		term_pat.bind(subj)
		return True
	else:
		return term_pat.value == subj

def match_terms_inplace(term_pats, subjs):
	for i in xrange(0,len(term_pats)):
		term_pat = term_pats[i]
		subj     = subjs[i]
		if not term_pat.is_ground():
			term_pat.bind(subj)
			# return True
		elif term_pat.value != subj:
			return False
		'''
		if not match_term_inplace(term_pats[i],subjs[i]):
			return False
		'''
	return True
	'''
	for term_pat,subj in zip(term_pats,subjs):
		if not match_term_inplace(term_pat,subj):
			return False
	return True
	'''

def match_fact_inplace(term_sym_pat, term_pats, fact_sym_subj, term_subjs):
	if term_sym_pat == fact_sym_subj:
		for term_pat,term_subj in zip(term_pats,term_subjs):
			if not match_term_inplace(subst, term_pat, term_subj):
				return False
		return True			
	else:
		return False



