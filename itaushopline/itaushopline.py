# coding: utf-8
import requests
from random import randint

class ItauShopline(object):
    urls = {}
    KEYS_MAP = {
        'pedido': 8, 
        'valor': 10, 
        'observacao': 40,
        'nome': 30,
        'codigo_inscricao': 2,
        'numero_inscricao': 14, 
        'endereco': 40,
        'bairro': 15,
        'cep': 8,
        'cidade': 15,
        'estado': 2,
        'vencimento': 29,
        'url_retorno': 60,
        'obs_1': 60,
        'obs_2': 60,
        'obs_3': 60
    }
    
    def __init__(self, codigo, chave, **extra):
        self.codigo = codigo
        self.chave = chave
        self.chave_itau = extra.get('chave_itau', 'SEGUNDA12345ITAU')
        
        self.urls['boleto'] = extra.get('boleto_url', 'https://shopline.itau.com.br/shopline/Itaubloqueto.asp')
        self.urls['consulta'] = extra.get('consulta_url', 'https://shopline.itau.com.br/shopline/consulta.asp')
        self.urls['shopline'] = extra.get('shopline_url', 'https://shopline.itau.com.br/shopline/shopline.asp')
        
    @classmethod
    def rnd(self):
        alfa = 'ABCDEFGHIJKLMNOPQRSTUVXWYZ'
        rd = randint(0, len(alfa)-1)
        return alfa[rd:rd+1]
    
    @classmethod
    def algoritmo(self, token, chave):
        self.indices = []
        self.asc_codes = []
        self.inicializa(chave)
        
        l = 0
        data_chave = []
        
        for j in range(1, len(token)+1):
            k = j % 256
            l = (l + self.indices[k]) % 256
            i = self.indices[k]
            self.indices[k] = self.indices[l]
            self.indices[l] = i
            caracter = int(ord(token[(j-1):j]) ^ int(self.indices[(self.indices[k] + self.indices[l]) % 256]))
            data_chave.append(chr(caracter))

        return ''.join(data_chave)
    
    @classmethod
    def inicializa(self, chave):
        for j in range(0, 256):
            self.indices.append('')
            self.asc_codes.append('')
            self.asc_codes[j] = ord(chave[(j % len(chave)):(j % len(chave))+1])
            self.indices[j] = j

        l = 0
        for k in range(0, 256):
            l = (l + self.indices[k] + self.asc_codes[k]) % 256

            i = self.indices[k]
            self.indices[k] = self.indices[l]
            self.indices[l] = i
    
    @classmethod
    def converte(self, chave):
        data_rand = [str(self.rnd())]
        
        for i in range(0, len(chave)):
            data_rand.append(str(ord(str(chave[i:(i+1)]))))
            data_rand.append(str(self.rnd()))
        
        return ''.join(data_rand)
    
    def clean(self):
        from collections import OrderedDict
        
        for k, v in self.KEYS_MAP.items():
            self.data[k] = str(self.data[k] if self.data.get(k) else '')[0:v].ljust(v, ' ')
         
    def process(self, **data):
        self.data = data
        
        assert len(self.codigo) == 26, u'Tamanho do codigo da empresa diferente de 26 posições'
        assert len(self.chave) == 16, u'Tamanho da chave da chave diferente de 16 posições'
        
        for k, v in self.data.items():
            assert k in self.KEYS_MAP, u'Chave não permitida'
            
            if hasattr(self, 'clean_%s' % k):
                 v = getattr(self, 'clean_%s' % k)()
            
            self.data[k] = v
        
        self.clean()
        
        chave1 = self.algoritmo(''.join([self.data[k] for k in ['pedido', 'valor', 'observacao',
            'nome', 'codigo_inscricao', 'numero_inscricao', 'endereco', 'bairro', 'cep', 
            'cidade', 'estado', 'vencimento', 'url_retorno', 'obs_1', 'obs_2', 'obs_3']]), self.chave)
            
        chave2 = self.algoritmo(''.join([self.codigo, chave1]), self.chave_itau)
        self.dc = self.converte(chave2)
        
        return self.dc
    
    @property
    def make_post_page(self):
        return """<HTML>
                    <BODY>
                        <form method="post" action="%(url)s" id="itaushopline">
                            <INPUT type="hidden" name="DC" value="%(DC)s">
                        </FORM>
                        <SCRIPT> document.getElementById('itaushopline').submit(); </SCRIPT>
                    </BODY>
                </HTML>""" % {'url':self.urls['boleto'], 'DC':self.dc}
    
    def sonda(self, pedido, formato):
        assert len(self.codigo) == 26, u'Tamanho do codigo da empresa diferente de 26 posições'
        assert len(self.chave) == 16, u'Tamanho da chave da chave diferente de 16 posições'
        assert formato in ("0", "1"), u'Formato inválido'
        
        chave1 = self.algoritmo(''.join([str(int(pedido)).rjust(8, '0'), str(formato)]), self.chave)
        chave2 = self.algoritmo(''.join([self.codigo, chave1]), self.chave_itau)
        dc = self.converte(chave2)
        
        r = requests.post(self.urls['consulta'], data={'DC': dc})
        return r.content
    
    def clean_pedido(self):
        return str(int(self.data.get('pedido'))).rjust(8, '0')
    
    def clean_valor(self):
        return ('%1.2f' % self.data.get('valor')).replace('.', '').rjust(10, '0')
    
    def clean_vencimento(self):
        return self.data.get('vencimento').strftime('%d%m%Y')
    
    def clean_codigo_inscricao(self):
        assert self.data.get('codigo_inscricao') in ("1", "01", "2", "02"), u'Código de Inscrição Inválido 01 = CPF, 02 = CNPJ'
        return str(self.data.get('codigo_inscricao')).rjust(2, '0')

if __name__ == '__main__':
    from datetime import datetime, timedelta
    CODIGO_EMPRESA = 'J0050887670001380000010324'
    CHAVE = 'T2B7R7A0Z1L2M5FT'

    itaushopline = ItauShopline(CODIGO_EMPRESA, CHAVE)
    itaushopline.process(pedido=300, valor=100.50, observacao='', nome='GABRIEL GALIASO DE ALMEIDA', 
        codigo_inscricao='02', numero_inscricao='36325625803', cep='14850000', 
        endereco='R RUI BARBOSA 1152', bairro='JD PRIMAVERA', cidade='PRADOPOLIS', estado='SP', 
        vencimento=(datetime.now()+timedelta(days=3)).date())
    
    print itaushopline.make_post_page
    print itaushopline.sonda(300, '1')