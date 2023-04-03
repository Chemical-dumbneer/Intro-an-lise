class nó_mistura{
    entradas(vazão_1, vazão_2){
        this.e1 = parsefloat(vazão_1);
        this.e2 = parsefloat(vazão_2);
        this.vazão_saída = e1 + e2;
    }
    
};

class reator{
    constructor(altura,raio){
        this.raio = raio
        this.altura = altura
        this.volume_tot = altura * Math.pow(raio,2) * Math.PI;
    };
    vazão_saída (contr_vaz){
        this.vazão = contr_vaz
    };
    
};