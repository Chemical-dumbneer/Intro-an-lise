import math
import matplotlib.pyplot as plt
import numpy as np

i = 0
n_s = 200
t_tot = 30
dt = 1/n_s
M_t = np.arange(0,t_tot,dt)

class Linha:
    def __init__(self, Entrada) -> None:
        self.Temp = Entrada.Temp
        self.Vaz = Entrada.vaz
        self.Conc = Entrada.Conc
        self.Fonte = Entrada
    
    def Update(self) -> None:
        self.Temp = self.Fonte.Temp
        self.Vaz = self.Fonte.Vaz
        self.Conc = self.Fonte.Conc

    def Publish(self) -> None:
        pass

class Nó_Mistura:
    def __init__(self, Entrada1:Linha, Entrada2:Linha) -> None:
        self.Vaz = Entrada1.Vaz + Entrada2.Vaz
        self.Temp = ((Entrada1.Temp*Entrada1.Vaz)+(Entrada2.Temp*Entrada2.Vaz))/self.Vaz
        self.Conc = []

        for j in range(0, len(Entrada1.Conc) - 1, 1):
            self.Conc[j] = ((Entrada1.Conc[j]*Entrada1.Vaz) + (Entrada2.Conc[j]*Entrada2.Vaz))/self.Vaz

        self.Fonte1 = Entrada1
        self.Fonte2 = Entrada2
    
    def Update(self) -> None:
        self.Vaz = self.Fonte1.Vaz + self.Fonte2.Vaz
        self.Temp = ((self.Fonte1.Temp*self.Fonte1.Vaz)+(self.Fonte2.Temp*self.Fonte2.Vaz))/self.Vaz

        for j in range(0, len(self.Conc) - 1, 1):
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

    def Update(self) -> None:
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

    Dados_Reação = type('',(),{})()
    Dados_Reação.Matriz_reagente = [-1,-1,1,1]
    Dados_Reação.Nomes_reagente = ["A","B","C","D"]
    Dados_Reação.Var_entalpia = -300
    Dados_Reação.Densidade = 1000
    Dados_Reação.Cp = 100
    Dados_Reação.A = 10
    Dados_Reação.Ej = 200

    Dados_Jaqueta = type('',(),{})()
    Dados_Jaqueta.Cp = 100
    Dados_Jaqueta.Densidade = 1000

    def K_arr(self, Temp):
        return self.Dados_Reação.A * math.exp((-self.Dados_Reação['Ej'])/(8.314 * Temp))

    def __init__(self, Fonte_Alimentção:Linha, Fonte_Jaqueta:Linha, Raz_Vol_in,
                 Raz_vaz_in, Raio, Altura, Area_Cobert_Jaqueta, Vol_Jaqueta,
                 Temp_in, Conc_in:list) -> None:
        
        self.Fonte_Alimentação = Fonte_Alimentção
        self.Fonte_Jaqueta     = Fonte_Jaqueta
        self.Temp_Jaqueta      = self.Fonte_Jaqueta.Temp
        self.His_Temp_J        = []
        self.His_Vaz_J         = []
        self.His_Temp_J.append(self.Temp_Jaqueta)
        self.His_Vaz_J.append(self.Fonte_Jaqueta.Vaz)

        self.A_tt        = Area_Cobert_Jaqueta
        self.Vol_Jaqueta = Vol_Jaqueta
        self.U_tt        = 368 # vide https://www.tlv.com/global/BR/steam-theory/overall-heat-transfer-coefficient.html para mais info

        self.Vol_Max       = Altura * math.pi * math.pow(Raio,2)
        self.Vol           = self.Vol_Max * Raz_Vol_in
        self.Altura_Reator = Altura

        self.His_vol  = []
        self.His_vol.append(self.Vol)
        self.Temp     = Temp_in + 273.15
        self.His_Temp = []
        self.His_Temp.append(self.Temp)

        self.alfa    = math.pi * math.pow(0.1 * Raio,2) * math.sqrt(2*9.81)
        self.Vaz_max = self.alfa * math.sqrt(self.Altura_Reator * (self.Vol/self.Vol_Max))
        self.Vaz     = self.Vaz_max * Raz_vaz_in

        self.His_Vaz  = []
        self.His_Conc = []
        self.His_Vaz.append(self.Vaz)
        self.Conc     = Conc_in
        self.His_Conc.append(self.Conc)
        self.Raz_Vaz  = 1

        self.Mol_Reator  = [0] * len(self.Conc)
        self.Mol_Entrada = [0] * len(self.Conc)
        self.Mol_Saída   = [0] * len(self.Conc)
        self.Mol_Reação  = [0] * len(self.Conc)
        self.Saldo_Molar = [0] * len(self.Conc)
    
    def Update(self) -> None:
        self.Vol = self.Vol + (self.Fonte_Alimentação.Vaz - self.Vaz) * dt
        self.Vaz = self.Vaz_max * self.Raz_Vaz
        self.His_vol.append(self.Vol)
        self.His_Vaz.append(self.Vaz)

        self.prod_reag = 1
        for j in range(0, len(self.Conc), 1):
            self.Mol_Reator[j]  = self.Conc[j] * self.Vol
            self.Mol_Entrada[j] = self.Fonte_Alimentação.Conc[j] * self.Fonte_Alimentação.Vaz * dt
            self.Mol_Saída[j]   = self.Conc[j] * self.Vaz * dt

            self.Mol_Reação[j]  = self.K_arr(self.Temp) * dt
            for k in range(0, len(self.Conc), 1):
                if self.Dados_Reação.Matriz_reagente[k] < 0:
                    self.Mol_Reação[j] = self.Mol_Reação[j] * math.pow(self.Conc[k], -self.Dados_Reação.Matriz_reagente[k])

            self.Saldo_Molar[j] = self.Mol_Entrada[j] - self.Mol_Saída[j] + (self.Mol_Reação[j] * (self.Dados_Reação.Matriz_reagente[j]/abs(self.Dados_Reação.Matriz_reagente[j])))
            self.Mol_Reator[j]  = self.Mol_Reator[j] + self.Saldo_Molar[j]
            self.Conc[j]        = self.Mol_Reator[j] / self.Vol
            if self.Dados_Reação.Matriz_reagente[j] < 0:
                self.prod_reag = self.prod_reag * math.pow(self.Conc[j], - self.Dados_Reação.Matriz_reagente[j])

        self.His_Conc.append(self.Conc)
        # saldo de temperatura para o fluido reativo
        self.Saldo_energia = (
            ((self.His_Vaz[i-1] * self.His_Temp[i-1]) - (self.Fonte_Alimentação.Vaz * self.Fonte_Alimentação.Temp) -
            (((self.His_vol[i-1] * self.K_arr(self.His_Temp[i-1]) * self.prod_reag * self.Dados_Reação.Var_entalpia) -
            ((self.U_tt * self.A_tt * (self.Temp - self.Temp_Jaqueta))/(self.Dados_Reação.Densidade * self.Dados_Reação.Cp)))))/self.Vol
        )
        self.Temp = self.Temp + self.Saldo_energia
        self.His_Temp.append(self.Temp)
        # saldo de temperatura para o fluido refrigerante
        self.Saldo_energia = (
            ((self.Fonte_Jaqueta.Vaz * (self.Temp_Jaqueta - self.Temp))/self.Vol_Jaqueta) +
            ((self.U_tt * self.A_tt * (self.Temp - self.Temp_Jaqueta))/(self.Vol_Jaqueta * self.Dados_Jaqueta.Densidade * self.Dados_Jaqueta.Cp))
        )

        self.Temp_Jaqueta = self.Temp_Jaqueta + self.Saldo_energia
        self.His_Temp_J.append(self.Temp_Jaqueta)
        self.His_Vaz_J.append(self.Fonte_Jaqueta.Vaz)
    
    def Publish(self) -> None:

        plt.subplot(2,3,1)
        plt.plot(M_t,
                 np.asarray(self.His_Temp) - 273.15,
                 ls= "-")
        plt.xlabel("Tempo [s]")
        plt.ylabel("Temp. Reator [ºC]")

        plt.subplot(2,3,2)
        plt.plot(np.asarray(self.His_Vaz),"-")
        plt.xlabel("Tempo [s]")
        plt.ylabel("Vazão Reator [Litros/s]")

        plt.subplot(2,3,3)
        plt.plot(np.asarray(self.His_vol)/self.Vol_Max,"-")
        plt.xlabel("Tempo [s]")
        plt.ylabel("Cap. Vol. Reator [%]")

        plt.subplot(2,3,4)
        plt.plot(np.asarray(self.His_Temp_J) - 273.15,"-")
        plt.xlabel("Tempo [s]")
        plt.ylabel("Temp. Jaqueta [ºC]")
        
        plt.subplot(2,3,5)
        plt.plot(np.asarray(self.His_Vaz_J),"-")
        plt.xlabel("Tempo [s]")
        plt.ylabel("Vazão Jaqueta [Litros/s]")

        plt.subplot(2,3,6)
        for j in range(0, len(self.Conc), 1):
            mat = []
            for k in range(0, n_s*t_tot,1):
                mat.append(self.His_Conc[k][j])
            plt.plot(np.asarray(mat),)

class Controlador_PID:
    def __init__(self, Objeto:object, Alvo_Obs, Hist_Obs:list, Set_Point_Obs,
                 Alvo_Ctrl, K_P, K_D, K_I, Resp_Mín, Resp_Max) -> None:
        
        self.Objeto = Objeto
        self.Alvo_Obs = Alvo_Obs
        self.His_Obs = Hist_Obs
        self.Set_Point = Set_Point_Obs
        self.Alvo_ctrl = Alvo_Ctrl
        self.P = K_P
        self.D = K_D
        self.I = K_I
        self.Resp_Min = Resp_Mín
        self.Resp_Max = Resp_Max
        self.Val_Der = 1
        self.Val_Int = 0
    
    def Update(self) -> None:
        self.Val_Der = (self.His_Obs[i] - self.His_Obs[i-1])/dt
        self.Val_Int = self.Val_Int + ((self.His_Obs[i-1] + self.His_Obs[i] - (2 * self.Set_Point)) / 2) *dt
        self.Var = self.Alvo_Obs - self.Set_Point

        self.Resp = self.P * self.Var + self.D * self.Val_Der + self.I * self.Val_Int
        self.Alvo_ctrl = self.Alvo_ctrl + self.Resp
        if self.Alvo_ctrl > self.Resp_Max:
            self.Alvo_ctrl = self.Resp_Max
        elif self.Alvo_ctrl < self.Resp_Min:
            self.Alvo_ctrl = self.Resp_Min

    def Publish(self) -> None:
        pass        

class Fonte:
    def __init__(self, Vaz_max, Raz_vaz, Temp, Conc:list) -> None:
        self.Vaz_Max = Vaz_max
        self.Raz_Vaz = Raz_vaz
        self.Vaz = self.Raz_Vaz * self.Vaz_Max
        self.Temp = Temp
        self.Conc = Conc

    def Update(self) -> None:
        self.Vaz = self.Raz_Vaz * self.Vaz_Max
    
    def Publish(self) -> None:
        pass

Fonte_1 = Fonte(
    Vaz_max= 40,
    Raz_vaz= 1,
    Temp= 50,
    Conc=[0.5,0.5,0,0]
)

Linha_1 = Linha(
    Entrada= Fonte_1
)

Nó_Mistura_1 = Nó_Mistura(
    Entrada1= Linha_1,
    Entrada2= Linha_1
)

Linha_2 = Linha(
    Entrada= Nó_Mistura_1
)

Fonte_J = Fonte(
    Vaz_max= 20,
    Raz_vaz= 1,
    Temp= 15,
    Conc= []
)

Linha_J = Linha(
    Entrada= Fonte_J
)

Reator = CSTR_C_Resfr(
    Fonte_Alimentção= Linha_2,
    Fonte_Jaqueta= Linha_J,
    Raz_Vol_in= 0.4,
    Raz_vaz_in= 0.2,
    Raio= 1,
    Altura= 2,
    Area_Cobert_Jaqueta= 15,
    Vol_Jaqueta= 2,
    Temp_in= 50,
    Conc_in= [0,0,0,0]
)

Linha_3 = Linha(
    Entrada= Reator
)

Reciclo = Nó_Reciclo(
    Entrada= Linha_3,
    Raz_reciclo_in= 0.5
)

Linha_4 = Linha(
    Entrada= Reciclo.Reciclo
)

Nó_Mistura_1.Fonte2 = Linha_4

Linha_5 = Linha(
    Reciclo.Saída
)

Sist = [
    Fonte_1,
    Linha_1,
    Nó_Mistura_1,
    Linha_2,
    Fonte_J,
    Linha_J,
    Reator,
    Linha_3,
    Reciclo,
    Linha_4,
    Linha_5
]

for i in range(1 , n_s*t_tot, 1):
    for Obj in Sist:
        Obj.Update()

for Obj in Sist:
    Obj.Publish()
