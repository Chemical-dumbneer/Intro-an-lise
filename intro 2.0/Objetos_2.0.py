import math
import matplotlib.pyplot as plt
import numpy as np
from tqdm.auto import tqdm

class Info:
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

    def Register(self, i) -> None:
        pass

    def Publish(self) -> None:
        pass

class Fonte:
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
    
    def Register(self, i) -> None:
        pass

    def Publish(self) -> None:
        pass
        
class Nó_Mistura:
    def __init__(self, Entrada_1:Linha, Entrada_2:Linha) -> None:
        
        self.Fonte_1 = Entrada_1
        self.Fonte_2 = Entrada_2
        
        self.Cs_Vaz = Entrada_1.Cs_Vaz + Entrada_2.Cs_Vaz
        if(self.Cs_Vaz == 0):
            self.Cs_Temp = 0
        else:
            self.Cs_Temp = ((Entrada_1.Cs_Vaz*Entrada_1.Cs_Temp) + (Entrada_2.Cs_Vaz*Entrada_2.Cs_Temp))/self.Cs_Vaz
        
        for j in range(0,len(Entrada_1.Cs_Conc),1):
            
