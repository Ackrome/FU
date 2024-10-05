import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

class Model(object):
    """Модель парной линейной регрессии"""
    
    def __init__(self):
        self.b0 = 0
        self.b1 = 0
        
    def predict(self, X, x_col=0):
        if str(type(X))=="<class 'pandas.core.frame.DataFrame'>":
            X=X.iloc[:,x_col]
        return self.b0 + self.b1 * X
    
    def error(self, X, Y, x_col=0,y_col=0):
        if str(type(X))=="<class 'pandas.core.frame.DataFrame'>":
            X=X.iloc[:,x_col]
        if str(type(Y))=="<class 'pandas.core.frame.DataFrame'>":
           Y=Y.iloc[:,y_col]
        s = sum(((self.predict(X) - Y)**2) / (2 * len(X)))

        return s
    
    def fit(self, X, Y, alpha=1, accuracy=0.01, max_steps=10000,til=1e-6, x_col=0,y_col=0):
        if str(type(X))=="<class 'pandas.core.frame.DataFrame'>":
            X=X.iloc[:,x_col]
        if str(type(Y))=="<class 'pandas.core.frame.DataFrame'>":
            Y=Y.iloc[:,y_col]
                
        steps, errors = [], []
        step = 0
        
        for _ in range(max_steps):
            dJ0 = sum(self.predict(X) - Y) /len(X)
            dJ1 = sum((self.predict(X) - Y) * X) /len(X)
            self.b0 -= alpha * dJ0
            self.b1 -= alpha * dJ1    
            new_err = self.error(X, Y)
            step += 1            
            steps.append(step)
            errors.append(new_err)
            
            if len(errors)>=2:
                if (errors[-2]-errors[-1])<til:
                    print('Ошибка перестала существенно меняться')
                    break
                
                elif (errors[-2]-errors[-1])>0:
                    alpha=alpha/2
                    
                    
                    
                    
            elif len(errors)==max_steps:
                print('Все шаги пройдены')
        
        return steps, errors
    
    def plot(self,X, Y, x_col=0,y_col=0):
        if str(type(X))=="<class 'pandas.core.frame.DataFrame'>":
            X=X.iloc[:,x_col]
        if str(type(Y))=="<class 'pandas.core.frame.DataFrame'>":
            Y=Y.iloc[:,y_col]
        xmin=(min(X)-1)//1
        xmax=(max(X)+1)//1
        X0 = np.linspace(xmin, xmax, 100)
        Y0 = self.predict(X0)
        plt.figure()
        plt.scatter(X, Y)
        plt.plot(X0, Y0, 'r')
        plt.show()