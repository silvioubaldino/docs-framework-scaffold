---
id: REQ-001
type: requirements
title: Requisitos e Glossário
status: draft
updated: 2026-08-23
parents: []
children: [AYD-001, AYD-002, AYD-003, AYD-004]
related: [ROAD-001, ARCH, GLO]
---

# Requisitos

> **Produto em uma frase:** _um app iOS que mostra a imagem ao vivo da minha IP camera e
> gira ela para onde eu quiser, de dentro ou de fora de casa, sem um único anúncio,
> sem telemetria e sem conta obrigatória num servidor de terceiro._

O motivo de existir é negativo: os apps de fábrica **funcionam**, mas cobram o uso em
anúncios em tela cheia, upsell de cloud storage e rastreamento opaco. Este app não
compete em features — compete em não atrapalhar.

## Funcionais (RF)
| ID | Requisito | Prioridade (MoSCoW) | Critério de aceite |
|----|-----------|---------------------|--------------------|
| RF-01 | Exibir o `Stream` ao vivo da `Camera` em tela cheia, retrato e paisagem | Must | Imagem visível e fluida (≥15 fps) em até 3s após abrir o app |
| RF-02 | Controlar rotação (`PTZ`) da `Camera` — pan e tilt | Must | Botões/gesto movem a câmera enquanto pressionados e param ao soltar (`ContinuousMove` + `Stop`) |
| RF-03 | Funcionar fora da rede local, via internet móvel | Must | Vídeo e PTZ funcionam em 4G/5G com o iPhone longe de casa |
| RF-04 | Guardar endereço e credenciais da `Camera` e reconectar sozinho | Must | Após o primeiro setup, abrir o app já mostra vídeo sem digitar nada |
| RF-05 | Reagir a queda de conexão sem travar | Must | Perda de rede mostra estado claro e reconecta ao voltar, sem precisar matar o app |
| RF-06 | `Preset`: salvar e voltar a posições da câmera | Should | Salvar posição atual e retornar a ela em um toque |
| RF-07 | Snapshot do frame atual para o rolo da câmera | Could | Um toque salva a imagem em Fotos |
| RF-08 | Escutar o áudio da câmera | Could | Áudio audível e sincronizado com o vídeo |
| RF-09 | Mais de uma `Camera` | Could | Lista de câmeras, troca sem reconfigurar |
| RF-10 | Gravação local / timeline / detecção de movimento | Won't (MVP) | — |

## Não-funcionais (RNF)
| ID | Categoria | Requisito | Alvo |
|----|-----------|-----------|------|
| RNF-01 | Performance | Latência glass-to-glass na rede local | < 2s |
| RNF-02 | Performance | Latência glass-to-glass fora de casa | < 4s |
| RNF-03 | Performance | Latência do comando `PTZ` (toque → câmera se mexer) | < 500 ms |
| RNF-04 | Privacidade | Zero anúncios, zero SDK de analytics, zero crash reporter de terceiro | Nenhuma dependência que faça rede para fora do controle do usuário |
| RNF-05 | Segurança | Credenciais da câmera só no Keychain — nunca em `UserDefaults`, plist, log ou repo | Auditável no código |
| RNF-06 | Segurança | A `Camera` não é exposta diretamente à internet | Sem port forwarding / sem DMZ (ver ADR-002) |
| RNF-07 | Compatibilidade | iPhone, iOS 17+ | Roda no aparelho do dono |
| RNF-08 | Custo | Infraestrutura recorrente além da conta Apple Developer | R$ 0/mês |
| RNF-09 | Manutenção | Frequência de reinstalação exigida pela assinatura do app | ≤ 1× por ano |

## Regras de negócio
- **RN-01:** app monousuário. Não há contas, login, papéis nem compartilhamento — o dono
  do iPhone é o dono da câmera.
- **RN-02:** o app nunca fala com um servidor operado pelo desenvolvedor. Só com a própria
  `Camera`, com um `Home Node` do usuário, ou — se e somente se o caminho C se confirmar —
  com a cloud do fabricante usando as credenciais do próprio usuário.
- **RN-03:** nenhum vídeo, snapshot ou metadado é enviado para fora sem ação explícita do
  usuário (ex.: salvar no rolo).

## Restrições
**Hardware alvo** (única `Camera` conhecida, dados lidos do app de fábrica):

| Campo | Valor |
|-------|-------|
| Modelo reportado | `CloudCam` (rótulo genérico de firmware white-label — não identifica o fabricante) |
| Firmware / app integrado | `33.2.0.0920` |
| Número de série | `AJWL2405081077M2XHXLDWKCUU023116` |
| MAC | `34:A6:EF:90:C6:FB` |
| IP na LAN | `192.168.15.16` |

- **O protocolo da câmera é desconhecido** e é a maior incógnita do projeto. Resolver isso
  é o pré-requisito de todo o resto — ver AYD-001 / SPEC-001.
- Conta Apple Developer paga já disponível → distribuição pessoal com assinatura anual,
  sem revisão da App Store. Isso libera bibliotecas LGPL/GPL (ex.: VLCKit) sem risco de loja.
- Desenvolvedor solo, tempo de hobby. O escopo precisa caber em fases curtas e úteis
  isoladamente.
- Build e teste exigem macOS + Xcode + iPhone físico — só o dono consegue executá-los.

## Escopo do MVP
- **Dentro:** uma câmera; vídeo ao vivo; pan/tilt contínuo; acesso de fora de casa;
  credenciais no Keychain; reconexão automática.
- **Fora (por enquanto):** gravação e timeline, detecção de movimento e notificações,
  áudio bidirecional (falar na câmera), múltiplas câmeras, Apple TV, widget, Picture in
  Picture, modo babá eletrônica.

---

# Glossário (Linguagem Ubíqua) — GLO

<!--
id: GLO / type: glossary
Definições canônicas do domínio. Toda a doc e todo o código usam estes termos com este
significado. Adicione o termo AQUI antes de usá-lo em outro doc ou no código.
Termos canônicos em INGLÊS (atravessam para o código); prosa em português.
-->

| Termo (canônico · EN) | Definição | Sinônimos a evitar |
|-----------------------|-----------|--------------------|
| **Camera** | O dispositivo físico de captura na rede do dono, endereçável por IP. Neste produto há exatamente uma no MVP. | "device", "câmera IP", "cam" |
| **Stream** | Fluxo contínuo de vídeo ao vivo vindo da `Camera`, independente do transporte (RTSP, WebRTC, HLS). | "feed", "transmissão", "vídeo" |
| **PTZ** | Capacidade de mover a `Camera` — *pan* (horizontal), *tilt* (vertical), *zoom*. Neste produto, PTZ sem qualificação significa pan+tilt; zoom pode não existir no hardware. | "rotação", "movimento", "giro" |
| **ContinuousMove** | Comando que inicia movimento `PTZ` numa direção e velocidade e **segue até receber `Stop`**. É o modelo que corresponde a "segurar o botão". Nome vem do ONVIF. | "move", "step" |
| **Stop** | Comando que interrompe um `ContinuousMove` em andamento. Sem ele a `Camera` gira até o fim do curso. | "parar", "halt" |
| **Preset** | Posição `PTZ` nomeada e salva **na própria `Camera`**, para onde se volta com um comando. | "favorito", "marcador" |
| **ONVIF** | Padrão aberto de interoperabilidade para câmeras IP; expõe descoberta, informações e `PTZ` por SOAP/HTTP. Se a `Camera` falar ONVIF, o `PTZ` é trabalho resolvido. | "onvif protocol" |
| **RTSP** | Protocolo de controle de sessão de mídia (porta 554 típica) pelo qual se obtém o `Stream`. `AVPlayer` do iOS **não** suporta — exige biblioteca externa. | "rtsp stream" |
| **Probe** | Procedimento de descoberta que determina quais protocolos a `Camera` realmente fala. Implementado em `tools/probe_camera.py`, especificado em SPEC-001. | "scan", "varredura" |
| **Home Node** | Dispositivo do usuário que fica sempre ligado na rede de casa (Raspberry Pi, NAS, mini PC, Mac) e serve de ponto de entrada para o acesso remoto. | "servidor", "gateway" |
| **Bridge** | Software rodando no `Home Node` que traduz o protocolo da `Camera` para um que o app consuma bem (ex.: RTSP → WebRTC). Ex.: go2rtc, MediaMTX. | "proxy", "relay" |
| **Mesh VPN** | Rede privada ponto a ponto que coloca iPhone e `Home Node` no mesmo espaço de endereços, esteja o iPhone onde estiver (ex.: Tailscale, WireGuard). | "VPN", "túnel" |
| **Vendor Cloud** | Servidor do fabricante da `Camera`, usado pelo app de fábrica. Só entra em jogo no caminho C, e sempre com credenciais do próprio usuário (RN-02). | "cloud", "servidor" |
