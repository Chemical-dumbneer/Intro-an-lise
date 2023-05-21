% Limpando vetores

 clear   tempoV;
 clear   CaV;
 clear    TV;
 clear    VV;
 clear    FV;
 clear    TjV;
 clear    FjV;
 clear    CbV;
 clear    CcV;
 clear    CdV;

 clear FrV;
 clear F1V;
 clear F0V;

%Condições iniciais de operação

% Alimentacao do Sistema (entrada) (F1)
F1=92;      % ft3/h
T1=530;     % ?R
Ca1=0.5;    % lb mol/ft3
Cb1=0.5;    % lb mol/ft3
Cc1=0;      % lb mol/ft3
Cd1=0;      % lb mol/ft3

Fj=17.027;  % ft3/h
Tj0=530;    % ?R

% Saida do CSTR (saida) (F)
F=115.00;                    % ft3/h
T=590.07;               % ?R
Ca=0.4022;               % lb mol/ft3
Cb=0.4022;               % lb mol/ft3
Cc=0.097771;               % lb mol/ft3
Cd=0.097771;               % lb mol/ft3
Tj=589.02;              % ?R

% Dimensões
V=97.852880299;       % ft3
vj=31.249030401;      % ft3;
A=397.701130124;      % ft2

%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%

    %Razão de reciclo
    razao_reciclo = 0.2;

    %Nó 2 (de bifurcação)
    f_reciclo=F*razao_reciclo;
    Ca_reciclo=Ca;
    Cb_reciclo=Cb;
    Cc_reciclo=Cc;
    Cd_reciclo=Cd;
    T_reciclo=T;

    %Na saída, após o reciclo (Saída, ponto 2)
    F_saida=F-f_reciclo; %f_saida é o F2
    Ca_saida=Ca;
    Cb_saida=Cb;
    Cc_saida=Cc;
    Cd_saida=Cd;
    T_saida=T;

    %Nó 1 (de mistura)
    F0=F1+f_reciclo;
    Ca0=(F1*Ca1+f_reciclo*Ca_reciclo)/(F0);
    Cb0=(F1*Cb1+f_reciclo*Cb_reciclo)/(F0);
    Cc0=(F1*Cc1+f_reciclo*Cc_reciclo)/(F0);
    Cd0=(F1*Cd1+f_reciclo*Cd_reciclo)/(F0);

    T0=(F1*T1+f_reciclo*T_reciclo)/(F0);

 %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
 %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%


% Coeficiente global de troca t?rmica
U=150;      % BTU/(h ft2 ?R)

% Propriedades do Fluido reativo
cp=0.75;    % BTU/(lb ?R)
ro=50;      % lb/ft3

% Propriedades do Fluido refrigerante (da jaqueta)
cpj=1;      % BTU/(lb ?R)
roj=62.3;   % lb/ft3

% Condicoes de operacao (set points)
Tset=590.07;   % ?R
Vset=97.852880299;        % ft3

% Vazoes para quando o erro (variavel no setponi - variavel) for zero
Fjerrozero = 17.027;    % ft3/h
Ferrozero = 115.00;         % ft3/h

% Calor de reacao
deltaH=-30000;          %BTU/lb mol de A

% Constantes de Arrenius
Aa=7.08e10; % fator pre-exponencial  1/h
Ea=30000;   % energia de ativa??o    BTU/lb mol
Ra=1.99;    % constante dos gases    BTU/(lb mol ?R)

% Constante do controlador do fluido refrigerante
Kj=-16;
Tdj=0;
Tij=0.2;

% Constantes do controlador da vazao de saida
Kf=-40;
Tdf=0;
Tif=0.7;

% Passo de tempo das equacoes diferenciais
dt=0.005;   % h

% Passo de impress?o da tabela
pi=0.2;

% Tempo de simulacao
tf=10;       % h

% Calculado os produtos V*Ca, V*Cb e V*T
VCa=V*Ca;
VCb=V*Cb;
VCc=V*Cc;
VCd=V*Cd;
VT=V*T;

% Valores iniciais dos controladores
intPID=0;
erro1V=0;
erro2V=erro1V;

intPIDj=0;
erro1Vj=0;
erro2Vj=erro1Vj;


% Disturbio
  %F1=150;     % ft3/h

 % Inicio do loop
 i=1;
 tempo=0;
 while (tempo<=tf)

    % Imprimindo os resultados
    %if abs( eval(sym(tempo)/pi) - ceil(eval(sym(tempo)/pi)) ) <= 1e-3
    %   fprintf(' Tempo=%0.3f   Ca=%0.4f   Cb=%0.4f   Cc=%0.4f   Cd=%0.4f   T=%0.3f   V=%0.3f   F=%0.3f   Tj=%0.3f   Fj=%0.3f\n', tempo,Ca,Cb,Cc,Cd,T,V,F,Tj,Fj );
    %end


    % Controlador PID na Vazao de Refrigerante (temperatura da camisa)
    %----------------------------------------------------------
    % A integral do PID no volume
      intPIDj= intPIDj + (Tset-T)*dt;
    % A derivada do PID no volume
      derPIDj = (erro2Vj-erro1Vj)/dt;
      erro1Vj = erro2Vj;
    % A parte proporcional do PID no volume
      proPIDj = (Tset-T);
    % A equa??o do PID no volume
      Fj = Fjerrozero + Kj*proPIDj + Kj*Tdj*derPIDj + (Kj/Tij)*intPIDj;
    %----------------------------------------------------------

    % Controlador PID no Volume
    %----------------------------------------------------------
    % A integral do PID no volume
      intPID = intPID + (Vset-V)*dt;
    % A derivada do PID no volume
      derPID = (erro2V-erro1V)/dt;
      erro1V = erro2V;
    % A parte proporcional do PID no volume
      proPID = (Vset-V);
    % A equa??o do PID no volume
      F = Ferrozero + Kf*proPID + Kf*Tdf*derPID + (Kf/Tif)*intPID;
    %----------------------------------------------------------

    % k da rea??o
    k=(Aa)*exp(-Ea/(Ra*T));

    % O calor trocado com a camisa
    Q=U*A*(T-Tj);

    % Calculando as derivadas
    dVdt=F0-F;
    dVCadt=F0*Ca0-F*Ca-V*k*Ca*Cb;
    dVCbdt=F0*Cb0-F*Cb-V*k*Ca*Cb;
    dVCcdt=F0*Cc0-F*Cc+V*k*Ca*Cb;
    dVCddt=F0*Cd0-F*Cd+V*k*Ca*Cb;
    dVTdt= F0*T0-F*T-deltaH*V*k*Ca*Cb/(cp*ro)-Q/(cp*ro); %fluido reativo
    dTjdt=Fj*(Tj0-Tj)/vj + Q/(cpj*roj*vj); %refrigerante

    % Calculando as variaveis
    V=V+dVdt*dt;
    VCa=VCa+dVCadt*dt;
    VCb=VCb+dVCbdt*dt;
    VCc=VCc+dVCcdt*dt;
    VCd=VCd+dVCddt*dt;
    VT=VT+dVTdt*dt;
    Tj=Tj+dTjdt*dt;
    Ca=VCa/V;
    Cb=VCb/V;
    Cc=VCc/V;
    Cd=VCd/V;
    T=VT/V;



    %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
    %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%

    %Razão de reciclo
    razao_reciclo = 0.2;

    %Nó 2 (de bifurcação)
    f_reciclo=F*razao_reciclo;
    Ca_reciclo=Ca;
    Cb_reciclo=Cb;
    Cc_reciclo=Cc;
    Cd_reciclo=Cd;
    T_reciclo=T;

    %Na saída, após o reciclo (Saída, ponto 2)
    F_saida=F-f_reciclo; %f_saida é o F2
    Ca_saida=Ca;
    Cb_saida=Cb;
    Cc_saida=Cc;
    Cd_saida=Cd;
    T_saida=T;

    %Nó 1 (de mistura)
    F0=F1+f_reciclo;
    Ca0=(F1*Ca1+f_reciclo*Ca_reciclo)/(F0);
    Cb0=(F1*Cb1+f_reciclo*Cb_reciclo)/(F0);
    Cc0=(F1*Cc1+f_reciclo*Cc_reciclo)/(F0);
    Cd0=(F1*Cd1+f_reciclo*Cd_reciclo)/(F0);

    T0=(F1*T1+f_reciclo*T_reciclo)/(F0);

    %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
    %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%


    erro2V = Vset-V;
    erro2Vj = Tset-T;

    tempoV(i)=tempo;
    CaV(i)=Ca; % O valor de todas as concentrações na saída e antes do ponto de bifurcação são iguais
    TV(i)=T; % O valor na saída e antes do ponto de bifurcação são iguais
    VV(i)=V;
    FV(i)=F; % O valor na saída e antes do ponto de bifurcação são iguais
    TjV(i)=Tj;
    FjV(i)=Fj;
    CbV(i)=Cb; % O valor de todas as concentrações na saída e antes do ponto de bifurcação são iguais
    CcV(i)=Cc; % O valor de todas as concentrações na saída e antes do ponto de bifurcação são iguais
    CdV(i)=Cd; % O valor de todas as concentrações na saída e antes do ponto de bifurcação são iguais

    FrV(i)=f_reciclo;
    F1V(i)=F1;
    F0V(i)=F0;

    i=i+1;

    tempo = tempo + dt;
 end

 % Plotando os gr?ficos
      subplot(3,4,1); plot(tempoV,CaV,'.');xlabel('tempo');ylabel('Ca');                hold on;
      subplot(3,4,2); plot(tempoV,TV,'.'); xlabel('tempo');ylabel('Temperatura');       hold on;
      subplot(3,4,3); plot(tempoV,VV,'.'); xlabel('tempo');ylabel('Volume');            hold on;
      subplot(3,4,4); plot(tempoV,FV,'.'); xlabel('tempo');ylabel('Vaz?o');             hold on;
      subplot(3,4,5); plot(tempoV,TjV,'.');xlabel('tempo');ylabel('Temp. Refigerante'); hold on;
      subplot(3,4,6); plot(tempoV,FjV,'.');xlabel('tempo');ylabel('Vaz?o Refrigerente');hold on;
      subplot(3,4,7); plot(tempoV,CbV,'.');xlabel('tempo');ylabel('Cb');                hold on;
      subplot(3,4,8); plot(tempoV,CcV,'.');xlabel('tempo');ylabel('Cc');                hold on;
      subplot(3,4,9); plot(tempoV,CdV,'.');xlabel('tempo');ylabel('Cd');                hold on;


