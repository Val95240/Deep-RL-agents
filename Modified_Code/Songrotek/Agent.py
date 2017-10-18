
import tensorflow as tf
import numpy as np

from CriticNetwork import CriticNetwork
from ActorNetwork import ActorNetwork
from Environment import Environment
from ExperienceBuffer import ExperienceBuffer

from Displayer import DISPLAYER
import parameters


class Agent:

    def __init__(self, sess):
        print("Initializing agent...")

        self.env = Environment()
        self.state_size = self.env.get_state_size()
        self.action_size = self.env.get_action_size()
        self.low_bound, self.high_bound = self.env.get_bounds()

        self.sess = sess

        print("\tInitializing the actor network")
        self.actor_network = ActorNetwork(self.sess,
                                          self.state_size, self.action_size,
                                          self.low_bound, self.high_bound)

        print("\tInitializing the critic network")
        self.critic_network = CriticNetwork(self.sess,
                                            self.state_size, self.action_size)

        print("\tCreating the experience buffer")
        self.buffer = ExperienceBuffer()

        self.epsilon = parameters.EPSILON_START
        self.gamma = parameters.DISCOUNT
        print("Agent initialized !\n")

    def epsilon_decay(self):

        if self.epsilon > parameters.EPSILON_STOP:
            self.epsilon -= parameters.EPSILON_DECAY

    def run(self):

        self.total_steps = 0

        for ep in range(1, parameters.TRAINING_STEPS + 1):

            episode_reward = 0
            episode_step = 0
            done = False

            # Initial state
            s = self.env.reset()

            # Render parameters
            self.env.set_render(ep % 500 == 0)
            gif = (ep % 1000 == 0)
            max_steps = parameters.MAX_EPISODE_STEPS + ep // 500

            while episode_step < max_steps and not done:

                a = self.actor_network.action(s)
                s_, r, done, info = self.env.act(a, gif)

                self.buffer.add((s, a, r, s_, done))

                if ep % parameters.TRAINING_FREQ == 0 and \
                        len(self.buffer) >= parameters.BATCH_SIZE:

                    minibatch = self.buffer.sample()
                    state_batch = np.asarray([data[0] for data in minibatch])
                    action_batch = np.asarray([data[1] for data in minibatch])
                    reward_batch = np.asarray([data[2] for data in minibatch])
                    next_state_batch = np.asarray(
                        [data[3] for data in minibatch])
                    done_batch = np.asarray([data[4] for data in minibatch])

                    action_batch = np.resize(
                        action_batch, [parameters.BATCH_SIZE, self.action_size])

                    next_action_batch = self.actor_network.target_actions(
                        next_state_batch)
                    q_value_batch = self.critic_network.target_q(
                        next_state_batch, next_action_batch)

                    targets = reward_batch[:, np.newaxis] + \
                        done_batch[:, np.newaxis] * self.gamma * q_value_batch

                    # Update critic by minimizing the loss L
                    self.critic_network.train(
                        targets, state_batch, action_batch)

                    # Update the actor policy using the sampled gradient:
                    action_batch_for_gradients = self.actor_network.actions(
                        state_batch)

                    q_gradient_batch = self.critic_network.gradients(
                        state_batch, action_batch_for_gradients)

                    self.actor_network.train(q_gradient_batch, state_batch)

                    # Update the target networks
                    self.actor_network.update_target()
                    self.critic_network.update_target()

                s = s_
                episode_reward += r
                episode_step += 1
                self.total_steps += 1

            self.epsilon_decay()

            if gif:
                self.env.save_gif('results/gif/', self.n_gif)
                self.n_gif = (self.n_gif + 1) % 5

            DISPLAYER.add_reward(episode_reward)
            if ep % 50 == 0:
                print("Episode %2i, Reward: %7.3f, Steps: %i, Epsilon: %7.3f"
                      " (max step: %i)" % (ep, episode_reward, episode_step,
                                           self.epsilon, max_steps))

            if ep % 500 == 0:
                DISPLAYER.disp()

    def test(self, nb_episodes):

        for ep in range(nb_episodes):

            episode_reward = 0
            s = self.env.reset()
            done = False

            while not done:
                a = self.actor_network.action(s)
                s_, r, done, info = self.env.act(a, False)
                episode_reward += r

            print('Episode reward : ', episode_reward)

    def close(self):
        self.env.close()