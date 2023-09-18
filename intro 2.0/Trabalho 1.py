import Objetos_2 as Ob

Fonte_1 = Ob.Fonte(
    Vaz_max= 0.72,  # [Litros/s] vazao máxima da fonte
    Raz_vaz= 1, # [x100%] razão de vazão da fonte
    Temp= 35, # [ºC] temperatura da fonte
    Conc= [16,8,0,0] # [M] concentração da fonte
)

Fonte_Placeholder = Ob.Fonte(
    Vaz_max= 0.72 ,#* 0.2, # [Litros/s] vazão inicial do reator vezes a razão de reciclo do sistema
    Raz_vaz= 1, # 100% da vazão máxima jorrando
    Temp= 26.3, # [ºC] temperatura inicial do reator
    Conc= [0.08762235968978731, 0.7569098679311016, 7.048998582730179, 14.097997165460358] # [M] concentração inicial do reator
)

Nó_Mistura_1 = Ob.Nó_2_p_1(
    Entrada_1= Fonte_1.Saída,
    Entrada_2= Fonte_Placeholder.Saída
)

Fonte_Jaqueta = Ob.Fonte(
    Vaz_max= 5*3, # [Litros/s] vazão máxima do fluido refrigerante
    Raz_vaz= 0.29720569541429015/3, # [x100%] razão de abertura do canal de vazão
    Temp= 5, # [ºC] temperatura da fonte do fluido refrigerante
    Conc= [] # [M] Concentração dos elementos no fluido refrigerante (vazio)
)

Reator = Ob.CSTR(
    Type= 1,
    Info_fluido_reativo= Ob.Info(
        Nomes_reag= ["AgNO3","Na2S","Ag2S","NaNO3"],
        Densidade= 800.9232,
        Cp= 3140.1
    ),
    Nome_Reator= "Reator com Aquecimento"
)

Reator.Add_Reação(
    Ob.Reação(
        Ej= 60000.0,
        A= 7.08e10,
        Matriz_Reação= [-2,-1,1,2],
        Var_entalpia= -10000000.0
    )
)

Reator.Parâm_Gerais(
    Entrada= Nó_Mistura_1.Saída,
    Raio= 0.75, # [metros] raio do reator
    Altura= 1.8, # [metros] altura do reator
    Raio_Canal_Saída= 0.05, # [metros] raio do canal de saída do reator (usado para calcular a vazão máxima em cada momento a depender da altura do nível d'água no reator)
    Raz_Vol_In= 0.7, # [x100%] razão de enchimento inicial do reator
    Vaz_Saída_In= 0.72, # [Litros/s] vazão inicial do reator
    Temp_in= 26.3, # [ºC] temperatura inicial do reator
    Conc_In= [0.22426178202043817, 0.11483166480750001, 7.884433149272131, 15.768866298544262] # [M] matriz de concentrações molares iniciais dos elementos no reator
)

