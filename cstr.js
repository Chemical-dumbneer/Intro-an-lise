class Linha{
    constructor(T0,Q0,CA0,CB0,CC0,CD0){
        this.Temp = T0;
        this.Vaz = Q0;
        this.Conc = [[CA0,CB0,null,null],[null,null,CC0,CD0]];
    };
};

class nó_mistura{
    entradas(vazão_1, vazão_2){
        this.e1 = parsefloat(vazão_1);
        this.e2 = parsefloat(vazão_2);
        this.vazão_saída = this.e1 + this.e2;
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