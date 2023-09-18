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
        Var_entalpia (int): [J / mol] Variação de entalpia da reação química.
        Densidade (float): [kg / m³] Densidade média do fluído reativo.
        Cp (float): [J / kg.ºC] Coeficiente de Troca térmica.
        A (int): [1 / s] Coeficiente pré-exponencial da equção de arrhenius.
        Ej (int): [J / mol] Energia de ativação da reação química

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

    def Update(self, dt:float) -> None:

        self.Cs_Vaz[0] = float(self.Fonte.Cs_Vaz[0])
        self.Cs_Temp[0] = float(self.Fonte.Cs_Temp[0])
        self.Cs_Conc[0] = float(self.Fonte.Cs_Conc[0])

    def Vectorize(self) -> None:        
        pass

    def Publish(self, M_t) -> None:
        pass
    
    def Print_Final_state(self) -> None:
        pass

class Fonte(object):
    def __init__(self, Vaz_max, Raz_vaz, Temp, Conc:list) -> None:
        
        self.Vaz_Max = Vaz_max / 1000
        self.Raz_Vaz = [Raz_vaz]
        self.Cs_Vaz = [self.Raz_Vaz[0] * self.Vaz_Max]
        self.Cs_Temp = [Temp + 273.15]
        self.Cs_Conc = [Conc]

        self.Output = Linha(self)

        self.Vect_Vaz = []
        self.Vect_Temp = []
        self.Vect_Conc = []
        
    def Update(self, dt:float) -> None:
        
        self.Cs_Vaz[0] = self.Raz_Vaz[0] * self.Vaz_Max
        self.Output.Update()
    
    def Vectorize(self) -> None:
        
        self.Vect_Vaz.append(float(self.Cs_Vaz[0]))
        self.Vect_Temp.append(float(self.Cs_Temp[0]))
        self.Vect_Conc.append(float(self.Cs_Conc[0]))

    def Publish(self, M_t) -> None:
        pass
    
    def Print_Final_state(self) -> None:
        pass
        
class Nó_2_p_1(object):
    def Calc_Temp(self) -> None:
        if self.Cs_Vaz[0] == 0:
            self.Cs_Temp[0] = 0
        else:
            self.Cs_Temp[0] = ((self.Fonte_1.Cs_Vaz[0] * self.Fonte_1.Cs_Temp[0]) + (self.Fonte_2.Cs_Vaz[0] * self.Fonte_2.Cs_Temp[0])) / self.Cs_Vaz[0]

    def Calc_Conc(self, init:bool) -> None:
        if init:
            self.Cs_Conc = []

        for j in range(0, len(self.Fonte_1.Cs_Conc), 1):
            Conc = ((self.Fonte_1.Cs_Conc[j] * self.Fonte_1.Cs_Vaz[0]) + (self.Fonte_2.Cs_Conc[j] * self.Fonte_2.Cs_Vaz[0])) / self.Cs_Vaz[0]    
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

    def Update(self, dt:float) -> None:
        
        self.Cs_Vaz[0] = float(self.Fonte_1.Cs_Vaz[0] + self.Fonte_2.Cs_Vaz[0])
        self.Calc_Temp()
        self.Calc_Conc(False)
        
        self.Saída.Update(dt)

    def Vectorize(self) -> None:
        pass

    def Publish(self, M_t) -> None:
        pass
    
    def Print_Final_state(self) -> None:
        pass

class Nó_1_p_2(object):
    class Saída(object):
        def __init__(self, Base, Raz) -> None:

            self.Base = Base
            self.Raz = Raz    
            self.Cs_Vaz = [float(self.Raz * self.Base.Cs_Vaz[0])]
            self.Cs_Temp = [float(self.Base.Cs_Temp[0])]
            self.Cs_Conc = [float(self.Base.Cs_Conc[0])]
        
        def Update(self, dt:float) -> None:
            
            self.Cs_Vaz = [float(self.Raz * self.Base.Cs_Vaz[0])]
            self.Cs_Temp = [float(self.Base.Cs_Temp[0])]
            self.Cs_Conc = [float(self.Base.Cs_Conc[0])]

    def __init__(self, Entrada:Linha, Raz_Vaz_2_a_1:float) -> None:
        
        self.Cs_Saída_1 = self.Saída(self, 1 - Raz_Vaz_2_a_1)
        self.Cs_Saída_2 = self.Saída(self, Raz_Vaz_2_a_1)

        self.Saída_1 = Linha(self.Cs_Saída_1)
        self.Saída_2 = Linha(self.Cs_Saída_2)
    
    def Update(self, dt:float) -> None:

        self.Cs_Saída_1.Update(dt)
        self.Cs_Saída_2.Update(dt)

        self.Saída_1.Update(dt)
        self.Saída_2.Update(dt)
    
    def Vectorize(self) -> None:
        pass

    def Publish(self, M_t) -> None:
        pass
    
    def Print_Final_state(self) -> None:
        pass

class Reação(object):
    def __init__(self, Ej:float, A:float, Matriz_Esteq:list, delta_Entalpia:float) -> None:
        
        self.Ej = Ej
        self.A = A
        self.Mr = Matriz_Esteq
        self.dH = delta_Entalpia
    
    def K_arr(self, Temp) -> float:
        K = self.A * math.exp((-self.Ej) / (8.314 * Temp))
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
    
    def dQreação_dt(self) -> float:
        dq = self.dH * self.Alfa
        return dq
    
class CSTR(object):
    
    def dQtransf_dt() -> float:
            a = 0
            return a
    
    def Vaz_Max(self) ->float:
        alfa = math.pi * pow(self.Dim_Raio_Saída,2) * math.sqrt(2 * 9.81)
        Vm = alfa * math.sqrt(self.Dim_Altura * (self.Cs_Vol / self.Dim_Vol_Max))
        return Vm

    def __init__(self, Type:int, Info_fluido_reativo:Info, Nome_Reator:str) -> None:
        """
        Type "1" --> CSTR COM RESFRIAMENTO
        Type "2" --> CSTR COM AQUECIMENTO
        """
        self.Name = Nome_Reator
        self.Info = Info_fluido_reativo
        self.Reações = []

        # declarando variáveis para facilitar a programação (desnecessário para a execução do código)
        
        self.Con_Entrada:Linha

        self.Dim_Raio:float
        self.Dim_Altura:float
        self.Dim_Raio_Saída:float

        self.Cin_Raz_Vol:float
        
        self.Cs_Vaz:list
        self.Cs_Temp:list
        self.Cs_Conc:list

        self.Dim_Vol_Max:float
        self.Cs_Vol:list

        self.Var_Raz_Vaz:list
        
        self.Dim_J_Area_TT:float
        self.Dim_J_Vol:float
        self.Dim_J_Vaz_max:float
        self.Dim_J_Temp_ent:float
        
        self.Par_J_Cp:float
        self.Par_J_U_tt:float
        self.Par_J_Dens:float

        self.Var_J_Raz_Vaz:list
        self.Cs_J_Vaz:list
        self.Cs_J_Temp:list
        
        self.Par_Vaz_Mass_Max:float
        self.Par_Ent_Vap:float
        self.Par_Ent_Liq:float
        
        self.Vect_Vaz = []
        self.Vect_Temp = []
        self.Vect_Temp_sp = []
        self.Vect_Conc = []
        self.Vect_Vol = []
        self.Vect_Vol_sp = []
        
        self.Vect_Vaz_j = []
        if self.Type == 1:
            self.Vect_Temp_j = []
            
        # término de declaração
        
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

            self.Var_Raz_Vaz = [self.Cs_Vaz / self.Vaz_Max()]       

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
                self.Cs_J_Vaz= self.Dim_J_Vaz_Max * self.Var_J_Raz_Vaz[0]
                self.Cs_J_Temp = [Temp_In_Jaq]

                
                def Novo_dQtransf_dt(self) -> float:
                    
                    Q = self.Par_J_U_tt * self.Dim_J_Area_TT * (self.Cs_Temp[0] - self.Cs_J_Temp[0])
                    en_troc = (Q) / (self.info.Densidade * self.info.Cp)
                    return en_troc

        elif Type == 2:
            def Parâm_Esp(self, Vaz_Mass_Max:float, Ent_Mass_vap:float, Ent_Mass_liq:float, Raz_Vaz_Vap_In:float) -> None:

                self.Par_Vaz_Mass_Max = Vaz_Mass_Max
                self.Par_Ent_Vap = Ent_Mass_vap
                self.Par_Ent_Liq = Ent_Mass_liq
                self.Var_J_Raz_Vaz[0] = [Raz_Vaz_Vap_In]
                self.Cs_J_Vaz[0] = [self.Var_J_Raz_Vaz[0] * self.Par_Vaz_Mass_Max]
                
                def Novo_dQtransf_dt(self) -> float:
                    
                    Q = - self.Cs_J_Vaz[0] * (self.Par_Ent_Vap - self.Par_Ent_Liq)
                    en_troc = (Q) / (self.info.Densidade * self.info.Cp)
                    return en_troc
        
        self.dQtransf_dt = self.Novo_dQtransf_dt
        self.Saída = Linha(self)

    def Add_Reação(self, Obj_Reação:Reação) -> None:
        self.Reações.append(Obj_Reação)
    
    def Update(self, dt:float) -> None:
        
        self.Cs_Vol = self.Cs_Vol + (self.Con_Entrada.Cs_Vaz - self.Cs_Vaz) * dt
        dTempR = 0
        R:Reação
        for R in self.Reações: 
            saldo = R.Saldo_molar(self.Cs_Temp[0], self.Cs_Conc, dt)
            for i in range(0, len(self.Cs_Conc)):
                self.Cs_Conc[i] = self.Cs_Conc[i] + saldo[i]
            dTempR = dTempR + R.dQreação_dt() / (self.Info.Cp * self.Info.Densidade)
            
        for i in range(0, len(self.Cs_Conc)):
            Mol_in = self.Con_Entrada.Cs_Conc[i] * self.Con_Entrada.Cs_Vaz[0] *  dt
            Mol_out = self.Cs_Conc[i] * self.Cs_Vaz[0] * dt
            self.Cs_Conc[i] = self.Cs_Conc[i] + Mol_in - Mol_out
        
        Temp_in = self.Con_Entrada.Cs_Temp[0] * self.Con_Entrada.Cs_Vaz[0] * dt
        Temp_out = self.Cs_Temp[0] * self.Cs_Vaz[0] * dt
        Temp_transf = self.dQtransf_dt() * dt
        
        self.Cs_Temp[0] = Temp_in - Temp_out + Temp_transf
        self.Cs_Vaz[0] = self.Var_Raz_Vaz[0] * self.Vaz_Max()
        
        self.Cs_J_Vaz[0] = self.Var_J_Raz_Vaz[0] * self.Dim_J_Vaz_max
        if self.Type == 2:
            t1 = (self.Cs_J_Vaz[0] * (self.Cs_J_Temp[0] - self.Cs_Temp[0]))/self.Dim_J_Vol
            Q = - self.Cs_J_Vaz[0] * (self.Par_Ent_Vap - self.Par_Ent_Liq)
            t2 = Q / (self.Dim_J_Vol * self.Par_J_Cp * self.Par_J_Dens)
            self.Cs_J_Temp[0] = self.Cs_J_Temp[0] + (t1 + t2) * dt
        
        self.Saída.Update(dt) # ficou faltando programar as trocas de energia na jaqueta
        
    def Vectorize(self) -> None:
        
        self.Vect_Vaz.append(float(self.Cs_Vaz[0]))
        self.Vect_Temp.append(float(self.Cs_Temp[0]))
        self.Vect_Conc.append(float(self.Cs_Conc[0]))
        self.Vect_Vol.append(float(self.Cs_Vol[0]))
        
        self.Vect_Vaz_j.append(float(self.Cs_J_Vaz[0]))
        if self.Type == 1:
            self.Vect_Temp_j.append(float(self.Cs_J_Temp[0]))

    def Publish(self, M_t) -> None:
        self.fig = plt.figure("Parâmetros de " + self.Name + " X Tempo")
        
        plt.subplot(2,3,1)
        plt.plot(M_t,np.asarray(self.Vect_Temp_sp) - 273.15,"-", markersize= 1, label= "Set Point", color= "r")
        plt.plot(M_t,np.asarray(self.Vect_Temp) - 273.15,"o", markersize= 1, label= "Temp. Obs")
        #plt.ylim((min(*self.Vect_Temp,*self.Vect_Temp_sp) - 273.15)*(0.9),(max(*self.Vect_Temp,*self.Vect_Temp_sp) - 273.15)*(1.1))
        plt.legend()
        plt.xlabel("Tempo [s]")
        plt.ylabel("Temp. Reator [ºC]")

        plt.subplot(2,3,2)
        plt.plot(M_t,np.asarray(self.Vect_Vaz)*1000,"o", markersize= 1)
        plt.ylim(min(self.Vect_Vaz)*(0.9*1000),max(self.Vect_Vaz)*(1.1*1000))
        plt.xlabel("Tempo [s]")
        plt.ylabel("Vazão Reator [Litros/s]")

        plt.subplot(2,3,3)
        plt.plot(M_t,(np.asarray(self.Vect_Vol_sp)*1000),"-", markersize= 1, label= "Set Point", color="r")
        plt.plot(M_t,(np.asarray(self.Vect_Vol)*1000),"o", markersize= 1, label= "Vol. Obs")
        plt.legend()
        plt.xlabel("Tempo [s]")
        plt.ylabel("Cap. Vol. Reator [Litros]")

        if self.Type == 1:
            plt.subplot(2,3,4)
            plt.plot(M_t,np.asarray(self.Vect_Temp_j) - 273.15,"o", markersize= 1)
            #plt.ylim((min(self.Vect_Temp_j) - 273.15)*(0.9),(max(self.Vect_Temp_j) - 273.15)*(1.1))
            plt.xlabel("Tempo [s]")
            plt.ylabel("Temp. Jaqueta [ºC]")
            
        plt.subplot(2,3,5)
        plt.plot(M_t,np.asarray(self.Vect_Vaz_j)*1000,"o", markersize= 1)
        plt.ylim(min(self.Vect_Vaz_j)*(0.9)*1000,max(self.Vect_Vaz_j)*(1.1)*1000)
        plt.xlabel("Tempo [s]")
        plt.ylabel("Vazão Jaqueta [Litros/s]")

        plt.subplot(2,3,6)
        for j in range(0, len(self.Cs_Conc), 1):
            mat = []
            for k in range(0, len(M_t) - 1,1):
                mat.append(float(self.His_Conc[k][j]))
            plt.plot(M_t,np.asarray(mat),"o", label= self.Info.Nomes_reagente[j], markersize= 1)
        plt.xlabel("Tempo [s]")
        plt.ylabel("Concentração Molar [M]")
        plt.legend()
    
    def Print_Final_state(self) -> None:
        pass
    
class Controlador_PID:
    
    def __init__(self, Objeto:object, Alvo_Obs:list, Set_Point_Obs:float, Alvo_Reg_SetPoint:list,
                 Alvo_Ctrl:list, K_P:float, K_D:float, K_I:float, Resp_Mín:float, Resp_Max:float) -> None:
        
        self.Con_Obj = Objeto
        self.Obs_Alvo = Alvo_Obs
        self.Obs_Alvo_Sp = Alvo_Reg_SetPoint
        self.Obs_Ante = float(Alvo_Obs[0])
        self.Cs_SetPoint = [Set_Point_Obs]
        self.Ctr_Ctrl = Alvo_Ctrl
        self.Dim_Kp = K_P
        self.Dim_Kd = K_D
        self.Dim_Ki = K_I
        self.Con_Resp_Min = Resp_Mín
        self.Con_Resp_Max = Resp_Max

        self.Con_Ctrl_SS = float(Alvo_Ctrl[0])
        self.Cs_Val_Der = 0
        self.Cs_Val_Int = 0
        self.Cs_Val_Pro = 0
    
    def Update(self, dt:float) -> None:
        
        self.Cs_Val_Pro = self.Cs_SetPoint - self.Obs_Alvo
        self.Cs_Val_Der = (self.Obs_Alvo[0] - self.Obs_Ante) / dt
        self.Cs_Val_Int = self.Cs_Val_Int + ((self.Obs_Alvo[0] + self.Obs_Ante - (2 * self.Cs_SetPoint[0])) / 2) * dt

        self.Resposta = self.Con_Ctrl_SS + self.Cs_Val_Pro * self.Dim_Kp + self.Cs_Val_Der * self.Dim_Kd + self.Cs_Val_Int * self.Dim_Ki
        
        if self.Resposta > self.Con_Resp_Max:
            self.Resposta = self.Con_Resp_Max
        elif self.Resposta < self.Con_Resp_Min:
            self.Resposta = self.Con_Resp_Min
        
        self.Ctr_Ctrl[0] = self.Resposta
        
        self.Vect_Var = []
        self.Vect_Pro = []
        self.Vect_Der = []
        self.Vect_Int = []
        
    def Vectorize(self) -> None:
        
        self.Vect_Var.append(float(self.Cs_SetPoint[0] - self.Obs_Alvo[0]))
        self.Vect_Pro.append(float(self.Cs_Val_Pro[0]))
        self.Vect_Der.append(float(self.Cs_Val_Pro[0]))
        self.Vect_Int.append(float(self.Cs_Val_Pro[0]))
        
        self.Obs_Alvo_Sp.append(float(self.Cs_SetPoint[0]))
    
    def Publish(self, M_t) -> None:
        
        self.fig = plt.figure("Respostas do Controlador X Tempo")
        plt.subplot(4,1,1)
        plt.plot(M_t,np.asarray(self.Vect_Pro,),"o", markersize= 1)
        plt.xlabel("Tempo [s]")
        plt.ylabel("Resposta Proporcional")

        plt.subplot(4,1,2)
        plt.plot(M_t,np.asarray(self.Vect_Der,),"o", markersize= 1)
        plt.xlabel("Tempo [s]")
        plt.ylabel("Resposta Diferencial")

        plt.subplot(4,1,3)
        plt.plot(M_t,np.asarray(self.Vect_Int,),"o", markersize= 1)
        plt.xlabel("Tempo [s]")
        plt.ylabel("Resposta Integral")

        plt.subplot(4,1,4)
        plt.plot(M_t,np.asarray(self.Vect_Var,),"o", markersize= 1, color="r")
        plt.xlabel("Tempo [s]")
        plt.ylabel("Erro Observado")
    
    def Print_Final_state(self) -> None:
        pass
    
class Fonte:
    def __init__(self, Vaz_max, Raz_vaz, Temp, Conc:list) -> None:
        self.Con_Vaz_Max = Vaz_max/1000
        
        self.Cs_Raz_Vaz = [Raz_vaz]
        self.Cs_Vaz = self.Cs_Raz_Vaz[0] * self.Con_Vaz_Max
        self.Cs_Temp = [Temp + 273.15]
        self.Cs_Conc = Conc

    def Update(self,dt) -> None:
        self.Cs_Vaz = self.Cs_Raz_Vaz[0] * self.Con_Vaz_Max
    
    def Vectorize(self) -> None:
        pass
    
    def Publish(self, M_t) -> None:
        pass
    
    def Print_Final_state(self) -> None:
        pass
    
class Perturbador_Step:
    def __init__(self,Ligado:bool, Variavel:list, Incremento, A_Partir_de) -> None:
        
        self.Ligado = Ligado
        self.Var = Variavel
        self.Inc = Incremento
        self.Tem = A_Partir_de
        self.pronto = False
        self.Cron = 0

    def Update(self, dt) -> None:
        self.Cron = self.Cron + dt
        if (self.Tem <= self.Cron) and (self.pronto == False) and (self.Ligado == True):
            self.Var[0] = self.Var[0] + self.Inc
            self.pronto = True
    
    def Vectorize(self) -> None:
        pass
    
    def Publish(self, M_t) -> None:
        pass
    
    def Print_Final_state(self) -> None:
        pass
    
def Run(Sist:list, Duração:float, Iterações_por_seg:float):
    print("Iterando simulação")
    n_s = Iterações_por_seg
    t_tot = Duração
    dt = 1/n_s
    total_iterations = n_s*t_tot
    global pb
    pb = tqdm(total=total_iterations, desc='Progresso', ascii=True, smoothing=0.05, position=0, leave=True,
              ncols=100, bar_format='{l_bar}{bar}|')
    for i in range(1, total_iterations):
        for Obj in Sist:
            Obj.Update(dt)
            Obj.Vectorize()
            
        pb.update(i)
            
    print("Gerando Gráficos")
    for Obj in Sist:
        M_t = np.arange(0,t_tot,dt)
        Obj.Publish(M_t)
    plt.show()

def Equalize(Sist:list, Var_Obs:list, Set_Point:float, Iterações_por_seg:int, t_max:int, It_min:int) -> None:
    print("Iterando simulação")
    n_s = Iterações_por_seg
    tmax = t_max
    dt = 1/n_s
    Vobs = Var_Obs
    Spoint = Set_Point
    it_min = It_min
    t = 0
    t_eq = 0
    equalizado = False
    pbar_Eq = tqdm(total= it_min, desc='Iterações no setpoint')
    with tqdm(total= tmax, desc= 'Tempo decorrido [s]') as pbar_t:
        while t<=tmax and not equalizado:
            for Obj in Sist:
                Obj.Update(dt)
            pbar_t.update(dt)
            
            if Spoint == Vobs[0]:
                pbar_Eq.update(1)
                t_eq =+ 1
            else:
                pbar_Eq.clear()
                t_eq = 0
            
            if t_eq >= it_min:
                equalizado = True
            
            t = t + dt
    print('========================================================================\n\n')
    if equalizado:
        print('Estado Estacionário atingido!')
    else:
        print('Estado Estacionário não atingido, escolher outros parâmetros...')
    for Obj in Sist:
        Obj.Print_Final_state()