import Objetos as Ob

print("Declarando Objetos")

Fluido_Reativo = Ob.info_Fluido_Reativo(
    Nomes_reag= ["AgNO3","Na2S","Ag2S","NaNO3"],
    Var_entalpia= -60000,
    Densidade= 800.9232,
    Cp= 3140.1,
    A= 7.08e10,
    Ej= 80000
)

Fluido_Refrigerante = Ob.info_Fluido_Refrigerante(
    Cp= 4186.8,
    Densidade= 997.9503
)

Fonte_1 =Ob.Fonte(
    Vaz_max= 0.72, # [Litros/s] vazao máxima da fonte
    Raz_vaz= 1, # [x100%] razão de vazão da fonte
    Temp= 26.30, # [ºC] temperatura da fonte
    Conc=[1,0.5,0,0] # [M] concentração da fonte
)
# como o sistema exige retro-alimentação, estou criando uma fonte e linha falsos para pré-inicializar o nó de mistura
Fonte_Placeholder = Ob.Fonte(
    Vaz_max= 0.72 * 0.2, # [Litros/s] vazão inicial do reator vezes a razão de reciclo do sistema
    Raz_vaz= 1, # 100% da vazão máxima jorrando
    Temp= 26.3, # [ºC] temperatura inicial do reator
    Conc= [0.4022*2,0.4022,0.097771,0.097771*2] # [M] concentração inicial do reator
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
    Raz_vaz= 3.6162405495373164e-03, # [x100%] razão de abertura do canal de vazão
    Temp= 25.0, # [ºC] temperatura da fonte do fluido refrigerante
    Conc= [] # [M] Concentração dos elementos no fluido refrigerante (vazio)
)

Linha_J = Ob.Linha(
    Entrada= Fonte_J # entrada da fonte j
)

Reator = Ob.CSTR_C_Resfr(
    Fonte_Alimentção= Linha_2, # fonte de alimentação do reator
    Fonte_Jaqueta= Linha_J, # fonte de alimentação do fluido refrigerante
    Dados_Reação= Fluido_Reativo,
    Matriz_Reação= [-2,-1,1,2],
    Dados_Jaqueta= Fluido_Refrigerante,
    Raz_Vol_in= 0.7, # [x100%] razão de enchimento inicial do reator
    Raio_Canal_Saída= 0.05, # [metros] raio do canal de saída do reator (usado para calcular a vazão máxima em cada momento a depender da altura do nível d'água no reator)
    Vaz_Saída_in= 0.9, # [Litros/s] vazão inicial do reator
    Raio= 0.75, # [metros] raio do reator
    Altura= 1.8, # [metros] altura do reator
    Area_Cobert_Jaqueta= 158.64, # [m²] área de troca térmica do reator
    Vol_Jaqueta= 0.88, # [m³] volume interno da camisa de resfriamento
    Temp_in= 26.3, # [ºC] temperatura inicial do reator
    Temp_in_Jaqueta= 26.299851, # [ºC] temperatura inicial da camisa de resfriamento
    Conc_in= [0.7957506311649223,0.2958595495467816,0.2041404508146229,0.2041404508146229] # [M] matriz de concentrações molares iniciais dos elementos no reator
)

Linha_3 = Ob.Linha(
    Entrada= Reator # entrada da linha 3
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

Controlador_volume = Ob.Controlador_PID(
    Objeto = Reator, # Objeto de controle do reator
    Alvo_Obs = Reator.Vol, # variável do reator a ser observada
    Hist_Obs = Reator.His_vol, # variavel do reator a ser registrada
    Reg_Set_Point= Reator.Vol_S_P,
    Set_Point_Obs = (0.7) * Reator.Vol_Max, # set-point da variável observada
    Alvo_Ctrl = Reator.Raz_Vaz, # variável de controle
    K_P= 7e-3,
    K_D= 1e+0,
    K_I= 5e-8,
    Resp_Mín= 0, # resposta mínima da variável de controle
    Resp_Max= 1, # resposta máxima da variável de controle
    Graf= False
)

Controlador_temp = Ob.Controlador_PID(
    Objeto = Reator, # objeto de controle do reator
    Alvo_Obs = Reator.Temp, # variável do reator a ser observada
    Hist_Obs = Reator.His_Temp, # variável do reator a ser registrada
    Reg_Set_Point= Reator.Temp_S_P,
    Set_Point_Obs = 26.3 + 273.15, # set-point da variável observada
    Alvo_Ctrl = Fonte_J.Raz_Vaz, # variável de controle
    K_P= 5e-7,
    K_D= 2e-2,
    K_I= 5e-9,
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
    Reator,
    Linha_3,
    Reciclo,
    Linha_4,
    Linha_5,
    Controlador_volume,
    Controlador_temp
]

Ob.Run(Sist) # rodar a simulação contendo os objetos desejados