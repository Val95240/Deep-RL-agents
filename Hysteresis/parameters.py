
ENV = "Acrobot-v1"

LOAD = True
DISPLAY = True

CONV = False

LEARNING_RATE = 7.5e-4

DISCOUNT = 0.99
N_STEP_RETURN = 3
DISCOUNT_N = DISCOUNT**(N_STEP_RETURN-1)

FRAME_SKIP = 0
BUFFER_SIZE = 100000
BATCH_SIZE = 32

# Number of episodes of game environment to train with
TRAINING_STEPS = 1000
PRE_TRAIN_STEPS = 100

# Maximal number of steps during one episode
MAX_EPISODE_STEPS = 6000
TRAINING_FREQ = 5

# Rate to update target network toward primary network
UPDATE_TARGET_RATE = 0.001


EPSILON_START = 0.8
EPSILON_STOP = 0.01
EPSILON_STEPS = 600
EPSILON_DECAY = (EPSILON_START - EPSILON_STOP) / EPSILON_STEPS

ALPHA = 0.5
BETA_START = 0.4
BETA_STOP = 1
BETA_STEPS = 25000
BETA_INCR = (BETA_STOP - BETA_START) / BETA_STEPS


# Display Frequencies
DISP_EP_REWARD_FREQ = 2
PLOT_FREQ = 250000
RENDER_FREQ = 2

SAVE_FREQ = 200
EP_ELONGATION = 50
