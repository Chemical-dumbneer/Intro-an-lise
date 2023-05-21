var i = 0; // define publicamente a variável de iteração do sistema
var n_s = 200; // define o número de iterações por segundo
var t_tot = 30; // define o tempo total de simulação em segundos
var dt = 1 / n_s; // define a duração em segundos de cada iteração  
var Linha = /** @class */ (function () {
    function Linha(entrada) {
        this.Temp = entrada.Temp;
        this.Vaz = entrada.Vaz;
        this.Conc = entrada.Conc;
        this.Fonte = entrada; // define qual objeto é a fonte de dados dessa linha
    }
    ;
    Linha.prototype.update = function () {
        this.Temp = this.Fonte.Temp;
        this.Vaz = this.Fonte.Vaz;
        this.Conc = this.Fonte.Conc;
    };
    ;
    Linha.prototype.Publish = function () {
    };
    return Linha;
}());
;
var Nó_Mistura = /** @class */ (function () {
    function Nó_Mistura(entrada1, entrada2) {
        this.Vaz = entrada1.Vaz + entrada2.Vaz; // define a vazão do nó como a soma das vazões da entrada
        this.Temp = ((entrada1.Temp * entrada1.Vaz) + (entrada2.Temp * entrada2.Vaz)) / this.Vaz; /* define a temperatura do nó como a média
                                                                                            ponderada pela vazção das temperaturas das
                                                                                            linhas de entrada
                                                                                            */
        for (var j = 0; j < this.Conc.length; j++) {
            this.Conc[j] = ((entrada1.Conc[j] * entrada1.Vaz) + (entrada2.Conc[j] * entrada2.Vaz)) / this.Vaz;
        }
        ; /* define, para cada (for each) elemento da matriz de concentrações, que a concentração inicial elementar do nó é
                uma média ponderada pelas vazões das concentrações elementares das linhas-fonte deste nó */
        this.Fonte1 = entrada1; // define qual objeto é a fonte da entrada #1 deste nó
        this.Fonte2 = entrada2; // define qual objeto é a fonte da entrada #2 deste nó
    }
    ;
    Nó_Mistura.prototype.update = function () {
        this.Vaz = this.Fonte1.Vaz + this.Fonte2.Vaz;
        this.Temp = ((this.Fonte1.Temp * this.Fonte1.Vaz) + (this.Fonte2.Temp * this.Fonte2.Vaz)) / this.Vaz;
        for (var j = 0; j < this.Conc.length; j++) {
            this.Conc[j] = ((this.Fonte1.Conc[j] * this.Fonte1.Vaz) + (this.Fonte2.Conc[j] * this.Fonte2.Vaz)) / this.Vaz;
        }
        ;
    };
    ;
    Nó_Mistura.prototype.Publish = function () {
    };
    return Nó_Mistura;
}());
;
var Nó_Reciclo = /** @class */ (function () {
    function Nó_Reciclo(entrada, Raz_reciclo_in) {
        this.Fonte = entrada;
        this.Vaz = entrada.Vaz;
        if (this.Vaz !== 0) { // condição if-else para caso a vazão seja zero. A princípio inútil, mas nunca se sabe kkkj
            this.Temp = entrada.Temp;
            this.Conc = entrada.Conc;
        }
        else {
            this.Temp = entrada.Temp;
            this.Conc = entrada.Conc;
        }
        this.Raz_Reciclo = Raz_reciclo_in;
        this.saída = {
            Temp: this.Temp,
            Conc: this.Conc,
            Vaz: this.Vaz * (1 - this.Raz_Reciclo)
        };
        this.reciclo = {
            Temp: this.Temp,
            Conc: this.Conc,
            Vaz: this.Vaz * this.Raz_Reciclo
        };
    }
    ;
    Nó_Reciclo.prototype.update = function () {
        this.Vaz = this.Fonte.Vaz;
        this.Temp = this.Fonte.Vaz;
        this.Conc = this.Fonte.Conc;
        this.Raz_Reciclo = this.Raz_reciclo_controlador;
        this.saída = {
            Temp: this.Temp,
            Conc: this.Conc,
            Vaz: this.Vaz * (1 - this.Raz_Reciclo)
        };
        this.reciclo = {
            Temp: this.Temp,
            Conc: this.Conc,
            Vaz: this.Vaz * this.Raz_Reciclo
        };
    };
    ;
    Nó_Reciclo.prototype.Publish = function () {
    };
    return Nó_Reciclo;
}());
;
var CSTR_C_Jaqueta = /** @class */ (function () {
    function CSTR_C_Jaqueta(Fonte_Alimentação, Fonte_Jaqueta, Raz_Vol_in, Raz_vaz_in, Raio, Altura, Raz_Cobertura_Jaqueta, Espessura_Da_Camisa, Temp_in, Conc_in) {
        this.Dados_Reação = {
            matriz_reagente: [-1, -1, 1, 1],
            Var_entalpia: -300,
            Densidade: 1000,
            Cp: 100,
            A: 10,
            Ej: 200, // Energia de Ativação da reação (equação de Arrhenius)
        };
        this.Dados_Jaqueta = {
            Cp: 100,
            Densidade: 1000 // densidade do fluido refrigerante [kg/m³]
        };
        this.Fonte_Alimentação = Fonte_Alimentação;
        this.Fonte_Jaqueta = Fonte_Jaqueta;
        this.Temp_Jaqueta = Fonte_Jaqueta.Temp;
        this.A_tt = Raz_Cobertura_Jaqueta * Altura * 2 * Math.PI * Raio;
        this.Vol_Camisa = Math.PI * ((2 * Raio * Espessura_Da_Camisa) + (Math.pow(Espessura_Da_Camisa, 2)));
        this.U_tt = 368; // vide https://www.tlv.com/global/BR/steam-theory/overall-heat-transfer-coefficient.html para mais info
        this.Vol_max = Altura * Math.PI * Math.pow(Raio, 2);
        this.Vol = this.Vol_max * Raz_Vol_in;
        this.altura_reator = Altura;
        this.His_Vol[i] = this.Vol;
        this.His_Temp[i] = Temp_in;
        this.Temp = Temp_in + 273.15;
        this.alfa = Math.PI * Math.pow(0.1 * Raio, 2) * Math.sqrt(2 * 9.81);
        this.Vaz_max = this.alfa * Math.sqrt(this.altura_reator * (this.Vol / this.Vol_max));
        this.Vaz = this.Vaz_max * Raz_vaz_in;
        this.His_Vaz[i] = this.Vaz;
        this.His_Conc[i] = Conc_in;
    }
    CSTR_C_Jaqueta.prototype.K_arr = function (Temp) {
        return this.Dados_Reação.A * Math.exp((-this.Dados_Reação.Ej) / (8.314 * (Temp)));
    };
    ;
    ;
    CSTR_C_Jaqueta.prototype.update = function () {
        this.Vol = this.Vol + this.Fonte_Alimentação.Vaz - this.Vaz;
        this.His_Vol[i] = this.Vol;
        this.Vaz = this.Vaz_max * this.Raz_vaz;
        this.His_Vaz[i] = this.Vaz;
        this.Prod_Reag = 1;
        this.Vol = this.His_Vol[i - 1] + (this.Fonte_Alimentação.Vaz - this.Vaz) * dt;
        for (var j = 0; j < this.Conc.length; j++) {
            this.Mol_Reator[j] = this.Conc[j] * this.Vol;
            this.Mol_Entrada[j] = this.Fonte_Alimentação.Conc[j] * this.Fonte_Alimentação.Vaz * dt;
            this.Mol_Saida[j] = this.Conc[j] * this.Vaz * dt;
            this.Mol_Reação[j] = this.K_arr(this.Temp) * dt;
            for (var k = 0; k < this.Dados_Reação.matriz_reagente.length; k++) {
                if (this.Dados_Reação.matriz_reagente[k] < 0) {
                    this.Mol_Reação[j] = this.Mol_Reação[j] * Math.pow(this.Conc[k], -this.Dados_Reação.matriz_reagente[k]);
                }
                ;
            }
            ;
            this.saldo_molar[j] = this.Mol_Entrada[j] - this.Mol_Saida[j] + (this.Mol_Reação[j] * this.Dados_Reação.matriz_reagente[j] /
                Math.abs(this.Dados_Reação.matriz_reagente[j]));
            this.Mol_Reator[j] = this.Mol_Reator[j] + this.saldo_molar[j];
            this.Conc[j] = this.Mol_Reator[j] / this.Vol;
            if (this.Dados_Reação.matriz_reagente[j] < 0) {
                this.Prod_Reag = this.Prod_Reag * this.Conc[j];
            }
            ;
        }
        ;
        this.His_Conc[i] = this.Conc;
        this.saldo_energia = ((this.His_Vaz[i - 1] * this.His_Temp[i - 1]) - (this.Fonte_Alimentação.Vaz * this.Fonte_Alimentação.Temp) -
            (((this.His_Vol[i - 1] * this.K_arr(this.His_Temp[i - 1]) * this.Prod_Reag * this.Dados_Reação.Var_entalpia) -
                ((this.U_tt * this.A_tt * (this.Temp - this.Temp_Jaqueta)) / (this.Dados_Reação.Densidade
                    * this.Dados_Reação.Cp))))) / this.Vol; // calculando o saldo de temperatura do fluido reativo
        this.Temp = this.Temp + this.saldo_energia;
        this.His_Temp[i] = this.Temp;
        this.saldo_energia = ((this.Fonte_Jaqueta.Vaz * (this.Temp_Jaqueta - this.Temp)) / this.Vol_Camisa) +
            ((this.U_tt * this.A_tt * (this.Temp - this.Temp_Jaqueta)) / (this.Vol_Camisa * this.Dados_Jaqueta.Densidade
                * this.Dados_Jaqueta.Cp)); // calculando o saldo de temperatura do fluido refrigerante
        this.Temp_Jaqueta = this.Temp_Jaqueta + this.saldo_energia;
    };
    ;
    CSTR_C_Jaqueta.prototype.Publish = function () {
    };
    return CSTR_C_Jaqueta;
}());
;
var Controlador_PID = /** @class */ (function () {
    function Controlador_PID(Objeto, Alvo_Observações, Historico_Observações, Set_point_Observações, Alvo_controlador, K_proporcional, K_derivativo, K_integrante, Resposta_Mínima, Resposta_Máxima) {
        this.objeto = Objeto;
        this.Obs = Alvo_Observações;
        this.His_Obs = Historico_Observações;
        this.Set_point = Set_point_Observações;
        this.Controle = Alvo_controlador;
        this.Const_Pro = K_proporcional;
        this.Const_Der = K_derivativo;
        this.Const_Int = K_integrante;
        this.Resp_Min = Resposta_Mínima;
        this.Resp_Max = Resposta_Máxima;
        this.Val_Der = 1;
        this.Val_Int = 0;
    }
    ;
    Controlador_PID.prototype.update = function () {
        this.Val_Der = (this.His_Obs[i] - this.His_Obs[i - 1]) / dt;
        this.Val_Int = this.Val_Int + ((this.His_Obs[i - 1] + this.His_Obs[i] - (2 * this.Set_point)) / 2) * dt;
        this.Resp = this.Const_Pro * (this.Obs - this.Set_point) +
            this.Const_Pro * this.Const_Der * this.Val_Der +
            (this.Const_Pro / this.Const_Int) * this.Val_Int;
        this.Controle = this.Controle * this.Resp;
        if (this.Controle > this.Resp_Max) {
            this.Controle = this.Resp_Max;
        }
        else if (this.Controle < this.Resp_Min) {
            this.Controle = this.Resp_Min;
        }
        ;
    };
    ;
    Controlador_PID.prototype.Publish = function () {
    };
    return Controlador_PID;
}());
;
var Fonte = /** @class */ (function () {
    function Fonte(Vazão_Máxima_Fonte, Razão_de_Vazão, Temperatura, Matriz_Conc) {
        this.Vaz_Max = Vazão_Máxima_Fonte;
        this.Raz_Vaz = Razão_de_Vazão;
        this.Vaz = this.Vaz_Max * this.Raz_Vaz;
        this.Temp = Temperatura;
        this.Conc = Matriz_Conc;
    }
    ;
    Fonte.prototype.update = function () {
        this.Vaz = this.Vaz_Max * this.Raz_Vaz;
    };
    ;
    Fonte.prototype.Publish = function () {
    };
    return Fonte;
}());
;
// declarando todos os objetos utilizados no sistema
var Fonte_1;
var Linha_1;
var Nó_mistura_1;
var Linha_2;
var Fonte_J;
var Linha_J;
var Controlador;
var Reator;
var Linha_3;
var Reciclo;
var Linha_4;
var Linha_5;
Fonte_1 = new Fonte(40, // vazão máxima da Fonte
1, // razão de Vazão inicial
35, // temperatura da fonte
[0.5, 0.5, 0, 0] // matriz de concentrações inicial da fonte
);
Linha_1 = new Linha(Fonte_1 // entrada da linha
);
Nó_mistura_1 = new Nó_Mistura(// pré-declarando o objeto para poder prosseguir
Linha_1, // entrada 1 no nó
Linha_1 // entrada 2 no nó
);
Linha_2 = new Linha(Nó_mistura_1 // entrada da linha
);
Fonte_J = new Fonte(20, // vazão máxima da fonte
1, // razão de vazão inicial
15, // temperatuda da fonte
[0, 0, 0, 0] // matriz de concentrações inicial da fonte
);
Linha_J = new Linha(Fonte_J // entrada da linha
);
Reator = new CSTR_C_Jaqueta(Linha_2, // entrada do fluido reativo do reator
Linha_J, // entrada do fluido refrigerante do reator
0.8, // razão de volume inicial do reator
0.2, // razão de vazão máxima inicial do reator
1, // raio do reator
2, // altura do reator
0.8, // razão de cobertura da jaqueta
0.2, // espessura da jaqueta
50, // temperatura inicial do reator
[0, 0, 0, 0] // matriz de concentrações inicial do reator
);
Linha_3 = new Linha(Reator // entrada da linha
);
Reciclo = new Nó_Reciclo(Linha_3, // entrada do nó
0.5 // razão de reciclo do nó
);
Linha_4 = new Linha(Reciclo.reciclo // entrada da linha
);
Nó_mistura_1 = new Nó_Mistura(// re-declarando o nó, agora com as entradas adequadas
Linha_1, // entrada 1 do nó
Linha_4 // entrada 2 do nó
);
Linha_5 = new Linha(Reciclo.saída // entrada da linha
);
var Sist = [
    Fonte_1,
    Linha_1,
    Nó_mistura_1,
    Linha_2,
    Fonte_J,
    Linha_J,
    Reator,
    Linha_3,
    Reciclo,
    Linha_4,
    Linha_5
];
for (var i_1 = 0; i_1 < (n_s * t_tot); i_1++) {
    Sist.forEach(function (objeto) {
        objeto.update();
    });
}
