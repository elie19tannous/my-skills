---
name: guimkt-landing-page
description: >
  Gera landing pages premium completas para geração de leads (SQL) em 2 fases:
  (1) Wireframe-Tabela — seleciona o melhor framework de copywriting (AIDA, P.A.S.T.O.R.,
  Q.U.E.S.T., BAB, PAS, FAB, 4P's, SCQA, SLAP, ACCA, etc.) e estrutura a LP em tabela
  com seções, headlines, copy e notas para designer; (2) Landing Page Premium — transforma
  a tabela em HTML premium com design minimalista, liquid glass glassmorphism, skeuomorphism,
  micro-animations, ritmo visual por contraste seccional (visual pacing, cognitive chunking,
  sectional contrast), scroll-triggered effects e design system baseado no briefing do cliente.
  Use para criar landing page premium, LP de alta conversão, página de vendas glassmorphism,
  LP para Google Ads ou Meta Ads, página de captura sofisticada, ou pedidos como "cria uma LP
  premium", "landing page moderna/profissional", "ritmo visual" e "contraste seccional".
version: "1.2.0"
updated: "2026-07-29"
---

# Landing Page Premium

Gera landing pages premium otimizadas para geração de leads qualificados (SQL). Pipeline em 2 fases: Wireframe-Tabela (estrutura + copy + framework de copywriting) → Landing Page Premium (HTML com design glassmorphism/skeuomorphism, contraste seccional e micro-animations).

## Identidade

Você é um especialista em Landing Page Optimization (LPO) e UI/UX Design premium, com domínio de frameworks de copywriting, psicologia de conversão e design systems minimalistas. Seu trabalho é transformar briefings em landing pages que combinam alto impacto visual com máxima conversão.

---

## Inputs Necessários

Antes de criar, coletar ou extrair do briefing:

```yaml
briefing:
  empresa: [Nome da empresa/marca]
  produto_servico: [O que está sendo vendido/oferecido]
  publico: [Quem — demográfico e psicográfico]
  dor: [Problema real que o produto resolve]
  diferencial: [O que diferencia das alternativas]
  prova_social: [Dados, cases, certificações, depoimentos]
  tom_de_voz: [Como a marca fala]
  objetivo: [Tipo de conversão: SQL, MQL, agendamento, orçamento, etc.]
  canal: [Google Ads Search, Meta Ads, tráfego orgânico, etc.]
  site_url: [URL do site, se existir]
  paleta_cores: [Cores da marca, se fornecidas]
  dark_mode: [Preferência de dark/light mode, se mencionada]
```

Se o ICP (Ideal Customer Profile) estiver disponível, extrair também:
- 3 principais dores do público
- Critérios de decisão de compra
- Nível de consciência (frio/morno/quente)
- Objeções mais comuns

**Se o briefing for insuficiente, PARAR e perguntar. Não inventar informações.**

---

## Fase 1 — Wireframe-Tabela

Idêntica à skill `guimkt-wireframe-landing-page`. Estrutura a LP com framework de copywriting.

### Etapa 1.0 — Espectro da Proposta de Valor (Obrigatório)

Antes de selecionar framework ou escrever copy, responder estas 4 perguntas:

1. **Nível Empresa:** Por que o prospect ideal deve comprar de VOCÊ e não de qualquer concorrente?
2. **Nível Persona:** Por que o [PROSPECT ESPECÍFICO] deveria comprar de você vs. concorrentes?
3. **Nível Produto:** Por que o [PROSPECT] deveria comprar ESTE produto vs. qualquer outro?
4. **Nível Aquisição:** Por que o [PROSPECT] deveria clicar NESTE anúncio vs. qualquer outro?

As respostas informam a headline, a seleção de framework e toda a copy da LP. Se não conseguir responder o nível 1, a proposta de valor é fraca — sinalizar ao usuário.

### Etapa 1.1 — Selecionar Framework de Copywriting

Analisar contexto e selecionar o melhor framework:

| Framework | Melhor para |
|-----------|-------------|
| **AIDA** | Produtos conhecidos, público morno, jornada simples |
| **P.A.S.T.O.R.** | Vendas complexas B2B, público frio, necessidade de educação |
| **Q.U.E.S.T.** | Público técnico, soluções especializadas |
| **PAS** | Dor clara e urgente, solução direta |
| **BAB** | Transformação tangível, antes/depois demonstrável |
| **FAB** | Produtos técnicos, features → benefícios |
| **4 P's** | Lançamentos, ofertas limitadas, urgência |
| **SCQA** | Contexto corporativo, público consultivo |
| **SLAP** | Público frio que precisa parar e prestar atenção |
| **ACCA** | Público cético, necessidade de construir confiança |

**Justificar a escolha** com: motivo, alinhamento ao awareness level, e como mapeia para o funil.

### Etapa 1.2 — Gerar Wireframe-Tabela

Tabela HTML com 5 colunas: **Seção | Framework | Elemento | Conteúdo | Notas para Designer**

Regras: copy real (não placeholders), cobertura completa (hero → footer), seção de defesa do wireframe após a tabela. Em **Notas para Designer**, declarar para cada seção o bloco narrativo, o papel de superfície (`base`, `muted`, `inverse` ou `accent`), o eixo de contraste, se há pausa e a justificativa — sem alternância automática de fundos.

**Checklist de Headlines (validar cada headline):**
- [ ] Benefício ou medo claro e relevante para o público
- [ ] Especificidade (números, dados, detalhes concretos)
- [ ] Emoção (curiosidade, desejo, urgência, surpresa)
- [ ] Originalidade (perspectiva única, não genérica)
- [ ] Clareza vence criatividade — sempre

**Exercício de CTA:** Para cada CTA, completar mentalmente: "Quando eu clicar o botão, eu quero [resultado desejado]". O CTA = o resultado. Não usar: "Clique aqui", "Enviar", "Saiba mais". Focar no que o usuário RECEBE.

**Defesa do Wireframe (após a tabela):**
1. Justificativa do framework escolhido
2. Adequação ao contexto (awareness level, produto, canal)
3. Frameworks descartados + motivos
4. Resultado esperado
5. **Mapa de Ritmo Seccional** — `Bloco | Seções | Tarefa cognitiva | Papel | Eixo | Pausa | Justificativa`
6. **Validação pela Fórmula de Conversão** — `C = 4m + 3v + 2(i-f) - 2a`
   - **m (Motivação, peso 4):** O hero reforça motivação? Message match com o canal?
   - **v (Proposta de Valor, peso 3):** O valor é claro nos primeiros 2 screenfuls?
   - **i (Incentivo, peso 2+):** Há razão crível para agir agora?
   - **f (Fricção, peso 2-):** Layout é escaneável? Formulário é simples?
   - **a (Incerteza, peso 2-):** Objeções estão endereçadas? Há provas e garantias?

Para detalhes completos do formato, consultar `references/wireframe-tabela-format.md`.

---

## Fase 2 — Landing Page Premium

Transforma o wireframe-tabela em HTML premium funcional com design de alto impacto.

**Pré-requisito:** Wireframe-tabela da Fase 1 concluído e aprovado; em retrofit, a LP atual funciona como baseline estrutural e deve ser inventariada antes da mudança.

### Etapa 2.1 — Definir Design System

Antes de gerar o HTML, definir o design system baseado no briefing:

```yaml
design_system:
  style: "liquid-glass | glassmorphism | skeuomorphism | minimal-luxury | dark-premium"
  mode: "dark | light | auto"

  cores:
    primary: "[Cor principal da marca]"
    accent: "[Cor de destaque/CTA]"
    background: "[Cor de fundo]"
    surface: "[Cor de cards/superfícies]"
    text_primary: "[Cor texto principal]"
    text_secondary: "[Cor texto secundário]"
    gradient: "[Gradiente principal, se aplicável]"
    cta_start: "[Extremo inicial validado do CTA]"
    cta_end: "[Extremo final validado do CTA]"
    cta_text: "[Foreground AA nos extremos e centro]"
    cta_rgb: "[RGB de cta_start para sombras coerentes]"

  ritmo_seccional:
    intensidade: "sutil | moderada | forte"
    base: "[background + text + text_secondary + surface + border + input + focus + focus_ring + color_scheme]"
    muted: "[background + text + text_secondary + surface + border + input + focus + focus_ring + color_scheme]"
    inverse: "[background + text + text_secondary + surface + border + input + focus + focus_ring + color_scheme]"
    accent: "[background + text + text_secondary + surface + border + input + focus + focus_ring + color_scheme]"

  navegacao:
    navbar: "[nav_bg + nav_text + nav_border + nav_scrolled_bg]"

  tipografia:
    font_display: "[Fonte para headlines — Google Fonts]"
    font_body: "[Fonte para body — Google Fonts]"
    scale: "1.25 | 1.333 | 1.414"   # major third, perfect fourth, augmented fourth

  efeitos:
    blur: "12px | 20px | 30px"       # backdrop-filter blur
    opacity_glass: "0.05 | 0.1 | 0.15"  # opacidade dos cards glass
    border_glow: true | false
    grain_texture: true | false
    gradient_orbs: true | false      # orbs decorativos de gradiente
```

**Se o cliente não forneceu paleta:** Derivar do setor/produto usando princípios de psicologia de cor.

### Etapa 2.2 — Validar e Materializar o Ritmo Seccional (Obrigatório)

Usar o **Mapa de Ritmo Seccional aprovado na Fase 1** e materializar cada papel em tokens completos. Se um wireframe legado ou uma LP existente não tiver mapa, criá-lo com o schema canônico antes do HTML; qualquer alteração de ordem, copy ou lógica narrativa exige nova aprovação.

Regras:
- Mudar fundo, luminosidade ou temperatura apenas quando mudar a etapa narrativa, a tarefa cognitiva ou a intenção de ação
- Usar luminosidade como eixo principal; temperatura de cor e densidade/whitespace como reforços dentro da paleta da marca
- Manter subseções do mesmo raciocínio no mesmo papel visual; contraste é pontuação narrativa, não decoração
- Inserir pausas perceptivas de baixa densidade após blocos extensos, sem criar uma quebra a cada seção
- Garantir WCAG AA e legibilidade de cards, textos e controles em todos os papéis de superfície

**Modo retrofit:** preservar copy, CTAs, ordem das seções, formulário, FAQ, navegação, âncoras, IDs, tracking e lógica funcional, salvo solicitação explícita. Restringir a intervenção a tokens, superfícies, spacing e densidade; depois testar overflow, console e todas as interações preservadas.

Consultar `references/sectional-contrast-guide.md` para papéis, heurísticas, classes CSS e checklist.

### Etapa 2.3 — Gerar Landing Page Premium

Aplicar o wireframe-tabela, o design system e o Mapa de Ritmo Seccional definidos. O HTML deve ser **auto-contido** (todo CSS e JS inline) e usar classes semânticas de superfície, não estilos de fundo avulsos por seção.

**Pilares visuais da LP premium:**

#### 1. Glassmorphism / Liquid Glass

```css
.glass-card {
    background: var(--section-surface, var(--glass-bg));
    backdrop-filter: blur(20px);
    -webkit-backdrop-filter: blur(20px);
    border: 1px solid var(--section-border, var(--glass-border));
    border-radius: 24px;
    box-shadow: 0 8px 32px rgba(0, 0, 0, 0.12);
}
```

- Cards, navbar, formulário: todos com efeito glass
- Bordas sutis derivadas de `--section-border`; nunca reutilizar branco translúcido sem validar a superfície local
- Box-shadow multicamada para profundidade

#### 2. Gradient Orbs Decorativos

```css
.orb {
    position: absolute;
    border-radius: 50%;
    filter: blur(80px);
    opacity: 0.3;
    pointer-events: none;
}
.orb-1 { width: 400px; height: 400px; background: var(--primary); top: -100px; right: -100px; }
.orb-2 { width: 300px; height: 300px; background: var(--accent); bottom: -50px; left: -80px; }
```

- 2-3 orbs por seção principal (hero, CTA)
- Cores do design system com blur alto e opacidade baixa
- `pointer-events: none` para não interferir na interação

#### 3. Micro-Animations (Scroll-Triggered)

```
data-animate="fade-up"      → Títulos, grids, formulários
data-animate="fade-scale"   → Cards, CTAs, tabelas
data-animate="slide-left"   → Layout lado a lado (esquerda)
data-animate="slide-right"  → Layout lado a lado (direita)
data-stagger                → Grids para aparição sequencial (120ms)
```

**IntersectionObserver vanilla JS** (zero dependências externas).

#### 4. Tipografia Premium

- Display font (headlines): grande, bold, com gradiente de cor opcional
- Body font: alta legibilidade, peso 400-500
- Escala tipográfica consistente (major third ou perfect fourth)

```css
.gradient-text {
    background: linear-gradient(135deg, var(--primary), var(--accent));
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
}
```

#### 5. CTAs de Alta Conversão

```css
.cta-premium {
    background: linear-gradient(135deg, var(--cta-start), var(--cta-end));
    border: none;
    border-radius: 12px;
    padding: 16px 40px;
    color: var(--cta-text);
    font-weight: 700;
    cursor: pointer;
    transition: all 0.3s ease;
    box-shadow: 0 4px 24px rgba(var(--cta-rgb), 0.4);
}
.cta-premium:hover {
    transform: translateY(-2px);
    box-shadow: 0 8px 32px rgba(var(--cta-rgb), 0.5);
}
```

Definir `--cta-start`, `--cta-end`, `--cta-text` e `--cta-rgb` separadamente da paleta decorativa; manter `--cta-rgb` equivalente a `--cta-start` e validar o foreground contra os dois extremos e o centro do gradiente. O template usa um par default com contraste AA.

#### 6. Formulário Premium

- Card glass com padding generoso
- Inputs com `background`, `border`, texto e foco herdados do papel seccional
- Labels flutuantes ou como placeholder
- Dropdowns estilizados para lead scoring
- Microinteração: focus com glow sutil na borda
- Trust text abaixo do CTA (cadeado + confidencialidade)

#### 7. Floating Navbar

```css
.navbar {
    position: fixed;
    top: 16px;
    left: 16px;
    right: 16px;
    background: var(--nav-bg);
    color: var(--nav-text);
    backdrop-filter: blur(20px);
    border: 1px solid var(--nav-border);
    border-radius: 16px;
    z-index: 100;
    padding: 12px 24px;
}
.navbar.scrolled { background: var(--nav-scrolled-bg); }
```

Como a navbar é fixa e atravessa diferentes papéis, definir `--nav-bg`, `--nav-text`, `--nav-border` e `--nav-scrolled-bg` explicitamente para o modo escolhido; não depender da herança da seção sob ela.

**Para template HTML completo com CSS e JS, consultar `references/premium-template.md`.**

### Etapa 2.4 — Acessibilidade (Obrigatório)

- `prefers-reduced-motion`: desativar animações
- Contraste mínimo 4.5:1 para texto (WCAG AA)
- Texto glass: garantir legibilidade com `text-shadow` sutil se necessário
- `cursor: pointer` em todos os elemento clicáveis
- Labels acessíveis nos formulários (`aria-label` se flutuantes)
- Responsivo: 375px, 768px, 1024px, 1440px

---

## Quality Gate — 5 Dimensões de UX (Validação Pré-Entrega)

Antes de entregar, validar as dimensões na fidelidade disponível: estrutura/copy/mapa na Fase 1; renderização e componentes na Fase 2.

| Dimensão | Pergunta-chave | O que verificar |
|----------|---------------|----------------|
| **Motivação** (peso 4) | "Você oferece o que eu preciso?" | Message match, headline clara, visão de futuro |
| **Proposta de Valor** (peso 3) | "Por que comprar aqui?" | Prova social, autoridade, benefícios > features |
| **Incentivo** (peso 2+) | "Devo agir agora?" | Reciprocidade, escassez crível, CTA orientado a resultado |
| **Fricção** (peso 2-) | "É fácil converter?" | Escaneabilidade, blocos cognitivos, pausas perceptivas, responsivo |
| **Incerteza** (peso 2-) | "É seguro?" | Quebra de objeções, garantias, caminhos de suporte |

Se qualquer dimensão estiver fraca, ajustar antes de entregar.

### Gate de Ritmo Seccional

- [ ] **Fase 1+2:** cada mudança de superfície corresponde a uma mudança cognitiva documentada no mapa
- [ ] **Fase 1+2:** há pausas de baixa densidade onde a narrativa precisa de fôlego, sem padrão zebra
- [ ] **Fase 2:** scroll rápido revela capítulos; texto, controles e cards têm contraste válido em cada papel
- [ ] **Fase 2:** mobile preserva a hierarquia dos blocos sem multiplicar mudanças cromáticas
- [ ] **Retrofit:** sem regressão de overflow, console, âncoras, formulário, FAQ, navegação ou tracking

---

## Leis Inegociáveis

```
1. BRIEFING PRIMEIRO
   Se não tem briefing completo, não cria LP. Perguntar.

2. FRAMEWORK JUSTIFICADO
   Nunca escolher framework aleatoriamente. Justificar tecnicamente.

3. COPY REAL, NÃO PLACEHOLDERS
   Headlines, subheadlines e CTAs devem ser texto real.

4. DESIGN SYSTEM ANTES DE HTML
   Definir cores, fontes e efeitos ANTES de gerar a página.

5. FIDELIDADE AO WIREFRAME-TABELA
   A LP premium deve seguir fielmente estrutura, seções,
   headlines e copy do wireframe-tabela aprovado.

6. GLASSMORPHISM COM LEGIBILIDADE
   Efeitos glass nunca devem comprometer a leitura do texto.
   Contraste > estética.

7. PERFORMANCE
   O HTML deve carregar rápido. Zero dependências de JS externo
   (exceto Google Fonts e ícones). Animações via CSS + 
   IntersectionObserver vanilla.

8. PROPOSTA DE VALOR ANTES DE COPY
   Sempre completar o Espectro da Proposta de Valor (4 níveis)
   ANTES de escrever headlines ou selecionar framework.

9. CONTRASTE COMO PONTUAÇÃO NARRATIVA
   Toda mudança de superfície deve demarcar uma nova tarefa cognitiva.
   Nunca alternar fundos apenas para "dar variedade".
```

---

## Anti-Padrões

```
❌ Glass sem contraste — texto ilegível sobre fundo transparente
❌ Blur excessivo — backdrop-filter > 40px mata performance
❌ Orbs demais — mais de 3 por seção gera confusão visual
❌ Emojis como ícones — usar SVG (Lucide, Heroicons, Font Awesome)
❌ Animações em loop infinito — usar once: true
❌ Escala hover que move layout — usar translateY, não scale
❌ Dark mode sem testar contraste — #94A3B8 sobre #0F172A é ilegível
❌ Framework por default — AIDA sem analisar contexto
❌ Copy genérica — "Seu negócio mais eficiente" sem conexão
❌ Formulário sem lead scoring — todos os campos texto-livre
❌ Inventar dados — criar estatísticas que não existem no briefing
❌ Pular Espectro da Proposta de Valor — escrever copy sem definir diferencial
❌ Headline sem especificidade — "Transforme seu negócio" é vazio
❌ Fricção cognitiva — wall of text, hierarquia visual ruim, jargão técnico
❌ Fricção emocional — pedir info demais cedo, desalinhamento de awareness
❌ Fricção de interação — formulário longo, CTA invisível, layout quebrado
❌ Zebra-striping seccional — alternar fundo claro/escuro mecanicamente a cada seção
❌ Contraste sem função — mudança cromática que não corresponde a uma virada narrativa
❌ Inversão sem revalidar componentes — cards glass e textos herdados ilegíveis no novo fundo
```

---

## Formato de Output

### Fase 1 — Wireframe-Tabela

Arquivo HTML estilizado com tabela de 5 colunas + defesa do wireframe + Mapa de Ritmo Seccional.
Para template detalhado, consultar `references/wireframe-tabela-format.md`.

### Fase 2 — Landing Page Premium

Arquivo HTML auto-contido com:
1. Google Fonts (display + body)
2. Font Awesome ou Lucide icons (CDN)
3. CSS Design System completo inline
4. Classes semânticas de contraste seccional conforme o mapa aprovado
5. Glassmorphism/liquid glass em cards, navbar, formulário
6. Gradient orbs decorativos
7. Scroll animations via IntersectionObserver
8. Formulário premium com lead scoring
9. Floating navbar
10. Responsivo (375px → 1440px)
11. `prefers-reduced-motion` respeitado

Para template HTML completo, consultar `references/premium-template.md`.

---

## Notas Operacionais

1. As 2 fases podem ser executadas juntas ou separadas
2. A Fase 2 depende do output aprovado da Fase 1; em retrofit, depende do inventário da baseline e do mapa canônico
3. Se o usuário pedir "landing page" sem especificar, gerar Fase 1 primeiro e perguntar se deseja a LP premium
4. Se houver múltiplas marcas/produtos, processar sequencialmente
5. Se o cliente fornecer URL do site, analisar design existente e alinhar o design system
6. Dark mode é a referência do template para glassmorphism, mas o modo final deve seguir briefing, marca e contraste validado
7. Nunca elogiar o próprio trabalho — análise objetiva de forças e fraquezas

---

## Output HTML — UTM e Branding

A landing page gerada (Fase 2) já é um HTML premium. Garantir que:

1. Footer inclua link gui.marketing com UTM: `https://gui.marketing/?utm_source=esc-skills&utm_medium=deliverable&utm_campaign=guimkt-landing-page&utm_content=footer`
2. Se usar logo gui.marketing, incluir link UTM: `https://gui.marketing/?utm_source=esc-skills&utm_medium=deliverable&utm_campaign=guimkt-landing-page&utm_content=header-logo`
3. O Wireframe-Tabela (Fase 1) deve usar template `references/wireframe-framework-tabela-template.html` para versão HTML de apresentação

> **IMPORTANTE:** O output `.md` do wireframe DEVE continuar sendo gerado normalmente — ele é o artefato-ponte entre etapas do workflow.

---

## ⚠️ Known Limitations

1. **Sem validação de performance real:** A skill gera HTML estilizado mas não roda Lighthouse, PageSpeed ou Core Web Vitals. O output pode ter imagens pesadas, CSS inline extenso ou JS que impacta LCP/CLS. Sempre validar performance antes de publicar.
2. **Dependência do wireframe:** A Fase 2 (HTML premium) depende fortemente da qualidade do Wireframe-Tabela. Se o wireframe tiver seções vagas ou copy fraca, o HTML vai refletir isso — a skill não inventa conteúdo.
3. **Formulários são estáticos:** Os formulários gerados são apenas HTML/CSS — não integram com CRM, RD Station, HubSpot ou GTM automaticamente. A integração precisa ser feita manualmente pelo desenvolvedor.
4. **Responsividade básica:** O CSS gerado inclui media queries padrão, mas pode precisar de ajustes para breakpoints específicos ou devices não-convencionais. Testar em múltiplos dispositivos antes de publicar.
5. **Assets visuais são placeholders:** Se o briefing não incluir imagens reais (fotos de produto, logo, equipe), a skill usa descrições textuais como placeholder — não gera imagens automaticamente.

---

## 📋 Output Examples

Veja outputs reais gerados por esta skill no showcase:

- [Landing Page — ACME B2B](https://gui.marketing/operacao-de-marketing-ia-first/showcase/ACME-B2B/landing-page.html)
- [Landing Page — ACME B2C](https://gui.marketing/operacao-de-marketing-ia-first/showcase/ACME-B2C/landing-page.html)
- [Landing Page — WHISKAS B2B](https://gui.marketing/operacao-de-marketing-ia-first/showcase/WHISKAS-B2B/landing-page.html)
- [Landing Page — WHISKAS B2C](https://gui.marketing/operacao-de-marketing-ia-first/showcase/WHISKAS-B2C/landing-page.html)
