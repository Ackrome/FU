def description():
    themes = {'Непрерывные случайные величины': ['CRV_1()', 'CRV_2()'],
              'Нормальные случайные векторы': ['NRV_1()', 'NRV_2()', 'NRV_3()']}
    text = ""
    for key in themes.keys():
        text += f'{key}: '
        for f in themes[key]:
            text += f'{f}; '
        text += '\n'
    print(text)
    
#ContinuousRandomVariables
def CRV_1():
    task = 'Абсолютно непрерывная случайная величина  X  может принимать значения только в отрезке [a, b]. На этом отрезке плотность распределения случайной величины  X  имеет вид: f(x)=C(1+a^0.1+2b^0.2+3c^0.3)^1.1, где С - положительная константа. Найти:\n- константу C математическое ожидание E(X)\n- стандартное отклонение σX\n- квантиль уровня k распределения X'
    print(task)
    answer = '\n#условие\n# [a,b]\na,b = 4,9\n# F = f(x) без C\nF = lambda x: (1 + 7*x**(0.5) + 8*x**(0.7) + 4*x**(0.9))**(1.3)\nC = 1 / integrate.quad(F, a, b)[0]\ndef f(x):\n    return C * F(x)\nclass dist_f_C(rv_continuous):\n  #функция вероятности\n  def _pdf(self,x):\n    return f(x) if (a<= x <=b) else 0\n  #функция значений\n  def _expect(self,x):\n    return x\n#зададим распределение\nf_C = dist_f_C(a = a, b = b)\n#1\nprint(f"C = {C}")\n#2\nprint(f"E = {f_C.mean()}")\n#3\nprint(f"sigma = {f_C.std()}")\n#4\nprint(f"q = {f_C.ppf(0.9)}")\n'
    print(answer)
def CRV_2():
    task = 'Случайная величина X равномерно распределена на отрезке [a,b]. Случайная величина Y выражается через X следующим образом: Y = (1+a^0.1+2b^0.2+3c^0.3)^1.1. Найдите:\n- математическое ожидание  E(Y)\n- стандартное отклонение σY\n- асимметрию As(Y)\n- квантиль уровня 0,8 распределения Y'
    print(task)
    answer = '\nF = lambda x: (1 + 6*x**0.5 + 4*x**0.7 + 5 * x**0.9)**1.3\nab = [4, 8]\np = 1/(ab[1]-ab[0])\nEY = p * integrate.quad(F, 4, 8)[0]\nprint(f"EY = {EY}")\nf = lambda x: (F(x))**2\nVarY = p * integrate.quad(f, 4, 8)[0] - EY**2\nQy = math.sqrt(VarY)\nprint(f"Qy = {Qy}")\nf = lambda x: p * (F(x) - EY)**3\nAsY = integrate.quad(f, 4, 8)[0]/Qy**3\nprint(f"AsY = {AsY}")\n#q_l = quantile_level\nq_l = 0.8\n# работает при равномерном случайном распределении!\nq = F(ab[0] + ab[0]*q_l)\nprint(f"q = {q}")\n'
    print(answer)

#NormalRandomVectors
def NRV_1():
    task = 'Для нормального случайного вектора (X,Y)∼N(−8;16;49;1;0,8) найдите вероятность P((X−3)(Y−7)<0).'
    print(task)
    answer = "\nN = {'muX': -8, 'muY': 16, 'sigmaX2': 49, 'sigmaY2': 1, 'rho': 0.8}\nmu = np.array([N['muX'], N['muY']])\nCov = np.array([[N['sigmaX2'], N['rho']*math.sqrt(N['sigmaX2'])*math.sqrt(N['sigmaY2'])],\n                [N['rho']*math.sqrt(N['sigmaX2'])*math.sqrt(N['sigmaY2']), N['sigmaY2']]])\nW = multivariate_normal(mu, Cov)\nX = norm(N['muX'], math.sqrt(N['sigmaX2']))\nY = norm(N['muY'], math.sqrt(N['sigmaY2']))\nPx = 3\nPy = 7\nPa=X.cdf(Px)-W.cdf([Px,Py])\nPb=Y.cdf(Py)-W.cdf([Px,Py])\nPa+Pb\n"
    print(answer)
def NRV_2():
    task = 'Для нормального случайного вектора (X,Y)∼N(−4;4;64;81;−0,31) найдите вероятность P((X−8)(X−10)(Y−1)<0).'
    print(task)
    answer = "\n#Смотрим на распределение, которое задано\nmuX = -4\nmuY = 4\nsigmaX = 64**0.5\nsigmaY = 81**0.5\nrho = -0.31\n#Смотрим на вероятность, которую хотят от нас\nxminus1 = 8\nxminus2 = 10\nyminus = 1\nmu = np.array([muX,muY])\nCov = np.array([[sigmaX**2, rho*sigmaX*sigmaY], [rho*sigmaX*sigmaY, sigmaY**2]])\nX = norm(muX, sigmaX)\nY = norm(muY, sigmaY)\nW = multivariate_normal(mu, Cov)\nPa = W.cdf([xminus1, yminus])\nPb = X.cdf(xminus2) - X.cdf(xminus1) - (W.cdf([xminus2, yminus]) - W.cdf([xminus1, yminus]))\nPc = Y.cdf(yminus) - W.cdf([xminus2, yminus])\nPa+Pb+Pc\n"
    print(answer)
def NRV_3():
    task = 'Случайный вектор (X,Y) имеет плотность распределения fX,Y(x,y)=(18e^(−30x2−48xy+8x−30y2−5y−8524))\π\nНайдите:\n- математическое ожидание E(X)\n-математическое ожидание E(Y)\n-дисперсию  Var(X)\n-дисперсию  Var(Y)\n-ковариацию  Cov(X,Y)\n-коэффициент корреляции  ρ(X,Y)'
    print(task)
    answer = "\n#после выноса -1/2!!!!!!\ncoefs = {\n    'x^2': 60,\n    'x': -16,\n    'xy': 96,\n    'y': 10,\n    'y^2': 60,\n}\nC = np.matrix([[coefs['x^2'], coefs['xy']/2], [coefs['xy']/2, coefs['y^2']]])\nC1 = C**(-1)\nVarX = C1[0, 0]\nsigmaX = np.sqrt(VarX)\nVarY = C1[1, 1]\nsigmaY = np.sqrt(VarY)\nCovXY = C1[0, 1]\nroXY = CovXY/(sigmaX*sigmaY)\nEX, EY = sympy.symbols('EX, EY')\nequations = (\n    sympy.Eq(coefs['x^2']*EX + coefs['xy']/2*EY, coefs['x']*(-1/2)),\n    sympy.Eq(coefs['xy']/2*EX + coefs['y^2']*EY, coefs['y']*(-1/2))\n)\nsol = sympy.solve(equations, (EX, EY))\nprint(f'EX = {sol[EX]}, EY = {sol[EY]}, VarX = {VarX}, VarY = {VarY}, CovXY = {CovXY}, roXY = {roXY}')\n"
    print(answer)