import numpy as np
import random as rn


class Learning:
	def __init__(self):
		
		self.num_actions = 18
		self.num_states = 15
		self.Q = np.zeros((self.num_states, self.num_actions))

		self.alpha = 0.5
		self.gamma = 0.5

		self.past_score = 0
		


	def _get_reward(self, current_score):
		"""
		Method that computes the reward after
		performing an action.

		:param current_score: int with the current game score
		:return: reward value
		"""
		# Failure
		if current_score == -1:
			reward = -100
			self.past_score = 0
		# Basket
		elif current_score != -1:
			reward = 100
			self.past_score = current_score
		return reward

	def update_q(self, state, action, score):
		reward_s_a = self._get_reward(score)
		q_s_a = self.Q[state, action]
		#new_q = q_s_a + alpha * (r_s_a + gamma * max(q[next_state, :]) - qsa)
		new_q = q_s_a + alpha * (r_s_a - qsa)
		self.Q[state, action] = new_q
		# renormalize row to be between 0 and 1
		#rn = q[state][q[state] > 0] / np.sum(q[state][q[state] > 0])
		#q[state][q[state] > 0] = rn
		#return r[state, action]

	def choose_action(self, state):
            if np.count_nonzero(self.Q[state]) > 0:
                action = np.argmax(self.Q[state])
            else:
                # Don't allow invalid moves at the start
                # Just take a random move
                action = rn.choice(range(1, self.num_actions+1))
            return action
