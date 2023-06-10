import Objetos as Ob

print("Declarando Objetos")

Fluido_Reativo = Ob.info_Fluido_Reativo(
    Nomes_reag= ["AgNO3","Na2S","Ag2S","NaNO3","HNO3","H2S"],
    Densidade= 800.9232,
    Cp= 3140.1
)

Fluido_Refrigerante = Ob.info_Fluido_Refrigerante(
    Cp= 4186.8,
    Densidade= 997.9503
)

Fonte_1 =Ob.Fonte(
    Vaz_max= 0.72, # [Litros/s] vazao máxima da fonte
    Raz_vaz= 1, # [x100%] razão de vazão da fonte
    Temp= 26.30, # [ºC] temperatura da fonte
    Conc=[1,0.5,0,0,0,0] # [M] concentração da fonte
)
# como o sistema exige retro-alimentação, estou criando uma fonte e linha falsos para pré-inicializar o nó de mistura
Fonte_Placeholder = Ob.Fonte(
    Vaz_max= 0.72 * 0.2, # [Litros/s] vazão inicial do reator vezes a razão de reciclo do sistema
    Raz_vaz= 1, # 100% da vazão máxima jorrando
    Temp= 26.3, # [ºC] temperatura inicial do reator
    Conc= [0.4022*2,0.4022,0.097771,0.097771*2,0,0] # [M] concentração inicial do reator
)

Linha_falsa = Ob.Linha(
    Entrada= Fonte_Placeholder
)

Linha_1 = Ob.Linha(
    Entrada= Fonte_1 # entrada da linha 1
)

Nó_Mistura_1 = Ob.Nó_Mistura(
    Entrada1= Linha_1, # entrada 1 do nó de mistura
    Entrada2= Linha_falsa # entrada 2 do nó de mistura (pré-definido como linha falsa somente para inicializar o objeto)
)

Linha_2 = Ob.Linha(
    Entrada= Nó_Mistura_1 # entrada da linha 2
)

Fonte_J = Ob.Fonte(
    Vaz_max= 1, # [Litros/s] vazão máxima do fluido refrigerante
    Raz_vaz= 0.0036162869512283264, # [x100%] razão de abertura do canal de vazão
    Temp= 25.0, # [ºC] temperatura da fonte do fluido refrigerante
    Conc= [] # [M] Concentração dos elementos no fluido refrigerante (vazio)
)

Linha_J = Ob.Linha(
    Entrada= Fonte_J # entrada da fonte j
)

Reator_1 = Ob.CSTR_C_Resfr(
    Mostrar_Val_Finais=True,
    Nome_Reator= "Reator 1",
    Fonte_Alimentção= Linha_2, # fonte de alimentação do reator
    Fonte_Jaqueta= Linha_J, # fonte de alimentação do fluido refrigerante
    Dados_Reação= Fluido_Reativo,
    Matriz_Reação= [-2,-1,1,2,0,0],
    Var_entalpia= -60000,
    Ej= 80000,
    A= 7.08e10,
    Dados_Jaqueta= Fluido_Refrigerante,
    Raz_Vol_in= 0.7, # [x100%] razão de enchimento inicial do reator
    Raio_Canal_Saída= 0.05, # [metros] raio do canal de saída do reator (usado para calcular a vazão máxima em cada momento a depender da altura do nível d'água no reator)
    Vaz_Saída_in= 0.9, # [Litros/s] vazão inicial do reator
    Raio= 0.75, # [metros] raio do reator
    Altura= 1.8, # [metros] altura do reator
    Area_Cobert_Jaqueta= 158.64, # [m²] área de troca térmica do reator
    Vol_Jaqueta= 0.88, # [m³] volume interno da camisa de resfriamento
    Temp_in= 26.3, # [ºC] temperatura inicial do reator
    Temp_in_Jaqueta= 26.299854645225196, # [ºC] temperatura inicial da camisa de resfriamento
    Conc_in= [0.7958124085721613, 0.29581834026726184, 0.20418165965338808, 0.20418165965338808, 0.0, 0.0] # [M] matriz de concentrações molares iniciais dos elementos no reator
)

Linha_3 = Ob.Linha(
    Entrada= Reator_1 # entrada da linha 3
)

Reciclo = Ob.Nó_Reciclo(
    Entrada= Linha_3, # entrada do nó de reciclo
    Raz_reciclo_in= 0.2 # razão de reciclo do sistema
)

Linha_4 = Ob.Linha(
    Entrada= Reciclo.Reciclo # entrada da linha 4
)

Nó_Mistura_1.Fonte2 = Linha_4 # re-ajuste do nó de mistura agora que a linha 4 já está devidamente declarada

Linha_5 = Ob.Linha(
    Reciclo.Saída # entrada da linha 5
)

Controlador_volume_R1 = Ob.Controlador_PID(
    Objeto = Reator_1, # Objeto de controle do reator
    Alvo_Obs = Reator_1.Vol, # variável do reator a ser observada
    Hist_Obs = Reator_1.His_vol, # variavel do reator a ser registrada
    Reg_Set_Point= Reator_1.Vol_S_P,
    Set_Point_Obs = (0.7) * Reator_1.Vol_Max, # set-point da variável observada
    Alvo_Ctrl = Reator_1.Raz_Vaz, # variável de controle
    K_P= 7e-3,
    K_D= 1e+0,
    K_I= 5e-8,
    Resp_Mín= 0, # resposta mínima da variável de controle
    Resp_Max= 1, # resposta máxima da variável de controle
    Graf= False
)

Controlador_temp_R1 = Ob.Controlador_PID(
    Objeto = Reator_1, # objeto de controle do reator
    Alvo_Obs = Reator_1.Temp, # variável do reator a ser observada
    Hist_Obs = Reator_1.His_Temp, # variável do reator a ser registrada
    Reg_Set_Point= Reator_1.Temp_S_P,
    Set_Point_Obs = 26.3 + 273.15, # set-point da variável observada
    Alvo_Ctrl = Fonte_J.Raz_Vaz, # variável de controle
    K_P= 64e-4,#5e-7,
    K_D= 1,#2e-2,
    K_I= 0,#5e-9,
    Resp_Mín= 0, # resposta mínima da variável de controle
    Resp_Max= 1, # resposta máxima da variável de controle
    Graf= False
)

Fonte_3 = Ob.Fonte(
    Vaz_max= 1,
    Raz_vaz= 0.5,
    Temp= 15,
    Conc= [0,0,0,0,0.5,0]
)

Linha_6 = Ob.Linha(
    Entrada= Fonte_3
)

Nó_Mistura_2 = Ob.Nó_Mistura(
    Entrada1= Linha_5,
    Entrada2= Linha_6
)

Linha_7 = Ob.Linha(
    Entrada= Nó_Mistura_2
)

Nó_Mistura_3 = Ob.Nó_Mistura(
    Entrada1= Linha_7,
    Entrada2= Linha_falsa
)

Linha_8 = Ob.Linha(
    Entrada= Nó_Mistura_3
)

Reator_2 = Ob.CSTR_C_Aquec(
    Mostrar_Val_Finais= True,
    Nome_Reator= "Reator 2",
    Fonte_Alimentção= Linha_8,
    Raz_Vol_in= 0.7,
    Vaz_Saída_in= 1.5250000000010095,
    Raio= 0.75,
    Altura= 1.8,
    Temp_in= 26.3,
    A= 7.08e10,
    Ej= 50000,
    Vaz_Mássica_Vapor_Máxima= 1,
    Raz_vaz_Vap_in= 0.006322025807139162,
    Ent_mass_Vapor= 2257000,
    Ent_mass_Líq= 4190,
    Raio_Canal_Saída= 0.05,
    Var_entalpia= 100000,
    Conc_in= [0.5900289517829574, 0.17459826464777223, 0.0001528279742041155, 0.12052041741186888, 0.08459018371672564, 0.12036909065356977],
    Dados_Reação= Fluido_Reativo,
    Matriz_Reação= [2,0,-1,0,-2,1]
)

Linha_9 = Ob.Linha(
    Entrada= Reator_2
)

Reciclo_2 = Ob.Nó_Reciclo(
    Entrada= Linha_9,
    Raz_reciclo_in= 0.2
)

Linha_10 = Ob.Linha(
    Entrada= Reciclo_2.Saída
)

Linha_11 = Ob.Linha(
    Entrada= Reciclo_2.Reciclo
)

Nó_Mistura_3.Fonte2 = Linha_11

Controlador_volume_R2 = Ob.Controlador_PID(
    Objeto = Reator_2, # Objeto de controle do reator
    Alvo_Obs = Reator_2.Vol, # variável do reator a ser observada
    Hist_Obs = Reator_2.His_vol, # variavel do reator a ser registrada
    Reg_Set_Point= Reator_2.Vol_S_P,
    Set_Point_Obs = (0.7) * Reator_2.Vol_Max, # set-point da variável observada
    Alvo_Ctrl = Reator_2.Raz_Vaz, # variável de controle
    K_P= 0.5,
    K_D= 1,
    K_I= 0,
    Resp_Mín= 0, # resposta mínima da variável de controle
    Resp_Max= 1, # resposta máxima da variável de controle
    Graf= False
)

Controlador_temp_R2 = Ob.Controlador_PID(
    Objeto = Reator_2, # objeto de controle do reator
    Alvo_Obs = Reator_2.Temp, # variável do reator a ser observada
    Hist_Obs = Reator_2.His_Temp, # variável do reator a ser registrada
    Reg_Set_Point= Reator_2.Temp_S_P,
    Set_Point_Obs = 26.3 + 273.15, # set-point da variável observada
    Alvo_Ctrl = Reator_2.Raz_Vaz_Vap, # variável de controle
    K_P= -64e-4,#5e-7,
    K_D= -1,#2e-2,
    K_I= 0,
    Resp_Mín= 0, # resposta mínima da variável de controle
    Resp_Max= 1, # resposta máxima da variável de controle
    Graf= False
)

Sist = [ # juntando todos os objetos reais do sistema a serem iterados na simulação
    Fonte_1,
    Linha_1,
    Nó_Mistura_1,
    Linha_2,
    Fonte_J,
    Linha_J,
    Reator_1,
    Linha_3,
    Reciclo,
    Linha_4,
    Linha_5,
    Linha_7,
    Nó_Mistura_3,
    Linha_8,
    Reator_2,
    Linha_9,
    Reciclo_2,
    Linha_10,
    Linha_11,
    Controlador_volume_R1,
    Controlador_temp_R1,
    Controlador_volume_R2,
    Controlador_temp_R2
]

Ob.Run(Sist) # rodar a simulação contendo os objetos desejados