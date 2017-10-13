
import os
import gym
from parameters import ENV, FRAME_SKIP

from PIL import Image
import imageio


class Environment:

    def __init__(self):

        self.env_no_frame_skip = gym.make(ENV)
        self.env = gym.wrappers.SkipWrapper(FRAME_SKIP)(self.env_no_frame_skip)
        print()
        self.frame_buffer = []
        # Add the first three states to the buffer
        self.env.reset()
        for _ in range(3):
            self.frame_buffer.append(self.env_no_frame_skip.step(0)[0])

        self.render = False
        self.offset = 0
        self.images = []

    def get_state_size(self):
        try:
            return (self.env.observation_space.n, )
        except AttributeError:
            return (84, 84, 3)

    def get_action_size(self):
        if ENV == "SpaceInvaders-v0" or ENV == "SpaceInvaders-ram-v0":
            return 4
        elif ENV == "Pong-v0" or ENV == "Pong-ram-v0":
            self.offset = 2
            return 3
        else:
            try:
                return self.env.action_space.n
            except AttributeError:
                return self.env.action_space.shape[0]

    def set_render(self, render):
        self.render = render

    def _add_state(self, state):
        state = cv2.resize(cv2.cvtColor(state, cv2.COLOR_RGB2GRAY), (84, 90))
        state = state[1:85, :]
        self.frame_buffer.append(state)
        if len(self.frame_buffer) > parameters.FRAME_BUFFER_SIZE:
            self.frame_buffer.pop(0)

    def reset(self):
        s = self.env.reset()
        self._add_state(s)
        for _ in range(2):
            s = self.env_no_frame_skip.step(0)[0]
            self._add_state(s)
        return self.frame_buffer

    def act(self, action, gif=False):
        if not gif:
            return self._act(action)
        else:
            return self._act_gif(action)

    def _act(self, action):
        action += self.offset
        assert self.env.action_space.contains(action)
        if self.render:
            self.env.render()
        s, r, done, info = self.env.step(action)
        self._add_state(s)
        return self.frame_buffer, r, done, info

    def _act_gif(self, action):
        action += self.offset
        assert self.env.action_space.contains(action)
        r = 0
        i, done = 0, False
        while i < (FRAME_SKIP + 1) and not done:
            if self.render:
                self.env_no_frame_skip.render()

            #Save image
            img = Image.fromarray(self.env.render(mode='rgb_array'))
            img.save('tmp.png')
            self.images.append(imageio.imread('tmp.png'))

            s_, r_tmp, done, info = self.env_no_frame_skip.step(action)
            r += r_tmp
            i += 1
        self._add_state(s_)
        return self.frame_buffer, r, done, info

    def save_gif(self, path):
        os.makedirs(os.path.dirname(path), exist_ok=True)
        imageio.mimsave(path, self.images, duration=1)
        self.images = []

    def close(self):
        self.env.render(close=True)
        self.env.close()
