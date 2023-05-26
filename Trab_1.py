import Objetos as Ob

print("Declarando Objetos")

Fonte_1 =Ob.Fonte(
    Vaz_max= 0.72,
    Raz_vaz= 1,
    Temp= 26.30,
    Conc=[0.5,0.5,0,0]
)

Linha_1 = Ob.Linha(
    Entrada= Fonte_1
)

Nó_Mistura_1 = Ob.Nó_Mistura(
    Entrada1= Linha_1,
    Entrada2= Linha_1
)

Linha_2 = Ob.Linha(
    Entrada= Nó_Mistura_1
)

Fonte_J = Ob.Fonte(
    Vaz_max= 0.13,
    Raz_vaz= 1,
    Temp= 26.30,
    Conc= []
)

Linha_J = Ob.Linha(
    Entrada= Fonte_J
)

Reator = Ob.CSTR_C_Resfr(
    Fonte_Alimentção= Linha_2,
    Fonte_Jaqueta= Linha_J,
    Raz_Vol_in= 0.7,
    Raz_vaz_in= 0,
    Raio= 0.75,
    Altura= 1.8,
    Area_Cobert_Jaqueta= 158.64,
    Vol_Jaqueta= 0.88,
    Temp_in= 26.3,
    Conc_in= [0.4022,0.4022,0.097771,0.097771]
)

Linha_3 = Ob.Linha(
    Entrada= Reator
)

Reciclo = Ob.Nó_Reciclo(
    Entrada= Linha_3,
    Raz_reciclo_in= 0.2
)

Linha_4 = Ob.Linha(
    Entrada= Reciclo.Reciclo
)

Nó_Mistura_1.Fonte2 = Linha_4

Linha_5 = Ob.Linha(
    Reciclo.Saída
)

Controlador_volume = Ob.Controlador_PID(
    Objeto = Reator,
    Alvo_Obs = Reator.Vol,
    Hist_Obs = Reator.His_vol,
    Set_Point_Obs = 0.7 * Reator.Vol_Max,
    Alvo_Ctrl = Reator.Raz_Vaz,
    K_P= -1,
    K_D= 0,
    K_I= 0,
    Resp_Mín= 0,
    Resp_Max= 1
)

Controlador_temp = Ob.Controlador_PID(
    Objeto = Reator,
    Alvo_Obs = Reator.Temp,
    Hist_Obs = Reator.His_Temp,
    Set_Point_Obs = 26.3,
    Alvo_Ctrl = Fonte_J.Raz_Vaz,
    K_P= 1,
    K_D= 1,
    K_I= 1,
    Resp_Mín= 0,
    Resp_Max= 1
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
    Linha_5,
    Controlador_volume,
    Controlador_temp
]

Ob.Run(Sist)