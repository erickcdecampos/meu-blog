---
title: "como fiz um media center automático e amigável com um raspberry pi velho"
date: 2023-06-11T13:12:30-03:00
draft: true
image: image-1.png
---

Na era dos infinitos serviços de streaming, limitação de usuários na Netflix e catalogos minguantes, a pirataria volta cada vez mais a ser uma opção interessante. Discussões éticas a parte, ter um biblioteca de mídia doméstica é cada vez mais viável, prático e barato. 

Esqueça passar filmes para HDs, baixar legendas e conectar na TV:a experiência pode ser quase idêntica a de um streaming. E para isso não é preciso de muito conhecimento técnico (eu não sei programar) e nem de muito dinheiro (em 2023 dá pra fazer com menos de R$1000). Você só precisa de um Raspberry Pi, um pouco de tempo e paciência.

O Raspberry Pi é uma Single Board Computer, ou seja, um computadorzinho montado em uma única placa e que tem todo o básico para rodar programas em geral. Uma outra forma de descrevê-lo é pensar em como seria um celular se ele tivesse as entradas habituais que um computador tem - rede, HDMI, USB, áudio, etc.

![](image-1.png)Sem um case, o Raspberry Pi é isso aqui, na sua 4ª edição (Créditos: Divulgação Raspberry Pi Foundation)

Não é o computador mais rápido do mundo, mas é poderoso o suficiente para rodar bastante coisa. Com a versão 4, tem gente que usa até como computador pessoal mesmo, para navegar pela internet e tal. 

Nele, é possível instalar um sistema operacional como o Windows (versão para ARM), alguma distribuição do Linux, ou, como veremos aqui, uma versão otimizada de um sistema Linux para alguma tarefa específica. Tem para todo os gostos: emuladores, VPN doméstico, servidor de arquivos e o que mais você puder imaginar.

Quando eu falo otimizado, eu falo sério. Com o LibreELEC, sistema especializado em media centers e que tenho utilizado há bastante tempo (já são quase 5 anos com esse bichinho trabalhando duramente aqui em casa!), tenho um sistema que automaticamente:

  * Gerencia minha watchlist e baixa novos episódios ou filmes diretamente das melhores locadoras online.
  * Baixa legendas de acordo com o release baixado.
  * Organiza minha biblioteca de mídia (série, filmes e música)
  * Disponibiliza para consumo em uma interface rápida e amigável a la Netflix em todos os dispositivos conectados a minha rede doméstica, com ótimos apps para celular e AndroidTV.



O gasto de energia é bastante reduzido, mesmo com ele ligado 24/7 e, ignorando os HDs que eu já tinha, gastei menos de R$400 para montar esse sistema.

Além disso, eu faço tudo isso sem ter que mexer diretamente nesse sistema, que atualmente nem está conectado a tela alguma. Eu controlo tudo diretamente do celular ou computador.

Se você achou interessante, vem comigo que eu vou contar em detalhes o que fiz e como fiz.

## ingredientes

Aqui em casa toda a estrutura roda em um Raspberry Pi 3B. Desde 2019, já temos disponível no mercado a versão 4, muito mais poderosa e moderna. 

No entanto, devido a diversos problemas na cadeia de produção e a pandemia, a nova versão não tem feito jus a proposta de um computador poderoso e barato. Sem falar na escassez no mercado. Para se ter uma ideia, em 2018 eu cerca de 300 reais pelo kit completo que incluía o Raspberry Pi, case, cooler, fonte e cartão SD. Hoje, não é raro ver as versões mais simples da quarta encarnação do SBC por mais de R$1000.

Por isso tudo, se você quer montar um equipamento desse em 2023, a minha sugestão é: faça uma boa pesquisa e encontre o SBC com o melhor custo benefício para o seu orçamento. No meu caso, por exemplo, estou planejando um upgrade para um Orange Pi 5.

![](OIP-edited.jpg)Orange Pi 5 (Créditos: Divulgação OrangePi)

![](XdfPDO3Aqb-1024x768.jpg)Raspbery Pi (Créditos: hackster.io)

No fim das contas, independente do hardware que você vai escolher, você vai precisar de mais ou menos a mesma coisa:

  * 1 SBC compatível com o LibreELEC. (Veja mais informações no [site oficial](<https://libreelec.tv>))
  * 1 fonte de qualidade. (Dê preferência para a original, mas se não for possível atenda fielmente às especificações do fabricante para evitar frustrações depois com um equipamento subalimentado)
  * 1 cartão microSD de boa capacidade para armazenar o sistema operacional. Essa opção é válida apenas se o seu SBC não tiver um armazenamento interno, como tem sido mais comum atualmente, mas ainda não é o caso dos Raspberry Pis.
  * O quanto baste de armazenamento de mídia, seja no próprio SD (se você não tem a pretensão de acumular muito conteúdo), um HD parado na gaveta, como no meu caso, ou um SSD externo (a opção mais rápida e mais cara).
  * 1 computador qualquer para instalar o LibreELEC no cartão SD.
  * 1 teclado e 1 tela para fazer as configurações iniciais no sistema.



## preparando o sistema operacional

Não sei como é com outros SBC e outros sistemas operacionais, mas o LibreELEC deve ser "instalado" de antemão no cartão SD que serve de armazenamento interno. Para isso, é necessário um computador _tradicional_.

Não tem segredo, basta baixar o criador de SD cards para seu sistema operacional no site oficial. Neste momento, porém, o site mostra que apenas a versão para Windows está disponível. Pelo "currently", imagino que isso deve mudar algum dia.

![](image.png)

Baixado o instalador, basta selecionar em 1 seu dispositivo e versão e depois em Download. Dessa forma, a própria ferramenta irá baixar o LibreELEC mais recente para seu dispositivo.

Depois de feita a transferência, plugue o seu cartão SD no computador e selecione em 3 a letra da unidade para formatar e instalar o sistema operacional. Clique em Write, aguarde e pronto.

Agora basta inserir o microSD na respectiva entrada do seu Raspberry Pi, conectar seus cabos de força, HDMI em alguma tela, um teclado ou mouse para controlá-lo e ligar a máquina.

Na primeira inicialização, você passará por um configurador do sistema, onde pode selecionar o idioma, rede wi-fi e essas coisas. Infelizmente, não me lembro dos detalhes e não estou com paciência para replicar aqui para rever tudo, mas é bem auto-explicativo e tudo pode ser mudado para depois. 

Se houver alguma opção para alterar as credenciais do sistema, eu sugiro que ainda não mude. Será prático no futuro ter o usuário e senha padrão para efetuar algumas operações via terminal ou conectar o app de controle remoto. Por outro lado, se você confia na sua memória ou gerenciar de senhas, pode mudar sim. No meu caso, são tantas senhas no media center que eu nunca encontro a certa no Bitwarden.

## conhecendo o Kodi

Pronto, você passou pelo assistente de configuração. A tela que você encontra é o Kodi.

![](about-devices.webp)O ecossistema Kodi na sua versão 20, disponível apenas a partir do Raspberry Pi 4. (Créditos da imagem: Divulgação Kodi)

Como eu comentei acima, esse sistema operacional foi escolhido por ser uma distribuição do Linux otimizada. For dummies (eu sou um), o LibrELEC é como um sistema operacional que basicamente só tem um software: o Kodi, uma ferramenta de consumo e gestão de bibliotecas de mídia.

O Kodi é um software livre, sucessor do XBMC (Xbox Media Center), que teve seu desenvolvimento iniciado em 2002, e já está na sua versão 20. No Raspberry Pi 3, a versão mais recente disponível é a 19, mas a partir do 4 já é possível desfrutar da última.

Ele tem recuros para gestão de músicas, filmes, fotos, IPTV e é completamente customizável. Pode receber diferentes add-ons, que acrescentam novas funcionalidades, e também skins, que mudam completamente sua cara.

Contudo, apesar do Kodi ser a base do nosso sistema, não se acostume muito com a interface dele. O consumo, ou seja, o uso em si se dará através de um outro programa, ainda mais amigável.

### rede e energia

Se você não fez isso no assistente inicial, é a hora de entrar nas configurações e conectar em uma rede. Dê preferencia para uma rede cabeada, afinal, estamos falando de um media center que irá baixar grandes quantidades de dado. Do contrário, seu wi-fi pode ficar congestionado e o dispositivo mais lerdo.

Para isso, vá até o menu 

Aproveite para configurar uma IP fixo para seu dispositivo. Com isso, será mais fácil localizar seu media center a partir de outros dispositivos e para acessar as suas funcionalidades.

Para isso, você deve .

Anote esse endereço, ou melhor, escolha um endereço simples de memorizar. Você irá precisar no futuro e não só para a configuração.

Além disso, em diversos momentos será útil acessar seu media center através do seu próprio computador. Basta digitar na barra de endereços do Windows Explorer o IP precedido por duas barras invertidas (diferentes das usadas na internet), exemplo: \192.168.0.10.

No primeiro acesso será pedido um usuário e senha e, se você não tiver alterado a senha padrão, basta usar root e libreelec

Um detalhe importante, é que você precisa desligar seu Raspberry Pi como um computador antigo, se quiser minimizar o risco de perder arquivos importantes. Esse botão está disponível no 

Outro recurso bastante útil é o Kore, acrônimo para Kodi Remote. É um app para Android e iOS pelo qual você consegue desligar e controlar a reprodução de mídia no Kodi. O primeiro recurso é útil, já o segundo, desnecessário, após outros ajustes.

Basta baixar o app no seu celular ou tablet e inserir o IP que você configurou acima no campo apropriado. Para a senha, mesma coisa: root:libreelec.

## configurando Medusa e Radarr

A parte interessante desse media center é feita por add-ons. Nas fontes nativas é possível encontrar diversos add-ons com diferentes objetivos. Particularmente, não vejo nada muito interessante neles, mas vale explorar.

O ouro mesmo está em outras fontes. Vamos utilizar nesse caso o Thoradia.

Acesse o site e baixe o arquivo zip referente a sua versão do LibreELEC. Esse arquivo deve ser transferido para o seu media center. Pode ser via cartão SD, HD externo ou rede doméstica.

Depois, vá até Add-ons, selecione a opção, localize o arquivo e ok.

Acesse então o Thoradia, 

### preparando seus arquivos

Não tem jeito, se estamos falando de um media center 

### baixando suas séries favoritas com o Medusa

o medua...

### baixando seus filmes com o Radarr

## complicando um pouco mais com o Docker

## fazendo minha própria Netflix