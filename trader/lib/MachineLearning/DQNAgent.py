import os
import numpy as np
import random
from collections import deque
from keras.models import Sequential
from keras.layers import Dense
from keras.optimizers import Adam


# Deep Q-learning Agent
class DQNAgent(object):
    def __init__(self, symbol, state_size, action_size, max_inventory=1):
        self.symbol = symbol
        self.episode = 0
        self.weights_path = "models/{}.h5".format(symbol)
        self.episode_path = "models/{}.txt".format(symbol)
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
        model = Sequential()
        model.add(Dense(24, input_dim=self.state_size, activation='relu'))
        model.add(Dense(24, activation='relu'))
        model.add(Dense(self.action_size, activation='linear'))
        model.compile(loss='mse',
                      optimizer=Adam(lr=self.learning_rate))
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
        if np.random.rand() <= self.epsilon:
            return random.randrange(self.action_size)
        act_values = self.model.predict(state)
        return np.argmax(act_values[0])  # returns action

    def replay(self, batch_size):
        minibatch = random.sample(self.memory, batch_size)
        for state, action, reward, next_state, done in minibatch:
            target = reward
            if not done:
              target = reward + self.gamma * \
                       np.amax(self.model.predict(next_state)[0])
            target_f = self.model.predict(state)
            target_f[0][action] = target
            self.model.fit(state, target_f, epochs=1, verbose=0)
        if self.epsilon > self.epsilon_min:
            self.epsilon *= self.epsilon_decay
