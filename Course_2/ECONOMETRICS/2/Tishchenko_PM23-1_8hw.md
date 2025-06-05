
```python
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
# from statsmodels.api import OLS, add_constant
from linearmodels import PanelOLS, RandomEffects, PooledOLS
from linearmodels.panel import compare
from scipy.stats import chi2, t
```
# Загрузим данные


```python
data = pd.read_excel('data/debtOECD.xls', 'datadebt', usecols=range(1, 13))
data
```
text_plain_output:

     country  year    growth     ngs         pop  school   openness  \
0          1  1979       NaN     NaN  225055.000     NaN        NaN   
1          1  1980 -1.852161  19.465  225055.000   11.86  20.751923   
2          1  1981  1.452103  20.662  227726.463   11.86  20.062474   
3          1  1982 -2.367766  19.104  229966.237   11.86  18.158172   
4          1  1983  3.973262  17.042  232187.835   11.86  17.258970   
..       ...   ...       ...     ...         ...     ...        ...   
553       18  2005  4.425367  24.510    8986.000   11.41  89.038791   
554       18  2006  3.931027  27.153    9002.000   11.41  94.117615   
555       18  2007  3.148673  29.566    9017.000   11.41  96.279448   
556       18  2008 -0.343097  28.904    9031.000   11.41  99.657369   
557       18  2009 -5.409407  23.441    9045.000   11.41  90.136776   

          infl  total_dep  bankcrisis   debtgov  realGDP  
0          NaN        NaN         NaN       NaN      NaN  
1    13.509370  50.796404         0.0  0.458956  25090.0  
2    10.315534  50.382611         0.0  0.451561  25454.0  
3     6.160616  50.144179         0.0  0.504318  24852.0  
4     3.212435  50.057573         0.0  0.537802  25839.0  
..         ...        ...         ...       ...      ...  
553   0.453171  52.800035         0.0  0.655969  34856.0  
554   1.360215  52.567226         0.0  0.586981  36227.0  
555   2.212169  52.461504         0.0  0.529283  37367.0  
556   3.437049  52.528023         0.0  0.515149  37239.0  
557  -0.278429  52.820595         0.0  0.578353  35225.0  

[558 rows x 12 columns]



```python
data = data.set_index(['country', 'year'])
data
```
text_plain_output:

                growth     ngs         pop  school   openness       infl  \
country year                                                               
1       1979       NaN     NaN  225055.000     NaN        NaN        NaN   
        1980 -1.852161  19.465  225055.000   11.86  20.751923  13.509370   
        1981  1.452103  20.662  227726.463   11.86  20.062474  10.315534   
        1982 -2.367766  19.104  229966.237   11.86  18.158172   6.160616   
        1983  3.973262  17.042  232187.835   11.86  17.258970   3.212435   
...                ...     ...         ...     ...        ...        ...   
18      2005  4.425367  24.510    8986.000   11.41  89.038791   0.453171   
        2006  3.931027  27.153    9002.000   11.41  94.117615   1.360215   
        2007  3.148673  29.566    9017.000   11.41  96.279448   2.212169   
        2008 -0.343097  28.904    9031.000   11.41  99.657369   3.437049   
        2009 -5.409407  23.441    9045.000   11.41  90.136776  -0.278429   

              total_dep  bankcrisis   debtgov  realGDP  
country year                                            
1       1979        NaN         NaN       NaN      NaN  
        1980  50.796404         0.0  0.458956  25090.0  
        1981  50.382611         0.0  0.451561  25454.0  
        1982  50.144179         0.0  0.504318  24852.0  
        1983  50.057573         0.0  0.537802  25839.0  
...                 ...         ...       ...      ...  
18      2005  52.800035         0.0  0.655969  34856.0  
        2006  52.567226         0.0  0.586981  36227.0  
        2007  52.461504         0.0  0.529283  37367.0  
        2008  52.528023         0.0  0.515149  37239.0  
        2009  52.820595         0.0  0.578353  35225.0  

[558 rows x 10 columns]



```python
data.isna().sum()
```
text_plain_output:

growth        18
ngs           18
pop            0
school        18
openness      18
infl          18
total_dep     18
bankcrisis    18
debtgov       18
realGDP       18
dtype: int64



```python
data.dropna(inplace=True)
```

```python
data.describe()
```
text_plain_output:

           growth         ngs            pop      school    openness  \
count  540.000000  540.000000     540.000000  540.000000  540.000000   
mean     1.729294   21.862954   44767.227372    8.890741   63.362239   
std      2.259371    4.812356   62053.269581    1.848069   30.030518   
min     -8.452431    5.117000    4072.517000    3.780000   16.106037   
25%      0.663914   19.070500    8815.940750    7.695000   44.779200   
50%      1.995269   21.420500   15962.649000    9.095000   57.637157   
75%      3.168777   24.624250   57793.329500   10.072500   73.527472   
max      8.748125   39.897000  304375.000000   12.050000  170.525815   

             infl   total_dep  bankcrisis     debtgov       realGDP  
count  540.000000  540.000000  540.000000  540.000000    540.000000  
mean     4.432042   50.139157    0.170370    0.742482  27461.155556  
std      4.616799    3.342928    0.376306    0.310144   6874.418694  
min     -9.628535   43.124670    0.000000    0.162530  10586.000000  
25%      1.827516   47.583379    0.000000    0.531158  22567.500000  
50%      2.837309   49.808985    0.000000    0.676252  27003.000000  
75%      5.244843   52.538560    0.000000    0.900066  31605.250000  
max     28.783333   59.080850    1.000000    2.126027  51101.000000  


# ![image.png](attachment:image.png)

Сделаем преобразования, о которых нас просят


```python
data['log_realGDP'] = np.log(data['realGDP'])
data['pop_growth_rate'] = data.groupby('country')['pop'].pct_change()
data['debtgov_quad'] = np.power(data['debtgov'], 2)
```

```python
col_names_regr = [
    'ngs', 'log_realGDP', 'pop_growth_rate',
    'openness', 'school', 'total_dep',
    'infl', 'bankcrisis', 'debtgov', 'debtgov_quad'
]
```
Добавим лаги независимых переменных


```python
for col_name in col_names_regr:
    lag_col_name = 'lag_' + col_name
    data[lag_col_name] = data.groupby('country')[col_name].shift(1)
```
Исключим появившиеся пропуски


```python
data = data.dropna()
```
Первые лаги столбцов независимых переменных



```python
col_names_regr = ['lag_' + col_name for col_name in col_names_regr]
```
Модели


```python
models = {
    'PooledOLS': PooledOLS.from_formula,
    'FixedEffects': PanelOLS.from_formula,
    'RandomEffects': RandomEffects.from_formula
}
```
Формулы для моделей


```python
formulas = {
    'PooledOLS': 'growth ~ 1 + ' + ' + '.join(col_names_regr),
    'FixedEffects': 'growth ~ 1 + ' + ' + '.join(col_names_regr) + ' + EntityEffects',
    'RandomEffects': 'growth ~ 1 + ' + ' + '.join(col_names_regr)
}
```
Словарь результатов


```python
models_result = {
    'PooledOLS': None,
    'FixedEffects': None,
    'RandomEffects': None    
}
```
Произведем обучение моделей


```python
for model in models:
    model_fit = models[model](formula=formulas[model],data=data).fit()
    models_result[model] = model_fit
```
Выведем результаты обучения



```python
for model in models_result:
    print(f'Модель: {model}')
    print(f'Формула: {formulas[model]}', end='\n'*2)
    display(models_result[model].summary)
    print(end='\n'*7)
```
text_plain_output:

<class 'linearmodels.compat.statsmodels.Summary'>
"""
                          PooledOLS Estimation Summary                          
================================================================================
Dep. Variable:                 growth   R-squared:                        0.2557
Estimator:                  PooledOLS   R-squared (Between):             -2.9709
No. Observations:                 504   R-squared (Within):               0.3131
Date:                Thu, Jun 05 2025   R-squared (Overall):              0.2557
Time:                        10:37:27   Log-likelihood                   -1052.2
Cov. Estimator:            Unadjusted                                           
                                        F-statistic:                      16.939
Entities:                          18   P-value                           0.0000
Avg Obs:                       28.000   Distribution:                  F(10,493)
Min Obs:                       28.000                                           
Max Obs:                       28.000   F-statistic (robust):             16.939
                                        P-value                           0.0000
Time periods:                      28   Distribution:                  F(10,493)
Avg Obs:                       18.000                                           
Min Obs:                       18.000                                           
Max Obs:                       18.000                                           
                                                                                
                                  Parameter Estimates                                  
=======================================================================================
                     Parameter  Std. Err.     T-stat    P-value    Lower CI    Upper CI
---------------------------------------------------------------------------------------
Intercept               49.851     6.1622     8.0899     0.0000      37.744      61.959
lag_ngs                 0.0622     0.0208     2.9967     0.0029      0.0214      0.1031
lag_log_realGDP        -5.5177     0.6439    -8.5697     0.0000     -6.7827     -4.2526
lag_pop_growth_rate    -29.195     25.054    -1.1653     0.2445     -78.422      20.032
lag_openness           -0.0078     0.0035    -2.2412     0.0255     -0.0146     -0.0010
lag_school              0.3509     0.0767     4.5738     0.0000      0.2001      0.5016
lag_total_dep           0.0771     0.0310     2.4897     0.0131      0.0163      0.1379
lag_infl               -0.2247     0.0298    -7.5474     0.0000     -0.2831     -0.1662
lag_bankcrisis         -1.8412     0.2515    -7.3213     0.0000     -2.3353     -1.3471
lag_debtgov             4.6547     1.3600     3.4226     0.0007      1.9826      7.3267
lag_debtgov_quad       -2.7047     0.7075    -3.8228     0.0001     -4.0949     -1.3146
=======================================================================================
"""


text_latex_output:

\begin{center}
\begin{tabular}{lclc}
\toprule
\textbf{Dep. Variable:}         &       growth       & \textbf{  R-squared:         }   &      0.2557      \\
\textbf{Estimator:}             &     PooledOLS      & \textbf{  R-squared (Between):}  &     -2.9709      \\
\textbf{No. Observations:}      &        504         & \textbf{  R-squared (Within):}   &      0.3131      \\
\textbf{Date:}                  &  Thu, Jun 05 2025  & \textbf{  R-squared (Overall):}  &      0.2557      \\
\textbf{Time:}                  &      10:37:27      & \textbf{  Log-likelihood     }   &     -1052.2      \\
\textbf{Cov. Estimator:}        &     Unadjusted     & \textbf{                     }   &                  \\
\textbf{}                       &                    & \textbf{  F-statistic:       }   &      16.939      \\
\textbf{Entities:}              &         18         & \textbf{  P-value            }   &      0.0000      \\
\textbf{Avg Obs:}               &       28.000       & \textbf{  Distribution:      }   &    F(10,493)     \\
\textbf{Min Obs:}               &       28.000       & \textbf{                     }   &                  \\
\textbf{Max Obs:}               &       28.000       & \textbf{  F-statistic (robust):} &      16.939      \\
\textbf{}                       &                    & \textbf{  P-value            }   &      0.0000      \\
\textbf{Time periods:}          &         28         & \textbf{  Distribution:      }   &    F(10,493)     \\
\textbf{Avg Obs:}               &       18.000       & \textbf{                     }   &                  \\
\textbf{Min Obs:}               &       18.000       & \textbf{                     }   &                  \\
\textbf{Max Obs:}               &       18.000       & \textbf{                     }   &                  \\
\textbf{}                       &                    & \textbf{                     }   &                  \\
\bottomrule
\end{tabular}
\begin{tabular}{lcccccc}
                                & \textbf{Parameter} & \textbf{Std. Err.} & \textbf{T-stat} & \textbf{P-value} & \textbf{Lower CI} & \textbf{Upper CI}  \\
\midrule
\textbf{Intercept}              &       49.851       &       6.1622       &      8.0899     &      0.0000      &       37.744      &       61.959       \\
\textbf{lag\_ngs}               &       0.0622       &       0.0208       &      2.9967     &      0.0029      &       0.0214      &       0.1031       \\
\textbf{lag\_log\_realGDP}      &      -5.5177       &       0.6439       &     -8.5697     &      0.0000      &      -6.7827      &      -4.2526       \\
\textbf{lag\_pop\_growth\_rate} &      -29.195       &       25.054       &     -1.1653     &      0.2445      &      -78.422      &       20.032       \\
\textbf{lag\_openness}          &      -0.0078       &       0.0035       &     -2.2412     &      0.0255      &      -0.0146      &      -0.0010       \\
\textbf{lag\_school}            &       0.3509       &       0.0767       &      4.5738     &      0.0000      &       0.2001      &       0.5016       \\
\textbf{lag\_total\_dep}        &       0.0771       &       0.0310       &      2.4897     &      0.0131      &       0.0163      &       0.1379       \\
\textbf{lag\_infl}              &      -0.2247       &       0.0298       &     -7.5474     &      0.0000      &      -0.2831      &      -0.1662       \\
\textbf{lag\_bankcrisis}        &      -1.8412       &       0.2515       &     -7.3213     &      0.0000      &      -2.3353      &      -1.3471       \\
\textbf{lag\_debtgov}           &       4.6547       &       1.3600       &      3.4226     &      0.0007      &       1.9826      &       7.3267       \\
\textbf{lag\_debtgov\_quad}     &      -2.7047       &       0.7075       &     -3.8228     &      0.0001      &      -4.0949      &      -1.3146       \\
\bottomrule
\end{tabular}
%\caption{PooledOLS Estimation Summary}
\end{center}


text_plain_output:

<class 'linearmodels.compat.statsmodels.Summary'>
"""
                          PanelOLS Estimation Summary                           
================================================================================
Dep. Variable:                 growth   R-squared:                        0.3647
Estimator:                   PanelOLS   R-squared (Between):             -35.786
No. Observations:                 504   R-squared (Within):               0.3647
Date:                Thu, Jun 05 2025   R-squared (Overall):             -0.2668
Time:                        10:37:27   Log-likelihood                   -1007.8
Cov. Estimator:            Unadjusted                                           
                                        F-statistic:                      27.328
Entities:                          18   P-value                           0.0000
Avg Obs:                       28.000   Distribution:                  F(10,476)
Min Obs:                       28.000                                           
Max Obs:                       28.000   F-statistic (robust):             27.328
                                        P-value                           0.0000
Time periods:                      28   Distribution:                  F(10,476)
Avg Obs:                       18.000                                           
Min Obs:                       18.000                                           
Max Obs:                       18.000                                           
                                                                                
                                  Parameter Estimates                                  
=======================================================================================
                     Parameter  Std. Err.     T-stat    P-value    Lower CI    Upper CI
---------------------------------------------------------------------------------------
Intercept               78.286     10.176     7.6934     0.0000      58.292      98.281
lag_ngs                 0.1037     0.0325     3.1880     0.0015      0.0398      0.1676
lag_log_realGDP        -7.5749     1.0140    -7.4701     0.0000     -9.5674     -5.5823
lag_pop_growth_rate    -92.478     34.258    -2.6995     0.0072     -159.79     -25.163
lag_openness            0.0093     0.0132     0.7046     0.4814     -0.0166      0.0352
lag_school             -0.2159     0.2307    -0.9358     0.3499     -0.6691      0.2374
lag_total_dep          -0.0065     0.0550    -0.1182     0.9060     -0.1146      0.1016
lag_infl               -0.3204     0.0382    -8.3872     0.0000     -0.3955     -0.2454
lag_bankcrisis         -1.9146     0.2471    -7.7487     0.0000     -2.4001     -1.4291
lag_debtgov             5.1661     1.6418     3.1465     0.0018      1.9399      8.3922
lag_debtgov_quad       -2.5348     0.8047    -3.1502     0.0017     -4.1159     -0.9537
=======================================================================================

F-test for Poolability: 5.3872
P-value: 0.0000
Distribution: F(17,476)

Included effects: Entity
"""


text_latex_output:

\begin{center}
\begin{tabular}{lclc}
\toprule
\textbf{Dep. Variable:}         &       growth       & \textbf{  R-squared:         }   &      0.3647      \\
\textbf{Estimator:}             &      PanelOLS      & \textbf{  R-squared (Between):}  &     -35.786      \\
\textbf{No. Observations:}      &        504         & \textbf{  R-squared (Within):}   &      0.3647      \\
\textbf{Date:}                  &  Thu, Jun 05 2025  & \textbf{  R-squared (Overall):}  &     -0.2668      \\
\textbf{Time:}                  &      10:37:27      & \textbf{  Log-likelihood     }   &     -1007.8      \\
\textbf{Cov. Estimator:}        &     Unadjusted     & \textbf{                     }   &                  \\
\textbf{}                       &                    & \textbf{  F-statistic:       }   &      27.328      \\
\textbf{Entities:}              &         18         & \textbf{  P-value            }   &      0.0000      \\
\textbf{Avg Obs:}               &       28.000       & \textbf{  Distribution:      }   &    F(10,476)     \\
\textbf{Min Obs:}               &       28.000       & \textbf{                     }   &                  \\
\textbf{Max Obs:}               &       28.000       & \textbf{  F-statistic (robust):} &      27.328      \\
\textbf{}                       &                    & \textbf{  P-value            }   &      0.0000      \\
\textbf{Time periods:}          &         28         & \textbf{  Distribution:      }   &    F(10,476)     \\
\textbf{Avg Obs:}               &       18.000       & \textbf{                     }   &                  \\
\textbf{Min Obs:}               &       18.000       & \textbf{                     }   &                  \\
\textbf{Max Obs:}               &       18.000       & \textbf{                     }   &                  \\
\textbf{}                       &                    & \textbf{                     }   &                  \\
\bottomrule
\end{tabular}
\begin{tabular}{lcccccc}
                                & \textbf{Parameter} & \textbf{Std. Err.} & \textbf{T-stat} & \textbf{P-value} & \textbf{Lower CI} & \textbf{Upper CI}  \\
\midrule
\textbf{Intercept}              &       78.286       &       10.176       &      7.6934     &      0.0000      &       58.292      &       98.281       \\
\textbf{lag\_ngs}               &       0.1037       &       0.0325       &      3.1880     &      0.0015      &       0.0398      &       0.1676       \\
\textbf{lag\_log\_realGDP}      &      -7.5749       &       1.0140       &     -7.4701     &      0.0000      &      -9.5674      &      -5.5823       \\
\textbf{lag\_pop\_growth\_rate} &      -92.478       &       34.258       &     -2.6995     &      0.0072      &      -159.79      &      -25.163       \\
\textbf{lag\_openness}          &       0.0093       &       0.0132       &      0.7046     &      0.4814      &      -0.0166      &       0.0352       \\
\textbf{lag\_school}            &      -0.2159       &       0.2307       &     -0.9358     &      0.3499      &      -0.6691      &       0.2374       \\
\textbf{lag\_total\_dep}        &      -0.0065       &       0.0550       &     -0.1182     &      0.9060      &      -0.1146      &       0.1016       \\
\textbf{lag\_infl}              &      -0.3204       &       0.0382       &     -8.3872     &      0.0000      &      -0.3955      &      -0.2454       \\
\textbf{lag\_bankcrisis}        &      -1.9146       &       0.2471       &     -7.7487     &      0.0000      &      -2.4001      &      -1.4291       \\
\textbf{lag\_debtgov}           &       5.1661       &       1.6418       &      3.1465     &      0.0018      &       1.9399      &       8.3922       \\
\textbf{lag\_debtgov\_quad}     &      -2.5348       &       0.8047       &     -3.1502     &      0.0017      &      -4.1159      &      -0.9537       \\
\bottomrule
\end{tabular}
%\caption{PanelOLS Estimation Summary}
\end{center}

F-test for Poolability: 5.3872 \newline
 P-value: 0.0000 \newline
 Distribution: F(17,476) \newline
  \newline
 Included effects: Entity


text_plain_output:

<class 'linearmodels.compat.statsmodels.Summary'>
"""
                        RandomEffects Estimation Summary                        
================================================================================
Dep. Variable:                 growth   R-squared:                        0.2557
Estimator:              RandomEffects   R-squared (Between):             -2.9709
No. Observations:                 504   R-squared (Within):               0.3131
Date:                Thu, Jun 05 2025   R-squared (Overall):              0.2557
Time:                        10:37:27   Log-likelihood                   -1052.2
Cov. Estimator:            Unadjusted                                           
                                        F-statistic:                      16.939
Entities:                          18   P-value                           0.0000
Avg Obs:                       28.000   Distribution:                  F(10,493)
Min Obs:                       28.000                                           
Max Obs:                       28.000   F-statistic (robust):             16.939
                                        P-value                           0.0000
Time periods:                      28   Distribution:                  F(10,493)
Avg Obs:                       18.000                                           
Min Obs:                       18.000                                           
Max Obs:                       18.000                                           
                                                                                
                                  Parameter Estimates                                  
=======================================================================================
                     Parameter  Std. Err.     T-stat    P-value    Lower CI    Upper CI
---------------------------------------------------------------------------------------
Intercept               49.851     6.1622     8.0899     0.0000      37.744      61.959
lag_ngs                 0.0622     0.0208     2.9967     0.0029      0.0214      0.1031
lag_log_realGDP        -5.5177     0.6439    -8.5697     0.0000     -6.7827     -4.2526
lag_pop_growth_rate    -29.195     25.054    -1.1653     0.2445     -78.422      20.032
lag_openness           -0.0078     0.0035    -2.2412     0.0255     -0.0146     -0.0010
lag_school              0.3509     0.0767     4.5738     0.0000      0.2001      0.5016
lag_total_dep           0.0771     0.0310     2.4897     0.0131      0.0163      0.1379
lag_infl               -0.2247     0.0298    -7.5474     0.0000     -0.2831     -0.1662
lag_bankcrisis         -1.8412     0.2515    -7.3213     0.0000     -2.3353     -1.3471
lag_debtgov             4.6547     1.3600     3.4226     0.0007      1.9826      7.3267
lag_debtgov_quad       -2.7047     0.7075    -3.8228     0.0001     -4.0949     -1.3146
=======================================================================================
"""


text_latex_output:

\begin{center}
\begin{tabular}{lclc}
\toprule
\textbf{Dep. Variable:}         &       growth       & \textbf{  R-squared:         }   &      0.2557      \\
\textbf{Estimator:}             &   RandomEffects    & \textbf{  R-squared (Between):}  &     -2.9709      \\
\textbf{No. Observations:}      &        504         & \textbf{  R-squared (Within):}   &      0.3131      \\
\textbf{Date:}                  &  Thu, Jun 05 2025  & \textbf{  R-squared (Overall):}  &      0.2557      \\
\textbf{Time:}                  &      10:37:27      & \textbf{  Log-likelihood     }   &     -1052.2      \\
\textbf{Cov. Estimator:}        &     Unadjusted     & \textbf{                     }   &                  \\
\textbf{}                       &                    & \textbf{  F-statistic:       }   &      16.939      \\
\textbf{Entities:}              &         18         & \textbf{  P-value            }   &      0.0000      \\
\textbf{Avg Obs:}               &       28.000       & \textbf{  Distribution:      }   &    F(10,493)     \\
\textbf{Min Obs:}               &       28.000       & \textbf{                     }   &                  \\
\textbf{Max Obs:}               &       28.000       & \textbf{  F-statistic (robust):} &      16.939      \\
\textbf{}                       &                    & \textbf{  P-value            }   &      0.0000      \\
\textbf{Time periods:}          &         28         & \textbf{  Distribution:      }   &    F(10,493)     \\
\textbf{Avg Obs:}               &       18.000       & \textbf{                     }   &                  \\
\textbf{Min Obs:}               &       18.000       & \textbf{                     }   &                  \\
\textbf{Max Obs:}               &       18.000       & \textbf{                     }   &                  \\
\textbf{}                       &                    & \textbf{                     }   &                  \\
\bottomrule
\end{tabular}
\begin{tabular}{lcccccc}
                                & \textbf{Parameter} & \textbf{Std. Err.} & \textbf{T-stat} & \textbf{P-value} & \textbf{Lower CI} & \textbf{Upper CI}  \\
\midrule
\textbf{Intercept}              &       49.851       &       6.1622       &      8.0899     &      0.0000      &       37.744      &       61.959       \\
\textbf{lag\_ngs}               &       0.0622       &       0.0208       &      2.9967     &      0.0029      &       0.0214      &       0.1031       \\
\textbf{lag\_log\_realGDP}      &      -5.5177       &       0.6439       &     -8.5697     &      0.0000      &      -6.7827      &      -4.2526       \\
\textbf{lag\_pop\_growth\_rate} &      -29.195       &       25.054       &     -1.1653     &      0.2445      &      -78.422      &       20.032       \\
\textbf{lag\_openness}          &      -0.0078       &       0.0035       &     -2.2412     &      0.0255      &      -0.0146      &      -0.0010       \\
\textbf{lag\_school}            &       0.3509       &       0.0767       &      4.5738     &      0.0000      &       0.2001      &       0.5016       \\
\textbf{lag\_total\_dep}        &       0.0771       &       0.0310       &      2.4897     &      0.0131      &       0.0163      &       0.1379       \\
\textbf{lag\_infl}              &      -0.2247       &       0.0298       &     -7.5474     &      0.0000      &      -0.2831      &      -0.1662       \\
\textbf{lag\_bankcrisis}        &      -1.8412       &       0.2515       &     -7.3213     &      0.0000      &      -2.3353      &      -1.3471       \\
\textbf{lag\_debtgov}           &       4.6547       &       1.3600       &      3.4226     &      0.0007      &       1.9826      &       7.3267       \\
\textbf{lag\_debtgov\_quad}     &      -2.7047       &       0.7075       &     -3.8228     &      0.0001      &      -4.0949      &      -1.3146       \\
\bottomrule
\end{tabular}
%\caption{RandomEffects Estimation Summary}
\end{center}


Напишем функцию для форматирования данных в таблице


```python
def format_val(val, std, pval, alpha=0.05, rounder=3):
    # Format value and standard deviation as strings with 4 decimal places
    val_str = np.round(val, rounder).astype(str)
    std_str = np.round(std, rounder).astype(str)
    
    # Combine into "value (std)" format
    base = np.char.add(np.char.add(np.char.add(val_str, ' ('), std_str), ')')
    
    # Append '*' if p-value is below significance level
    condition = pval < alpha
    result = np.where(condition, np.char.add(base, '*'), base)
    
    return result
```
Параметры моделей


```python
params = ['Intercept'] + col_names_regr
```

```python
# результаты моделей, * - значимый коэффициент
df_params = pd.DataFrame({model: format_val(models_result[model].params.values,models_result[model].std_errors.values,models_result[model].pvalues.values) for model in models_result},).set_index(pd.Index(params))
df_params
```
text_plain_output:

                            PooledOLS       FixedEffects     RandomEffects
Intercept             49.851 (6.162)*   78.286 (10.176)*   49.851 (6.162)*
lag_ngs                0.062 (0.021)*     0.104 (0.033)*    0.062 (0.021)*
lag_log_realGDP       -5.518 (0.644)*    -7.575 (1.014)*   -5.518 (0.644)*
lag_pop_growth_rate  -29.195 (25.054)  -92.478 (34.258)*  -29.195 (25.054)
lag_openness          -0.008 (0.003)*      0.009 (0.013)   -0.008 (0.003)*
lag_school             0.351 (0.077)*     -0.216 (0.231)    0.351 (0.077)*
lag_total_dep          0.077 (0.031)*     -0.006 (0.055)    0.077 (0.031)*
lag_infl               -0.225 (0.03)*     -0.32 (0.038)*    -0.225 (0.03)*
lag_bankcrisis        -1.841 (0.251)*    -1.915 (0.247)*   -1.841 (0.251)*
lag_debtgov             4.655 (1.36)*     5.166 (1.642)*     4.655 (1.36)*
lag_debtgov_quad      -2.705 (0.708)*    -2.535 (0.805)*   -2.705 (0.708)*


# ![image.png](attachment:image.png)

Пройдем по всем парам моделей

## PooledOLS и FixedEffects


```python
models_result['FixedEffects'].f_pooled
```
text_plain_output:

Pooled F-statistic
H0: Effects are zero
Statistic: 5.3872
P-value: 0.0000
Distributed: F(17,476)
WaldTestStatistic, id: 0x24e038cec10


## FixedEffects и RandomEffects


```python
def hausman_test(fe_model, re_model):
    """
    Проводит тест Хаусмана для сравнения фиксированных (FE) и случайных (RE) эффектов.
    
    Аргументы:
    - fe_model: модель с фиксированными эффектами (объект с атрибутами params и cov).
    - re_model: модель со случайными эффектами (объект с атрибутами params и cov).
    
    Возвращает:
    - stat: значение статистики теста.
    - p_value: p-значение для статистики.
    - df: степени свободы.
    - conclusion: вывод на основе p-значения (на русском языке).
    """
    # 1. Извлечение общих коэффициентов
    common_coef = fe_model.params.index.intersection(re_model.params.index)
    b_fe = fe_model.params.loc[common_coef].values
    b_re = re_model.params.loc[common_coef].values
    
    # 2. Ковариационные матрицы для общих коэффициентов
    V_fe = fe_model.cov.loc[common_coef, common_coef].values
    V_re = re_model.cov.loc[common_coef, common_coef].values
    
    # 3. Разность коэффициентов и ковариационных матриц
    coeff_diff = b_fe - b_re
    cov_diff = V_fe - V_re
    
    # 4. Обращение матрицы разности ковариаций
    try:
        inv_cov_diff = np.linalg.inv(cov_diff)
    except np.linalg.LinAlgError:
        inv_cov_diff = np.linalg.pinv(cov_diff)  # Используем псевдообратную матрицу при сингулярности
    
    # 5. Вычисление статистики теста
    stat = coeff_diff.T @ inv_cov_diff @ coeff_diff
    df = len(coeff_diff)
    p_value = 1 - chi2.cdf(stat, df)
    
    # 6. Вывод на основе p-значения
    conclusion = "Выбирайте Fixed Effects (p-value < 0.05)" if p_value < 0.05 else "Выбирайте Random Effects (p-value >= 0.05)"
    
    return stat, p_value, df, conclusion
```

```python
hausman_results = hausman_test(models_result['FixedEffects'],models_result['RandomEffects'])

print(f'''Статтистика: {hausman_results[0]}
p-value: {hausman_results[1]}
Степени свободы: {hausman_results[2]}
f'Заключение: {hausman_results[3]}''')
```
## PooledOLS и RandomEffects


```python
def breusch_pagan_test(pooled_model, re_model):
    """
    Проводит тест Бреуша-Пагана для сравнения моделей Pooled OLS и Random Effects (RE).
    
    Аргументы:
    - pooled_model: модель Pooled OLS (объект с атрибутом resids).
    - re_model: модель Random Effects (объект с атрибутом resids).
    
    Возвращает:
    - bp_stat: значение статистики теста.
    - p_value: p-значение для статистики (односторонний тест).
    - df: степени свободы (фиксированы как 1).
    - conclusion: вывод на основе p-значения (на русском языке).
    """
    # Проверка совпадения длин остатков (модели должны быть оценены на одинаковых данных)
    if len(pooled_model.resids) != len(re_model.resids):
        raise ValueError("Модели оценивались на разных данных")
    
    # Извлечение остатков из моделей
    pooled_residuals = pooled_model.resids
    re_residuals = re_model.resids
    
    # Вычисление суммы квадратов остатков для обеих моделей
    sum_squared_pooled = np.sum(pooled_residuals**2)
    sum_squared_re = np.sum(re_residuals**2)
    
    # Расчет логарифма отношения дисперсий (аналог теста на гетероскедастичность)
    log_ratio = np.log(sum_squared_pooled / sum_squared_re)
    
    # Расчет статистики теста Бреуша-Пагана
    n = len(pooled_residuals)
    bp_stat = (n * log_ratio) / 2
    
    # Вычисление p-значения (χ²-распределение с 1 степенью свободы)
    p_value = 1 - chi2.cdf(bp_stat, df=1)
    
    # Интерпретация результата на основе порога 0.05
    conclusion = ("Выбирайте Random Effects (p-value < 0.05)" if p_value < 0.05
                  else "Выбирайте Pooled OLS (p-value >= 0.05)")
    
    return bp_stat, p_value, 1, conclusion
```

```python
breusch_pagan_results = breusch_pagan_test(models_result['PooledOLS'],models_result['RandomEffects'])

print(f'''Статтистика: {breusch_pagan_results[0]}
p-value: {breusch_pagan_results[1]}
Степени свободы: {breusch_pagan_results[2]}
Заключение: {breusch_pagan_results[3]}''')
```
**Тесты показывают несогласованные результаты:**  
* **F-тест $\Rightarrow$ Fixed Effects** (проверяет значимость фиксированных эффектов через сравнение моделей с и без них)   
* **Hausman’а тест $\Rightarrow$ Random Effects** (сравнивает оценки FE и RE, отвергая случайные эффекты при значимых различиях)   
* **Breusch-Pagan тест $\Rightarrow$ Pooled OLS** (предпочитает модель без учета индивидуальных эффектов)   

**Учитывая строгость F-теста в оценке необходимости фиксированных эффектов и приоритетность его вывода, остановимся на модели Fixed Effects. Для уточнения выбора также сравним модели по критериям AIC и BIC.**


```python
# Вычисление информационных критериев AIC и BIC для сравнения моделей
def get_aic_bic(model):
    """
    Рассчитывает критерии Акаике (AIC) и Байесовский (BIC) для заданной модели.
    
    Формулы:
    AIC = -2 * log-likelihood + 2 * k  
    BIC = -2 * log-likelihood + log(n) * k  
    где k - число параметров, n - число наблюдений [[6]]
    
    Аргументы:
    - model: обученная модель с атрибутами params (параметры), resids (остатки), s2 (дисперсия)
    
    Возвращает:
    - aic: значение информационного критерия Акаике
    - bic: значение байесовского информационного критерия
    """
    # Количество параметров модели
    k = model.params.shape[0]
    
    # Количество наблюдений
    n = model.resids.shape[0]
    
    # Аппроксимация логарифма правдоподобия для нормального распределения
    llf = -n / 2 * (1 + np.log(2 * np.pi) + np.log(model.s2))
    
    # Расчёт AIC и BIC по классическим формулам
    aic = -2 * llf + 2 * k         # Критерий Акаике [[5]]
    bic = -2 * llf + np.log(n) * k # Байесовский критерий [[3]]
    
    return aic, bic

# Сравнение моделей по информационным критериям
for model_name in models_result:
    aic, bic = get_aic_bic(models_result[model_name])
    print(f"{model_name} | AIC: {aic:.4f} | BIC: {bic:.4f}")
```
**FixedEffects показал самые маленькие AIC и BIC $$\Downarrow$$ нашей моделью будет FixedEffects**

# ![image.png](attachment:image.png)


```python
model = models_result['FixedEffects']
b1 = model.params['lag_debtgov']
b2 = model.params['lag_debtgov_quad']
```
Порогом будет экстремум параболы


```python
threshold = -b1 / (2 * b2)
print(f"Пороговое значение долга: {threshold:.4f}")
```
Расчёт стандартной ошибки для оценки порогового значения


```python
cov_matrix = model.cov
```
Дисперсии оценок коэффициентов


```python
var_b1 = cov_matrix.loc['lag_debtgov', 'lag_debtgov']
var_b2 = cov_matrix.loc['lag_debtgov_quad', 'lag_debtgov_quad']
```
Ковариация между коэффициентами


```python
cov_b1_b2 = cov_matrix.loc['lag_debtgov', 'lag_debtgov_quad']
```
Компоненты формулы дисперсии порога


```python
term1 = (1 / (2 * b2))**2 * var_b1
term2 = (b1 / (2 * b2**2))**2 * var_b2
term3 = 2 * (1 / (2 * b2)) * (b1 / (2 * b2**2)) * cov_b1_b2
```
 Стандартная ошибка порога


```python
se_threshold = np.sqrt(term1 + term2 - term3)
```
Проверка гипотезы H0: threshold = 0.9


```python
t_stat = (threshold - 0.9) / se_threshold
p_value = 2 * (1 - t.cdf(abs(t_stat), df=model.df_resid))

print(f"t = {t_stat:.3f}, p-value = {p_value:.3f}")
```
Не можем отвергнуть H0

# ![image.png](attachment:image.png)


```python
model.params['lag_bankcrisis']
```
text_plain_output:

np.float64(-1.9145642367844455)


**Коэффициент при переменной `lag_bankcrisis` статистически значим и имеет отрицательное значение. Наличие банковского кризиса в предыдущем году приводит к снижению темпа прироста реального ВВП на душу населения (`growth`) на 1.91 \%. Это свидетельствует о наличии запаздывающего негативного влияния кризиса на экономическое развитие .**

