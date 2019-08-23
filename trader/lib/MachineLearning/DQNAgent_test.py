import os
import numpy as np
import random
from collections import deque
import keras
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
        n_actions = self.action_size
        obs_shape = (32, self.state_size)
        observations_input = keras.layers.Input(obs_shape, name='observations_input')
        action_mask = keras.layers.Input((n_actions,), name='action_mask')
        hidden = keras.layers.Dense(32, activation='relu')(observations_input)
        hidden_2 = keras.layers.Dense(32, activation='relu')(hidden)
        output = keras.layers.Dense(n_actions)(hidden_2)
        filtered_output = keras.layers.multiply([output, action_mask])
        model = keras.models.Model([observations_input, action_mask], filtered_output)
        optimizer = keras.optimizers.Adam(lr=self.learning_rate, clipnorm=1.0)
        model.compile(optimizer, loss='mean_squared_error')
        # Neural Net for Deep-Q learning Model
        #model = Sequential()
        #model.add(Dense(24, input_dim=self.state_size, activation='relu'))
        #model.add(Dense(24, activation='relu'))
        #model.add(Dense(self.action_size, activation='linear'))
        #model.compile(loss='mse',
        #              optimizer=Adam(lr=self.learning_rate))
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

    def one_hot_encode(self, n, action):
        one_hot = np.zeros(n)
        one_hot[int(action)] = 1
        return one_hot

    def predict(self, states):
        action_mask = np.ones((len(states), self.action_size))
        print(action_mask)
        return self.model.predict(x=[states, action_mask])

    def replay(self, batch_size):
        minibatch = random.sample(self.memory, batch_size)

        states = np.zeros((batch_size, self.state_size))
        actions = np.zeros(batch_size)
        rewards = np.zeros(batch_size)
        next_states = np.zeros((batch_size, self.state_size))
        dones = []

        for i in range(0, len(minibatch)):
            states[i] = minibatch[i][0]
            actions[i] = minibatch[i][1]
            rewards[i] = minibatch[i][2]
            next_states[i] = minibatch[i][3]
            dones.append(minibatch[i][4])
        dones = np.array(dones).reshape(1, -1)
        next_q_values = self.predict([next_states])
        next_q_values[dones] = 0
        q_values = self.gamma * np.amax(next_q_values, axis=1)
        print(q_values)

        #for state, action, reward, next_state, done in minibatch:
        #    target = reward
        #    if not done:
        #      target = reward + self.gamma * \
        #               np.amax(self.model.predict(next_state)[0])
        #    target_f = self.model.predict(state)
        #    target_f[0][action] = target
        #    self.model.fit(state, target_f, epochs=1, verbose=0)
        #self.model.train_on_batch(trainX, trainY)
        if self.epsilon > self.epsilon_min:
            self.epsilon *= self.epsilon_decay

    # def replay(self, batch_size):
    #     minibatch = random.sample(self.memory, batch_size)
    #     inputs = np.zeros(batch_size, self.state_size)
    #     targets = np.zeros(batch_size, self.action_size)
    #     for state, action, reward, next_state, done in minibatch:
    #         target = reward
    #         if not done:
    #           target = reward + self.gamma * \
    #                    np.amax(self.model.predict(next_state)[0])
    #         target_f = self.model.predict(state)
    #         target_f[0][action] = target
    #         self.model.fit(state, target_f, epochs=1, verbose=0)
    #     #self.model.train_on_batch(trainX, trainY)
    #     if self.epsilon > self.epsilon_min:
    #         self.epsilon *= self.epsilon_decay
