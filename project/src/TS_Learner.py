from Learner import *
import numpy as np
import itertools

# Implementation of the specific Multi Armed Bandit algorithm TS (Thompson Sampling), derived from general Learner class 
class TS_Learner(Learner):

    # TS keeps track of the parameters of a Beta distribution that models the expected rewards (initialized as zeros)
    # previous_arms : arms selected at the previous call of the bandit are used to make an estimation of the new best arms to pick and speed up the pull of new candidate prices
    def __init__(self, prices, bandit_split=None):
        super().__init__(prices, bandit_split)
        self.prices = prices
        self.beta_parameteres = np.ones((2, self.n_items, self.n_prices)) #matrice 5x4x2
        self.previous_arms = [0] * prices.shape[0]

        """Gaussian-Gamma model (conjugate prior of a normal distribution with unknown mean and precision)
        self.n = np.zeros((self.n_items, self.n_prices))          #collect the number of times an price is pulled, for each item

        self.alphas = np.ones((self.n_items, self.n_prices))      #gamma shape parameters
        self.betas = np.ones((self.n_items, self.n_prices)) * 10  #gamma rate parameters

        self.mu_zero = np.ones((self.n_items, self.n_prices))     #prior (normal estimated mean)
        self.v_zero = self.betas / (self.alphas + 1)              #prior (normal estimated variance)"""

    def pull_prices(self):
        idx = np.zeros(self.n_items, dtype=int)
        precision = np.zeros((self.n_items, self.n_prices))
        estimated_variance = np.empty((self.n_items, self.n_prices))

        for i in range(self.n_items):
            idx[i] = np.argmax(np.random.beta(self.beta_parameteres[0, i, :], self.beta_parameteres[1, i, :]))

        """ Gaussian-Gamma model: sample from our estimated gaussian-gamma distribution
        for i in range(self.n_items):
            precision[i] = np.random.gamma(self.alphas[i, :], 1/self.betas[i, :])
            for k in range(precision.shape[1]):
                if precision[i, k] == 0 or self.n[i, k] == 0: precision[i, k] = 0.001
            estimated_variance[i] = 1/precision[i]
            idx[i] = np.argmax(np.random.normal(self.mu_zero[i, :], np.sqrt(estimated_variance[i, :])))"""

        return idx

    # Method that pulls new candidate arms before the collection of the rewards. Arms selected optimize the expected rewards estimated with best arms sampled from the Beta distribution,
    # given the distribution of the number of items bought for each item and the activation probabilities
    # estimated : when True it uses previous arms instead of all possible combinations to optimize the expected rewards of new pulled arms, with a notable speedup in computation
    def pull_prices_activations(self, n_items_to_buy_distr, activation_probs, estimated=True):
        
        combinations = []

        if estimated==False:
            idx = np.zeros(self.n_items, dtype=int)
            possible_arms_indeces = np.arange(self.prices.shape[1])
            combinations = []
            for comb in itertools.product(possible_arms_indeces, repeat=len(possible_arms_indeces)+1):
                combinations.append(comb)
        else:
            for item in range(self.prices.shape[0]):
                for arm in range(self.prices.shape[1]):
                    combination = self.previous_arms.copy()
                    combination[item] = arm
                    combinations.append(combination)

        combinations_rewards = []
        for starting_point in range(0, self.prices.shape[0]):
            for comb in combinations:
                cur_sum = 0
                for item, arm in enumerate(comb):
                    cur_sum += self.prices[item][arm] * (np.random.beta(self.beta_parameteres[0, item, arm], self.beta_parameteres[1, item, arm])) * np.mean(n_items_to_buy_distr[:, item, 0], axis=0) * np.mean(np.array(activation_probs)[:,starting_point, item], axis=0)
                combinations_rewards.append(cur_sum)
        combinations = combinations * self.prices.shape[0]
        pulled_arms_idx = combinations[np.argmax(combinations_rewards)]
        self.previous_arms = pulled_arms_idx

        return pulled_arms_idx

    # Reinitialize the bandit
    def reset(self):
        self.__init__(self.prices, self.bandit_split)

    # This method extends the Learner update to also update Beta parameters for each sample of collected rewards
    def update(self, pulled_arms, rewards):
        #self.t += 1

        super().update(pulled_arms, rewards)

        for i in range(self.n_items):
            for j in range(len(rewards[i])): 
                self.beta_parameteres[0, i, pulled_arms[i]] = self.beta_parameteres[0, i, pulled_arms[i]] + rewards[i][j]
                self.beta_parameteres[1, i, pulled_arms[i]] = self.beta_parameteres[1, i, pulled_arms[i]] + 1.00 - rewards[i][j]

        """#When rewards are not binary, we can use different distributions to model out the problem, for instance 
        #under assumption of normal reward with unknown mean and variance, we can use a Gaussian-Gamma conjugate-prior
        for item in range(self.n_items):
            n = len(rewards[item])
            v = self.n[item, pulled_arms[item]]
            for j in range(n): 
                self.alphas[item, pulled_arms[item]] = self.alphas[item, pulled_arms[item]] + n/2
                self.betas[item, pulled_arms[item]] = self.betas[item, pulled_arms[item]] + ((n*v/(v + n)) * (((rewards[item][j] - self.mu_zero[item, pulled_arms[item]])**2)/2))
                # estimate the prior variance: calculate from the gamma hyper-parameters
                self.v_zero[item, pulled_arms[item]] = self.betas[item, pulled_arms[item]] / (self.alphas[item, pulled_arms[item]] + 1)
                # estimate the prior mean: calculate from the collected rewards
                self.mu_zero[item, pulled_arms[item]] = np.array(self.rewards_per_item_arm[item][pulled_arms[item]]).mean()
            self.n[item, pulled_arms[item]] += n"""
                