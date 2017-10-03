
import tensorflow as tf
import numpy as np
from Environment import Environment
from parameters import ENV
import scipy


# Discounting function used to calculate discounted returns.
def discount(x):
    return scipy.signal.lfilter([1],
                                [1, -parameters.DISCOUNT],
                                x[::-1],
                                axis=0)[::-1]


# Copies one set of variables to another.
# Used to set worker network parameters to those of global network.
def update_target_graph(from_scope, to_scope):
    from_vars = tf.get_collection(tf.GraphKeys.TRAINABLE_VARIABLES, from_scope)
    to_vars = tf.get_collection(tf.GraphKeys.TRAINABLE_VARIABLES, to_scope)

    op_holder = []
    for from_var, to_var in zip(from_vars, to_vars):
        op_holder.append(to_var.assign(from_var))
    return op_holder


class Agent:

    def __init__(self, worker_index, render=False):
        print("Initialization of the agent", str(worker_index))

        self.worker_index = worker_index
        self.name = 'Worker_' + str(worker_index)

        self.env = Environment()
        state_size = self.env.get_state_size()
        action_size = self.env.get_action_size()

        self.network = Network(state_size, action_size, self.name)
        self.update_local_vars = update_target_graph('global', self.name)

        self.states_buffer = []
        self.actions_buffer = []
        self.rewards_buffer = []
        self.values_buffer = []

        self.rewards = []
        self.mean_values = []

    def update_global_network(self, sess, lstm_state):
        bootstrap_value = sess.run(self.network.value,
                                   feed_dict={self.network.inputs: [s],
                                              self.network.state_in: lstm_state})

        # Add the bootstrap value to our experience
        self.rewards_buffer.append(bootstrap_value)
        discounted_reward = discount(self.rewards_buffer)[:-1]

        self.values_buffer.append(bootstrap_value)
        advantage = self.rewards_buffer[:-1] + \
            parameters.DISCOUNT * self.values_buffer[1:] - \
            self.values_buffer[:-1]
        advantage = discount(advantage)

        # Update the global network
        feed_dict = {
            self.network.discounted_reward: discounted_reward,
            self.network.inputs: self.states_buffer,
            self.network.actions: self.actions_buffer,
            self.network.advantage: advantage,
            self.network.state_in: lstm_state}
        losses = sess.run([self.network.value_loss,
                           self.network.policy_loss,
                           self.network.entropy,
                           self.network.grad_norm,
                           self.network.state_out,
                           self.network.apply_grads],
                          feed_dict=feed_dict)

        # Get the losses for tensorboard (TO DO)
        value_loss, policy_loss, entropy = losses[:3]
        grad_norm, lstm_state, _ = losses[3:]

        # Reinitialize buffers and variables
        self.states_buffer = []
        self.actions_buffer = []
        self.rewards_buffer = []
        self.values_buffer = []
        sess.run(self.update_local_vars)

        return lstm_state

    def work(self, sess, coord):
        print("Starting", self.name)
        total_steps = 0

        with sess.as_default(), sess.graph.as_default():

            while not coord.should_stop():
                self.states_buffer = []
                self.actions_buffer = []
                self.rewards_buffer = []
                self.values_buffer = []
                reward = 0
                episode_step = 0

                # Reset the local network to the global
                sess.run(self.update_local_vars)

                s = self.env.reset()
                done = False
                lstm_state = self.network.lstm_state_init

                while not done and episode_step < parameters.MAX_EPISODE_STEP:
                    # Prediction of the policy and the value
                    feed_dict = {self.network.inputs: [s],
                                 self.network.state_in: lstm_state}
                    policy, value, lstm_state = sess.run(
                        [self.network.policy,
                         self.network.value,
                         self.network.state_out], feed_dict=feed_dict)

                    # Choose an action according to the policy
                    action = np.random.choice(action_size, p=policy)
                    s_, r, done, _ = self.env.act(action)

                    # Store the experience
                    self.states_buffer.append(s)
                    self.actions_buffer.append(a)
                    self.rewards_buffer.append(r)
                    self.values_buffer.append(value)
                    reward += r
                    s = s_

                    episode_step += 1
                    total_steps += 1

                    # If we have more than MAX_LEN_BUFFER experiences, we apply
                    # the gradients and update the global network, then we empty
                    # the episode buffers
                    if len(self.states_buffer) == parameters.MAX_LEN_BUFFER \
                            and not done:
                        lstm_state = self.update_global_network(sess,
                                                                lstm_state)

                self.rewards.append(reward)
                self.mean_values.append(np.mean(values_buffer))

                if len(states_buffer) != 0:
                    lstm_state = self.update_global_network(sess, lstm_state)