---
id: ADR-002
type: adr
title: Acesso remoto por mesh VPN, nunca por port forwarding
status: review
updated: 2026-08-23
parents: []
related: [REQ-001, ARCH, AYD-004]
superseded_by: null
---

# ADR-002: Acesso remoto por mesh VPN, nunca por port forwarding

## Contexto
RF-03 exige que o app funcione fora da rede de casa. O jeito tradicional e mais óbvio de
conseguir isso — abrir uma porta no roteador apontando para a câmera, com um DDNS — é
também o pior possível **para este hardware em específico**.

A `Camera` é um dispositivo white-label, com firmware sem procedência clara
(modelo reportado literalmente como `CloudCam`), sem canal de atualização de segurança
conhecido e provavelmente com credenciais de fábrica fracas. Câmeras exatamente com esse
perfil são material de primeira escolha para botnets: a exposição não é hipotética, é
varredura automatizada contínua.

Há ainda uma consequência de arquitetura, e ela é o que torna a decisão fácil: o modo como
o acesso remoto é resolvido determina quanto código de rede o app precisa ter.

## Decisão
O acesso remoto é resolvido **fora do app**, por uma `Mesh VPN` (WireGuard, direto ou
através de uma malha gerenciada) entre o iPhone e um `Home Node` na rede de casa.

Do lado do app, **não existe modo remoto**: um endereço só, sempre o mesmo, dentro e fora
de casa. O app não faz descoberta de rede, não troca de endpoint, não implementa NAT
traversal e não tem fallback.

**Port forwarding da `Camera` para a internet fica proibido** no produto — não como
recomendação, mas como restrição de arquitetura (RNF-06). Nenhuma feature futura pode
reintroduzi-lo.

## Alternativas consideradas
| Opção | Prós | Contras | Por que (não) escolhida |
|-------|------|---------|-------------------------|
| **Mesh VPN + `Home Node`** | Nada exposto; criptografia ponta a ponta; grátis; zero código de rede remota no app | Exige um dispositivo sempre ligado; VPN precisa estar conectada no iPhone | **Escolhida** |
| Port forwarding + DDNS | Nenhum hardware extra; configuração de 5 minutos | Expõe firmware sem manutenção à varredura da internet inteira; um comprometimento vira câmera dentro de casa nas mãos de terceiros | Rejeitada — o risco é desproporcional ao benefício |
| Túnel reverso via terceiro (Cloudflare Tunnel e similares) | Funciona sob CGNAT; sem porta aberta | O vídeo da casa trafega por um intermediário; mais peças; termos de uso restritivos para streaming contínuo | Rejeitada |
| `Vendor Cloud` do fabricante | Zero infraestrutura; funciona de imediato | Reintroduz a dependência de fornecedor que motivou o projeto (RN-02) | Só se o `Probe` fechar no caminho C |
| VPN embarcada no app (`NEPacketTunnelProvider`) | Não depende de app externo | Muito esforço de implementação e manutenção para ganho de conforto | Rejeitada por custo/benefício |

## Consequências / trade-offs
- **Positivas:** a `Camera` continua invisível para a internet. RF-03 custa zero linha de
  código no app. Testar em casa passa a ser suficiente — se funciona local, funciona remoto.
- **Negativas:** **dependência de hardware.** Sem um `Home Node`, os caminhos A e B do
  `ARCH` ficam inviáveis para uso remoto. Esse é o risco de nível alto declarado no
  `roadmap.md` (F3), e precisa de resposta antes da F1.
- **Negativas:** o dono precisa manter a VPN conectada no iPhone — um passo manual que um
  app de fábrica não exige. É o preço consciente de não ter a câmera na internet.
- **Impacto:** ARCH (caminhos A e B), AYD-004, ROAD-001 (marco M3).
