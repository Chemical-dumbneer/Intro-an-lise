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
        self.Cs_Vaz = [float(Entrada.Cs_Vaz[0])]
        self.Cs_Temp = [float(Entrada.Cs_Temp[0])]
        self.Cs_Conc = [float(Entrada.Cs_Conc[0])]

    def Update(self) -> None:

        self.Cs_Vaz[0] = float(self.Fonte.Cs_Vaz[0])
        self.Cs_Temp[0] = float(self.Fonte.Cs_Temp[0])
        self.Cs_Conc[0] = float(self.Fonte.Cs_Conc[0])

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
        self.Cs_Conc = [Conc]

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
        if self.Cs_Vaz[0] == 0:
            self.Cs_Temp[0] = 0
        else:
            self.Cs_Temp[0] = ((self.Fonte_1.Cs_Vaz[0] * self.Fonte_1.Cs_Temp[0]) + (self.Fonte_2.Cs_Vaz[0] * self.Fonte_2.Cs_Temp[0]))/self.Cs_Vaz[0]

    def Calc_Conc(self, init:bool) -> None:
        if init:
            self.Cs_Conc = []

        for j in range(0, len(self.Fonte_1.Cs_Conc), 1):
            Conc = ((self.Fonte_1.Cs_Conc[j] * self.Fonte_1.Cs_Vaz[0]) + (self.Fonte_2.Cs_Conc[j] * self.Fonte_2.Cs_Vaz[0]))/self.Cs_Vaz[0]    
            if init:
                self.Cs_Conc.append(Conc)
            else:
                self.Cs_Conc[j] = Conc
            
    def __init__(self, Entrada_1:Linha, Entrada_2:Linha) -> None:
        
        self.Fonte_1 = Entrada_1
        self.Fonte_2 = Entrada_2
        
        self.Cs_Vaz = [float(Entrada_1.Cs_Vaz + Entrada_2.Cs_Vaz)]
        
        self.Calc_Temp()
        self.Calc_Conc(True)

        self.Saída = Linha(self)

    def Update(self) -> None:
        
        self.Cs_Vaz[0] = float(self.Fonte_1.Cs_Vaz[0] + self.Fonte_2.Cs_Vaz[0])
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
            self.Cs_Vaz = [float(self.Raz * self.Base.Cs_Vaz[0])]
            self.Cs_Temp = [float(self.Base.Cs_Temp[0])]
            self.Cs_Conc = [float(self.Base.Cs_Conc[0])]
        
        def Update(self) -> None:
            
            self.Cs_Vaz = [float(self.Raz * self.Base.Cs_Vaz[0])]
            self.Cs_Temp = [float(self.Base.Cs_Temp[0])]
            self.Cs_Conc = [float(self.Base.Cs_Conc[0])]

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
    def __init__(self, Ej:float, A:float, Matriz_Esteq:list, delta_Entalpia:float) -> None:
        
        self.Ej = Ej
        self.A = A
        self.Mr = Matriz_Esteq
        self.dH = delta_Entalpia
    
    def K_arr(self, Temp) -> float:
        K = self.A * math.exp((-self.Ej)/(8.314 * Temp))
        return K
    
    def Saldo_molar(self, Temp:float, Mconc:list, dt:float) -> list:
        self.Alfa = self.K_arr(Temp)
        for k in range(0, len(self.Mr), 1):
            if self.Mr[k] < 0:
                self.Alfa = self.Alfa * pow(Mconc[k],self.Mr[k])
        
        Saldo_M = []
        for k in range(0, len(self.Mr), 1):
            Saldo_M.append(self.Mr[k] * self.Alfa * dt)
        
        return Saldo_M
    
    def dQ_dt(self) -> float:
        dq = self.dH * self.Alfa
        return dq
    
class CSTR(object): 

    def __init__(self, Type:int, Info_fluido_reativo:Info) -> None:
        """
        Type "1" --> CSTR COM RESFRIAMENTO
        Type "2" --> CSTR COM AQUECIMENTO
        """
        self.Info = Info_fluido_reativo

        # declarando variáveis
        self.Con_Entrada = any()

        self.Dim_Raio = any()
        self.Dim_Altura = any()
        self.Dim_Raio_Saída = any()

        self.Cin_Raz_Vol = any()
        
        self.Cs_Vaz = any()
        self.Cs_Temp = any()
        self.Cs_Conc = any()

        self.Dim_Vol_Max = 2 * math.pi * pow(self.Dim_Raio,2) * self.Dim_Altura
        self.Cs_Vol = [self.Dim_Vol_Max * self.Cin_Raz_Vol]

        self.Var_Raz_Vaz = [self.Cs_Vaz/self.Vaz_Max()]       

        # término de declaração
        def Vaz_Max(self) ->float:
            alfa = math.pi * pow(self.Dim_Raio_Saída,2) * math.sqrt(2*9.81)
            Vm = alfa * math.sqrt(self.Dim_Altura * (self.Cs_Vol/self.Dim_Vol_Max))
            return Vm

        def Parâm_Gerais(self, Entrada:Linha, Raio:float, Altura:float, Raio_Canal_Saída:float,
                        Raz_Vol_In:float, Vaz_Saída_In:float, Temp_in:float, Conc_In:list) ->None:

            self.Con_Entrada = Entrada

            self.Dim_Raio = Raio
            self.Dim_Altura = Altura
            self.Dim_Raio_Saída = Raio_Canal_Saída

            self.Cin_Raz_Vol = Raz_Vol_In
            
            self.Cs_Vaz = [Vaz_Saída_In]
            self.Cs_Temp = [Temp_in]
            self.Cs_Conc = [Conc_In]

            self.Dim_Vol_Max = 2 * math.pi * pow(self.Dim_Raio,2) * self.Dim_Altura
            self.Cs_Vol = [self.Dim_Vol_Max * self.Cin_Raz_Vol]

            self.Var_Raz_Vaz = [self.Cs_Vaz/self.Vaz_Max()]       

        self.Type = Type
        if Type == 1:
            def Parâm_Esp(self, Área_Cob_Jaq:float, Vol_Jaq:float,
                          Vaz_Máx:float, Temp_Entrada:float, Cp:float, Densidade:float,
                          Raz_Vaz_In:float, Temp_In_Jaq:float) -> None:
                
                self.Dim_J_Area_TT = Área_Cob_Jaq
                self.Dim_J_Vol = Vol_Jaq
                self.Dim_J_Vaz_max = Vaz_Máx
                self.Dim_J_Temp_ent = Temp_Entrada
                
                self.Par_J_Cp = Cp
                self.Par_J_U_tt = 851.7395
                self.Par_J_Dens = Densidade

                self.Var_J_Raz_Vaz = [Raz_Vaz_In]
                self.Cs_J_Temp = [Temp_In_Jaq]
            
                def dQ_dt(self) -> float:
                    
                    Q = self.Par_J_U_tt * self.Dim_J_Area_TT * (self.Cs_Temp[0] - self.Cs_J_Temp[0])
                    en_troc = (Q)/(self.info.Densidade * self.info.Cp)
                    return en_troc



        elif Type == 2:
            def Parâm_Esp(self, Vaz_Mass_Max:float, Ent_Mass_vap:float, Ent_Mass_liq:float, Raz_Vaz_Vap_In:float) -> None:

                self.Par_Vaz_Mass_Max = Vaz_Mass_Max
                self.Par_Ent_Vap = Ent_Mass_vap
                self.Par_Ent_Liq = Ent_Mass_liq
                self.Cs_Raz_Vaz_Vap = [Raz_Vaz_Vap_In]
        
    def Update(self) -> None:
        self.atumalaca.ahahahahahah
    def Vectorize(self) -> None:
        pass

    def Publish(self) -> None:
        pass