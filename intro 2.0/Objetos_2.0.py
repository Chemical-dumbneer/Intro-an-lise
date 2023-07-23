import math
import matplotlib.pyplot as plt
import numpy as np
from tqdm.auto import tqdm

class Info(object):
    def __init__(self, Nomes_reag:list, Densidade:float, Cp:float) -> None:
        """
        Informações sobre o fluído reativo do sistema
        
        no momento este trabalha com apenas uma reação química

        Parâmetros:

        Mat_reag (list): Matriz dos coeficientes estequimétricos da reação sendo que os reagentes devem ser negativos e os produtos positivos.
        Nomes_reag (list): Matriz com as mesmas dimensões da anterior, mas dessa vez contendo os nomes das espécies do sistema.
        Var_entalpia (int): [J/mol] Variação de entalpia da reação química.
        Densidade (float): [kg/m³] Densidade média do fluído reativo.
        Cp (float): [J/kg.ºC] Coeficiente de Troca térmica.
        A (int): [1/s] Coeficiente pré-exponencial da equção de arrhenius.
        Ej (int): [J/mol] Energia de ativação da reação química

        """
        self.Nomes_reagente = Nomes_reag
        self.Densidade = Densidade
        self.Cp = Cp

class Linha:
    def __init__(self, Entrada:any) -> None:
        
        self.Fonte = Entrada
        self.Cs_Vaz = Entrada.Cs_Vaz
        self.Cs_Temp = Entrada.Cs_Temp
        self.Cs_Conc = Entrada.Cs_Conc

    def Update(self) -> None:

        self.Cs_Vaz = self.Fonte.Cs_Vaz
        self.Cs_Temp = self.Fonte.Cs_Temp
        self.Cs_Conc = self.Fonte.Cs_Conc

    def Vectorize(self) -> None:
        pass

    def Publish(self) -> None:
        pass

class Fonte(object):
    def __init__(self, Vaz_max, Raz_vaz, Temp, Conc:list) -> None:
        
        self.Vaz_Max = Vaz_max/1000
        self.Raz_Vaz = [Raz_vaz]

        self.Cs_Vaz = [self.Raz_Vaz[0] * self.Vaz_Max]
        self.Cs_Temp = [Temp + 273.15]
        self.Cs_Conc = Conc

        self.Output = Linha(self)

    def Update(self) -> None:
        
        self.Cs_Vaz[0] = self.Raz_Vaz[0] * self.Vaz_Max
        self.Output.Update()
    
    def Vectorize(self) -> None:
        pass

    def Publish(self) -> None:
        pass
        
class Nó_2_p_1(object):
    def Calc_Temp(self) -> None:
        if self.Cs_Vaz == 0:
            self.Cs_Temp = 0
        else:
            self.Cs_Temp = ((self.Fonte_1.Cs_Vaz * self.Fonte_1.Cs_Temp) + (self.Fonte_2.Cs_Vaz * self.Fonte_2.Cs_Temp))/self.Cs_Vaz

    def Calc_Conc(self, init:bool) -> None:
        if init:
            self.Cs_Conc = []

        for j in range(0, len(self.Fonte_1.Cs_Conc), 1):
            Conc = ((self.Fonte_1.Cs_Conc[j] * self.Fonte_1.Cs_Vaz) + (self.Fonte_2.Cs_Conc[j] * self.Fonte_2.Cs_Vaz))/self.Cs_Vaz    
            if init:
                self.Cs_Conc.append(Conc)
            else:
                self.Cs_Conc[j] = Conc
            
    def __init__(self, Entrada_1:Linha, Entrada_2:Linha) -> None:
        
        self.Fonte_1 = Entrada_1
        self.Fonte_2 = Entrada_2
        
        self.Cs_Vaz = Entrada_1.Cs_Vaz + Entrada_2.Cs_Vaz
        
        self.Calc_Temp()
        self.Calc_Conc(True)

        self.Saída = Linha(self)

    def Update(self) -> None:
        
        self.Cs_Vaz = self.Fonte_1.Cs_Vaz + self.Fonte_2.Cs_Vaz
        self.Calc_Temp()
        self.Calc_Conc(False)
        
        self.Saída.Update()

    def Vectorize(self) -> None:
        pass

    def Publish(self) -> None:
        pass

class Nó_1_p_2(object):
    class Saída(object):
        def __init__(self, Base, Raz) -> None:

            self.Base = Base
            self.Raz = Raz    
            self.Cs_Vaz = self.Raz * self.Base.Cs_Vaz
            self.Cs_Temp = self.Base.Cs_Temp
            self.Cs_Conc = self.Base.Cs_Conc
        
        def Update(self) -> None:
            
            self.Cs_Vaz = self.Raz * self.Base.Cs_Vaz
            self.Cs_Temp = self.Base.Cs_Temp
            self.Cs_Conc = self.Base.Cs_Conc

    def __init__(self, Entrada:Linha, Raz_Vaz_2_a_1:float) -> None:
        
        self.Cs_Saída_1 = self.Saída(self, 1 - Raz_Vaz_2_a_1)
        self.Cs_Saída_2 = self.Saída(self, Raz_Vaz_2_a_1)

        self.Saída_1 = Linha(self.Cs_Saída_1)
        self.Saída_2 = Linha(self.Cs_Saída_2)
    
    def Update(self) -> None:

        self.Cs_Saída_1.Update()
        self.Cs_Saída_2.Update()

        self.Saída_1.Update()
        self.Saída_2.Update()
    
    def Vectorize(self) -> None:
        pass

    def Publish(self) -> None:
        pass

class Reação(object):
    def __init__(self) -> None:
        
    