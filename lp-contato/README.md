# LP de contato: Carvalho Campos & Macedo Advogados

Landing page estática (HTML + CSS + JS puro, sem dependências) para receber o tráfego da rede de pesquisa do Google Ads e converter em conversa no WhatsApp.

## Estrutura
- `index.html`: página completa (CSS e JS embutidos, carregamento rápido)
- `img/`: foto da Dra. Fernanda, fotos do escritório e logo (extraídas das páginas atuais do site)

## Como publicar no Elementor
1. Edite a página (ex.: `/contato-site`) com o Elementor. Em **Configurações da página → Layout**, escolha **Elementor Canvas** (sem cabeçalho/rodapé do tema).
2. Apague o conteúdo antigo e adicione um container com **Largura: largura total** e **Preenchimento (padding): 0**.
3. Arraste um widget **HTML** e cole todo o conteúdo de `wordpress-colar.html` (imagens embutidas, ~490 KB).
4. Atualize/publique e limpe o cache (WP Rocket, LiteSpeed etc.), se houver.

O código já se protege do tema: todo o CSS fica dentro de `#ccm-lp` com classes prefixadas `ccm-`, a página ocupa 100% da largura mesmo dentro de container "boxed", e os links do WhatsApp já estão no HTML (funcionam mesmo se um plugin atrasar o JavaScript). O GTM do site continua valendo, não precisa colar de novo.

Se editar `index.html`, rode `python3 build-wordpress.py` (requer Pillow) para gerar o arquivo de colar de novo.

## Headline dinâmica (correspondência com o anúncio)
Adicione `?area=<chave>` na URL final do anúncio. A headline e a mensagem do WhatsApp mudam para a área:

| chave | uso sugerido (grupo de anúncios) |
|---|---|
| `previdenciario` / `inss` / `aposentadoria` | INSS, aposentadoria, BPC |
| `trabalhista` | advogado trabalhista |
| `criminal` | criminalista, plantão |
| `familia` / `divorcio` / `inventario` | família e sucessões |
| `servidor` | concurso / servidor público |
| `consumidor` | consumidor, plano de saúde |
| `militar` | direito militar |

Sem parâmetro, aparece a headline geral.

## Conversões (Google Ads / GA4)
A página carrega o GTM do site (`GTM-5V93PH7`) e envia para o `dataLayer`:
- `whatsapp_click` com `cta_local` (hero, area, barra-mobile, final…) e `area`
- `phone_click` com `cta_local`

No GTM: crie um acionador de *Evento personalizado* `whatsapp_click` → tag *Acompanhamento de conversões do Google Ads* (e evento GA4 `generate_lead`).

## Conformidade OAB
Texto informativo e sóbrio (Provimento 205/2021): sem promessa de resultado, sem preço, sem depoimentos de clientes e sem superlativos comparativos.
