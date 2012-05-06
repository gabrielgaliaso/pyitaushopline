from itaushopline import ItauShopline

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