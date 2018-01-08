import numpy as np
import random as rn


class Learning:
	def __init__(self):
		
		self.num_actions = 18
		self.num_states = 20
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
		print reward
		return reward

	def update_q(self, state, action, score):
		reward_s_a = self._get_reward(score)
		q_s_a = self.Q[state, action-1]
		#new_q = q_s_a + alpha * (r_s_a + gamma * max(q[next_state, :]) - qsa)
		new_q = q_s_a + self.alpha * (reward_s_a - q_s_a)
		self.Q[state, action-1] = new_q
                np.savetxt('q.txt', self.Q)
		#print self.Q
		# renormalize row to be between 0 and 1
		#rn = q[state][q[state] > 0] / np.sum(q[state][q[state] > 0])
		#q[state][q[state] > 0] = rn
		#return r[state, action]

	def choose_action(self, state):
            if np.max(self.Q[state]) == 0:
                zeros = [i for i in range(self.num_actions) if self.Q[state, i]==0]
                action = rn.choice(zeros)
            else:
                action = np.argmax(self.Q[state])
            return action+1
