import os
import numpy as np
import random
from collections import deque
from keras.models import Sequential, Model
from keras.layers import Dense, Input
from keras.optimizers import Adam
from keras.utils import to_categorical
import keras


# Deep Q-learning Agent
class DQNAgent(object):
    def __init__(self, symbol, state_size, action_size, is_eval=False, max_inventory=1):
        self.symbol = symbol
        self.episode = 0
        self.weights_path = "models/{}.h5".format(symbol)
        self.episode_path = "models/{}.txt".format(symbol)
        self.is_eval = is_eval
        self.state_size = state_size
        self.action_size = action_size
        self.memory = deque(maxlen=2000)
        self.inventory = []
        self.max_inventory = max_inventory
        self.gamma = 0.95    # discount rate
        self.epsilon = 1.0  # exploration rate
        self.epsilon_min = 0.01
        self.epsilon_decay = 0.995
        self.learning_rate = 0.001
        self.model = self._build_model()

    def _build_model(self):
        # Neural Net for Deep-Q learning Model
        # model = Sequential()
        # model.add(Dense(24, input_shape=(self.state_size,), activation='relu'))
        # model.add(Dense(24, activation='relu'))
        # model.add(Dense(self.action_size, activation='linear'))
        # model.compile(loss='mse',
        #               optimizer=Adam(lr=self.learning_rate))
        input_layer = Input((self.state_size,), batch_shape=(None, 1, self.state_size))
        actions_input = keras.layers.Input((self.action_size,), name='mask')
        hl = Dense(24, activation="relu")(input_layer)
        h2 = Dense(24, activation="relu")(hl)
        h3 = Dense(24, activation="relu")(h2)
        output_layer = Dense(self.action_size, activation="linear")(h3)
        filtered_output = keras.layers.multiply([output_layer, actions_input])
        model = keras.models.Model(input=[input_layer, actions_input], output=filtered_output) #Model(input_layer, output_layer)
        model.compile(loss="mse", optimizer=Adam(lr=self.learning_rate))
        return model

    def load_weights(self):
        self.model.load_weights(self.weights_path)

    def save_weights(self):
        self.model.save_weights(self.weights_path, overwrite=True)

    def load(self):
        if not os.path.exists(self.episode_path):
            return 0
        with open(self.episode_path, 'r') as f:
            self.episode = int(f.readline().strip()) + 1
        self.load_weights()
        print("Loaded episode {}".format(self.episode))
        return self.episode

    def save(self):
        with open(self.episode_path, 'w') as f:
            f.write(str(self.episode))
        self.save_weights()

    def remember(self, state, action, reward, next_state, done):
        self.memory.append((state, action, reward, next_state, done))

    def act(self, state):
        if not self.is_eval and np.random.rand() <= self.epsilon:
            return random.randrange(self.action_size)
        action_mask = np.ones((1, self.action_size))
        act_values = self.model.predict([state[0].reshape(1, 1, self.state_size), action_mask], batch_size=1)
        return np.argmax(act_values[0])  # returns action

    def replay(self, batch_size):
        idx = np.random.choice(len(self.memory), size=batch_size, replace=False)
        minibatch = np.array(self.memory)[idx]

        # Extract the columns from our sample
        states = np.array(list(minibatch[:, 0]))
        actions = minibatch[:, 1]
        rewards = np.array(minibatch[:, 2])
        next_states = np.array(list(minibatch[:, 3]))
        is_terminal = minibatch[:, 4].tolist()

        action_mask = np.ones((len(next_states), self.action_size))
        # First, predict the Q values of the next states. Note how we are passing ones as the mask.
        next_Q_values = self.model.predict([next_states, action_mask])

        # The Q values of the terminal states is 0 by definition, so override them
        next_Q_values[is_terminal] = 0

        # actions one hot encoded
        actions_encoded = to_categorical(actions, num_classes=3)

        # fix the shape of next_Q_values
        next_Q_values = next_Q_values.reshape(batch_size, self.action_size)
        # The Q values of each start state is the reward + gamma * the max next state Q value
        Q_values = rewards + self.gamma * np.amax(next_Q_values, axis=1)

        targets = actions_encoded * Q_values[:, None]
        targets = targets.reshape(batch_size, 1, self.action_size)

        # Fit the keras model. Note how we are passing the actions as the mask and multiplying
        # the targets by the actions.
        self.model.fit(
            [states, actions_encoded], targets,
            nb_epoch=1, batch_size=len(states), verbose=0
        )
        if self.epsilon > self.epsilon_min:
            self.epsilon *= self.epsilon_decay
