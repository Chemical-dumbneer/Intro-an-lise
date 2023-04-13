class Linha{
    public Temp:number;
    public Vaz:number;
    public Conc:number[];
    public Fonte:any;

    constructor(entrada:any){
        this.Temp = entrada.Temp;
        this.Vaz = entrada.Vaz;
        this.Conc = entrada.Conc;
        this.Fonte = entrada;
    };

    update(){
        this.Temp = this.Fonte.Temp
        this.Vaz = this.Fonte.Vaz
        this.Conc = this.Fonte.Conc
    };
};

class Nó_Mistura{
    public Temp:number;
    public Vaz:number;
    public Conc:number[];
    public Fonte1:Linha;
    public Fonte2:Linha;

    constructor(entrada1:Linha,entrada2:Linha){
        this.Vaz = entrada1.Vaz + entrada2.Vaz;
        this.Temp = ((entrada1.Temp*entrada1.Vaz)+(entrada2.Temp*entrada2.Vaz))/this.Vaz;
        this.Conc.forEach(function(index:number){
            this.Conc[index] = ((entrada1.Conc[index]*entrada1.Vaz) + (entrada2.Conc[index]*entrada2.Vaz))/this.Vaz;
        });
        this.Fonte1 = entrada1;
        this.Fonte2 = entrada2;
    };

    update(){
        this.Vaz = this.Fonte1.Vaz + this.Fonte2.Vaz;
        this.Temp = ((this.Fonte1.Temp*this.Fonte1.Vaz)+(this.Fonte2.Temp*this.Fonte2.Vaz))/this.Vaz;
        this.Conc.forEach(function(index:number){
            this.Conc[index] = ((this.Fonte1.Conc[index]*this.Fonte1.Vaz) + (this.Fonte2.Conc[index]*this.Fonte2.Vaz))/this.Vaz;
        });
    };
};

class Nó_Reciclo{
    public Temp:number;
    public Vaz:number;
    public Conc:number[];
    public Raz_Reciclo:number;
    public Fonte:Linha;
    public saída:any;
    public reciclo:any;

    constructor(entrada:Linha,Raz_reciclo_in:number){
        this.Fonte = entrada;
        this.Vaz = entrada.Vaz;
        if (this.Vaz !== 0) {
            this.Temp = entrada.Temp;
            this.Conc = entrada.Conc;
        } else {
            this.Temp = entrada.Temp;
            this.Conc = entrada.Conc;
        }
        
        this.Raz_Reciclo = Raz_reciclo_in

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

    update(Raz_reciclo_controlador:number){
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

class Válvula{
    public Temp:number;
    public Vaz:number;
    public Conc:number[];
    public Fonte:any;
    public Raz_Abertura:number;

    constructor(entrada:any){
        this.Temp = entrada.Temp;
        this.Vaz = entrada.Vaz;
        this.Conc = entrada.Conc;
        this.Fonte = entrada;
    };

    update(Raz_Abertura_Controlador:number){
        this.Raz_Abertura = Raz_Abertura_Controlador
        this.Temp = this.Fonte.Temp
        this.Vaz = this.Fonte.Vaz
        this.Conc = this.Fonte.Conc
    };
};