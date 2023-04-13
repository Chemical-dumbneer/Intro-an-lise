var Linha = /** @class */ (function () {
    function Linha(T0, Q0, CA0, CB0, CC0, CD0) {
        this.Temp = T0;
        this.Vaz = Q0;
        this.Conc = Array((CA0), (CB0), (CC0), (CD0));
    }
    ;
    return Linha;
}());
;
var nó_mistura = /** @class */ (function () {
    function nó_mistura() {
    }
    nó_mistura.prototype.calcular = function (Entrada1, Entrada2, Saída) {
        Saída.Temp = ((Entrada1.Temp * Entrada1.Vaz) + (Entrada2.Temp * Entrada2.Vaz)) / (Entrada1.Vaz + Entrada2.Vaz);
        Saída.Vaz = (Entrada1.Vaz + Entrada2.Vaz);
    };
    ;
    return nó_mistura;
}());
;
var reator = /** @class */ (function () {
    function reator(altura, raio) {
        this.raio = (raio);
        this.altura = (altura);
        this.volume_disp = altura * Math.pow(raio, 2) * Math.PI;
    }
    ;
    reator.prototype.vazão_saída = function (contr_vaz) {
        this.vazão = contr_vaz;
    };
    ;
    return reator;
}());
;
