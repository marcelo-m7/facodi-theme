#!/usr/bin/env python3
"""Idempotently rebuild the FACODI public editorial shell after a DB reset.

Run in an Odoo shell after `theme_facodi` and `facodi_learning` are installed:

    odoo shell -d facodi < theme_facodi/scripts/recover_editorial_pages.py

This is an explicit disaster-recovery helper. It is not imported by the module and
therefore does not violate the theme rule that normal install/upgrade must not
create editor-owned website.page records.
"""

from odoo import SUPERUSER_ID

WEBSITE_ID = 1
LANGS = ("en_GB", "pt_PT", "es_ES", "fr_FR")


def _upsert_view(key, name, arch):
    View = env["ir.ui.view"].sudo().with_context(lang="en_GB")
    view = View.search([("key", "=", key), ("website_id", "in", [False, WEBSITE_ID])], limit=1)
    vals = {
        "name": name,
        "key": key,
        "type": "qweb",
        "arch_db": arch,
        "website_id": WEBSITE_ID,
        "active": True,
    }
    if view:
        view.write(vals)
    else:
        view = View.create(vals)
    return view


def _upsert_page(url, name, view):
    Page = env["website.page"].sudo().with_context(lang="en_GB")
    page = Page.search([("url", "=", url), ("website_id", "=", WEBSITE_ID)], limit=1)
    vals = {
        "name": name,
        "url": url,
        "view_id": view.id,
        "website_id": WEBSITE_ID,
        "is_published": True,
        "active": True,
    }
    if page:
        page.write(vals)
    else:
        page = Page.create(vals)
    return page


def _set_translation(view, lang, name, arch):
    view.with_context(lang=lang).write({"name": name, "arch_db": arch})


website = env["website"].sudo().browse(WEBSITE_ID).exists()
if not website:
    raise RuntimeError("FACODI website record not found")
website.write({"name": "FACODI"})

homepage = env["ir.ui.view"].sudo().browse(611).exists()
if not homepage:
    homepage = env["ir.ui.view"].sudo().search(
        [("key", "=", "website.homepage"), ("website_id", "=", WEBSITE_ID)],
        limit=1,
    )
if not homepage:
    raise RuntimeError("Website homepage view not found")
homepage.write(
    {
        "arch_db": """<t name="Homepage" t-name="website.homepage">
  <t t-call="website.layout" pageName.f="homepage">
    <t t-call="theme_facodi.new_page_template_sections_facodi_home"/>
  </t>
</t>"""
    }
)

about_template = env.ref("theme_facodi.new_page_template_sections_facodi_about")
about_body = about_template.with_context(lang="en_GB").arch_db.strip()
if "t-snippet-call" in about_body:
    raise RuntimeError("FACODI About recovery requires a static, runtime-safe composition")
if 'id="wrap"' not in about_body:
    raise RuntimeError("FACODI About recovery composition must own the Website wrap")

about = _upsert_view(
    "website.facodi_about",
    "About FACODI",
    """<t name="About FACODI" t-name="website.facodi_about">
  <t t-call="website.layout">
%s
  </t>
</t>""" % about_body,
)
_upsert_page("/about", "About FACODI", about)

PAGES = {
    "/academic-model": {
        "key": "website.facodi_academic_model",
        "en_GB": (
            "FACODI Academic Model",
            """<t name="FACODI Academic Model" t-name="website.facodi_academic_model"><t t-call="website.layout"><div id="wrap" class="oe_structure"><section class="facodi-section facodi-grid-paper"><div class="container"><div class="facodi-sheet"><p class="facodi-kicker">FACODI · Academic model</p><h1><span class="facodi-highlight">Official curricular context + open learning resources.</span></h1><p class="facodi-lead">FACODI connects official curriculum references with open courses, videos and community resources while keeping the academic boundary explicit.</p><h2>How the model works</h2><ul><li><strong>Curriculum references</strong> preserve institutional facts such as curricular year, semester, ECTS and option groups.</li><li><strong>FACODI courses</strong> use Odoo eLearning as the canonical learning structure.</li><li><strong>Coverage evidence</strong> records whether an open course supports a curricular unit and how confident that mapping is.</li><li><strong>Community contributions</strong> remain separate from publication until reviewed.</li></ul><div class="facodi-highlighter-callout"><strong>Academic boundary:</strong> content correspondence is not academic equivalence, credit recognition or a substitute for the official programme.</div><p><a class="btn btn-primary" href="/roadmaps">Explore roadmaps</a> <a class="btn btn-outline-primary" href="/curricular-units">Browse curricular units</a></p></div></div></section></div></t></t>""",
        ),
        "pt_PT": (
            "Modelo Académico FACODI",
            """<t name="Modelo Académico FACODI" t-name="website.facodi_academic_model"><t t-call="website.layout"><div id="wrap" class="oe_structure"><section class="facodi-section facodi-grid-paper"><div class="container"><div class="facodi-sheet"><p class="facodi-kicker">FACODI · Modelo académico</p><h1><span class="facodi-highlight">Contexto curricular oficial + recursos de aprendizagem abertos.</span></h1><p class="facodi-lead">A FACODI liga referências curriculares oficiais a cursos, vídeos e recursos comunitários abertos, mantendo explícita a fronteira académica.</p><h2>Como funciona</h2><ul><li><strong>Referências curriculares</strong> preservam factos institucionais como ano curricular, semestre, ECTS e grupos de opção.</li><li><strong>Cursos FACODI</strong> usam o eLearning standard do Odoo como estrutura canónica.</li><li><strong>Evidência de cobertura</strong> regista se um curso aberto apoia uma unidade curricular e com que nível de confiança.</li><li><strong>Contribuições da comunidade</strong> permanecem separadas da publicação até serem revistas.</li></ul><div class="facodi-highlighter-callout"><strong>Fronteira académica:</strong> correspondência de conteúdo não é equivalência académica, reconhecimento de créditos nem substituição do programa oficial.</div><p><a class="btn btn-primary" href="/roadmaps">Explorar percursos</a> <a class="btn btn-outline-primary" href="/curricular-units">Ver unidades curriculares</a></p></div></div></section></div></t></t>""",
        ),
        "es_ES": (
            "Modelo académico FACODI",
            """<t name="Modelo académico FACODI" t-name="website.facodi_academic_model"><t t-call="website.layout"><div id="wrap" class="oe_structure"><section class="facodi-section facodi-grid-paper"><div class="container"><div class="facodi-sheet"><p class="facodi-kicker">FACODI · Modelo académico</p><h1><span class="facodi-highlight">Contexto curricular oficial + recursos de aprendizaje abiertos.</span></h1><p class="facodi-lead">FACODI conecta referencias curriculares oficiales con cursos, vídeos y recursos comunitarios abiertos, manteniendo explícita la frontera académica.</p><h2>Cómo funciona</h2><ul><li><strong>Referencias curriculares</strong> conservan datos institucionales como curso, semestre, ECTS y grupos optativos.</li><li><strong>Cursos FACODI</strong> usan eLearning estándar de Odoo como estructura canónica.</li><li><strong>Evidencia de cobertura</strong> registra si un curso abierto apoya una unidad curricular y con qué nivel de confianza.</li><li><strong>Contribuciones de la comunidad</strong> permanecen separadas de la publicación hasta ser revisadas.</li></ul><div class="facodi-highlighter-callout"><strong>Frontera académica:</strong> la correspondencia de contenido no es equivalencia académica, reconocimiento de créditos ni sustitución del programa oficial.</div></div></div></section></div></t></t>""",
        ),
        "fr_FR": (
            "Modèle académique FACODI",
            """<t name="Modèle académique FACODI" t-name="website.facodi_academic_model"><t t-call="website.layout"><div id="wrap" class="oe_structure"><section class="facodi-section facodi-grid-paper"><div class="container"><div class="facodi-sheet"><p class="facodi-kicker">FACODI · Modèle académique</p><h1><span class="facodi-highlight">Contexte curriculaire officiel + ressources d’apprentissage ouvertes.</span></h1><p class="facodi-lead">FACODI relie des références curriculaires officielles à des cours, vidéos et ressources communautaires ouvertes tout en rendant explicite la frontière académique.</p><div class="facodi-highlighter-callout"><strong>Frontière académique :</strong> une correspondance de contenu n’est ni une équivalence académique, ni une reconnaissance de crédits.</div></div></div></section></div></t></t>""",
        ),
    },
    "/infrastructure": {
        "key": "website.facodi_infrastructure",
        "en_GB": ("FACODI Technical Infrastructure", """<t name="FACODI Technical Infrastructure" t-name="website.facodi_infrastructure"><t t-call="website.layout"><div id="wrap" class="oe_structure"><section class="facodi-section facodi-grid-paper"><div class="container"><div class="facodi-sheet"><p class="facodi-kicker">Open infrastructure</p><h1><span class="facodi-highlight">A standard-first stack built to remain understandable.</span></h1><p class="facodi-lead">FACODI uses Odoo 19 Community for Website, eLearning and canonical editorial records, with Supabase Edge Functions for resource-analysis pipelines.</p><ul><li>Odoo 19 Community</li><li>Supabase analysis pipelines</li><li>GitHub versioned addons and deployment contracts</li><li>Containerized reproducible deployment</li></ul></div></div></section></div></t></t>"""),
        "pt_PT": ("Infraestrutura Técnica FACODI", """<t name="Infraestrutura Técnica FACODI" t-name="website.facodi_infrastructure"><t t-call="website.layout"><div id="wrap" class="oe_structure"><section class="facodi-section facodi-grid-paper"><div class="container"><div class="facodi-sheet"><p class="facodi-kicker">Infraestrutura aberta</p><h1><span class="facodi-highlight">Uma stack standard-first feita para continuar compreensível.</span></h1><p class="facodi-lead">A FACODI utiliza Odoo 19 Community para Website, eLearning e registos editoriais canónicos, com Supabase Edge Functions para pipelines de análise de recursos.</p><ul><li>Odoo 19 Community</li><li>Pipelines de análise Supabase</li><li>Addons e contratos de deployment versionados no GitHub</li><li>Deployment reproduzível em contentores</li></ul></div></div></section></div></t></t>"""),
        "es_ES": ("Infraestructura técnica FACODI", """<t name="Infraestructura técnica FACODI" t-name="website.facodi_infrastructure"><t t-call="website.layout"><div id="wrap" class="oe_structure"><section class="facodi-section facodi-grid-paper"><div class="container"><div class="facodi-sheet"><p class="facodi-kicker">Infraestructura abierta</p><h1><span class="facodi-highlight">Una arquitectura standard-first diseñada para seguir siendo comprensible.</span></h1><p>FACODI utiliza Odoo 19 Community y Supabase Edge Functions con componentes versionados en GitHub.</p></div></div></section></div></t></t>"""),
        "fr_FR": ("Infrastructure technique FACODI", """<t name="Infrastructure technique FACODI" t-name="website.facodi_infrastructure"><t t-call="website.layout"><div id="wrap" class="oe_structure"><section class="facodi-section facodi-grid-paper"><div class="container"><div class="facodi-sheet"><p class="facodi-kicker">Infrastructure ouverte</p><h1><span class="facodi-highlight">Une architecture standard-first conçue pour rester compréhensible.</span></h1><p>FACODI utilise Odoo 19 Community et Supabase Edge Functions avec des composants versionnés sur GitHub.</p></div></div></section></div></t></t>"""),
    },
    "/about-marcelo": {
        "key": "website.facodi_about_marcelo",
        "en_GB": ("Marcelo Santos — FACODI", """<t name="Marcelo Santos — FACODI" t-name="website.facodi_about_marcelo"><t t-call="website.layout"><div id="wrap" class="oe_structure"><section class="facodi-section facodi-grid-paper"><div class="container"><div class="facodi-sheet"><p class="facodi-kicker">Project author</p><h1><span class="facodi-highlight">Marcelo Santos</span></h1><p class="facodi-lead">Creator and technical architect of FACODI, working across software engineering, open education, Odoo platforms and community-built digital infrastructure.</p><p><a class="btn btn-primary" href="https://github.com/marcelo-m7" target="_blank" rel="noopener noreferrer">GitHub</a></p></div></div></section></div></t></t>"""),
        "pt_PT": ("Marcelo Santos — FACODI", """<t name="Marcelo Santos — FACODI" t-name="website.facodi_about_marcelo"><t t-call="website.layout"><div id="wrap" class="oe_structure"><section class="facodi-section facodi-grid-paper"><div class="container"><div class="facodi-sheet"><p class="facodi-kicker">Autor do projeto</p><h1><span class="facodi-highlight">Marcelo Santos</span></h1><p class="facodi-lead">Criador e arquiteto técnico da FACODI, atuando entre engenharia de software, educação aberta, plataformas Odoo e infraestrutura digital construída em comunidade.</p><p><a class="btn btn-primary" href="https://github.com/marcelo-m7" target="_blank" rel="noopener noreferrer">GitHub</a></p></div></div></section></div></t></t>"""),
        "es_ES": ("Marcelo Santos — FACODI", """<t name="Marcelo Santos — FACODI" t-name="website.facodi_about_marcelo"><t t-call="website.layout"><div id="wrap" class="oe_structure"><section class="facodi-section facodi-grid-paper"><div class="container"><div class="facodi-sheet"><p class="facodi-kicker">Autor del proyecto</p><h1><span class="facodi-highlight">Marcelo Santos</span></h1><p>Creador y arquitecto técnico de FACODI.</p></div></div></section></div></t></t>"""),
        "fr_FR": ("Marcelo Santos — FACODI", """<t name="Marcelo Santos — FACODI" t-name="website.facodi_about_marcelo"><t t-call="website.layout"><div id="wrap" class="oe_structure"><section class="facodi-section facodi-grid-paper"><div class="container"><div class="facodi-sheet"><p class="facodi-kicker">Auteur du projet</p><h1><span class="facodi-highlight">Marcelo Santos</span></h1><p>Créateur et architecte technique de FACODI.</p></div></div></section></div></t></t>"""),
    },
    "/about-ualg": {
        "key": "website.facodi_about_ualg",
        "en_GB": ("University of the Algarve and FACODI", """<t name="University of the Algarve and FACODI" t-name="website.facodi_about_ualg"><t t-call="website.layout"><div id="wrap" class="oe_structure"><section class="facodi-section facodi-grid-paper"><div class="container"><div class="facodi-sheet"><p class="facodi-kicker">Curricular context</p><h1><span class="facodi-highlight">University of the Algarve (UAlg)</span></h1><p class="facodi-lead">FACODI uses official UAlg curriculum references as structured academic context. It is complementary and does not replace official university systems, teaching, assessment or academic recognition.</p><p><a class="btn btn-primary" href="/roadmaps">Explore the LESTI roadmap</a></p></div></div></section></div></t></t>"""),
        "pt_PT": ("Universidade do Algarve e FACODI", """<t name="Universidade do Algarve e FACODI" t-name="website.facodi_about_ualg"><t t-call="website.layout"><div id="wrap" class="oe_structure"><section class="facodi-section facodi-grid-paper"><div class="container"><div class="facodi-sheet"><p class="facodi-kicker">Contexto curricular</p><h1><span class="facodi-highlight">Universidade do Algarve (UAlg)</span></h1><p class="facodi-lead">A FACODI utiliza referências curriculares oficiais da UAlg como contexto académico estruturado. É complementar e não substitui sistemas oficiais, ensino, avaliação ou reconhecimento académico.</p><p><a class="btn btn-primary" href="/roadmaps">Explorar o percurso LESTI</a></p></div></div></section></div></t></t>"""),
        "es_ES": ("Universidad del Algarve y FACODI", """<t name="Universidad del Algarve y FACODI" t-name="website.facodi_about_ualg"><t t-call="website.layout"><div id="wrap" class="oe_structure"><section class="facodi-section facodi-grid-paper"><div class="container"><div class="facodi-sheet"><p class="facodi-kicker">Contexto curricular</p><h1><span class="facodi-highlight">Universidad del Algarve (UAlg)</span></h1><p>FACODI utiliza referencias curriculares oficiales de la UAlg como contexto académico estructurado.</p></div></div></section></div></t></t>"""),
        "fr_FR": ("Université de l’Algarve et FACODI", """<t name="Université de l’Algarve et FACODI" t-name="website.facodi_about_ualg"><t t-call="website.layout"><div id="wrap" class="oe_structure"><section class="facodi-section facodi-grid-paper"><div class="container"><div class="facodi-sheet"><p class="facodi-kicker">Contexte curriculaire</p><h1><span class="facodi-highlight">Université de l’Algarve (UAlg)</span></h1><p>FACODI utilise les références curriculaires officielles de l’UAlg comme contexte académique structuré.</p></div></div></section></div></t></t>"""),
    },
    "/accessibility": {
        "key": "website.facodi_accessibility",
        "en_GB": ("Accessibility Statement", """<t name="Accessibility Statement" t-name="website.facodi_accessibility"><t t-call="website.layout"><div id="wrap" class="oe_structure"><section class="facodi-section facodi-grid-paper"><div class="container"><div class="facodi-sheet"><p class="facodi-kicker">Accessibility</p><h1><span class="facodi-highlight">Learning should remain reachable.</span></h1><p>FACODI continuously improves keyboard navigation, semantics, visible focus, colour contrast and reduced-motion behaviour.</p></div></div></section></div></t></t>"""),
        "pt_PT": ("Declaração de Acessibilidade", """<t name="Declaração de Acessibilidade" t-name="website.facodi_accessibility"><t t-call="website.layout"><div id="wrap" class="oe_structure"><section class="facodi-section facodi-grid-paper"><div class="container"><div class="facodi-sheet"><p class="facodi-kicker">Acessibilidade</p><h1><span class="facodi-highlight">Aprender deve continuar ao alcance de todos.</span></h1><p>A FACODI melhora continuamente navegação por teclado, semântica, foco visível, contraste e movimento reduzido.</p></div></div></section></div></t></t>"""),
        "es_ES": ("Declaración de accesibilidad", """<t name="Declaración de accesibilidad" t-name="website.facodi_accessibility"><t t-call="website.layout"><div id="wrap" class="oe_structure"><section class="facodi-section facodi-grid-paper"><div class="container"><div class="facodi-sheet"><p class="facodi-kicker">Accesibilidad</p><h1><span class="facodi-highlight">Aprender debe seguir al alcance de todos.</span></h1></div></div></section></div></t></t>"""),
        "fr_FR": ("Déclaration d’accessibilité", """<t name="Déclaration d’accessibilité" t-name="website.facodi_accessibility"><t t-call="website.layout"><div id="wrap" class="oe_structure"><section class="facodi-section facodi-grid-paper"><div class="container"><div class="facodi-sheet"><p class="facodi-kicker">Accessibilité</p><h1><span class="facodi-highlight">L’apprentissage doit rester accessible à tous.</span></h1></div></div></section></div></t></t>"""),
    },
}

for url, spec in PAGES.items():
    en_name, en_arch = spec["en_GB"]
    view = _upsert_view(spec["key"], en_name, en_arch)
    _upsert_page(url, en_name, view)
    for lang in LANGS:
        name, arch = spec[lang]
        _set_translation(view, lang, name, arch)

env.cr.commit()
print("FACODI editorial recovery complete: homepage, /about and %s public pages" % len(PAGES))
