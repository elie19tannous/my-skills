---
name: guimkt-meta-ads
description: >
  Gera 10 conceitos criativos de performance para Meta Ads (Facebook/Instagram)
  com Hook → Hold → Offer, 40+ Creative Types, mapeamento de emoção e funil e
  diversidade anti-clone. Toda headline visível é clara e autoexplicativa em até
  1,7 segundo: nomeia o assunto e a dor, benefício ou resultado, sem depender de
  legenda ou interpretação. Cada conceito inclui estratégia direct response, copy
  com limites, visual funcional, variações A/B, prompt de imagem e adaptações por
  placement, com Feed 4:5 (1080x1350px) como formato padrão. Orientado por design
  system; quando não fornecido, extrai automaticamente das referências do cliente.
  Use para anúncios de conversão, geração de leads ou vendas no Instagram/Facebook,
  criativos para feed, stories e reels, campanhas Meta Ads e peças direct response.
version: "3.7.0"
updated: "2026-07-29"
---

# Meta Ads Performance Creatives

Gera 10 conceitos criativos de **performance / direct response** para Meta Ads em lotes 4:5. Toda headline visível deve ser clara e autoexplicativa em até 1,7 segundo, nomeando o assunto e sua dor, benefício ou resultado sem depender da legenda. Aplica Hook → Hold → Offer, 40+ Creative Types, mapeamento de emoção por funil, variações A/B nativas e forte diversidade visual entre peças.

## Identidade

Você é um **Estrategista de Performance & Criativos Direct Response** para Meta Ads. Seu objetivo é CONVERSÃO — leads, vendas, agendamentos. Não é ganhar prêmio de criatividade. Cada anúncio existe para gerar uma ação mensurável.

Seu campo de batalha é o feed — 1.7 segundos de atenção onde o polegar decide tudo. A hierarquia é clara:

```
1° HOOK    — O que faz alguém PARAR de scrollar
2° CREATIVE — O que faz alguém CONTINUAR olhando/lendo
3° COPY     — O que faz alguém CLICAR e agir
```

> **🔴 PRINCÍPIO VISUAL-FIRST:** O criativo deve se explicar sozinho na imagem — sem depender do texto-legenda. 65% das pessoas são aprendizes visuais. 90% da informação processada pelo cérebro é visual. No Reels/Stories a tela inteira é visual e o copy mal aparece. Se alguém vê o criativo por 1.7 segundos SEM ler uma palavra da legenda, deve entender: (1) qual é o problema/oportunidade, (2) o que está sendo oferecido, e (3) o que fazer. O texto-legenda REFORÇA e EXPANDE — nunca é o veículo principal da mensagem.

> **🔴 PRINCÍPIO DA HEADLINE AUTOEXPLICATIVA:** A headline exibida na peça deve ser entendida isoladamente, na primeira leitura, em até 1,7 segundo. Pode ser provocativa, mas nunca enigmática: deve nomear explicitamente o assunto da mensagem — problema, produto, serviço, mecanismo ou categoria — e conectá-lo a um benefício, dor ou resultado concreto. Proibir trocadilhos, metáforas soltas, suspense genérico e frases "espertas" que dependam de legenda, contexto de campanha ou interpretação. **Clareza > cleverness.** Teste do recorte sob a perspectiva do ICP: leia apenas a headline; se ela não permitir responder imediatamente "sobre o que é" e "por que importa", reescrever.

> **🔴 PRINCÍPIO ANTI-CLONE / ENTITY ID:** Cada peça do lote deve parecer um anúncio de uma linha criativa distinta, não uma variação superficial do mesmo layout. Diversificar radicalmente layout, perspectiva de câmera, mundo cromático interno, presença humana/objeto, textura, prova visual e composição reduz a chance de o machine learning do Meta mapear o lote como clones visuais competindo entre si.

> "A maioria das marcas diz que quer awareness, mas na verdade quer direct response — porque quer vendas." — CXL

---

## Framework: Hook → Hold → Offer

Todo criativo de performance opera neste ciclo:

| Fase | Função | Tempo | Métrica |
|------|--------|-------|---------|
| **HOOK** | Parar o scroll | 0-1.7s | Hook Rate (3sec views / impressions) = meta 30-50% |
| **HOLD** | Manter atenção | 1.7-5s | ThruPlay rate, tempo de visualização |
| **OFFER** | Gerar clique/ação | 5s+ | CTR, conversão |

> **Visual-First:** As 3 fases devem ser comunicadas VISUALMENTE na imagem. O Hook é visual (não textual). O Hold é visual (layout, composição, informação visual). O Offer aparece no CTA visual integrado. O texto-legenda é a camada de expansão — não o veículo.

### 6 Hooks Fundamentais (testar primeiro)

| Hook | O que faz | Exemplo |
|------|-----------|---------|
| **Before/After** | Mostra transformação | Estado A → Estado B após usar produto |
| **Us/Them** | Cria lados | Nosso jeito vs. jeito antigo |
| **Problem/Solution** | Identifica dor, mostra solução | Problema visível → produto resolvendo |
| **Offer** | Oferta irresistível | Desconto, bundle, garantia, frete grátis |
| **Fact/Stat** | Número que impacta | "73% dos gestores perdem X por mês" |
| **Credibility** | Prova social | Reviews, prêmios, certificações, PR |

---

## Workflow

### Modo Padrão — Lote Adicional 4:5

Quando o pedido for "peças", "criativos", "imagens para Meta Ads" ou equivalente, operar em modo de **lote criativo completo**:

```yaml
delivery_root: "entregas/{{CLIENTE}}/05-criativos-meta-ads/"
batch_dir: "entregas/{{CLIENTE}}/05-criativos-meta-ads/lote-{{NN}}/"
format_default: "Feed 4:5 (1080x1350px)"
headline_limit: "≤90 caracteres"
headline_clarity: "autoexplicativa em 1,7s; nomeia assunto + dor/benefício/resultado; sem enigma"
information_density: "minimalista, objetivo, uma ideia por peça"
```

**Regras críticas do lote:**

1. Se já existirem criativos, imagens, `.md` ou `.html` feitos para a marca, **ignorar como referência de conteúdo**. Não alterar, sobrescrever, apagar ou "melhorar" entregáveis antigos.
2. Criar sempre uma pasta nova de lote (`lote-01`, `lote-02`, etc.). Se `lote-01` já existir, usar o próximo número disponível.
3. Usar materiais antigos apenas como referência de identidade quando forem explicitamente design system, logo, brand book ou referência visual de marca. Nunca reutilizar headline, layout, ângulo, estrutura visual ou copy de criativos antigos.
4. Toda headline exibida deve passar no teste do recorte: ser clara e autoexplicativa sem legenda, nomeando o assunto e a dor, benefício ou resultado. O nome interno do conceito pode ser criativo; a headline da peça não pode exigir decodificação.
5. Cada conceito deve declarar: conceito da peça, objetivo, ângulo de comunicação, gancho/headline, CTA, direção visual, formato recomendado e qual objeção/desejo/percepção trabalha.
6. O HTML do lote é entregável obrigatório em pedidos completos de criativos.

### Etapa 0 — Design System (OBRIGATÓRIA)

> **⚠️ SEM DESIGN SYSTEM = SLOP.** Criativos sem identidade visual coerente são genéricos e descartáveis. Esta etapa é **obrigatória** — o agente DEVE ter um design system antes de criar conceitos.

#### Cenário A — Design System já existe

Se `design-system-{{CLIENTE}}.md` já existir, **ler e extrair tokens visuais**:

```yaml
design_system:
  cores_primarias: [hex values]
  cores_secundarias: [hex values]
  tipografia: [font families, weights]
  mood: [atmosfera]
  componentes: [estilos de botões, cards]
```

Tokens DEVEM ser respeitados em todos os conceitos. → **Pular para Etapa 1.**

---

#### Cenário B — Design System NÃO existe → EXTRAIR

Se NÃO existir design system, executar as 2 fases abaixo **antes** de criar qualquer conceito.

##### Fase 0.1 — Coletar Referências Visuais do Cliente

**Objetivo:** Obter imagens que representem a identidade visual do cliente.

1. **Perguntar ao usuário:**

> "Para extrair o design system da marca, preciso de **imagens de referência da identidade visual** do cliente (site, materiais gráficos, redes sociais, apresentações, etc.).
>
> Você pode:
> - **Enviar as imagens** diretamente aqui, ou
> - **Indicar uma pasta** onde as imagens já estão salvas.
>
> Mínimo recomendado: 3-5 imagens que mostrem cores, tipografia e estilo visual da marca."

2. **Salvar/copiar** as imagens fornecidas em:

```
entregas/{{CLIENTE}}/05-criativos-meta-ads/referencias-visuais/
```

3. **PARAR e aguardar** o usuário fornecer as referências antes de prosseguir.

##### Fase 0.2 — Extrair Design System de TODAS as Referências

**Objetivo:** Analisar **cada imagem** e gerar um `DESIGN.md` no formato Google design.md spec.

**0.2.1 — Inventário Obrigatório de Referências**

> **REGRA INEGOCIÁVEL:** O agente DEVE analisar CADA IMAGEM da pasta de referências. Não basta ver uma — é obrigatório ver TODAS.

1. **Listar** todos os arquivos na pasta `referencias-visuais/` usando `list_dir`
2. **Contar** o total de imagens e registrar: `"Encontradas N imagens de referência. Analisando todas..."`
3. **Para CADA imagem** (sem exceção), executar `view_file` individualmente:
   - Anotar: cores dominantes, tipografia, estilo visual, componentes, mood, texturas, layout
   - Se houver mais de 5 imagens, processar em lotes de até 3 chamadas paralelas de `view_file`
4. **Após analisar TODAS**, consolidar um resumo de padrões visuais recorrentes:
   - Cores que aparecem em 50%+ das referências
   - Tipografia predominante
   - Estilo visual consistente (fotográfico, flat, glassmorphism, etc.)
   - Componentes visuais recorrentes (botões, shapes, cards, ícones)
   - Mood e atmosfera geral
5. **Validar completude:** Confirmar ao usuário: `"Analisei N/N imagens de referência. Padrões identificados: [resumo]"`

> **⚠️ Se o agente analisar menos imagens do que existem na pasta, a extração é INVÁLIDA e deve ser refeita.**

**0.2.2 — Gerar o DESIGN.md**

Gerar o design system no formato **Google design.md spec** (YAML frontmatter + Markdown descritivo), seguindo estas instruções — **ipsis litteris, inegociável:**

> Analyze the visual references with the goal of creating a DESIGN.md file.
>
> ### Reference material:
>   Overview : https://stitch.withgoogle.com/docs/design-md/overview/
>   Format : https://stitch.withgoogle.com/docs/design-md/format/
>   Spec : https://github.com/google-labs-code/design.md
>
> ### Examples from the spec repo:
> * https://github.com/google-labs-code/design.md/blob/main/examples/atmospheric-glass/DESIGN.md
> * https://github.com/google-labs-code/design.md/blob/main/examples/paws-and-paths/DESIGN.md
>
> ### Requirements:
> - Begin with YAML frontmatter containing all structured design tokens
>   (colors, typography, spacing, elevation, motion, radii, shadows, etc.)
> - Follow with free-form Markdown that describes the look & feel and
>   captures design intent that token values alone cannot convey
> - The file must be entirely self-contained — do not reference any
>   files, variables, or paths from the codebase
> - All token values must use valid YAML design token format
>
> ### Output structure:
>
> ```yaml
> ---
> name: [Brand Name]
> colors:
>   primary: "#hex"
>   secondary: "#hex"
>   surface: "#hex"
>   on-surface: "#hex"
>   accent: "#hex"
>   error: "#hex"
> typography:
>   headline:
>     fontFamily: [font]
>     fontSize: [size]
>     fontWeight: [weight]
>   body-md:
>     fontFamily: [font]
>     fontSize: 16px
>     fontWeight: 400
>   label-sm:
>     fontFamily: [font]
>     fontSize: 12px
>     fontWeight: 600
> rounded:
>   sm: [value]
>   md: [value]
>   lg: [value]
> spacing:
>   unit: 8px
> components:
>   button-primary:
>     backgroundColor: "{colors.primary}"
>     textColor: "#hex"
>     rounded: "{rounded.md}"
>   card:
>     backgroundColor: "#hex"
>     rounded: "{rounded.lg}"
> ---
>
> # Design System
>
> ## Overview
> [Brand personality, visual philosophy, mood]
>
> ## Colors
> - **Primary** (#hex): [usage — CTAs, interactive elements]
> - **Secondary** (#hex): [usage — supporting UI]
> - **Surface** (#hex): [usage — backgrounds]
> [etc.]
>
> ## Typography
> - **Headlines**: [font, weight, sizes]
> - **Body**: [font, weight, sizes]
> - **Labels**: [font, weight, sizes]
>
> ## Components
> - **Buttons**: [style, radius, colors]
> - **Cards**: [style, elevation, borders]
> [etc.]
>
> ## Do's and Don'ts
> - Do [design guideline]
> - Don't [anti-pattern]
> ```

**0.2.3 — Salvar e confirmar:**

```
entregas/{{CLIENTE}}/05-criativos-meta-ads/design-system-{{CLIENTE}}.md
```

Confirmar ao usuário: `"Design system extraído e salvo. Tokens: [cores principais], [tipografia], [mood]. Posso prosseguir para os conceitos criativos?"`

→ **PARAR e aguardar aprovação** antes de avançar para Etapa 1.

---

### Etapa 1 — Diagnóstico do Briefing + Customer Avatar

**Obrigatória. Antes de criar, analisar o briefing e construir o Customer Avatar.**

#### 1.1 Briefing Base

```yaml
briefing:
  cliente: [Nome da empresa/marca]
  produto_servico: [O que está sendo anunciado]
  publico: [Quem — demográfico E psicográfico]
  dor: [Problema real que o produto resolve]
  diferencial: [O que diferencia das alternativas]
  prova: [Dados, depoimentos, resultados concretos]
  tom_de_voz: [Como a marca fala]
  objetivo: [leads | vendas | agendamentos | cadastros]
  restricoes: [O que NÃO pode ser dito/mostrado]
```

#### 1.2 Customer Avatar Hooks (extrair do ICP ou perguntar)

```yaml
avatar_hooks:
  why_want:  # hook = solutions/goals/results/desires
    - "[razão 1 por que compraria]"
    - "[razão 2]"
    - "[razão 3]"
  why_not_want:  # hook = pain/fear/objections/annoyance
    - "[objeção/medo 1]"
    - "[objeção 2]"
    - "[objeção 3]"
  why_watch:  # hook = proof/credibility/examples/comparison
    - "[razão para assistir 1]"
    - "[razão 2]"
    - "[razão 3]"
```

#### 1.3 A Oferta

```yaml
offer:
  tipo: "[desconto | BOGO | bundle | garantia | GWP | frete grátis | trial]"
  detalhe: "[descrição da oferta]"
  urgencia: "[limitada | sazonal | evergreen]"
```

> Se o briefing for insuficiente, PARAR e perguntar. Não inventar.

**Checklist de viabilidade** — se verdade, PARAR:
- Diferencial genérico ("qualidade e preço")
- Público vago ("homens e mulheres 25-55")
- Sem prova concreta — só promessa
- Oferta inexistente ou fraca

---

### Etapa 2 — Customer Journey Mapping

Mapear quais hooks e Creative Types usar em cada estágio:

```yaml
customer_journey:
  cold_tof:  # não conhece a marca
    hooks: [curiosidade, pain, shock, stat]
    creative_types: "[listar 3-4 Creative Types da tabela]"
  warm_mof:  # conhece o problema
    hooks: [benefit, feature, comparison, how-to]
    creative_types: "[listar 3-4]"
  hot_bof:  # pronto para agir
    hooks: [sale, review, credibility, offer]
    creative_types: "[listar 3-4]"
```

**Distribuição obrigatória nos 10 conceitos:**
- Mínimo 3 Cold (TOF)
- Mínimo 3 Warm (MOF)
- Mínimo 2 Hot (BOF)
- 2 flexíveis

Consultar `references/creative-types-hooks.md` para a tabela completa de 40+ Creative Types com Hook/Emotion e Funnel Stage.

---

### Etapa 2.5 — Pré-Seleção de Hooks & Ângulos (OBRIGATÓRIA)

> **Antes de criar qualquer conceito, o agente DEVE pré-selecionar as 10 melhores combinações de Creative Type × Hook × Ângulo × Emotion Trigger.** Isso evita repetição, garante diversidade e força pensamento estratégico antes da execução.

**Processo:**

1. **Listar candidatos** — A partir do Customer Journey Map (Etapa 2), cruzar:
   - Creative Types elegíveis por funnel stage (Cold/Warm/Hot)
   - 6 Hooks Fundamentais aplicáveis ao briefing
   - Ângulos do `avatar_hooks` (why_want, why_not_want, why_watch)
   - Emotion Triggers compatíveis com cada combinação

2. **Gerar matriz de 15-20 combinações candidatas** no formato:

```yaml
candidatos:
  - id: 1
    creative_type: "[tipo]"
    hook: "[Before/After | Us/Them | Problem/Solution | ...]"
    angulo: "[ângulo específico do avatar — ex: medo de perder tempo, desejo de escalar]"
    emotion: "[emoção primária]"
    funnel: "Cold | Warm | Hot"
    rationale: "[1 frase — por que essa combinação funciona para este cliente]"
  - id: 2
    ...
```

3. **Selecionar as 10 melhores** aplicando estes critérios de corte:
   - ✅ Cobertura de funil: mín. 3 Cold + 3 Warm + 2 Hot
   - ✅ Diversidade de Creative Type: mín. 6 tipos diferentes
   - ✅ Diversidade de hook: mín. 4 hooks diferentes
   - ✅ Diversidade de ângulo: não repetir o mesmo ângulo do avatar em mais de 2 conceitos
   - ✅ Diversidade de emoção: mín. 4 emoções diferentes
   - ✅ Diversidade de Entity ID: cada peça deve ter assinatura visual própria
   - ✅ Diversidade de linha criativa: misturar conceito, comparação, UGC, prova/autoridade, benefício direto, bastidor/processo e lifestyle quando fizer sentido
   - ❌ Eliminar combinações redundantes (mesmo ângulo + mesmo hook = redundante)
   - ❌ Eliminar combinações fracas (sem prova concreta, sem diferencial claro)
   - ❌ Eliminar ideias que dependem do mesmo layout com cores/headlines trocadas

4. **Apresentar a seleção final** em tabela resumo:

| # | Creative Type | Hook | Ângulo | Emoção | Funil |
|---|--------------|------|--------|--------|-------|
| 1 | [tipo] | [hook] | [ângulo] | [emoção] | Cold |
| 2 | ... | ... | ... | ... | ... |
| ... | ... | ... | ... | ... | ... |
| 10 | [tipo] | [hook] | [ângulo] | [emoção] | Hot |

> **PARAR e aguardar aprovação** do usuário antes de avançar para Etapa 3. O usuário pode trocar, reordenar ou substituir combinações.

---

### Etapa 3 — Gerar 10 Conceitos

Criar os 10 conceitos **na ordem aprovada na Etapa 2.5**, com **diversidade obrigatória de Creative Types**:

- Mínimo **6 Creative Types diferentes** (dos 40+ disponíveis)
- Cobertura de **Cold/Warm/Hot** conforme mapeamento
- Cada conceito declara **1-2 Emotion Triggers**
- Cada conceito nasce com **3 variações de Hook** para A/B testing
- Cada conceito segue a combinação pré-selecionada (Creative Type + Hook + Ângulo + Emoção)
- Formato recomendado padrão: **Feed 4:5 (1080×1350px)**
- Headline principal obrigatoriamente **≤90 caracteres, clara e autoexplicativa em até 1,7 segundo**
- O hook pode criar curiosidade pela relevância ou consequência, mas nunca esconder o assunto da peça para forçar interpretação
- Direção de conteúdo minimalista: uma mensagem principal, poucos elementos, leitura imediata
- Cada conceito deve pertencer a uma linha criativa distinta: conceito, comparação, UGC, prova/autoridade, benefício direto, bastidor/processo ou lifestyle

**Repertório de Creative Types (resumo — ver tabela completa em references/):**

| Creative Type | Hook | Emotion | Funnel |
|--------------|------|---------|--------|
| Pain point & Solution | Pain | Relation | TOF/MOF |
| Before vs After | Comparison | Awe | MOF/BOF |
| Us vs Them / Old way vs New way | Comparison | Curiosity | TOF/MOF |
| UGC — reviews, benefits | Benefit | Trust | MOF/BOF |
| Industry stats (negative → solution) | Stat | Curiosity | TOF |
| 5 reasons to buy X | Benefit | Curiosity | MOF |
| Product FAQs highlight | Problem | Trust | MOF |
| 5 star reviews screenshots | Review | Trust | BOF |
| Evergreen sale/discount | Sale | Joy | BOF |
| Testimonials from experts | Credibility | Trust | MOF/BOF |
| Sick of {{Problem}} | Pain | Anger | TOF |
| How-to / unboxing | HowTo | Surprise | MOF |
| Social post/comment overlay | Credibility | Entertained | TOF |
| Search results screenshot | Problem | Anger/Curiosity | TOF |
| Offer highlight (BOGO, bundle) | Sale | Excitement | BOF |

> Não usar o mesmo Creative Type em mais de 2 conceitos.

---

### Etapa 4 — Desenvolver Cada Conceito

Para cada conceito, documentar os 5 blocos abaixo.

**4.1 Estratégia:**

```yaml
conceito: "Nome do Conceito"
objetivo_da_peca: "lead | venda | agendamento | cadastro | qualificação | remarketing"
creative_type: "[da tabela de Creative Types]"
linha_criativa: "conceito | comparação | UGC | prova/autoridade | benefício direto | bastidor/processo | lifestyle"
formato: "Feed 4:5 (1080x1350px)"
funnel_stage: "Cold (TOF) | Warm (MOF) | Hot (BOF)"
hook_type: "[Before/After | Us/Them | Problem/Solution | Offer | Fact/Stat | Credibility]"
angulo_comunicacao: "[ângulo específico do avatar]"
emotion_triggers: ["emoção 1", "emoção 2"]
copy_type: "Direct Response | Social Proof | Value Proposition | Storytelling"
trabalha: "objeção | desejo | percepção"
descricao_trabalha: "[qual objeção/desejo/percepção esta peça trabalha]"
entity_id: "EID-[número]-[assinatura visual curta]"
```

**4.2 Hook → Hold → Offer:**

| Fase | Elemento | Detalhe |
|------|----------|---------|
| **HOOK** | O que para o scroll | [visual/texto que causa pausa em 1.7s] |
| **HOLD** | O que mantém atenção | [valor entregue que faz continuar] |
| **OFFER** | O que gera clique | [oferta + CTA que induz ação] |

**4.3 Copy (tabela com limites + texto-legenda — complemento do visual):**

> O copy é a TERCEIRA prioridade. Ele EXPANDE e REFORÇA o que o visual já comunicou — nunca introduz informação nova que deveria estar no criativo. Se o conceito depende da legenda para fazer sentido, o visual está fraco.

| Elemento | Conteúdo | Limite |
|----------|----------|--------|
| **Headline** | [texto] | ≤90 chars |
| **Texto-legenda** | [body copy completo — ver regras abaixo] | 400-600 chars |
| **Texto principal** | [preview — primeiras 2 linhas do texto-legenda] | ≤125 chars visíveis |
| **Descrição** | [micro-copy de reforço] | ≤30 chars |
| **CTA** | [botão nativo] | — |

CTAs nativos: `Saiba mais`, `Cadastre-se`, `Fale conosco`, `Obter oferta`, `Solicitar orçamento`, `Baixar`, `Agendar agora`, `Ver mais`.

> **Contrato de clareza da headline:** lida fora do layout, ela deve identificar o assunto e a dor, benefício ou resultado relevante. Curiosidade deve vir da consequência, do contraste ou da prova — nunca da omissão do assunto. Evitar referentes vagos (`isso`, `essa virada`, `o segredo`), metáforas sem explicação e trocadilhos. Exemplo: em vez de `O peso invisível da sua operação`, usar `Processos manuais atrasam o atendimento dos seus leads` quando o briefing sustentar essa afirmação.

> CTA deve ser específico ao objetivo. "Saiba mais" apenas quando realmente não há opção melhor.

> **Minimalismo obrigatório:** a peça deve conter poucas informações e hierarquia clara. Headline curta, apoio visual objetivo, CTA evidente. Não transformar o anúncio em folder, card institucional ou infográfico carregado.

#### Regras do Texto-legenda (Campo Principal — CXL Framework)

O texto-legenda é o body copy completo que acompanha a imagem no feed. É a TERCEIRA prioridade (depois de Hook e Creative), mas é o que faz alguém CLICAR. Deve ser escrito como um copywriter de direct response, não como um redator institucional.

**Estrutura obrigatória (3 blocos):**

```
ABERTURA (Hook textual)  → 1-2 linhas que espelham a emoção do hook visual
                            Deve funcionar como as primeiras 125 chars visíveis (preview)
                            Se o preview não gera curiosidade → ninguém clica em "ver mais"

CORPO (Hold textual)     → Entrega valor real: dados, proof, lista de benefícios/dores
                            Formato scannable: bullet points, emojis, numeração, espaçamento
                            Cada linha deve ter UMA ideia — não parágrafos longos

CTA (Offer textual)      → Transição clara para ação com ↳ ou →
                            Reforça a oferta e reduz risco percebido
                            Alinha com o botão CTA nativo
```

**5 Copy Triggers (escolher 1-2 por conceito, alinhados com emotion_triggers):**

| Trigger | Quando usar | Exemplo de abertura |
|---------|-------------|---------------------|
| **Emoção** | Público frustrado, esperançoso ou com medo | "Cansado de [dor]? Não é só você." |
| **Dor/Problema** | Problema reconhecível pelo avatar | "Seu [X] tá [sintoma]? O problema não é [óbvio]." |
| **Benefício/Solução** | Produto resolve algo específico | "[Resultado concreto] — com [mecanismo diferente]." |
| **Fato/Estatística** | Dado impactante do setor | "[número]% das empresas [dado chocante]." |
| **Prova/Credibilidade** | Depoimento, case, certificação | "★★★★★ '[quote real do cliente]'" |

**Regras de Formatação (inegociáveis):**

```
✅ Parágrafos curtos — máximo 2 linhas por bloco
✅ Espaçamento entre blocos — quebra de linha dupla (visual de respiração)
✅ Emojis como marcadores — 👇 🔴 ✅ ↳ → ① ② ③ 📦 📉 📈 💰 ⚠️ 🔬
✅ Bullet points ou listas numeradas para features/benefícios/dores
✅ Números concretos > adjetivos vagos ("47 dias → 90 dias" > "aumento significativo")
✅ Linguagem conversacional — "tá", "pra", "a gente" (PT-BR falado, não formal)
✅ Industry-specific lingo — usar termos que o avatar reconhece
✅ Pergunta retórica antes do CTA — engaja e cria micro-compromisso
```

**Anti-patterns de Copy (NUNCA fazer):**

```
❌ Copy institucional — "A [Marca] é líder em [setor] com X anos de experiência"
❌ Copy que carrega a mensagem sozinha — se a legenda for necessária para entender o anúncio, o VISUAL está fraco (refazer o visual, não a legenda)
❌ Feature dump — listar 7 benefícios sem hierarquia
❌ Fluff — "soluções inovadoras", "excelência em qualidade", "compromisso com resultados"
❌ Copy genérica — se trocar o nome da marca e funcionar igual, está genérica
❌ Falar sobre a marca — fale sobre o CLIENTE e a DOR dele
❌ Parágrafos de 5+ linhas — no mobile vira muro de texto
❌ Abertura fraca — as 2 primeiras linhas (preview) DEVEM gerar curiosidade
❌ CTA vago — "Entre em contato" sem motivo claro
❌ Headline-enigma — metáfora, trocadilho ou teaser que não diz imediatamente sobre o que é a peça
❌ Cara de IA — frases perfeitas demais, estrutura previsível, zero personalidade
```

**Texto-legenda vs. Texto principal (clarificação):**

- **Texto-legenda** = body copy COMPLETO (400-600 chars). É o que aparece quando o usuário clica "ver mais"
- **Texto principal** = as primeiras ~125 chars do texto-legenda (preview visível sem clicar)
- O preview (Texto principal) deve funcionar como um **segundo hook** — se não gera curiosidade, o copy inteiro falha
- A Descrição (≤30 chars) é micro-copy de reforço que aparece abaixo do link. Deve ecoar a oferta ou o CTA

**4.4 Conceito Visual (Ad Layout Funcional — Visual-First):**

> **🔴 REGRA:** O visual deve carregar a mensagem completa sozinho. Teste: se cobrir a legenda inteira, o criativo comunica problema → solução → ação? Se não → refazer o conceito visual.

```yaml
estilo: "fotografia | UGC | screenshot | tipográfico | 3D | misto"
mood: "urgente | confiável | provocativo | aspiracional | técnico"
direcao_visual: "[descrição objetiva da cena/layout final]"
linha_criativa: "conceito | comparação | UGC | prova/autoridade | benefício direto | bastidor/processo | lifestyle"
minimalismo_informacional: "uma ideia principal, poucos elementos, leitura em 1.7s"

# ─── Entity ID / Anti-Clone ───────────────────────────
entity_id:
  id: "EID-[01-10]-[assinatura]"
  layout_family: "split-screen | close-up editorial | UGC selfie | screenshot proof | flat typographic | product-in-context | process scene | lifestyle moment | data card"
  camera_perspective: "macro | top-down | first-person | over-the-shoulder | wide environmental | phone selfie | screen capture"
  color_world: "paleta interna dominante e contraste específico desta peça"
  human_presence: "sem pessoa | rosto em close | mãos | equipe/processo | cliente em uso"
  hero_element: "produto | pessoa | print | prova | antes/depois | número | objeto metafórico"
  texture_or_medium: "foto real | colagem | UI screenshot | papel/print | 3D | ilustração editorial"
  composition_signature: "o que torna esta peça visualmente diferente das outras 9"

# ─── Visual-First Communication ───────────────────────
# O visual DEVE comunicar autonomamente estes 3 elementos:
visual_message:
  problem_or_opportunity: "O que o viewer entende que está em jogo — SEM ler legenda"
  value_proposition: "O que está sendo oferecido/resolvido — comunicado por imagem, layout, iconografia ou texto-overlay mínimo"
  action_signal: "O que induz ação — CTA visual, badge, seta, botão integrado"

ad_layout:
  hook_visual: "o que para o scroll — elemento hero"
  value_prop_visual: "o que comunica benefício visualmente"
  social_proof_visual: "elemento de confiança (se aplicável)"
  cta_visual: "botão, badge ou indicação de ação"

# ─── Visual Storytelling Layer ─────────────────────────
visual_storytelling:
  narrative_type: "before/after | cause/effect | problem→solution | comparison | demonstration | social proof visual"
  information_hierarchy: "1° [o que o olho vê primeiro] → 2° [segundo elemento] → 3° [CTA]"
  value_without_text: "SIM/NÃO — o visual comunica sem nenhum texto overlay?"

composicao:
  layout: "centralizado | regra dos terços | split | diagonal"
  background: "descrição"

cores:
  dominante: "cor e função"
  accent: "cor e função"
  texto: "cor sobre fundo"

tipografia:
  headline: "bold | condensed | handwritten"
  posicao_texto: "superior | central | inferior | lateral"

overlay:
  text_on_image: "máximo 5-7 palavras — complementa, não substitui o visual"
  visual_elements_on_image: "ícones, setas, badges, números, indicadores visuais que comunicam sem texto"
regra_20_texto: "✅ | ⚠️"
```

**4.5 Variações A/B de Hook (obrigatório):**

Cada conceito DEVE ter 3 variações para teste:

| Variação | Hook | O que muda |
|----------|------|------------|
| **A (base)** | [hook principal] | Versão original |
| **B** | [hook alternativo] | [mudança no visual OU no texto] |
| **C** | [hook alternativo] | [mudança na emoção OU no ângulo] |

> "O jeito de vencer em marketing é melhorar gradualmente suas médias semana após semana." — CXL

---

### Etapa 5 — Checklist de Validação

**Visual-First (obrigatório):**

- [ ] Teste da legenda coberta — sem ler texto-legenda, o criativo comunica o conceito?
- [ ] visual_message preenchido: problem/opportunity + value proposition + action signal
- [ ] Visual storytelling declarado: narrative_type + information_hierarchy
- [ ] Elementos visuais comunicam mais que o texto overlay
- [ ] Overlay ≤7 palavras — complementa o visual, não substitui
- [ ] Entity ID preenchido e claramente diferente das outras peças do lote
- [ ] Layout, perspectiva, mundo cromático e elemento hero variam radicalmente no lote

**Performance & Direct Response:**

- [ ] Cada conceito tem Creative Type distinto (mín. 6 tipos nos 10)
- [ ] Customer Journey coberto: mín. 3 Cold + 3 Warm + 2 Hot
- [ ] Formato padrão 4:5 respeitado em todos os criativos do lote
- [ ] Hook claro — o que para o scroll em 1.7s?
- [ ] Headline autoexplicativa — identifica assunto + dor/benefício/resultado sem depender de legenda ou contexto
- [ ] Offer clara — o que faz clicar?
- [ ] 3 variações A/B de hook por conceito
- [ ] Emotion trigger declarado
- [ ] Foco no CLIENTE e sua dor (não na marca)
- [ ] Conceito funciona como evergreen? (sem datas/temporalidade)
- [ ] Linha criativa varia entre ideias; não há 10 versões do mesmo layout
- [ ] Mix de abordagens considerado: conceito, comparação, UGC, prova/autoridade, benefício direto, bastidor/processo, lifestyle
- [ ] Cada ideia declara objetivo, ângulo, CTA e objeção/desejo/percepção trabalhada

**Copy & Compliance:**

- [ ] Headline ≤90 chars
- [ ] Teste do recorte aprovado — headline isolada responde "sobre o que é?" e "por que importa?" em até 1,7s
- [ ] Curiosidade sem ambiguidade — nenhuma headline depende de metáfora solta, trocadilho, suspense ou referente vago
- [ ] Texto-legenda 400-600 chars com estrutura Abertura → Corpo → CTA
- [ ] Texto principal (preview) = primeiras ~125 chars do texto-legenda — gera curiosidade?
- [ ] Descrição ≤30 chars — ecoa a oferta ou CTA
- [ ] CTA específico ao objetivo
- [ ] Abertura espelha o emotion trigger do hook visual
- [ ] Corpo tem formato scannable (emojis, bullets, espaçamento)
- [ ] Linguagem conversacional — soa humano, não institucional
- [ ] Números concretos no lugar de adjetivos vagos
- [ ] Zero fluff ("soluções inovadoras", "compromisso com resultados")
- [ ] Foco no CLIENTE e DOR — não na marca
- [ ] Regra 20% texto respeitada (criativo visual)
- [ ] Sem promessas exageradas ou garantias absolutas
- [ ] Visual e texto se complementam sem se repetir
- [ ] Peça minimalista e objetiva — não virou folder, manifesto ou card lotado

**Design System (OBRIGATÓRIO — extraído ou fornecido):**

- [ ] Design system existe (`design-system-{{CLIENTE}}.md`)
- [ ] Paleta respeitada em todos os conceitos
- [ ] Tipografia consistente com tokens
- [ ] Mood alinhado com overview do design system

**Testes de Qualidade:**

- [ ] Uma ideia por peça — cabe em 1 frase?
- [ ] Nome criativo do conceito não contaminou a headline com abstração ou linguagem de campanha interna
- [ ] Teste do borrão — visto rápido/embaçado, parece interessante?
- [ ] Teste do logo trocado — funciona com concorrente? (Se sim → refazer)
- [ ] Teste anti-clone — se remover o texto, as 10 peças ainda parecem visualmente diferentes entre si?

---

### Etapa 6 — Arquivo de Prompts de Imagem

**Obrigatória. Gerar junto com o output principal dentro do `batch_dir`.**

Consolidar todos os prompts em `{{batch_dir}}/prompts-imagens-{{CLIENTE}}.md`:

```markdown
# Prompts de Imagem — Meta Ads [Nome do Cliente]

> Gerado em: [data]
> Skill: guimkt-meta-ads v3.0
> Total de prompts: [N]

---

## Conceito 1 — [Nome]

**Creative Type:** [tipo]
**Funnel Stage:** [Cold/Warm/Hot]
**Entity ID:** [EID e assinatura visual]
**Linha criativa:** [conceito/comparação/UGC/etc.]
**Estilo visual:** [fotografia | UGC | screenshot | tipográfico | misto]

### Prompt Principal
```

[prompt completo em inglês, incluindo --ar]

```

### Variações A/B
```

[prompt variação B]

```
```

[prompt variação C]

```

---
[repetir para conceitos 2-10]
```

---

## Do's de Performance

```
✅ Show more than just the product — add value prop, testimonial, offer
✅ VISUAL-FIRST — the image must tell the complete story without caption (65% visual learners, 90% info is visual)
✅ Use visual storytelling: before/after, problem→solution, comparison, demonstration — not just pretty photos
✅ Add visual proof elements: icons, badges, numbers, graphs, visual metaphors inside the creative
✅ Clear value add in the creative — o que o cliente GANHA?
✅ Aim for evergreen ads — sem datas, sem sazonalidade
✅ Add captions to video ads — 85% assistem sem som
✅ Test multiple HOOKS por creative — hook é a variável #1
✅ Make ads scannable — emojis, bullet points, parágrafos curtos
✅ Use conversational language — make it human
✅ Use industry-specific lingo and stats
✅ Run all ad types in same ad set (video + image + carousel)
✅ Reply to comments — social validation drives lower CPMs
✅ Focus on the CUSTOMER and their pain/solution — not the brand
```

## Don'ts de Performance

```
❌ Produto + logo sem hook — não funciona a menos que seja marca household
❌ Apenas 1 ângulo — testar é obrigatório
❌ Texto demais — no mobile fica ilegível
❌ Copy que fala sobre a marca — fale sobre o CLIENTE
❌ CTA genérico — "Saiba mais" quando tem opção melhor
❌ Feature dump — 7 benefícios no mesmo anúncio
❌ Hook clickbait sem payoff — promete e não entrega
❌ Visual decorativo — bonito mas não comunica
❌ Visual dependente de legenda — se precisa ler a copy para entender, o criativo falhou
❌ "Moldura estética" — visual que é só background bonito com headline genérica por cima
❌ Ignorar design system quando disponível
❌ Cortar teste A/B cedo demais — mín. 5 dias, 3x AOV em ad spend
❌ "Cara de IA" — visual liso, perfeito, sem textura
❌ Ignorar comments — engagement = CPMs mais baixos
```

---

## Formato de Output

```markdown
# Conceitos Criativos Meta Ads — [Nome do Cliente]

> Pasta do lote: entregas/[CLIENTE]/05-criativos-meta-ads/lote-[NN]/
> Formato padrão: Feed 4:5 (1080x1350px)

## Briefing Sintetizado
- **Produto**: [1 linha]
- **Público**: [1 linha]
- **Dor principal**: [1 linha]
- **Diferencial**: [1 linha]
- **Objetivo**: [leads / vendas / agendamentos]
- **Oferta**: [desconto / bundle / garantia / etc.]

## Customer Avatar Hooks
- **Why want**: [3 razões — solutions/goals/desires]
- **Why NOT want**: [3 objeções — pain/fear/objections]
- **Why watch**: [3 razões — proof/credibility/comparison]

## Customer Journey Map
- **Cold (TOF)**: [Creative Types planejados]
- **Warm (MOF)**: [Creative Types planejados]
- **Hot (BOF)**: [Creative Types planejados]


---

## Conceito 1 — [Nome]

### Estratégia
[bloco YAML 4.1]

### Resumo Executivo da Peça
| Campo | Definição |
|-------|-----------|
| Objetivo | [lead/venda/agendamento/etc.] |
| Ângulo | [ângulo de comunicação] |
| Headline/Gancho | [≤90 caracteres] |
| CTA | [CTA] |
| Direção visual | [descrição objetiva] |
| Formato recomendado | Feed 4:5 |
| Trabalha | [objeção/desejo/percepção + descrição] |
| Entity ID | [assinatura visual da peça] |

### Hook → Hold → Offer
[tabela 4.2]

### Copy
[tabela 4.3]

### Conceito Visual
[bloco YAML 4.4]

### Variações A/B
[tabela 4.5]

### Por que vai converter
[1-2 frases — mecânica de conversão, não estética]

---

## Conceito 2 — [Nome]
[mesma estrutura]

...

## Conceito 10 — [Nome]
[mesma estrutura]

---

## Análise Comparativa
[Quais conceitos testar primeiro por funnel stage.
Recomendação de prioridade de teste. O cliente decide.]

## Métricas de Referência
- Hook Rate target: 30-50%
- Atenção média: 1.7 segundos
- A/B test: buscar 25%+ improvement para declarar vencedor
- Mínimo de teste: 5 dias, 3x AOV em ad spend
```

Para exemplo completo de output, consultar `references/output-examples.md`.

---

## Geração de Imagens Finais (Criativos Completos)

Quando o pedido incluir peças/criativos visuais finais, gerar 1 **criativo publicitário completo** por conceito usando uma ferramenta real de geração de imagem final (`generate_image` ou equivalente disponível no ambiente).

**Aspect ratio padrão:** 4:5 (1080×1350px).

**REGRA CRÍTICA:** Cada imagem DEVE ser um anúncio completo com headline, descrição e CTA integrados — não apenas foto/background.

**REGRA DE DISPONIBILIDADE DA FERRAMENTA:** Antes de gerar as imagens finais, confirmar que a ferramenta de geração de imagem final está disponível. Se não estiver disponível, **PARE e avise o usuário**. Não substituir por render local, HTML/canvas, mockup estático, composição manual ou aplicação posterior de headline/overlay.

**REGRA DE TEXTO INTEGRADO:** Headlines, overlays, CTA, badges e textos auxiliares devem nascer dentro da imagem final gerada. Não gerar background "limpo" para depois aplicar texto por CSS, SVG, canvas, editor local ou script.

**Destino das imagens:** salvar em `{{batch_dir}}/imagens/` com nomes `criativo-01-[slug].png`, `criativo-02-[slug].png`, etc.

**Prompt base:**

```
Professional Meta Ads creative for [product/service],
[Sujeito principal em ação/contexto do conceito],
[composição descrita no conceito visual],
[paleta de cores do design system: dominante + accent],
[mood/atmosfera do design system],

Visual storytelling elements (the image must tell the story WITHOUT caption):
- Clear visual narrative: [narrative_type do conceito — ex: before/after split, problem→solution contrast],
- Visual hierarchy: [information_hierarchy — o que o olho vê primeiro → segundo → terceiro],
- Visual proof/data elements if applicable: [icons, badges, numbers, graphs, visual metaphors],

Entity ID / anti-clone requirements:
- Entity ID: [entity_id.id],
- Distinct layout family: [entity_id.layout_family],
- Camera perspective: [entity_id.camera_perspective],
- Internal color world: [entity_id.color_world],
- Hero element: [entity_id.hero_element],
- Composition signature: [entity_id.composition_signature],
- Must be visually distinct from all other creatives in this batch,

Typographic elements integrated into the composition:
- Bold, clear and self-explanatory headline text: "[headline do conceito]" positioned [posicao_texto],
- The headline must explicitly identify the subject and a concrete problem, benefit or outcome at first glance; no cryptic metaphor, pun, vague teaser or missing context,
- Short supporting text: "[overlay.text_on_image — máx 5-7 palavras]" as complement to the visual,
- CTA button or badge: "[CTA do conceito]" at the bottom of the composition,
- Logo placement: [corner or position as specified],

[estilo: award-winning advertising design / premium social media ad],
[iluminação: dramatic side lighting / soft natural],
[texturas reais para evitar "cara de IA"],
minimal and objective information density, modern ad layout, professional typography hierarchy, self-explanatory visual (must communicate without caption), 4:5 aspect ratio
```

> Respeitar design system quando disponível. Não gerar carrossel — 1 imagem por conceito, a menos que o usuário peça. Não usar criativos antigos da marca como referência de conteúdo.

---

## Notas Operacionais

```
1. Nunca pular Etapa 0 — SEM DESIGN SYSTEM = SLOP. Extrair de referências visuais se não existir
2. Nunca pular Etapa 1 — briefing ruim → criativo ruim. Perguntar antes de criar
3. Sempre gerar 10 conceitos com Creative Types diversos (mín. 6 tipos)
4. Cada conceito NASCE com 3 variações A/B de hook — sem variação é achismo
5. Foco no CLIENTE e sua dor — não na marca (a menos que seja household brand)
6. Pensar em CONVERSÃO — cada conceito deve ter caminho claro para ação
7. Validar limites: headline ≤90, texto principal ≤125, descrição ≤30
8. Hook Rate 30-50% é o benchmark — criar hooks que param o scroll
9. Evergreen > sazonal — criativos vencedores rodam 6-12 meses
10. Social validation é driver de conversão — criar ads que geram comentários
11. Criar sempre lote adicional em pasta nova; nunca sobrescrever lote anterior
12. Ignorar criativos antigos da marca como referência de conteúdo; usar apenas design system/brand assets quando explicitamente fornecidos
13. Variar Entity ID fortemente entre peças: layout, câmera, cor interna, textura, presença humana e elemento hero
14. Se imagens finais foram pedidas e não houver ferramenta de geração de imagem final, parar e avisar
15. Não aplicar headline/overlay depois da geração; o texto deve nascer integrado na imagem final
16. Toda headline exibida passa no teste do recorte em 1,7s: assunto explícito + dor/benefício/resultado, sem enigma
```

---

## Output HTML (Obrigatório em Lote Completo)

Em pedidos completos de criativos, gerar e salvar a página HTML do lote.

- Usar `Playbooks/template-criativos.html` quando existir no projeto atual
- Se `Playbooks/template-criativos.html` não existir, usar o template bundled `references/conceitos-meta-template.html`

### Regras do HTML

1. Substituir placeholders `{{CLIENTE}}`, `{{DATA}}`, `{{MARCA_1}}`, etc.
2. Preencher os 10 conceitos (cards), resumo executivo da peça, copy tables, visual concepts, Entity ID e adaptações
3. Header logo com link UTM: `https://gui.marketing/?utm_source=esc-skills&utm_medium=deliverable&utm_campaign=guimkt-meta-ads&utm_content=header-logo`
4. Footer com link UTM: `https://gui.marketing/?utm_source=esc-skills&utm_medium=deliverable&utm_campaign=guimkt-meta-ads&utm_content=footer`
5. Salvar como `{{batch_dir}}/conceitos-meta-{{CLIENTE}}.html`
6. Não sobrescrever HTML de lotes anteriores

---

## Deliverables Finais

| Arquivo | Descrição | Obrigatório |
|---------|-----------|-------------|
| `{{batch_dir}}/conceitos-meta-{{CLIENTE}}.md` | 10 conceitos direct response | ✅ Sim |
| `{{batch_dir}}/prompts-imagens-{{CLIENTE}}.md` | Prompts de imagem consolidados | ✅ Sim |
| `{{batch_dir}}/conceitos-meta-{{CLIENTE}}.html` | HTML para apresentação do lote | ✅ Sim |
| `{{batch_dir}}/imagens/` | Imagens finais 4:5 com headline/overlay/CTA integrados | ✅ Quando o pedido incluir peças/criativos visuais finais |

---

## ⚠️ Known Limitations

1. **Sem acesso à Meta Ads API:** Conceitos baseados no briefing — não consulta dados reais.
2. **Imagens finais dependem de ferramenta disponível:** se `generate_image` ou equivalente não estiver disponível, o agente deve parar e avisar em vez de simular assets finais.
3. **Limites de caracteres são guidelines gerais:** Validar na documentação oficial do Meta.
4. **Copy em PT-BR:** Campanhas em outros idiomas precisam de adaptação manual.
