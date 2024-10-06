def find_params(x):
    
    import numpy as np
    
    Median = np.median(x)
    
    Q1 = np.quantile(x,0.25)
    Q3 = np.quantile(x,0.75)
    
    R=Q3-Q1
    Range = [Q1-1.5*R,Q3+1.5*R]
    
    Atypical = x[np.logical_or(x<Range[0],x>Range[1])]
    
    return dict(list(zip('Median,Q1,Q3,R,Range,Atypical'.split(','),[Median,Q1,Q3,R,Range,Atypical])))