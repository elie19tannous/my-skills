# Landing Page Premium — Template HTML

Template de referência para o HTML da Fase 2 (Landing Page Premium). O arquivo deve ser auto-contido: todo CSS e JS inline. Antes de aplicar as classes de superfície, reutilizar e validar o Mapa de Ritmo Seccional aprovado na Fase 1 conforme `sectional-contrast-guide.md`; os exemplos abaixo são semânticos e não prescrevem alternância por índice.

## Estrutura Completa

```html
<!DOCTYPE html>
<html lang="pt-BR">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>[MARCA] — [PROPOSTA DE VALOR CURTA]</title>
    <meta name="description" content="[Meta description com proposta de valor e CTA]">

    <!-- FONTS -->
    <link href="https://fonts.googleapis.com/css2?family=[DISPLAY_FONT]:wght@600;700;800&family=[BODY_FONT]:wght@400;500;600&display=swap" rel="stylesheet">

    <!-- ICONS -->
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.5.1/css/all.min.css">

    <!-- CSS inline (ver seção completa) -->
</head>
<body>
    <!-- FLOATING NAVBAR -->
    <nav class="navbar">
        <div class="navbar-inner">
            <span class="navbar-logo">[MARCA]</span>
            <a href="#form" class="navbar-cta">[CTA curto] →</a>
        </div>
    </nav>

    <!-- HERO -->
    <section class="hero section-tone section-tone--base" data-chapter="promessa">
        <div class="orb orb-1"></div>
        <div class="orb orb-2"></div>
        <div class="container">
            <div data-animate="fade-up">
                <span class="badge">[Badge de contexto]</span>
                <h1>[Headline com <span class="gradient-text">destaque gradiente</span>]</h1>
                <p class="hero-sub">[Subheadline de proposta de valor]</p>
                <a href="#form" class="cta-premium">[CTA] →</a>
            </div>
            <!-- Trust bar -->
            <div class="trust-bar" data-animate="fade-up">
                <div class="trust-item"><i class="fas fa-shield-alt"></i> [Trust 1]</div>
                <div class="trust-item"><i class="fas fa-check-circle"></i> [Trust 2]</div>
                <div class="trust-item"><i class="fas fa-star"></i> [Trust 3]</div>
            </div>
        </div>
    </section>

    <!-- SEÇÕES DO FRAMEWORK: atribuir o tom pelo mapa, nunca alternar automaticamente -->
    <section class="section-tone section-tone--muted" data-chapter="diagnostico">
        <div class="container">
            <h2 data-animate="fade-up">[Headline da seção]</h2>
            <p class="section-sub" data-animate="fade-up">[Subheadline]</p>
            <div class="cards-grid" data-animate="fade-up" data-stagger>
                <div class="glass-card">
                    <i class="fas fa-icon icon"></i>
                    <h3>[Título]</h3>
                    <p>[Descrição]</p>
                </div>
                <!-- mais cards -->
            </div>
        </div>
    </section>

    <!-- PAUSA / VIRADA NARRATIVA: baixa densidade e uma ideia dominante -->
    <section class="section-tone section-tone--inverse section-pause" data-chapter="mecanismo">
        <div class="container text-center">
            <span class="badge">[Virada narrativa]</span>
            <h2 data-animate="fade-up">[Uma ideia dominante que apresenta o mecanismo]</h2>
            <p class="section-sub text-center" data-animate="fade-up">[Explicação curta que prepara o próximo capítulo sem adicionar um novo grid.]</p>
        </div>
    </section>

    <!-- FORMULÁRIO -->
    <section id="form" class="section-form section-tone section-tone--accent" data-chapter="acao">
        <div class="orb orb-3"></div>
        <div class="container">
            <h2 class="text-center" data-animate="fade-up">[Headline do form]</h2>
            <p class="section-sub text-center" data-animate="fade-up">[Reforço de valor]</p>
            <div class="form-card glass-card" data-animate="fade-scale">
                <input type="text" placeholder="Seu nome completo">
                <input type="email" placeholder="Seu melhor e-mail">
                <input type="tel" placeholder="WhatsApp com DDD">
                <input type="text" placeholder="Nome da empresa">
                <select><option value="">Seu cargo</option><!-- opções --></select>
                <select><option value="">Segmento da empresa</option></select>
                <select><option value="">Principal desafio</option></select>
                <button class="cta-premium full-width">[CTA do form] →</button>
                <p class="form-trust"><i class="fas fa-lock" aria-hidden="true"></i> Seus dados são confidenciais. Respondemos em até 24h.</p>
            </div>
        </div>
    </section>

    <!-- FOOTER -->
    <footer class="footer">
        <div class="container">
            <p class="footer-logo">[MARCA]</p>
            <p class="footer-copy">© 2026 [MARCA] — Todos os direitos reservados</p>
        </div>
    </footer>

    <!-- SCROLL ANIMATIONS -->
    <script>
        document.addEventListener('DOMContentLoaded', () => {
            const els = document.querySelectorAll('[data-animate], [data-stagger]');
            if (window.matchMedia('(prefers-reduced-motion: reduce)').matches) {
                els.forEach(el => { el.style.opacity = '1'; });
                return;
            }
            const observer = new IntersectionObserver((entries) => {
                entries.forEach(entry => {
                    if (entry.isIntersecting) {
                        entry.target.classList.add('is-visible');
                        observer.unobserve(entry.target);
                    }
                });
            }, { threshold: 0.15, rootMargin: '0px 0px -40px 0px' });
            els.forEach(el => observer.observe(el));
        });

        // Smooth scroll
        document.querySelectorAll('a[href^="#"]').forEach(anchor => {
            anchor.addEventListener('click', function(e) {
                e.preventDefault();
                const target = document.querySelector(this.getAttribute('href'));
                if (target) target.scrollIntoView({ behavior: 'smooth', block: 'start' });
            });
        });

        // Navbar scroll effect
        window.addEventListener('scroll', () => {
            const navbar = document.querySelector('.navbar');
            if (window.scrollY > 50) {
                navbar.classList.add('scrolled');
            } else {
                navbar.classList.remove('scrolled');
            }
        });
    </script>
</body>
</html>
```

## CSS Design System Completo

```css
/* ══════════════════════════════════════════ */
/* CSS VARIABLES (design system tokens)      */
/* Adaptar às cores da marca do cliente      */
/* ══════════════════════════════════════════ */
:root {
    --primary: #6366f1;
    --primary-rgb: 99, 102, 241;
    --accent: #a855f7;
    --accent-rgb: 168, 85, 247;
    --cta-start: #4338ca;
    --cta-end: #7e22ce;
    --cta-text: #ffffff;
    --cta-rgb: 67, 56, 202;

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

    --bg: var(--section-base-bg);
    --bg-surface: rgba(255, 255, 255, 0.03);

    --text: var(--section-base-text);
    --text-secondary: var(--section-base-secondary);
    --text-muted: #64748b;

    --glass-bg: rgba(255, 255, 255, 0.05);
    --glass-border: rgba(255, 255, 255, 0.08);
    --glass-blur: 20px;
    --nav-bg: rgba(10, 10, 15, 0.72);
    --nav-text: #f1f5f9;
    --nav-border: rgba(255, 255, 255, 0.10);
    --nav-scrolled-bg: rgba(10, 10, 15, 0.90);

    --font-display: 'Inter Tight', sans-serif;
    --font-body: 'Inter', sans-serif;

    --radius-sm: 8px;
    --radius-md: 16px;
    --radius-lg: 24px;
    --radius-xl: 32px;

    --shadow-sm: 0 2px 8px rgba(0,0,0,0.2);
    --shadow-md: 0 8px 32px rgba(0,0,0,0.2);
    --shadow-lg: 0 16px 48px rgba(0,0,0,0.3);
    --shadow-glow: 0 4px 24px rgba(var(--primary-rgb), 0.3);
}

/* ═══ Light mode override ═══ */
/* Descomentar se o briefing pedir light mode */
/*
:root {
    --section-base-bg: #fafafa;
    --section-base-text: #0f172a;
    --section-base-secondary: #475569;
    --section-base-surface: rgba(255, 255, 255, 0.72);
    --section-base-border: rgba(15, 23, 42, 0.08);
    --section-base-input: rgba(15, 23, 42, 0.03);
    --section-base-focus: #4f46e5;
    --section-base-focus-ring: rgba(79, 70, 229, 0.18);
    --section-base-color-scheme: light;

    --section-muted-bg: #f1f5f9;
    --section-muted-text: #0f172a;
    --section-muted-secondary: #475569;
    --section-muted-surface: rgba(255, 255, 255, 0.72);
    --section-muted-border: rgba(15, 23, 42, 0.08);
    --section-muted-input: rgba(15, 23, 42, 0.03);
    --section-muted-focus: #4f46e5;
    --section-muted-focus-ring: rgba(79, 70, 229, 0.18);
    --section-muted-color-scheme: light;

    --section-inverse-bg: #0f172a;
    --section-inverse-text: #f8fafc;
    --section-inverse-secondary: #cbd5e1;
    --section-inverse-surface: rgba(255, 255, 255, 0.06);
    --section-inverse-border: rgba(255, 255, 255, 0.12);
    --section-inverse-input: rgba(255, 255, 255, 0.05);
    --section-inverse-focus: #818cf8;
    --section-inverse-focus-ring: rgba(129, 140, 248, 0.20);
    --section-inverse-color-scheme: dark;

    --section-accent-bg: #eef2ff;
    --section-accent-text: #1e1b4b;
    --section-accent-secondary: #4f46e5;
    --section-accent-surface: rgba(255, 255, 255, 0.72);
    --section-accent-border: rgba(79, 70, 229, 0.18);
    --section-accent-input: rgba(79, 70, 229, 0.05);
    --section-accent-focus: #4f46e5;
    --section-accent-focus-ring: rgba(79, 70, 229, 0.18);
    --section-accent-color-scheme: light;

    --bg-surface: rgba(0, 0, 0, 0.02);
    --text-muted: #64748b;
    --glass-bg: rgba(255, 255, 255, 0.7);
    --glass-border: rgba(0, 0, 0, 0.06);
    --nav-bg: rgba(250, 250, 250, 0.78);
    --nav-text: #0f172a;
    --nav-border: rgba(15, 23, 42, 0.10);
    --nav-scrolled-bg: rgba(250, 250, 250, 0.92);
}
*/

/* ═══ RESET ═══ */
* { margin: 0; padding: 0; box-sizing: border-box; }

body {
    font-family: var(--font-body);
    background: var(--bg);
    color: var(--text);
    line-height: 1.7;
    overflow-x: hidden;
}

h1, h2, h3, h4 {
    font-family: var(--font-display);
    font-weight: 700;
    line-height: 1.2;
    color: var(--text);
}
h1 { font-size: clamp(2.2rem, 5vw, 3.5rem); letter-spacing: -0.02em; }
h2 { font-size: clamp(1.6rem, 3.5vw, 2.5rem); letter-spacing: -0.01em; }
h3 { font-size: 1.25rem; }

.container { max-width: 1100px; margin: 0 auto; padding: 0 24px; }

/* ═══ GRADIENT TEXT ═══ */
.gradient-text {
    background: linear-gradient(135deg, var(--primary), var(--accent));
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
}

/* ═══ GLASSMORPHISM ═══ */
.glass-card {
    background: var(--section-surface, var(--glass-bg));
    backdrop-filter: blur(var(--glass-blur));
    -webkit-backdrop-filter: blur(var(--glass-blur));
    border: 1px solid var(--section-border, var(--glass-border));
    border-radius: var(--radius-lg);
    padding: 32px;
    box-shadow: var(--shadow-md);
    transition: all 0.3s ease;
}
.glass-card:hover {
    border-color: var(--section-focus, var(--primary));
    box-shadow: var(--shadow-lg), 0 0 0 1px var(--section-focus-ring, rgba(var(--primary-rgb), 0.15));
}

/* ═══ GRADIENT ORBS ═══ */
.orb {
    position: absolute;
    border-radius: 50%;
    filter: blur(80px);
    opacity: 0.25;
    pointer-events: none;
    will-change: transform;
}
.orb-1 { width: 400px; height: 400px; background: var(--primary); top: -100px; right: -100px; }
.orb-2 { width: 300px; height: 300px; background: var(--accent); bottom: -50px; left: -80px; }
.orb-3 { width: 350px; height: 350px; background: var(--primary); top: 50%; left: -120px; }

/* ═══ FLOATING NAVBAR ═══ */
.navbar {
    position: fixed;
    top: 16px; left: 16px; right: 16px;
    background: var(--nav-bg);
    color: var(--nav-text);
    backdrop-filter: blur(var(--glass-blur));
    -webkit-backdrop-filter: blur(var(--glass-blur));
    border: 1px solid var(--nav-border);
    border-radius: var(--radius-md);
    z-index: 100;
    padding: 12px 24px;
    transition: all 0.3s ease;
}
.navbar.scrolled {
    background: var(--nav-scrolled-bg);
    box-shadow: var(--shadow-md);
}
.navbar-inner {
    display: flex; align-items: center; justify-content: space-between;
    max-width: 1100px; margin: 0 auto;
}
.navbar-logo {
    font-family: var(--font-display); font-weight: 800;
    font-size: 1.1rem; color: var(--nav-text);
}
.navbar-cta {
    background: linear-gradient(135deg, var(--cta-start), var(--cta-end));
    color: var(--cta-text); padding: 8px 20px; border-radius: var(--radius-sm);
    text-decoration: none; font-weight: 600; font-size: 0.85rem;
    transition: all 0.3s;
}
.navbar-cta:hover { transform: translateY(-1px); box-shadow: var(--shadow-glow); }

/* ═══ HERO ═══ */
.hero {
    position: relative; padding: 140px 0 80px; overflow: hidden;
}
.hero-sub {
    font-size: 1.15rem; color: var(--section-text-secondary, var(--text-secondary));
    max-width: 560px; margin-bottom: 32px; line-height: 1.8;
}

/* ═══ BADGE ═══ */
.badge {
    display: inline-block; padding: 6px 16px; border-radius: 50px;
    background: var(--section-surface, transparent);
    border: 1px solid var(--section-focus, var(--primary));
    color: var(--section-text, var(--text)); font-size: 0.8rem; font-weight: 600;
    margin-bottom: 20px; letter-spacing: 0.5px;
}

/* ═══ CTA BUTTON ═══ */
.cta-premium {
    display: inline-block;
    background: linear-gradient(135deg, var(--cta-start), var(--cta-end));
    color: var(--cta-text); border: none; border-radius: var(--radius-sm);
    padding: 16px 40px; font-size: 1rem; font-weight: 700;
    cursor: pointer; text-decoration: none;
    transition: all 0.3s ease;
    box-shadow: 0 4px 24px rgba(var(--cta-rgb), 0.4);
    font-family: var(--font-body);
}
.cta-premium:hover {
    transform: translateY(-2px);
    box-shadow: 0 8px 32px rgba(var(--cta-rgb), 0.5);
}
.cta-premium.full-width { width: 100%; text-align: center; }

/* ═══ TRUST BAR ═══ */
.trust-bar {
    display: flex; gap: 24px; margin-top: 48px; flex-wrap: wrap;
}
.trust-item {
    display: flex; align-items: center; gap: 8px;
    color: var(--section-text-secondary, var(--text-muted)); font-size: 0.85rem;
}
.trust-item i { color: var(--section-focus, var(--primary)); }

/* ═══ SECTIONS ═══ */
section { padding: 100px 0; position: relative; overflow: hidden; }
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
.section-tone h3,
.section-tone h4 { color: var(--section-text); }
.section-tone .section-sub,
.section-tone .trust-item,
.section-tone .form-trust { color: var(--section-text-secondary); }
.section-pause { padding-block: clamp(6rem, 10vw, 10rem); }
.section-pause > .container { max-width: 760px; }
.section-sub {
    color: var(--section-text-secondary, var(--text-secondary)); font-size: 1.05rem;
    max-width: 600px; margin-bottom: 48px; line-height: 1.8;
}

/* ═══ CARDS GRID ═══ */
.cards-grid {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
    gap: 24px;
}

.icon {
    font-size: 28px; color: var(--section-focus, var(--primary)); margin-bottom: 16px;
    display: inline-block;
}

/* ═══ FORM ═══ */
.form-card { max-width: 520px; margin: 0 auto; }

input, textarea, select {
    font-family: var(--font-body);
    width: 100%; padding: 14px 18px; margin-bottom: 16px;
    background: var(--section-input-bg, var(--bg-surface));
    border: 1px solid var(--section-border, var(--glass-border));
    border-radius: var(--radius-sm);
    color: var(--section-text, var(--text)); font-size: 0.95rem;
    outline: none; transition: all 0.3s;
}
input::placeholder, textarea::placeholder { color: var(--section-text-secondary, var(--text-muted)); }
input:focus, textarea:focus, select:focus {
    border-color: var(--section-focus, var(--primary));
    box-shadow: 0 0 0 3px var(--section-focus-ring, rgba(var(--primary-rgb), 0.15));
}

select {
    appearance: auto;
    background-image: none;
    padding-right: 18px;
}

.form-trust {
    text-align: center; font-size: 0.8rem;
    color: var(--text-muted); margin-top: 16px;
}

/* ═══ FOOTER ═══ */
.footer {
    padding: 40px 0; text-align: center;
    border-top: 1px solid var(--glass-border);
}
.footer-logo {
    font-family: var(--font-display); font-weight: 800;
    font-size: 1.2rem; margin-bottom: 8px; color: var(--text);
}
.footer-copy { font-size: 0.8rem; color: var(--text-muted); }

/* ═══ UTILITIES ═══ */
.text-center { text-align: center; }

/* ═══ SCROLL ANIMATIONS ═══ */
@keyframes fadeInUp {
    from { opacity: 0; transform: translateY(40px); }
    to { opacity: 1; transform: translateY(0); }
}
@keyframes fadeInScale {
    from { opacity: 0; transform: scale(0.92); }
    to { opacity: 1; transform: scale(1); }
}
@keyframes slideInLeft {
    from { opacity: 0; transform: translateX(-40px); }
    to { opacity: 1; transform: translateX(0); }
}
@keyframes slideInRight {
    from { opacity: 0; transform: translateX(40px); }
    to { opacity: 1; transform: translateX(0); }
}

[data-animate] { opacity: 0; }
[data-animate].is-visible {
    animation-fill-mode: both;
    animation-duration: 0.8s;
    animation-timing-function: cubic-bezier(0.22, 1, 0.36, 1);
}
[data-animate="fade-up"].is-visible    { animation-name: fadeInUp; }
[data-animate="fade-scale"].is-visible { animation-name: fadeInScale; }
[data-animate="slide-left"].is-visible { animation-name: slideInLeft; }
[data-animate="slide-right"].is-visible{ animation-name: slideInRight; }

/* Stagger */
[data-stagger]>*:nth-child(1) { --delay: 0s; }
[data-stagger]>*:nth-child(2) { --delay: 0.12s; }
[data-stagger]>*:nth-child(3) { --delay: 0.24s; }
[data-stagger]>*:nth-child(4) { --delay: 0.36s; }
[data-stagger]>*:nth-child(5) { --delay: 0.48s; }
[data-stagger]>*:nth-child(6) { --delay: 0.6s; }
[data-stagger].is-visible>* {
    animation: fadeInUp 0.6s cubic-bezier(0.22, 1, 0.36, 1) both;
    animation-delay: var(--delay, 0s);
}
[data-stagger]>* { opacity: 0; }

/* ═══ REDUCED MOTION ═══ */
@media (prefers-reduced-motion: reduce) {
    *, *::before, *::after {
        animation-duration: 0.01ms !important;
        transition-duration: 0.01ms !important;
    }
    [data-animate] { opacity: 1 !important; }
    [data-stagger]>* { opacity: 1 !important; }
}

/* ═══ RESPONSIVE ═══ */
@media (max-width: 768px) {
    section { padding: 64px 0; }
    .hero { padding: 120px 0 60px; }
    .cards-grid { grid-template-columns: 1fr; }
    .trust-bar { flex-direction: column; gap: 12px; }
    .cta-premium { width: 100%; text-align: center; }
    .navbar { top: 8px; left: 8px; right: 8px; padding: 10px 16px; }
    .orb { display: none; }  /* Hide orbs on mobile for performance */
}

@media (max-width: 480px) {
    h1 { font-size: 1.8rem; }
    .glass-card { padding: 20px; }
}
```

## Componentes de Referência

### Glass Card com Ícone

```html
<div class="glass-card">
    <i class="fas fa-shield-alt icon"></i>
    <h3>[Título]</h3>
    <p>[Descrição com copy real do wireframe-tabela]</p>
</div>
```

### Gradient Text em Headline

```html
<h1>Pare de perder leads com <span class="gradient-text">páginas genéricas</span></h1>
```

### Badge de Contexto

```html
<span class="badge">[Marca] · [Produto/Serviço]</span>
```

### Seção com Orbs

```html
<section class="section-tone section-tone--muted" data-chapter="diagnostico">
    <div class="orb orb-2"></div>
    <div class="container">
        <h2 data-animate="fade-up">[Headline]</h2>
        <!-- conteúdo -->
    </div>
</section>
```

### Continuidade de Capítulo + Virada Narrativa

```html
<!-- As duas primeiras seções compartilham tarefa cognitiva e superfície -->
<section class="section-tone section-tone--muted" data-chapter="diagnostico">...</section>
<section class="section-tone section-tone--muted" data-chapter="diagnostico">...</section>

<!-- A inversão marca a passagem de problema para mecanismo -->
<section class="section-tone section-tone--inverse section-pause" data-chapter="mecanismo">...</section>
```

Não alternar `base`/`muted`/`inverse` por posição. O `data-chapter` e o papel de superfície devem corresponder ao mapa aprovado.

### Grid com Stagger

```html
<div class="cards-grid" data-animate="fade-up" data-stagger>
    <div class="glass-card">...</div>
    <div class="glass-card">...</div>
    <div class="glass-card">...</div>
</div>
```

## Design System — Paletas de Referência

Usar quando o cliente não fornecer paleta de cores:

As cores de marca abaixo são pontos de partida. Para botões, derivar `--cta-start`, `--cta-end`, `--cta-text` e `--cta-rgb` (equivalente a `--cta-start`) e validar contraste mínimo de 4.5:1 nos dois extremos e no centro do gradiente.

### Dark Mode (Default)

| Setor | Primary | Accent | Background |
|-------|---------|--------|------------|
| **Tech/SaaS** | `#6366f1` (indigo) | `#a855f7` (purple) | `#0a0a0f` |
| **Fintech** | `#06b6d4` (cyan) | `#3b82f6` (blue) | `#0a0f1a` |
| **Saúde** | `#10b981` (emerald) | `#6ee7b7` (mint) | `#0a0f12` |
| **Educação** | `#f59e0b` (amber) | `#f97316` (orange) | `#0f0a05` |
| **Arquitetura** | `#f1f5f9` (slate) | `#d4a853` (gold) | `#0a0a0a` |
| **Jurídico** | `#1e40af` (blue) | `#3b82f6` (blue) | `#050a15` |
| **Varejo** | `#ef4444` (red) | `#f97316` (orange) | `#0f0505` |

### Light Mode

| Setor | Primary | Accent | Background |
|-------|---------|--------|------------|
| **Tech/SaaS** | `#4f46e5` (indigo) | `#7c3aed` (violet) | `#fafafa` |
| **Beleza/Spa** | `#ec4899` (pink) | `#d946ef` (fuchsia) | `#fdf2f8` |
| **Saúde** | `#059669` (emerald) | `#10b981` (green) | `#f0fdf4` |
| **Consultoria** | `#1e40af` (blue) | `#6366f1` (indigo) | `#f8fafc` |

## Ícones Sugeridos (Font Awesome)

| Contexto | Ícone |
|----------|-------|
| Dor/problema | `fa-exclamation-triangle`, `fa-times-circle` |
| Benefício | `fa-check-circle`, `fa-chart-line`, `fa-shield-alt` |
| Dinheiro | `fa-dollar-sign`, `fa-coins` |
| Tempo | `fa-clock`, `fa-hourglass` |
| Segurança | `fa-lock`, `fa-shield-alt` |
| Pessoas | `fa-users`, `fa-user-tie` |
| Processo | `fa-cogs`, `fa-sitemap`, `fa-project-diagram` |
| Suporte | `fa-headset`, `fa-life-ring` |
| Crescimento | `fa-rocket`, `fa-chart-bar`, `fa-arrow-up` |

## Checklist de Ritmo Seccional

- [ ] Scroll rápido/full-page revela capítulos sem depender da leitura da copy
- [ ] Cada mudança de tom corresponde a uma virada registrada no mapa
- [ ] Headings, textos secundários, cards, inputs, bordas e foco usam tokens do papel local
- [ ] Não há padrão zebra nem mais papéis visuais do que a narrativa exige
- [ ] As viradas permanecem perceptíveis e acessíveis em 375px, 768px, 1024px e 1440px
