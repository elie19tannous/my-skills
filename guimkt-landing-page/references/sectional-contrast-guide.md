# Ritmo Visual por Contraste Seccional

Guia transversal: a Fase 1 cria e aprova o mapa semântico; a Fase 2 o materializa em tokens e componentes. Contraste seccional funciona como pontuação narrativa: cria fôlego, sinaliza mudança de tarefa e ajuda o usuário a entender em que etapa da história está.

## Output Obrigatório da Fase 1: Mapa de Ritmo Seccional

Gerar na defesa do wireframe e reutilizar sem remapeamento silencioso na Fase 2:

| Bloco | Seções | Tarefa cognitiva | Papel | Eixo | Pausa | Justificativa |
|---|---|---|---|---|---|---|
| Promessa | Hero + trust bar | Reconhecer relevância | `base` | luminosidade + foco | não | Entrada contínua e direta |
| Diagnóstico | Dor + custo da inação | Reconhecer o problema | `muted` | luminosidade sutil | não | Agrupa o mesmo raciocínio |
| Virada | Mecanismo único | Entender a solução | `inverse` | inversão de luminosidade | sim | Marca a passagem de problema para solução |
| Evidência | Benefícios + provas | Reduzir incerteza | `base` | retorno à base | não | Retoma leitura detalhada |
| Ação | Oferta + formulário | Decidir e converter | `accent` | temperatura + foco | não | Isola a próxima ação sem chamar o formulário de pausa |

Os nomes e a quantidade de blocos devem seguir o framework e a extensão real da página. Não forçar cinco blocos quando a narrativa exigir menos ou mais.

## Papéis de Superfície

| Papel | Função | Uso típico |
|---|---|---|
| `base` | Ritmo principal de leitura | Hero, explicação central, conteúdo longo |
| `muted` | Separação suave sem interromper o fluxo | Diagnóstico, detalhes, grids de apoio |
| `inverse` | Virada narrativa forte | Novo mecanismo, antes/depois, prova decisiva |
| `accent` | Ênfase e preparação para ação | Pausa, oferta, CTA final, formulário |

Usar no máximo os papéis necessários. Uma LP curta pode funcionar apenas com `base`, `muted` e `accent`.

## Eixos de Contraste

1. **Luminosidade — eixo principal:** a mudança precisa continuar perceptível em escala de cinza.
2. **Temperatura — eixo secundário:** alternar entre neutro/frio/quente somente dentro da paleta da marca.
3. **Densidade — ritmo:** reduzir cards, colunas e elementos simultâneos nos pontos de pausa.
4. **Whitespace — fôlego:** ampliar espaçamento vertical para encerrar um bloco e preparar o seguinte.

Não usar cor como único sinal de significado. Texto normal deve manter contraste mínimo de 4.5:1 em cada superfície; componentes e estados de foco devem continuar distinguíveis.

## Regras de Decisão

1. Primeiro agrupar a copy por tarefa cognitiva; depois escolher as superfícies.
2. Manter seções que desenvolvem o mesmo argumento no mesmo papel visual.
3. Trocar de papel quando houver mudança clara de pergunta: “qual é o problema?” → “como funciona?” → “por que acreditar?” → “o que faço agora?”.
4. Após 2–4 seções densas, avaliar uma pausa de baixa densidade; não aplicar por contagem automática.
5. Usar uma dimensão dominante por transição. Luminosidade + temperatura + textura fortes ao mesmo tempo fragmentam a página.
6. Reservar o contraste mais forte para a virada narrativa ou para a ação principal, não para ambas repetidamente.
7. Revalidar texto, ícones, cards glass, bordas e formulário sempre que o papel mudar.

## Implementação Semântica

```css
:root {
    --section-base-bg: #0a0a0f;
    --section-base-text: #f1f5f9;
    --section-base-secondary: #94a3b8;
    --section-base-surface: rgba(255, 255, 255, 0.05);
    --section-base-border: rgba(255, 255, 255, 0.10);
    --section-base-input: rgba(255, 255, 255, 0.03);
    --section-base-focus: #818cf8;
    --section-base-focus-ring: rgba(129, 140, 248, 0.20);
    --section-base-color-scheme: dark;

    --section-muted-bg: #0f0f18;
    --section-muted-text: #f1f5f9;
    --section-muted-secondary: #a1aab8;
    --section-muted-surface: rgba(255, 255, 255, 0.04);
    --section-muted-border: rgba(255, 255, 255, 0.09);
    --section-muted-input: rgba(255, 255, 255, 0.03);
    --section-muted-focus: #818cf8;
    --section-muted-focus-ring: rgba(129, 140, 248, 0.20);
    --section-muted-color-scheme: dark;

    --section-inverse-bg: #f8fafc;
    --section-inverse-text: #0f172a;
    --section-inverse-secondary: #475569;
    --section-inverse-surface: rgba(15, 23, 42, 0.05);
    --section-inverse-border: rgba(15, 23, 42, 0.12);
    --section-inverse-input: rgba(15, 23, 42, 0.04);
    --section-inverse-focus: #4f46e5;
    --section-inverse-focus-ring: rgba(79, 70, 229, 0.18);
    --section-inverse-color-scheme: light;

    --section-accent-bg: #161026;
    --section-accent-text: #f8fafc;
    --section-accent-secondary: #c4b5fd;
    --section-accent-surface: rgba(255, 255, 255, 0.06);
    --section-accent-border: rgba(196, 181, 253, 0.20);
    --section-accent-input: rgba(255, 255, 255, 0.05);
    --section-accent-focus: #c4b5fd;
    --section-accent-focus-ring: rgba(196, 181, 253, 0.22);
    --section-accent-color-scheme: dark;
}

.section-tone {
    background: var(--section-bg, var(--section-base-bg));
    color: var(--section-text, var(--section-base-text));
    color-scheme: var(--section-color-scheme, dark);
}
.section-tone--base {
    --section-bg: var(--section-base-bg);
    --section-text: var(--section-base-text);
    --section-text-secondary: var(--section-base-secondary);
    --section-surface: var(--section-base-surface);
    --section-border: var(--section-base-border);
    --section-input-bg: var(--section-base-input);
    --section-focus: var(--section-base-focus);
    --section-focus-ring: var(--section-base-focus-ring);
    --section-color-scheme: var(--section-base-color-scheme);
}
.section-tone--muted {
    --section-bg: var(--section-muted-bg);
    --section-text: var(--section-muted-text);
    --section-text-secondary: var(--section-muted-secondary);
    --section-surface: var(--section-muted-surface);
    --section-border: var(--section-muted-border);
    --section-input-bg: var(--section-muted-input);
    --section-focus: var(--section-muted-focus);
    --section-focus-ring: var(--section-muted-focus-ring);
    --section-color-scheme: var(--section-muted-color-scheme);
}
.section-tone--inverse {
    --section-bg: var(--section-inverse-bg);
    --section-text: var(--section-inverse-text);
    --section-text-secondary: var(--section-inverse-secondary);
    --section-surface: var(--section-inverse-surface);
    --section-border: var(--section-inverse-border);
    --section-input-bg: var(--section-inverse-input);
    --section-focus: var(--section-inverse-focus);
    --section-focus-ring: var(--section-inverse-focus-ring);
    --section-color-scheme: var(--section-inverse-color-scheme);
}
.section-tone--accent {
    --section-bg: var(--section-accent-bg);
    --section-text: var(--section-accent-text);
    --section-text-secondary: var(--section-accent-secondary);
    --section-surface: var(--section-accent-surface);
    --section-border: var(--section-accent-border);
    --section-input-bg: var(--section-accent-input);
    --section-focus: var(--section-accent-focus);
    --section-focus-ring: var(--section-accent-focus-ring);
    --section-color-scheme: var(--section-accent-color-scheme);
}
.section-tone h1,
.section-tone h2,
.section-tone h3 { color: var(--section-text, var(--section-base-text)); }
.section-tone .section-sub { color: var(--section-text-secondary, var(--section-base-secondary)); }
.section-tone .glass-card {
    background: var(--section-surface);
    border-color: var(--section-border);
}
.section-tone :is(input, select, textarea) {
    background: var(--section-input-bg);
    color: var(--section-text);
    border-color: var(--section-border);
}
.section-tone :is(input, select, textarea):focus {
    border-color: var(--section-focus);
    outline-color: var(--section-focus);
    box-shadow: 0 0 0 3px var(--section-focus-ring);
}
.section-pause { padding-block: clamp(6rem, 10vw, 10rem); }
.section-pause > .container { max-width: 760px; }
```

```html
<section class="section-tone section-tone--muted" data-chapter="diagnostico">
    <!-- Seções do mesmo argumento podem compartilhar este papel -->
</section>

<section class="section-tone section-tone--inverse section-pause" data-chapter="mecanismo">
    <!-- Uma ideia dominante e menor densidade marcam a virada -->
</section>
```

As cores são exemplos. Derivar os tokens da marca e testar cada combinação; não copiar a paleta literalmente para todos os clientes.

## QA Pré-Entrega

- [ ] **Scroll rápido:** os capítulos são identificáveis sem ler todos os parágrafos
- [ ] **Teste de desfoque/squint:** as massas de fundo e pausas mostram hierarquia, não ruído
- [ ] **Escala de cinza:** as principais viradas continuam visíveis sem depender de matiz
- [ ] **Função narrativa:** cada troca de papel tem justificativa registrada no mapa
- [ ] **Sem zebra:** não há alternância mecânica entre toda seção adjacente
- [ ] **Acessibilidade:** texto, foco, bordas e controles passam em todos os papéis
- [ ] **Continuidade de marca:** a LP continua parecendo um único sistema visual
- [ ] **Mobile:** o ritmo permanece claro com menos colunas, menos decoração e espaçamento proporcional

## Anti-Padrões

- Fundo A/B/A/B aplicado por índice de seção
- Mudança de cor usada para compensar copy longa ou estrutura fraca
- Gradiente, orb ou divisor tratado como substituto de um novo bloco cognitivo
- Inversão forte em várias seções consecutivas, tornando tudo igualmente prioritário
- Pausa preenchida com grid denso, múltiplos CTAs ou animações concorrentes
- Card glass herdado do dark mode sobre superfície clara sem novos tokens de texto e borda
