## Deep Reinforcement Learning Notes

### RL Loop:
1. Environment sends state to Agent (observation) starting with state S0
- in example of mario, state S0 is frame 1
2. Based on state S0, Agent performs action A0 (for mario, moves right for example)
3. Environment transitions to state S1 (for mario, transitions to frame 2)
4. Environment gives reward R1 to Agent
- in example of mario, not dead +1
5. RL loop outputs tuple (state, action, reward)
-- Goal of Agent is to maximize cumulative reward

### Episodic vs Continuous:
1. Monte Carlo method: (episodic)
- collect rewards at end of "episode" and then calculate max expected future reward
2. Temporal Difference (TD) method: (continuous)
- waits until next time step to update value estimates
- forms a TD target used observed reward R(t+1) and the current estimate V(st + 1)

### Exploration vs Exploitation
1. Exploration is getting more info about environment
2. Exploitation is exploiting known info to maximize reward

### Approaches to Reinforcement Learning
1. Value based:
- goal is to maximize value function V(s)
- V(s) tells us max expected future reward agent will get at each state
2. Policy based:
- a = pi(s) (action = policy(state)
- policy function maps each state to best corresponding action
- two policy types:
- 1. deterministic: policy at given state will always return the same action
- 2. stochastic: output distribution probability over actions
3. Model based:
- create model for behavior of a given environment

### Deep Q Value Network (DQN)
- uses neural network to approximate the reward based on the current state, and the action on that state
