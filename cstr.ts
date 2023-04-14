class Linha{ // apenas carrega informação entre outros objetos

    public Temp:number; // define Temperatura da linha como uma variável pública
    public Vaz:number; // define Vazão da linha como uma variável pública 
    public Conc:number[]; // define concentrações de elementos como uma matriz de elementos pública
    public Fonte:any; // define a fonte de entrada na linha como um objeto qualquer público

    constructor(entrada:any){ // Copia os dados de temperatura, vazão e concentração do objeto fonte
        this.Temp = entrada.Temp;
        this.Vaz = entrada.Vaz;
        this.Conc = entrada.Conc;
        this.Fonte = entrada; // define qual objeto é a fonte de dados dessa linha
    };

    update(){ // atualiza os dados de temperatura, vazão e concentração copiando-os do objeto fonte
        this.Temp = this.Fonte.Temp
        this.Vaz = this.Fonte.Vaz
        this.Conc = this.Fonte.Conc
    };
};

class Nó_Mistura{ // Mistura as informações de duas linhas distintas e armazena as informações em si para serem acessadas por outra linha

    public Temp:number; // define temperatura final do nó como uma variável pública
    public Vaz:number; // define vazão final do nó como uma variável pública
    public Conc:number[]; // define a matriz de concentração final do nó como uma variável pública
    public Fonte1:Linha; // define a linha de entrada #1 do nó como um objeto do tipo "linha" público
    public Fonte2:Linha; // define a linha de entrada #2 do nó como um objeto do tipo "linha" público

    constructor(entrada1:Linha,entrada2:Linha){ /* Copia os dados de temperatura, vazão e concentração das linhas fonte e
                                                faz o cálculo dos parâmetros internos em um momento inicial 
                                                */

        this.Vaz = entrada1.Vaz + entrada2.Vaz; // define a vazão do nó como a soma das vazões da entrada
        this.Temp = ((entrada1.Temp*entrada1.Vaz)+(entrada2.Temp*entrada2.Vaz))/this.Vaz;   /* define a temperatura do nó como a média
                                                                                            ponderada pela vazção das temperaturas das
                                                                                            linhas de entrada
                                                                                            */                                          
        this.Conc.forEach(function(index:number){
            this.Conc[index] = ((entrada1.Conc[index]*entrada1.Vaz) + (entrada2.Conc[index]*entrada2.Vaz))/this.Vaz;
        });     /* define, para cada (for each) elemento da matriz de concentrações, que a concentração inicial elementar do nó é
                uma média ponderada pelas vazões das concentrações elementares das linhas-fonte deste nó */
        this.Fonte1 = entrada1; // define qual objeto é a fonte da entrada #1 deste nó
        this.Fonte2 = entrada2; // define qual objeto é a fonte da entrada #2 deste nó
    };

    update(){ // atualiza os parâmetros internos desse nó com base nas fontes definidas no construtor

        this.Vaz = this.Fonte1.Vaz + this.Fonte2.Vaz;
        this.Temp = ((this.Fonte1.Temp*this.Fonte1.Vaz)+(this.Fonte2.Temp*this.Fonte2.Vaz))/this.Vaz;
        this.Conc.forEach(function(index:number){
            this.Conc[index] = ((this.Fonte1.Conc[index]*this.Fonte1.Vaz) + (this.Fonte2.Conc[index]*this.Fonte2.Vaz))/this.Vaz;
        });
    };
};

class Nó_Reciclo{ // recebe informações de uma linha e divide a vazão dessa linha em outras 2 com base em uma razão de reciclo pré definida

    public Temp:number; // define a temperatura base do nó como uma variável pública
    public Vaz:number; // define a vazão base do nó como uma variável pública
    public Conc:number[]; // define a matriz de concentrações base do nó como uma variável pública
    public Raz_Reciclo:number; // define a razão de reciclo base no nó como uma variável pública
    public Fonte:Linha; // define a fonte de entrada de informação do nó como um objeto do tipo "linha" público
    public saída:any; // define a saída principal do nó como um objeto qualquer público
    public reciclo:any; // define a saída de recíclo do nó como um objeto qualquer público

    constructor(entrada:Linha,Raz_reciclo_in:number){   /* Copia os dados de temperatura, vazão e concentração da linha fonte e
                                                        faz o cálculo dos parâmetros internos em um momento inicial 
                                                        */

        this.Fonte = entrada;
        this.Vaz = entrada.Vaz;
        if (this.Vaz !== 0) { // condição if-else para caso a vazão seja zero. A princípio inútil, mas nunca se sabe kkkj
            this.Temp = entrada.Temp;
            this.Conc = entrada.Conc;
        } else {
            this.Temp = entrada.Temp;
            this.Conc = entrada.Conc;
        }
        
        this.Raz_Reciclo = Raz_reciclo_in

        this.saída={ // cria um objeto para carregar as informações da saída principal do nó
            Temp : this.Temp,
            Conc : this.Conc,
            Vaz : this.Vaz * (1 - this.Raz_Reciclo)
        };

        this.reciclo={ // cria um objeto para carregar as informações do reciclo do nó
            Temp : this.Temp,
            Conc : this.Conc,
            Vaz : this.Vaz * this.Raz_Reciclo
        };

    };

    update(Raz_reciclo_controlador:number){ // atualiza as informações das saídas do nó
        this.Vaz = this.Fonte.Vaz;
        this.Temp = this.Fonte.Vaz;
        this.Conc = this.Fonte.Conc;
        this.Raz_Reciclo = Raz_reciclo_controlador

        this.saída={
            Temp : this.Temp,
            Conc : this.Conc,
            Vaz : this.Vaz * (1 - this.Raz_Reciclo)
        };

        this.reciclo={
            Temp : this.Temp,
            Conc : this.Conc,
            Vaz : this.Vaz * this.Raz_Reciclo
        };

    };

};

class CSTR_C_Jaqueta{   /* recebe informações de entrada, executa balanços de massa e energia com essas informações e passa as informações
                        novas para frente
                        */
    public Temp:number;
    public Vaz:number;
    public Conc:number[];
    public His_Temp:number[];
    public His_Vaz:number[];
    public His_Conc:number[];
    public Fonte_Alimentação:Linha;
    public Fonte_Jaqueta:Linha;
    public Vol:number;
    public Raz_vaz:number;
    private Vaz_max:number;
    private Vol_max:number;
    
    constructor(Fonte_Alimentação:Linha, Fonte_Jaqueta:Linha, Raz_Vol_in:number, 
        Raz_vaz_in:number, Raio:number, Altura:number, Raz_Cobertura_Jaqueta:number){

        this.Fonte_Alimentação = Fonte_Alimentação;
        this.Fonte_Jaqueta = Fonte_Jaqueta;
        this.Vol_max = Altura * Math.PI * Math.pow(Raio,2);
        this.Vol = this.Vol_max * Raz_Vol_in;
        /* para calcular a vazão máxima do reator será necessário definir abertura da saída, densidade do fluído calculado, através
        da equaçãod de Bernoulli, essas variáveis serão assumidas para fins iniciais de simplificação, mas deverão ser calculadas
        com precisão no futuro */

    };


}