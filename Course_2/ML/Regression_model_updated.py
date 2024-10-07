import pandas as pd
import numpy as np
import time as dt
import matplotlib.pyplot as plt

class Model(object):
    """Модель линейной регрессии"""
    def __init__(self, shape):
        """Initialize Model

        Args:
            shape (tuple-like): shape of X dataset
        """
        
        self.shape = shape
        self.b = np.zeros([self.shape[1] + 1, 1])
        self.x0 = pd.DataFrame({'x0': np.ones(self.shape[0])})
        
    def predict(self, X=pd.DataFrame()):
        if X.shape==(0,0):
            X=self.x_all
        
        return X @ self.b
    
    def error(self,Y,X=pd.DataFrame()):
        if X.shape==(0,0):
            X=self.x_all
            
        return 1/(2*self.shape[0]) * (Y - self.predict(X)).T @ (Y - self.predict(X))
    
    def fit(self, X, Y, alpha=0.01, accuracy=0.01, max_steps=10000):
        start_time = dt.time()
        x_all = pd.concat([self.x0, X], axis=1)
        self.x_all = x_all
        steps, errors = [], []
        step = 0
        for _ in range(1000):
            dJ_b = -1/self.shape[0] * x_all.T @ (Y - self.predict(x_all))
            self.b -= alpha * dJ_b
            new_err = self.error(Y)
            step += 1
            steps.append(step)
            errors.append(new_err)
        stop_time=dt.time()
        self.study_time_seconds = stop_time-start_time
        
        return steps, errors, self.b
    
    
    def plot(self, Y,X=pd.DataFrame()):
        if X.shape==(0,0):
            X=self.x_all

        yy=self.predict()
        plt.scatter(yy,Y)
        plt.plot(yy,yy,c='r')
        plt.show()
    
    def score(self, Y,X=pd.DataFrame() ):
        y_pred = self.predict()
        ss_res = np.sum((Y - y_pred)**2)
        ss_total = np.sum((Y - np.mean(Y))**2)
        r2 = 1 - (ss_res / ss_total)
        return r2

    def MSE(self, Y,X=pd.DataFrame() ):
        Y_pred = self.predict()
        MSE = (1/Y_pred.shape[0]) * np.sum((Y_pred - Y)**2)
        return MSE

    def RMSE(self, Y,X=pd.DataFrame() ):
        return np.sqrt(self.MSE(Y))

    def MAE(self, Y,X=pd.DataFrame() ):
        Y_pred = self.predict()
        MAE = (1/Y_pred.shape[0]) * np.sum(abs(Y_pred - Y))
        return MAE

    def MAPE(self, Y,X=pd.DataFrame() ):
        Y_pred = self.predict()
        MAPE = (1/Y_pred.shape[0]) * np.sum(abs(Y_pred - Y)/Y)*100
        return MAPE
    
    def show_metrics(self, y,X=pd.DataFrame() ):
        text=f'''
Error after gradient descent = {self.error(y).iloc[0,0]}
Mean Absolute Percentage Error = {round(self.MAPE(y)[0],2)}%
R2 Score = {round(self.score(y)[0],4)}
Root of Mean Squared Error = {round(self.RMSE(y)[0],2)}
Mean Squared Error = {round(self.MSE(y)[0],2)}
Mean Absolute Error = {round(self.MAE(y)[0],2)}
Study Time = {self.study_time_seconds*1000} ms
        '''
        print(text)
    
    def complex_out(self,x,y):
        self.fit(x, y)
        self.plot(y)
        self.show_metrics(y)