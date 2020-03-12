import h5py
import numpy as np 
import matplotlib.pyplot as plt
from scipy.special import expit

def load_dataset(): 
  train_set = h5py.File('train_catvnoncat.h5', 'r')
  train_set_X = np.array(train_set['train_set_x'])
  train_set_y = np.array(train_set['train_set_y'])
  train_classes = np.array(train_set['list_classes'])
  # Prepare the dataset 
  train_set_y = train_set_y.reshape(1, train_set_y.shape[0])
  return train_set_X, train_set_y, train_classes 

# Load the dataset 
X, y, classes = load_dataset()
# Get the dataset features 
m = y.shape[1] # Number of training samples 
n = X.shape[1] * X.shape[2] * X.shape[3] # Number of features
# Flatten the X matrix 
X_flatten = X.reshape(m, n).T
# Standardize the results 
X_flatten = X_flatten/255

# Describe the data 
print('\n------------ DATASET INFO ---------------\n')
print('Shape of Input (pre-flatten):', X.shape)
print('Shape of Input (post-flatten):', X_flatten.shape)
print('Shape of Output:', y.shape)
print('Memory occupied by Input:', str(X_flatten.nbytes/1000) + 'kb')
print('Memory occupied by Output:', str(y.nbytes/1000)+'kb')
print('\n---------------------------------------\n')

class Model: 
  def __init__(self, parameters): 
    self.learning_rate = parameters['learning_rate']
    self.num_iters = parameters['num_iters'] 
    self.layers = parameters['layers']

    # Used for storing interim results 
    self.cache = []
    # Parameters of different layers in the network 
    self.parameters = {}

    # Initalize the parameters 
    self.initialize_parameters()

    # The growth rate of the cost function 
    self.growth_rate = None
    # Store the cost history 
    self.J_hist = []

  # Helper functions 
  def sigmoid(self, Z): 
    return expit(Z)

  def dsigmoid(self, Z): 
    # Returns the derivative of the sigmoid function 
    sig = self.sigmoid(Z)
    return sig * (1-sig)
  
  def relu(self, Z):
    return np.maximum(0, Z)
  
  def drelu(self, Z): 
    return np.heaviside(Z, 0)

  # Initialize parameters 
  def initialize_parameters(self):
    for i in range(1, len(self.layers)): 
      self.parameters['W'+str(i)] = np.random.randn(self.layers[i], self.layers[i-1]) * 0.1
      self.parameters['b'+str(i)] = np.zeros((self.layers[i], 1))
  
  # Feed forward algorithm 
  def feed_forward(self, X): 
    # Clear the previous values in the cache
    if len(self.cache) == 0:
      self.cache.append({
        'A': X
      })
    else: 
      # Remove the previous results in the cache
      del self.cache[1:]
    L = len(self.parameters)//2 # Number of hidden layers
    A = X
    for i in range(1, L): 
      A_prev = A
      Z = np.dot(self.parameters['W'+str(i)], A_prev) + self.parameters['b'+str(i)]
      A = self.relu(Z)
      self.cache.append({
        'A': A, 
        'Z': Z
      })
    # Calculate the output 
    Z_output = np.dot(self.parameters['W'+str(L)], A) + self.parameters['b'+str(L)]
    A_output = self.sigmoid(Z_output)
    self.cache.append({
      'A': A_output, 
      'Z': Z_output
    })
    return A_output
   

  # Results the cost of the predictions
  def computeCost(self, y, predictions):
    m = y.shape[1]
    epsilon = 1e-5 # Prevent divison by zero error
    # Compute the error in the predictions 
    error = -(np.dot(y, np.log(predictions+epsilon).T) + np.dot((1-y), np.log(1-predictions+epsilon).T))
    # Compute the total cost of the predictions
    cost = 1/m * np.sum(error, axis=1)
    return np.squeeze(cost)

  def back_propagate(self, X, y):
    m = y.shape[1]
    # Returns the gradients for each parameter
    epsilon = 1e-5 # Prevent division by zero error
    # Stores the gradients 
    grads = {} 
    L = len(self.parameters)//2 # Number of hidden layers 
    # Compute the gradients for the output layer 
    dA = -np.divide(y, self.cache[-1]['A']+epsilon) + np.divide(1-y, 1-self.cache[-1]['A'] + epsilon)
    dZ = dA * self.dsigmoid(self.cache[-1]['Z'])
    dW = 1./m * np.dot(dZ, self.cache[-2]['A'].T)
    db = 1./m * np.sum(dZ, axis=1, keepdims=True)
    da_prev = np.dot(self.parameters['W'+str(L)].T, dZ) 
    grads['dW'+str(L)] = dW
    grads['db'+str(L)] = db
    # Calculate the grads for the rest of the layers
    for i in reversed(range(1, L)): 
      dA = da_prev
      dZ = dA * self.drelu(self.cache[i]['Z'])
      dW = 1./m * np.dot(dZ, self.cache[i-1]['A'].T)
      db = 1/m * np.sum(dZ, axis = 1, keepdims = True)
      grads['dW'+str(i)] = dW
      grads['db'+str(i)] = db
      # Calculate the gradient for the previous layer 
      da_prev = np.dot(self.parameters['W'+str(i)].T, dZ)
    return grads

  def train(self, X, y): 
    # Perform the training num_iters times
    for i in range(self.num_iters):
      # Get the predictions
      predictions = self.feed_forward(X)
      # Compute the total cost of the predictions 
      cost = self.computeCost(y, predictions)
      # Compute the gradients 
      grads = self.back_propagate(X, y)
      # Adjust the parameters of each layer 
      for j in range(1, len(self.layers)): 
        self.parameters['W'+str(j)] = self.parameters['W'+str(j)] - self.learning_rate*grads['dW'+str(j)]
        self.parameters['b'+str(j)] = self.parameters['b'+str(j)] - self.learning_rate*grads['db'+str(j)]
      # Save the cost 
      self.J_hist.append(cost)
      # Find the growth rate 
      if len(self.J_hist) > 3: 
        epsilon = 1e-5 # Prevent division by zero
        self.growth_rate = (self.J_hist[-1]-self.J_hist[-2])/(self.J_hist[-2]-self.J_hist[-3]+epsilon)
        
        if self.growth_rate < 0.25: 
          # Exit the loop if growth is slow 
            break
      # Print the cost for every 50 iterations 
      if i%50 == 0: 
        print(f'Cost at iteration {i}:', cost)
    print('Final cost is:', cost)
    # Flush the cache
    self.cache.clear()
    
  def predict(self, X, prepare=True): 
    # Check if the input needs to be prepared
    if prepare is True: 
      # Flatten the image matrix 
      X_flatten = X.reshape(64*64*3, 1)
      # Standardize the values of X
      X_flatten = X_flatten/255
    
    # Get the prediction 
    prediction = self.feed_forward(X_flatten)
    print('Prediction:', np.squeeze(prediction))

  def plotCost(self): 
    # Plot the cost hist
    plt.plot(self.J_hist)
    plt.xlabel('Iterations')
    plt.ylabel('Cost')
    plt.title('Cost function history')
    plt.savefig('Ok.png')
   

# Two layer neural network 
layer_dims = [n, 20, 7, 5, 1]
# Define a new model 
model = Model({
  'layers': layer_dims, 
  'learning_rate': 0.0005,
  'num_iters': 2000
})

model.train(X_flatten, y)

# Plot the final cost
model.plotCost()