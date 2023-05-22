# api_webhook

Este projeto é um teste para uma empresa, basicamente consiste em receber webhooks de pagamento, os webhooks trazem informações de compra ex: nome, email, status, valor, forma de pagamento e parcela. recebo isso na minha api e trato esses dados, salvo todas as alterações que eu tratei no meu banco de dados e as credenciais do usuario. a url principal é a seguinte:

https://apiwebhook.herokuapp.com/login

a api possui 4 rotas, sendo elas a de /login, /signup, /tratativas e webhooks.

em /tratativas é filtrado todos os recebimentos de webhooks e os status de cada ume suas devidas alterações assim com a /webhooks.
