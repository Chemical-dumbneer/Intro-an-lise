class Linha{
    constructor(T0,Q0,CA0,CB0,CC0,CD0){
        this.Temp = parsefloat(T0);
        this.Vaz = parsefloat(Q0);
        this.Conc = array(parsefloat(CA0),parsefloat(CB0),parsefloat(CC0),parsefloat(CD0));
    };
};

class nó_mistura{
    calcular(Entrada1, Entrada2, Saída){
        Saída.Temp = ((Entrada1.Temp * Entrada1.Vaz) + (Entrada2.Temp * Entrada2.Vaz))/(Entrada1.Vaz + Entrada2.Vaz);
        Saída.Vaz = (Entrada1.Vaz + Entrada2.Vaz);
        
    };
};

class reator{
    constructor(altura,raio){
        this.raio = parsefloat(raio);
        this.altura = parsefloat(altura)
        this.volume_disp = altura * Math.pow(raio,2) * Math.PI;
    };
    vazão_saída (contr_vaz){
        this.vazão = contr_vaz
    };
    
};