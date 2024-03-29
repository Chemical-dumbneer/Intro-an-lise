import math
import matplotlib.pyplot as plt
import numpy as np
from tqdm.auto import tqdm


n_s = 50
t_tot = int(1*60*60)
dt = 1/n_s
M_t = np.arange(0,t_tot,dt)
print("Declarando Classes")

class info_Fluido_Reativo:
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

class info_Fluido_Refrigerante:
    def __init__(self, Cp:float, Densidade:float) -> None:
        self.Cp = Cp
        self.Densidade = Densidade

class Linha:
    def __init__(self, Entrada) -> None:
        self.Temp = Entrada.Temp
        self.Vaz = Entrada.Vaz
        self.Conc = Entrada.Conc
        self.Fonte = Entrada
    
    def Update(self,i) -> None:
        self.Temp = self.Fonte.Temp
        self.Vaz = self.Fonte.Vaz
        self.Conc = self.Fonte.Conc

    def Publish(self) -> None:
        pass

class Nó_Mistura:
    def __init__(self, Entrada1:Linha, Entrada2:Linha) -> None:
        self.Vaz = Entrada1.Vaz + Entrada2.Vaz
        if self.Vaz == 0:
            self.Temp = [0]
        else:
            self.Temp = [((Entrada1.Temp[0] * Entrada1.Vaz)+(Entrada2.Temp[0] * Entrada2.Vaz))/self.Vaz]
        
        self.Conc = []

        for j in range(0, len(Entrada1.Conc), 1):
            if self.Vaz == 0:
                self.Conc.append(0)
            else:
                self.Conc.append(((Entrada1.Conc[j]*Entrada1.Vaz) + (Entrada2.Conc[j]*Entrada2.Vaz))/self.Vaz)
            

        self.Fonte1 = Entrada1
        self.Fonte2 = Entrada2
    
    def Update(self,i) -> None:
        self.Vaz = self.Fonte1.Vaz + self.Fonte2.Vaz
        if self.Vaz == 0:
            self.Temp[0] = 0
        else:
            self.Temp[0] = ((self.Fonte1.Temp[0] * self.Fonte1.Vaz)+(self.Fonte2.Temp[0] * self.Fonte2.Vaz))/self.Vaz

        for j in range(0, len(self.Conc), 1):
            if self.Vaz == 0:
                self.Conc[j] = 0
            else:
                self.Conc[j] = ((self.Fonte1.Conc[j]*self.Fonte1.Vaz)+(self.Fonte2.Conc[j]*self.Fonte2.Vaz))/self.Vaz

    def Publish(self) -> None:
        pass

class Nó_Reciclo:
    def __init__(self, Entrada:Linha, Raz_reciclo_in) -> None:
        self.Fonte = Entrada
        self.Vaz = Entrada.Vaz
        self.Temp = Entrada.Temp
        self.Conc = Entrada.Conc
        self.Raz_Reciclo = Raz_reciclo_in

        Base = self
        self.Saída = Linha(Base)
        self.Saída.Vaz = self.Vaz * (1 - self.Raz_Reciclo)
        
        self.Reciclo = Linha(Base)
        self.Reciclo.Vaz = self.Vaz * self.Raz_Reciclo

    def Update(self,i) -> None:
        self.Vaz = self.Fonte.Vaz
        self.Temp = self.Fonte.Temp
        self.Conc = self.Fonte.Conc

        self.Saída.__dict__.update({
            'Temp':self.Temp,
            'Conc':self.Conc,
            'Vaz':self.Vaz * (1 - self.Raz_Reciclo)
        })

        self.Reciclo.__dict__.update({
            'Temp':self.Temp,
            'Conc':self.Conc,
            'Vaz':self.Vaz * self.Raz_Reciclo
        })
    
    def Publish(self) -> None:
        pass

class CSTR_C_Resfr:

    def K_arr(self, Temp):
        a = self.A
        b = int(-self.Ej)
        c = int(8.314 * Temp)
        d = b // c
        val =  a* np.exp(d)
        return val

    def __init__(self, Fonte_Alimentção:Linha, Fonte_Jaqueta:Linha, Raz_Vol_in, A:int, Ej:int, Plotar_grafico:bool,
                 Vaz_Saída_in, Raio, Altura, Area_Cobert_Jaqueta, Vol_Jaqueta, Var_entalpia:int,
                 Temp_in, Temp_in_Jaqueta, Raio_Canal_Saída, Conc_in:list, Dados_Reação:info_Fluido_Reativo,
                 Matriz_Reação:list, Dados_Jaqueta:info_Fluido_Refrigerante, Nome_Reator:str, Mostrar_Val_Finais:bool) -> None:
        
        self.MVF = Mostrar_Val_Finais
        self.Name = Nome_Reator
        self.A = A
        self.Ej = Ej
        self.Var_entalpia = Var_entalpia
        self.Dados_Reação = Dados_Reação
        self.Matriz_Reação = Matriz_Reação
        self.Dados_Jaqueta = Dados_Jaqueta
        self.Fonte_Alimentação = Fonte_Alimentção
        self.Fonte_Jaqueta     = Fonte_Jaqueta
        self.Temp_Jaqueta      = [Temp_in_Jaqueta + 273.15]
        self.His_Temp_J        = []
        self.His_Vaz_J         = []
        self.His_Temp_J.append(float(self.Temp_Jaqueta[0]))
        self.His_Vaz_J.append(float(self.Fonte_Jaqueta.Vaz))

        self.A_tt        = Area_Cobert_Jaqueta
        self.Vol_Jaqueta = Vol_Jaqueta
        self.U_tt        = 851.7395

        self.Vol_Max       = Altura * math.pi * math.pow(Raio,2)
        vol_in = self.Vol_Max * Raz_Vol_in
        self.Vol           = list([vol_in])
        self.Altura_Reator = Altura

        self.His_vol  = []
        self.His_vol.append(float(self.Vol[0]))
        kelvin_in = Temp_in + 273.15
        self.Temp     = []
        self.Temp.append(float(kelvin_in))
        self.His_Temp = []
        self.His_Temp.append(float(self.Temp[0]))

        self.Raio_Canal_Saída = Raio_Canal_Saída
        self.alfa    = math.pi * math.pow(self.Raio_Canal_Saída,2) * math.sqrt(2*9.81)
        self.Vaz_max = self.alfa * math.sqrt(self.Altura_Reator * (float(self.Vol[0])/self.Vol_Max))
        self.Raz_Vaz = [Vaz_Saída_in/(self.Vaz_max*1000)]
        self.Vaz     = Vaz_Saída_in/1000

        self.Vol_S_P = []
        self.Temp_S_P = []
        self.His_Vaz  = [float(self.Vaz)]
        self.His_Conc = []
        self.Conc     = Conc_in
        MConc = list(self.Conc)
        self.His_Conc.append(MConc)

        self.Mol_Reator  = [0] * len(self.Conc)
        self.Mol_Entrada = [0] * len(self.Conc)
        self.Mol_Saída   = [0] * len(self.Conc)
        self.Mol_Reação  = [0] * len(self.Conc)
        self.Saldo_Molar = [0] * len(self.Conc)

        self.Plotar = Plotar_grafico
    
    def Update(self,i) -> None:
        self.Vol[0] = self.Vol[0] + (self.Fonte_Alimentação.Vaz - self.Vaz) * dt
        self.alfa    = math.pi * math.pow(self.Raio_Canal_Saída,2) * math.sqrt(2*9.81)
        self.Vaz_max = self.alfa * math.sqrt(self.Altura_Reator * (self.Vol[0]/self.Vol_Max))
        self.Vaz = self.Vaz_max * self.Raz_Vaz[0]
        self.His_vol.append(float(self.Vol[0]))
        self.His_Vaz.append(float(self.Vaz))

        self.prod_reag = 1

        for j in range(0, len(self.Conc), 1):
            self.Mol_Reator[j]  = self.Conc[j] * self.Vol[0]
            self.Mol_Entrada[j] = self.Fonte_Alimentação.Conc[j] * self.Fonte_Alimentação.Vaz * dt
            self.Mol_Saída[j]   = self.Conc[j] * self.Vaz * dt
            
            k_arrhenius = float(self.K_arr(self.Temp[0]))
            self.Mol_Reação[j]  = k_arrhenius * dt
            for k in range(0, len(self.Conc), 1):
                if self.Matriz_Reação[k] < 0:
                    self.Mol_Reação[j] = self.Mol_Reação[j] * math.pow(self.Conc[k], - self.Matriz_Reação[k])

            self.Saldo_Molar[j] = self.Mol_Entrada[j] - self.Mol_Saída[j] + (self.Mol_Reação[j] * (self.Matriz_Reação[j]))
            self.Mol_Reator[j]  = self.Mol_Reator[j] + self.Saldo_Molar[j] * dt
            self.Conc[j]        = self.Mol_Reator[j] / self.Vol[0]
            if self.Matriz_Reação[j] < 0:
                self.prod_reag = self.prod_reag * math.pow(self.Conc[j], - self.Matriz_Reação[j])

        MConc = list(self.Conc)
        self.His_Conc.append(MConc)
        # saldo de temperatura para o fluido reativo
        Q = self.U_tt * self.A_tt * (self.Temp[0] - self.Temp_Jaqueta[0])
        T_ant = self.Temp[0]
        f0t0 = self.Fonte_Alimentação.Vaz * self.Fonte_Alimentação.Temp[0]
        ft = self.Vaz * self.Temp[0]
        k_arr = self.K_arr(self.Temp[0])
        en_quim = (self.Vol[0] * k_arr * self.prod_reag * self.Var_entalpia) / (self.Dados_Reação.Densidade * self.Dados_Reação.Cp)
        en_troc = (Q)/(self.Dados_Reação.Densidade * self.Dados_Reação.Cp)
        self.Saldo_energia = (f0t0 - ft - en_quim - en_troc)/self.Vol[0]
        self.Temp[0] = self.Temp[0] + self.Saldo_energia * dt
        self.His_Temp.append(float(self.Temp[0]))
        # saldo de temperatura para o fluido refrigerante
        t1 = (self.Fonte_Jaqueta.Vaz * (self.Fonte_Jaqueta.Temp[0] - self.Temp_Jaqueta[0]))/self.Vol_Jaqueta
        t2 = (Q) / (self.Vol_Jaqueta * self.Dados_Jaqueta.Cp * self.Dados_Jaqueta.Densidade)
        self.Saldo_energia = t1 + t2
        self.Temp_Jaqueta[0] = self.Temp_Jaqueta[0] + self.Saldo_energia * dt
        self.His_Temp_J.append(float(self.Temp_Jaqueta[0]))
        self.His_Vaz_J.append(float(self.Fonte_Jaqueta.Vaz))
    
    def Publish(self) -> None:
        if self.Plotar:
            self.fig = plt.figure("Parâmetros de " + self.Name + " X Tempo")

            plt.subplot(2,3,1)
            plt.plot(M_t,np.asarray(self.Temp_S_P) - 273.15,"-", markersize= 1, label= "Set Point", color= "r")
            plt.plot(M_t,np.asarray(self.His_Temp) - 273.15,"o", markersize= 1, label= "Temp. Obs")
            plt.ylim((min(*self.His_Temp,*self.Temp_S_P) - 273.15)*(0.9),(max(*self.His_Temp,*self.Temp_S_P) - 273.15)*(1.1))
            plt.legend()
            plt.xlabel("Tempo [s]")
            plt.ylabel("Temp. Reator [ºC]")

            plt.subplot(2,3,2)
            plt.plot(M_t,np.asarray(self.His_Vaz)*1000,"o", markersize= 1)
            plt.ylim(min(self.His_Vaz)*(0.9*1000),max(self.His_Vaz)*(1.1*1000))
            plt.xlabel("Tempo [s]")
            plt.ylabel("Vazão Reator [Litros/s]")

            plt.subplot(2,3,3)
            plt.plot(M_t,(np.asarray(self.Vol_S_P)*1000),"-", markersize= 1, label= "Set Point", color="r")
            plt.plot(M_t,(np.asarray(self.His_vol)*1000),"o", markersize= 1, label= "Vol. Obs")
            plt.legend()
            plt.xlabel("Tempo [s]")
            plt.ylabel("Cap. Vol. Reator [Litros]")

            plt.subplot(2,3,4)
            plt.plot(M_t,np.asarray(self.His_Temp_J) - 273.15,"o", markersize= 1)
            plt.ylim((min(self.His_Temp_J) - 273.15)*(0.9),(max(self.His_Temp_J) - 273.15)*(1.1))
            plt.xlabel("Tempo [s]")
            plt.ylabel("Temp. Jaqueta [ºC]")
            
            plt.subplot(2,3,5)
            plt.plot(M_t,np.asarray(self.His_Vaz_J)*1000,"o", markersize= 1)
            plt.ylim(min(self.His_Vaz_J)*(0.9)*1000,max(self.His_Vaz_J)*(1.1)*1000)
            plt.xlabel("Tempo [s]")
            plt.ylabel("Vazão Jaqueta [Litros/s]")

            plt.subplot(2,3,6)
            for j in range(0, len(self.Conc), 1):
                mat = []
                for k in range(0, n_s*t_tot,1):
                    mat.append(float(self.His_Conc[k][j]))
                plt.plot(M_t,np.asarray(mat),"o", label= self.Dados_Reação.Nomes_reagente[j], markersize= 1)
            plt.xlabel("Tempo [s]")
            plt.ylabel("Concentração Molar [M]")
            plt.legend()
        
        if (self.MVF == True):
            print("\n\n\nValores finais para: " + self.Name + "========================================")
            print("\nTemperatura Final do Reator: " + str(self.His_Temp[-1] - 273.15) + " ºC")
            print("\nVazão Final do Reator: " + str(self.His_Vaz[-1] * 1000) + " Litros/s")
            print("\nCap. Vol. Final do Reator: " + str(self.His_vol[-1] * 1000) + " Litros (" + str(self.His_vol[-1]/self.Vol_Max) + " x100%)")
            print("\nTemperatura Final da Jaqueta: " + str(self.His_Temp_J[-1] - 273.15) + " ºC")
            print("\nVazão Final da Jaqueta: " + str((self.His_Vaz_J[-1])/self.Fonte_Jaqueta.Fonte.Vaz_Max) + " x100%")
            print("\nMatriz Final de Concentração Molar: \n" + str(self.His_Conc[-1]))

class CSTR_C_Aquec:

    def K_arr(self, Temp):
        return self.A * np.exp((-self.Ej)/(8.314 * Temp))

    def __init__(self, Fonte_Alimentção:Linha, Raz_Vol_in, Vaz_Saída_in, Raio, Altura, Temp_in, A:int, Ej:int, Plotar_graficos:bool,
                 Vaz_Mássica_Vapor_Máxima, Raz_vaz_Vap_in, Ent_mass_Vapor, Ent_mass_Líq, Raio_Canal_Saída, Var_entalpia:int,
                 Conc_in:list, Dados_Reação:info_Fluido_Reativo, Matriz_Reação:list, Nome_Reator:str, Mostrar_Val_Finais:bool) -> None:
        
        self.MVF = Mostrar_Val_Finais
        self.Name = Nome_Reator
        self.A = A
        self.Ej = Ej
        self.Var_entalpia = Var_entalpia
        self.Dados_Reação = Dados_Reação
        self.Matriz_Reação = Matriz_Reação
        self.Fonte_Alimentação = Fonte_Alimentção
        self.Vaz_Vap_Max = Vaz_Mássica_Vapor_Máxima
        self.Raz_Vaz_Vap = [Raz_vaz_Vap_in]
        self.Vaz_Vap = self.Vaz_Vap_Max * self.Raz_Vaz_Vap[0]
        self.His_Vaz_Vap = []
        self.His_Vaz_Vap.append(self.Vaz_Vap)
        self.hv = Ent_mass_Vapor
        self.hl = Ent_mass_Líq

        self.Vol_Max       = Altura * math.pi * math.pow(Raio,2)
        vol_in = self.Vol_Max * Raz_Vol_in
        self.Vol           = list([vol_in])
        self.Altura_Reator = Altura

        self.His_vol  = []
        self.His_vol.append(float(self.Vol[0]))
        kelvin_in = Temp_in + 273.15
        self.Temp     = []
        self.Temp.append(float(kelvin_in))
        self.His_Temp = []
        self.His_Temp.append(float(self.Temp[0]))

        self.Raio_Canal_Saída = Raio_Canal_Saída
        self.alfa    = math.pi * math.pow(self.Raio_Canal_Saída,2) * math.sqrt(2*9.81)
        self.Vaz_max = self.alfa * math.sqrt(self.Altura_Reator * (float(self.Vol[0])/self.Vol_Max))
        self.Raz_Vaz = [Vaz_Saída_in/(self.Vaz_max*1000)]
        self.Vaz     = Vaz_Saída_in/1000

        self.Vol_S_P = []
        self.Temp_S_P = []
        self.His_Vaz  = [float(self.Vaz)]
        self.His_Conc = []
        self.Conc     = Conc_in
        MConc = list(self.Conc)
        self.His_Conc.append(MConc)

        self.Mol_Reator  = [0] * len(self.Conc)
        self.Mol_Entrada = [0] * len(self.Conc)
        self.Mol_Saída   = [0] * len(self.Conc)
        self.Mol_Reação  = [0] * len(self.Conc)
        self.Saldo_Molar = [0] * len(self.Conc)

        self.Plotar = Plotar_graficos
    
    def Update(self,i) -> None:
        self.Vaz_Vap = self.Vaz_Vap_Max * self.Raz_Vaz_Vap[0]
        self.His_Vaz_Vap.append(self.Vaz_Vap)
        self.Vol[0] = self.Vol[0] + (self.Fonte_Alimentação.Vaz - self.Vaz) * dt
        self.alfa    = math.pi * math.pow(self.Raio_Canal_Saída,2) * math.sqrt(2*9.81)
        self.Vaz_max = self.alfa * math.sqrt(self.Altura_Reator * (self.Vol[0]/self.Vol_Max))
        self.Vaz = self.Vaz_max * self.Raz_Vaz[0]
        self.His_vol.append(float(self.Vol[0]))
        self.His_Vaz.append(float(self.Vaz))

        self.prod_reag = 1

        for j in range(0, len(self.Conc), 1):
            self.Mol_Reator[j]  = self.Conc[j] * self.Vol[0]
            self.Mol_Entrada[j] = self.Fonte_Alimentação.Conc[j] * self.Fonte_Alimentação.Vaz * dt
            self.Mol_Saída[j]   = self.Conc[j] * self.Vaz * dt
            
            k_arrhenius = float(self.K_arr(self.Temp[0]))
            self.Mol_Reação[j]  = k_arrhenius * dt
            for k in range(0, len(self.Conc), 1):
                if self.Matriz_Reação[k] < 0:
                    self.Mol_Reação[j] = self.Mol_Reação[j] * math.pow(self.Conc[k], - self.Matriz_Reação[k])

            self.Saldo_Molar[j] = self.Mol_Entrada[j] - self.Mol_Saída[j] + (self.Mol_Reação[j] * np.sign(self.Matriz_Reação[j]))
            self.Mol_Reator[j]  = self.Mol_Reator[j] + self.Saldo_Molar[j] * dt
            self.Conc[j]        = self.Mol_Reator[j] / self.Vol[0]
            if self.Matriz_Reação[j] < 0:
                self.prod_reag = self.prod_reag * math.pow(self.Conc[j], - self.Matriz_Reação[j])

        MConc = list(self.Conc)
        self.His_Conc.append(MConc)
        # saldo de temperatura para o fluido reativo
        f0t0 = self.Fonte_Alimentação.Vaz * self.Fonte_Alimentação.Temp[0]
        ft = self.Vaz * self.Temp[0]
        en_quim = (self.Vol[0] * self.K_arr(self.Temp[0]) * self.prod_reag * self.Var_entalpia) / (self.Dados_Reação.Densidade * self.Dados_Reação.Cp)
        en_troc = (- self.Vaz_Vap * (self.hv - self.hl))/(self.Dados_Reação.Densidade * self.Dados_Reação.Cp)
        self.Saldo_energia = (f0t0 - ft - en_quim - en_troc)/self.Vol[0]
        self.Temp[0] = self.Temp[0] + self.Saldo_energia * dt
        self.His_Temp.append(float(self.Temp[0]))
    
    def Publish(self) -> None:
        if self.Plotar:
            self.fig = plt.figure("Parâmetros de " + self.Name + " X Tempo")
            plt.subplot(2,3,1)
            plt.plot(M_t,np.asarray(self.Temp_S_P) - 273.15,"-", markersize= 1, label= "Set Point", color= "r")
            plt.plot(M_t,np.asarray(self.His_Temp) - 273.15,"o", markersize= 1, label= "Temp. Obs")
            plt.ylim((min(*self.His_Temp,*self.Temp_S_P) - 273.15)*(0.9),(max(*self.His_Temp,*self.Temp_S_P) - 273.15)*(1.1))
            plt.legend()
            plt.xlabel("Tempo [s]")
            plt.ylabel("Temp. Reator [ºC]")

            plt.subplot(2,3,2)
            plt.plot(M_t,np.asarray(self.His_Vaz)*1000,"o", markersize= 1)
            plt.ylim(min(self.His_Vaz)*(0.9*1000),max(self.His_Vaz)*(1.1*1000))
            plt.xlabel("Tempo [s]")
            plt.ylabel("Vazão Reator [Litros/s]")

            plt.subplot(2,3,3)
            plt.plot(M_t,(np.asarray(self.Vol_S_P)*1000),"-", markersize= 1, label= "Set Point", color="r")
            plt.plot(M_t,(np.asarray(self.His_vol)*1000),"o", markersize= 1, label= "Vol. Obs")
            plt.legend()
            plt.xlabel("Tempo [s]")
            plt.ylabel("Cap. Vol. Reator [Litros]")
            
            plt.subplot(2,3,5)
            plt.plot(M_t,np.asarray(self.His_Vaz_Vap),"o", markersize= 1)
            plt.ylim(min(self.His_Vaz_Vap)*(0.9),max(self.His_Vaz_Vap)*(1.1))
            plt.xlabel("Tempo [s]")
            plt.ylabel("Vazão Vapor Saturado [kg/s]")

            plt.subplot(2,3,6)
            for j in range(0, len(self.Conc), 1):
                mat = []
                for k in range(0, n_s*t_tot,1):
                    mat.append(float(self.His_Conc[k][j]))
                plt.plot(M_t,np.asarray(mat),"o", label= self.Dados_Reação.Nomes_reagente[j], markersize= 1)
            plt.xlabel("Tempo [s]")
            plt.ylabel("Concentração Molar [M]")
            plt.legend()

        if (self.MVF == True):
            print("\n\n\nValores finais para: " + self.Name + "========================================")
            print("\nTemperatura Final do Reator:" + str(self.His_Temp[-1] - 273.15) + " ºC")
            print("\nVazão Final do Reator:" + str(self.His_Vaz[-1] * 1000) + " Litros/s")
            print("\nCap. Vol. Final do Reator:" + str(self.His_vol[-1] * 1000) + " Litros (" + str(self.His_vol[-1]/self.Vol_Max) + " x100%)")
            print("\nVazão de Vapor final: " + str(self.His_Vaz_Vap[-1]) + " kg/s (" + str(self.His_Vaz_Vap[-1]/self.Vaz_Vap_Max) + " x100%")
            print("\nMatriz Final de Concentração Molar: \n" + str(self.His_Conc[-1]))


class Controlador_PID:
    def __init__(self, Objeto:object, Alvo_Obs:list, Hist_Obs:list, Reg_Set_Point:list, Set_Point_Obs,
                 Alvo_Ctrl, K_P, K_D, K_I, Resp_Mín, Resp_Max, Graf:bool) -> None:
        
        self.Objeto = Objeto
        self.Alvo_Obs = Alvo_Obs
        self.His_Obs = Hist_Obs
        self.Set_Point = [Set_Point_Obs]
        self.Reg_Set_Point = Reg_Set_Point
        self.Reg_Set_Point.append(self.Set_Point[0])
        self.Alvo_ctrl = Alvo_Ctrl
        self.P = K_P
        self.D = K_D
        self.I = K_I
        self.Resp_Min = Resp_Mín
        self.Resp_Max = Resp_Max
        self.Val_Der = 1
        self.Val_Int = 0
        self.Graf = Graf
        self.Base = float(Alvo_Ctrl[0])
        if (self.Graf == True):
            self.Hist_P = [0]
            self.Hist_I = [0]
            self.Hist_D = [0]
            self.Hist_Var = [0]
    
    def Update(self,i) -> None:
        self.Reg_Set_Point.append(self.Set_Point[0])
        self.Val_Der = (self.His_Obs[i] - self.His_Obs[i-1])/dt
        self.Val_Int = self.Val_Int + ((self.His_Obs[i-1] + self.His_Obs[i] - (2 * self.Set_Point[0])) / 2) *dt
        self.Var = self.Alvo_Obs[0] - self.Set_Point[0]
        P = self.P * self.Var
        D = self.D * self.Val_Der
        I = self.I * self.Val_Int
        self.Resp = self.Base + P + D + I
        self.Alvo_ctrl[0] = self.Resp
        if self.Alvo_ctrl[0] > self.Resp_Max:
            self.Alvo_ctrl[0] = self.Resp_Max
        elif self.Alvo_ctrl[0] < self.Resp_Min:
            self.Alvo_ctrl[0] = self.Resp_Min

        if (self.Graf == True):
            self.Hist_P.append(P)
            self.Hist_I.append(I)
            self.Hist_D.append(D)
            self.Hist_Var.append(self.Var)

    def Publish(self) -> None:
        if (self.Graf == True):
            self.fig = plt.figure("Respostas do Controlador X Tempo")
            plt.subplot(4,1,1)
            plt.plot(M_t,np.asarray(self.Hist_P,),"o", markersize= 1)
            plt.xlabel("Tempo [s]")
            plt.ylabel("Resposta Proporcional")

            plt.subplot(4,1,2)
            plt.plot(M_t,np.asarray(self.Hist_D,),"o", markersize= 1)
            plt.xlabel("Tempo [s]")
            plt.ylabel("Resposta Diferencial")

            plt.subplot(4,1,3)
            plt.plot(M_t,np.asarray(self.Hist_I,),"o", markersize= 1)
            plt.xlabel("Tempo [s]")
            plt.ylabel("Resposta Integral")

            plt.subplot(4,1,4)
            plt.plot(M_t,np.asarray(self.Hist_Var,),"o", markersize= 1, color="r")
            plt.xlabel("Tempo [s]")
            plt.ylabel("Erro Observado")

class Fonte:
    def __init__(self, Vaz_max, Raz_vaz, Temp, Conc:list) -> None:
        self.Vaz_Max = Vaz_max/1000
        self.Raz_Vaz = [Raz_vaz]
        self.Vaz = self.Raz_Vaz[0] * self.Vaz_Max
        self.Temp = [Temp + 273.15]
        self.Conc = Conc

    def Update(self,i) -> None:
        self.Vaz = self.Raz_Vaz[0] * self.Vaz_Max
    
    def Publish(self) -> None:
        pass

class Perturbador_Step:
    def __init__(self,Ligado:bool, Variavel:list, Incremento, A_Partir_de) -> None:
        
        self.Ligado = Ligado
        self.Var = Variavel
        self.Inc = Incremento
        self.Tem = A_Partir_de
        self.pronto = False

    def Update(self,i) -> None:
        if (self.Tem <= i*dt) and (self.pronto == False) and (self.Ligado == True):
            self.Var[0] = self.Var[0] + self.Inc
            self.pronto = True
    
    def Publish(self) -> None:
        pass


def Run(Sist:list):
    print("Iterando simulação")
    total_iterations = n_s*t_tot
    global pb
    pb = tqdm(total=total_iterations, desc='Progresso', ascii=True, smoothing=0.05, position=0, leave=True,
              ncols=100, bar_format='{l_bar}{bar}|')
    for i in range(1, total_iterations):
        for Obj in Sist:
            Obj.Update(i)
            
        pb.update()
            
    print("Gerando Gráficos")
    for Obj in Sist:
        Obj.Publish()
    plt.show()
