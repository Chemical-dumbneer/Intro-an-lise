import numpy as np
import matplotlib.pyplot as plt

# Limpando vetores
tempoV = []
TV = []
TambV = []
MrefV = []
AMrefV = []

# Condicoes iniciais de operacao
# Fluido estocado: Propano
# Refrigerante: 134a

U = 250                         # W/m2C
A = 2                           # m2
Cp = 2520                       # J/kgC
ma = 10                         # kg
Mref = 0                        # kg/s
Rmax = 0.1                      # razao de velocidade da valvula
dt = 0.001                      # s
hv = 247000                     # J/kg
hl = 50000                      # J/kg
M = 44                          # g/mol
T = 10                          # C  
Tant = T                        

# Temperatura do SetPoint
Tset = -12.2                    # temperatura do setpoint

# Constantes do controlador PID
kc = -0.1  #VR= -0.1  S= -0.037   Sa= -0.018
Tdv = 0
Tiv = 10  #VR= 10  S= -20 S  SA= -1

# Variaveis erro 0
Mref_erro0 = 0.1

# Valores Iniciais dos Controladores
intPID = 0
erro1V = 0
erro2V = erro1V

# Tempo Sample
tsample = 2   #S= 2  SA= tsampe>2
Mrefant = Mref

# Tempo de simulacao
tf = 80
AMref = 0
tempo = 0
i = 1

# Inicio do loop do tempo
while tempo <= tf:

    # Temperatura ambientes
    Tamb = 18.3
    
    # O controlador PID de vazao de refrigerante
    # ---------------------------------------------------------------------------
    # A integral do PID no volume
    intPID = intPID + (Tset-T)*dt
    # A derivada do PID no volume
    derPID = (erro2V-erro1V)/dt
    erro1V = erro2V
    # A parte proporcional do PID no volume
    proPID = (Tset-T)
    # A equacao do PID no volume
    Mref = Mref_erro0 + kc*proPID + kc*Tdv*derPID + (kc/Tiv)*intPID
    
   #Sample:
       
    # if (abs(round(tempo/tsample) - (tempo/tsample)) < 1e-4):
        
    #     #     print(tempo)
        
    #     # O controlador PID de vazao de refrigerante
    #     # ---------------------------------------------------------------------------
    #     # A integral do PID no volume
    #     intPID = intPID + (Tset-T)*dt
    #     # A derivada do PID no volume
    #     derPID = (erro2V-erro1V)/dt
    #     erro1V = erro2V
    #     # A parte proporcional do PID no volume
    #     proPID = (Tset-T)
    #     # A equacao do PID no volume
    #     Mref = Mref_erro0 + kc*proPID + kc*Tdv*derPID + (kc/Tiv)*intPID
   
    
    

    # Sample Adaptativo:
   
    # if (abs(T-Tant)/dt)>2:
    #     tsample = 2
    #     Tant = T
    #     if (abs(round(tempo/tsample) - (tempo/tsample)) < 1e-4):
           
    #         # O controlador PID de vazao de refrigerante
    #         # ---------------------------------------------------------------------------
    #         # A integral do PID no volume
    #         intPID = intPID + (Tset-T)*dt
    #         # A derivada do PID no volume
    #         derPID = (erro2V-erro1V)/dt
    #         erro1V = erro2V
    #         # A parte proporcional do PID no volume
    #         proPID = (Tset-T)
    #         # A equacao do PID no volume
    #         Mref = Mref_erro0 + kc*proPID + kc*Tdv*derPID + (kc/Tiv)*intPID

       
        # ---------------------------------------------------------------------------

    erro2V = Tset - T

    # A Valvula real
    if Mref >= Mrefant:
        if (Mref - Mrefant) > Rmax:
            Mref = Mrefant + Rmax

    if Mref < Mrefant:
        if (Mrefant - Mref) > Rmax:
            Mref = Mrefant - Rmax

    Mrefant = Mref

    # Calculo da integral sobre Mref
    AMref = AMref + Mref*dt

    # Calculando a derivada dT/dtempo
    dTdt = (U*A/(ma*Cp))*(Tamb - T) - (Mref/(ma*Cp))*(hv-hl)

    # Calculando a temperatura
    T = T + dTdt*dt

    # Vetorizando para a plotagem
    tempoV.append(tempo)
    TV.append(T)
    TambV.append(Tamb)
    MrefV.append(Mref)
    AMrefV.append(AMref)

    tempo = tempo + dt
    i = i + 1

# Plotando os graficos
plt.subplot(2, 2, 1)
plt.plot(tempoV, TV, '.')
plt.xlabel('tempo')
plt.ylabel('T')
plt.subplot(2, 2, 2)
plt.plot(tempoV, TambV, '.')
plt.xlabel('tempo')
plt.ylabel('Temperatura amb.')
plt.subplot(2, 2, 3)
plt.plot(tempoV, MrefV, '.')
plt.xlabel('tempo')
plt.ylabel('Vazao de Refrigerante')
plt.subplot(2, 2, 4)
plt.plot(tempoV, AMrefV, '.')
plt.xlabel('tempo')
plt.ylabel('Massa de Refrigerante')
#plt.subplots_adjust(left=0.125, bottom=0.1, right=1.9, top=1.5, wspace=0.4, hspace=0.4)
plt.show()
##    print('Foram utilizados', str(AMref), 'kg de r134.')


