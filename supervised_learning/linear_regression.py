from __future__ import print_function
import matplotlib.pyplot as plt
import numpy as np
from sklearn import datasets
import pandas as pd
import sys
import os
import math

# Import helper functions
dir_path = os.path.dirname(os.path.realpath(__file__))
sys.path.insert(0, dir_path + "/../utils")
from data_operation import mean_squared_error
from data_manipulation import train_test_split, polynomial_features
from loss_functions import SquareLoss
from optimization import GradientDescent



class LinearRegression(object):
    """Linear model for doing regression.
    Parameters:
    -----------
    n_iterations: float
        The number of training iterations the algorithm will tune the weights for.
    learning_rate: float
        The step length that will be used when updating the weights.
    gradient_descent: boolean
        True or false depending if gradient descent should be used when training. If 
        false then we use batch optimization by least squares.
    """
    def __init__(self, n_iterations=1500, learning_rate=0.001, gradient_descent=True):
        self.w = None
        self.n_iterations = n_iterations
        self.learning_rate = learning_rate
        self.gradient_descent = gradient_descent    # Opt. method. If False => Least squares
        self.square_loss = SquareLoss()

    def fit(self, X, y):
        # Insert constant ones as first column (for bias weights)
        X = np.insert(X, 0, 1, axis=1)
        # Get weights by gradient descent opt.
        if self.gradient_descent:
            n_features = np.shape(X)[1]
            # Initial weights randomly [0, 1]
            self.w = np.random.random((n_features, ))
            # Do gradient descent for n_iterations
            for _ in range(self.n_iterations):
                # Gradient of squared loss w.r.t the weights
                grad_w = self.square_loss.gradient(y, X, self.w)
                # Move against the gradient to minimize loss
                self.w -= self.learning_rate * grad_w
        # Get weights by least squares (by pseudoinverse)
        else:
            U, S, V = np.linalg.svd(X.T.dot(X))
            S = np.diag(S)
            X_sq_inv = V.dot(np.linalg.pinv(S)).dot(U.T)
            self.w = X_sq_inv.dot(X.T).dot(y)

    def predict(self, X):
        # Insert constant ones for bias weights
        X = np.insert(X, 0, 1, axis=1)
        y_pred = X.dot(self.w)
        return y_pred


class PolynomialRegression(LinearRegression):
    def __init__(self, degree, n_iterations=1500, learning_rate=0.001, gradient_descent=True):
        self.degree = degree
        super(PolynomialRegression, self).__init__(n_iterations, learning_rate, gradient_descent)

    def fit(self, X, y):
        X_transformed = polynomial_features(X, degree=self.degree)
        super(PolynomialRegression, self).fit(X_transformed, y)

    def predict(self, X):
        X_transformed = polynomial_features(X, degree=self.degree)
        return super(PolynomialRegression, self).predict(X_transformed)


def main():

    # Load temperature data
    data = pd.read_csv('data/TempLinkoping2016.txt', sep="\t")

    time = np.atleast_2d(data["time"].as_matrix()).T
    temp = np.atleast_2d(data["temp"].as_matrix()).T

    X = time
    y = temp

    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.4)

    clf = PolynomialRegression(degree=2, n_iterations=3000)
    clf.fit(X_train, y_train)
    y_pred = clf.predict(X_test)

    mse = mean_squared_error(y_test, y_pred)

    # Print the mean squared error
    print ("Mean Squared Error:", mse)

    # Plot the results
    m = plt.scatter(X_test[:, 0], y_test, color='gray', s=10)
    p = plt.scatter(X_test[:, 0], y_pred, color='black', s=15)
    plt.suptitle("Linear Regression of temperature data in Linkoping, Sweden 2016")
    plt.title("(%.2f MSE)" % mse)
    plt.xlabel('Fraction of year')
    plt.ylabel('Temperature in Celcius')
    plt.legend((m, p), ("Measurements", "Prediction"), scatterpoints=1, loc='lower right')

    plt.show()

if __name__ == "__main__":
    main()
